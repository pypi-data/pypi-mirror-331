# import library
import numpy as np
import scipy.sparse as sp
from scipy.stats import (
    nbinom, 
    poisson, 
    bernoulli, 
)
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')
from joblib import Parallel, delayed
from multiprocessing import cpu_count

def simulate_gene_batch(gene_indices, gene_names, adata, model_params, rr):
    """Generate simulated gene expression data for a batch of genes based on the given model parameters."""
    batch_results = []
    for iter in gene_indices:
        gene_name = gene_names[iter]
        if gene_name in adata.var_names:
            gene_expr = adata[:, gene_name].X.toarray().flatten()
            # Sort the gene expression values, and keep the original order
            original_order = np.argsort(gene_expr)
            param = model_params['marginal_param1'][iter]
            model_type = model_params['model_selected'][iter]

            param = [float(p) if p != 'inf' else np.inf for p in param]
            
            # Simulate gene expression based on the selected model
            try:
                if model_type == 'Poisson':
                    lambda_param = param[2] * rr
                    sim_raw_expr = poisson.rvs(lambda_param, size=adata.shape[0])
                elif model_type == 'NB':
                    r_param = param[1]
                    # safeguard for r_param
                    r_param = np.maximum(r_param, 1e-10)

                    if np.isinf(r_param):
                        lambda_param = param[2] * rr
                        sim_raw_expr = poisson.rvs(lambda_param, size=adata.shape[0])
                    else:
                        p_param = r_param / (r_param + param[2] * rr)
                        r_param = np.maximum(r_param, 1e-8)
                        p_param = np.clip(p_param, 1e-8, 1 - 1e-8)
                        sim_raw_expr = nbinom.rvs(r_param, p_param, size=adata.shape[0])
                elif model_type == 'ZIP':
                    pi0 = param[0]
                    lambda_param = param[2] * rr
                    zero_mask = bernoulli.rvs(pi0, size=adata.shape[0])
                    sim_raw_expr = poisson.rvs(lambda_param, size=adata.shape[0]) * (1 - zero_mask)
                elif model_type == 'ZINB':
                    pi0 = param[0]
                    r_param = param[1]
                    p_param = r_param / (r_param + param[2] * rr)

                    if r_param <= 0 or not (0 < p_param < 1):
                        raise ValueError(f"Invalid parameters for nbinom: r = {r_param}, p = {p_param}")
                    
                    zero_mask = bernoulli.rvs(pi0, size=adata.shape[0])
                    sim_raw_expr = nbinom.rvs(r_param, p_param, size=adata.shape[0]) * (1 - zero_mask)
                else:
                    raise ValueError(f"Unknown model type: {model_type}")
                
            except Exception as e:
                print(f"Warning: Error simulating gene {gene_name} with {model_type} model: {e}")
                print("Falling back to Poisson distribution with mean as lambda")
                mean_expr = np.mean(gene_expr)
                sim_raw_expr = poisson.rvs(mean_expr, size=adata.shape[0])
            
            try:
                # Post-processing to preserve the original distribution
                sim_order = np.argsort(sim_raw_expr)
                final_expr = np.zeros_like(gene_expr)
                final_expr[original_order] = sim_raw_expr[sim_order]
                batch_results.append(final_expr)
            except Exception as e:
                print(f"Error in post-processing for gene {gene_name}: {e}")
                batch_results.append(sim_raw_expr)
        else:
            batch_results.append(np.zeros(adata.shape[0]))

    return np.array(batch_results)

def simulator_remain_simulate_count(simulator, adata, num_cores=None, verbose=False):
    """Main function to simulate gene expression data for all cell types based on the given model parameters."""
    if simulator.simcolData is None:
        simulator.simcolData = simulator.refcolData.copy()

    oldnum_loc = simulator.refcolData.shape[0]
    newnum_loc = simulator.simcolData.shape[0]
    param_res = simulator.EstParam[0] 

    # Calculate total counts in the old data
    total_count_old = adata.obs['total_counts'].sum()
    total_count_new = total_count_old  
    r = (total_count_new / newnum_loc) / (total_count_old / oldnum_loc) 

    if verbose:
        print(f"The ratio between the seqdepth per location is: {r}")

    # Generate the simulated count matrix
    p = len(param_res['genes'])  
    rawcount = np.zeros((p, newnum_loc), dtype=float)  

    if num_cores is None:
        num_cores = -1  # 让 joblib 自动选择最优核心数
    
    gene_names = list(param_res['genes'].values())
    
    # 优化批处理大小
    batch_size = max(1, p // (cpu_count() * 2))
    gene_batches = [range(i, min(i + batch_size, p)) 
                   for i in range(0, p, batch_size)]

    try:
        # 使用 joblib 进行并行处理
        results = Parallel(
            n_jobs=num_cores,
            verbose=10,
            backend='loky',
            prefer='processes'
        )(
            delayed(simulate_gene_batch)(
                batch, gene_names, adata, param_res, r
            ) for batch in gene_batches
        )

        # 处理结果
        for batch_idx, batch_result in enumerate(results):
            if batch_result is not None:
                batch_indices = gene_batches[batch_idx]
                for i, gene_idx in enumerate(batch_indices):
                    rawcount[gene_idx, :] = batch_result[i, :]

    except Exception as e:
        print(f"Error in parallel processing: {e}")
        raise

    # Handle all-zero genes
    all_zero_idx = np.where(np.sum(rawcount, axis=1) == 0)[0]
    if len(all_zero_idx) > 0:
        for idx in all_zero_idx:
            nonzero_idx = np.random.choice(newnum_loc, 1)[0]
            rawcount[idx, nonzero_idx] = 1

    outcount = np.round(rawcount).astype(int)
    simulator.simCounts = sp.csr_matrix(outcount)

    return simulator