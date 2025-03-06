import numpy as np
import scipy.sparse as sp
import pandas as pd
import anndata
from scipy import stats


def extract_data(X):
    """calculate variances of genes from adata"""
    variances = np.var(X, axis=0, ddof=1)
    variances = np.nan_to_num(variances, nan=np.nanmean(variances))
    variances = np.maximum(variances, 1e-10)
    return variances


def get_initial_params(data):
    """get initial parameters for GIG fitting"""
    mean = np.mean(data)
    var = np.var(data)
    skewness = stats.skew(data)

    # predict initial values based on skewness
    alpha_init = max(0.1, (2 + skewness ** 2) / abs(skewness))
    beta_init = 1.0
    theta_init = mean * (alpha_init - 1) if alpha_init > 1 else mean
    k_init = 1.0
    lambda_init = 0.5

    return [alpha_init, beta_init, theta_init, k_init, lambda_init]


def fit_simple_ig(data):
    """fit simple inverse gamma distribution"""
    try:
        params = stats.invgamma.fit(data, floc=0)
        return {'alpha': params[0], 'scale': params[2]}
    except:
        return {'alpha': 1.0, 'scale': np.mean(data)}