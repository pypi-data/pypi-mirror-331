import numpy as np
import scipy.stats as stats
import pandas as pd
from scipy.optimize import minimize
from joblib import Parallel, delayed
from tqdm import tqdm
import anndata
import scipy.sparse as sp


# Poisson log-likelihood
def poisson_loglikelihood(mu, x):
    return -np.sum(stats.poisson.logpmf(x, mu))

# ZIP log-likelihood (pi and lambda are optimized)
def zip_loglikelihood_fixed_mu(pi_lambda, x):
    pi, mu = pi_lambda
    x_is_zero = (x == 0)
    ll_zero = x_is_zero * np.log(pi + (1 - pi) * np.exp(-mu))
    ll_nonzero = ~x_is_zero * (np.log(1 - pi) + stats.poisson.logpmf(x, mu))
    return -np.sum(ll_zero + ll_nonzero)

# ZINB log-likelihood (pi, r, and p are optimized)
def zinb_loglikelihood_fixed_mu(params, x):
    pi, r, p = params
    p_nb = r / (r + p)
    x_is_zero = (x == 0)
    ll_zero = x_is_zero * np.log(pi + (1 - pi) * stats.nbinom.pmf(0, r, p_nb))
    ll_nonzero = ~x_is_zero * (np.log(1 - pi) + stats.nbinom.logpmf(x, r, p_nb))
    return -np.sum(ll_zero + ll_nonzero)

# Negative Binomial log-likelihood
def nb_loglikelihood_fixed_mu(r, x, mu):
    p = r / (r + mu)
    return -np.sum(stats.nbinom.logpmf(x, r, p))

def fit_with_simulated_mean_and_var(gene, simulated_mean, simulated_var, n_total, n_true, maxiter=100):
    epsilon = 1e-10
    try:
        mu_sim = max(simulated_mean, epsilon)  # Ensure mean is positive
        var_sim = max(simulated_var, epsilon)  # Ensure variance is positive
        n_true = max(n_true, 1)
        zero_prop_obs = 1 - (n_true / n_total)

        # Poisson
        try:
            ll_poisson = -poisson_loglikelihood(mu_sim, gene)
            aic_poisson = 2 * 1 - 2 * ll_poisson
        except:
            ll_poisson = -np.inf
            aic_poisson = np.inf

        # Negative Binomial
        is_nb_valid = (var_sim - mu_sim) > epsilon
        if is_nb_valid:
            try:
                r_nb = mu_sim**2 / (var_sim - mu_sim)
                if r_nb > 0:
                    ll_nb = -nb_loglikelihood_fixed_mu(r_nb, gene, mu_sim)
                    aic_nb = 2 * 2 - 2 * ll_nb
                else:
                    ll_nb = -np.inf
                    aic_nb = np.inf
                    r_nb = None
            except:
                ll_nb = -np.inf
                aic_nb = np.inf
                r_nb = None
        else:
            ll_nb = -np.inf
            aic_nb = np.inf
            r_nb = None

        # ZIP optimization
        try:
            result_zip = minimize(
                zip_loglikelihood_fixed_mu, 
                [0.5, mu_sim],  # Initial guess for pi and lambda
                args=(gene,), 
                bounds=[(1e-6, 1 - 1e-6), (1e-6, None)], 
                method='L-BFGS-B',
                options={'maxiter': maxiter}
            )
            pi_true_zip, mu_corrected_zip = result_zip.x
            ll_zip = -result_zip.fun
            aic_zip = 2 * 2 - 2 * ll_zip  # ZIP has 2 parameters (pi, lambda)
        except:
            ll_zip = -np.inf
            aic_zip = np.inf
            pi_true_zip = 0

        # ZINB optimization
        if is_nb_valid:
            try:
                result_zinb = minimize(
                    zinb_loglikelihood_fixed_mu, 
                    [0.5, r_nb, mu_sim],  # Initial guess for pi, r, and p
                    args=(gene,), 
                    bounds=[(1e-6, 1 - 1e-6), (1e-6, None), (1e-6, None)], 
                    method='L-BFGS-B',
                    options={'maxiter': maxiter}
                )
                pi_true_zinb, r_zinb, p_zinb = result_zinb.x
                ll_zinb = -result_zinb.fun
                aic_zinb = 2 * 3 - 2 * ll_zinb  # ZINB has 3 parameters (pi, r, p)
            except:
                ll_zinb = -np.inf
                aic_zinb = np.inf
                pi_true_zinb = 0
        else:
            ll_zinb = -np.inf
            aic_zinb = np.inf

        # Model Selection
        aics = [aic_nb if is_nb_valid else np.inf,
                aic_zinb if is_nb_valid else np.inf,
                aic_zip,
                aic_poisson]
        
        best_model_idx = np.argmin(aics)

        if best_model_idx == 0:
            if not is_nb_valid or r_nb is None:
                model_selected = "Poisson"
                pi0_est = 1 - np.mean(gene > 0)
                theta_est = mu_sim
            else:
                model_selected = "NB"
                theta_est = r_nb
                pi0_est = 1 - np.mean(gene > 0)
        elif best_model_idx == 1:
            model_selected = "ZINB"
            pi0_est = pi_true_zinb
            theta_est = r_zinb
        elif best_model_idx == 2:
            model_selected = "ZIP"
            pi0_est = pi_true_zip
            theta_est = mu_corrected_zip
        else:
            model_selected = "Poisson"
            pi0_est = 1 - np.mean(gene > 0)
            theta_est = mu_sim

        return [pi0_est, theta_est, mu_sim, model_selected]
    
    except:
        return [0, 0, 0, "Poisson"]

# Overall model fitting function
def fit_marginal_model_with_simulated_params(adata, simulated_means, simulated_vars,
                                             maxiter=500, n_jobs=-1):
    if not isinstance(adata, anndata.AnnData):
        raise ValueError("Input adata should be an AnnData object")

    if sp.issparse(adata.X):
        x = adata.X.toarray()
    else:
        x = adata.X

    gene_names = adata.var_names.tolist()
    n_total, p = x.shape

    if len(simulated_means) != p or len(simulated_vars) != p:
        raise ValueError("Length of simulated parameters does not match number of genes")

    # Calculate n_true for each gene
    n_trues = []
    for i in range(p):
        n_zero = np.sum(x[:, i] == 0)
        n_trues.append(max(n_total - n_zero, 1))

    results = Parallel(n_jobs=n_jobs)(
        delayed(fit_with_simulated_mean_and_var)(
            x[:, i],
            max(simulated_means[gene_names[i]], 1e-10),
            max(simulated_vars[gene_names[i]], 1e-10),
            n_total,
            n_trues[i],
            maxiter
        )
        for i in tqdm(range(p), desc="Fitting models")
    )

    params_df = pd.DataFrame(results,
                             index=gene_names,
                             columns=['pi0', 'theta', 'mu', 'model_selected'])

    model_params = {
        'genes': {i: gene_names[i] for i in range(p)},
        'marginal_param1': params_df[['pi0', 'theta', 'mu']].values.tolist(),
        'model_selected': params_df['model_selected'].tolist(),
        'n_cell': n_total,
        'n_read': np.sum(x)
    }

    return model_params