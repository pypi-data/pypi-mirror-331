import os
import warnings
import pickle
from multiprocessing import Pool
from joblib import Parallel, delayed
import time


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import sparse as sp
from scipy import stats
from scipy.stats import (
    genpareto, nbinom, poisson, bernoulli, invgamma
)
from scipy.optimize import minimize, minimize_scalar
from scipy.spatial.distance import cdist
from scipy.special import gammaln
from scipy.spatial import cKDTree
import scanpy as sc
import alphashape
from shapely.geometry import Point, Polygon, MultiPolygon
import torch
from tqdm import tqdm
import anndata as ad

# 自定义模块
from variable_process import increase_sparsity, subsample_genes, add_poisson_noise, simulate_low_quality_data,batch_process_slice

# import from other modules
from var_cal import simulate_gene_average_expression, simulate_gene_variances_advanced
from simulator_generation import simulator_remain_simulate_count
from simulator_fit import fit_marginal_model_with_simulated_params
from threed_val_cal import threeD_simulate_gene_variances_advanced


class SimulatorSRT:
    def __init__(self, adata, model_params):
        self.refCounts = adata.to_df()  
        self.refcolData = adata.obs.copy()  
        self.simcolData = None
        self.EstParam = [model_params]
        self.simCounts = None

def run_simulation_tissue(adata, var_adjust_ratio = None, mean_adjust_ratio = None):
    """Run the simulation of the spatial transcriptomics data in one whole slice model.""" 

    simulated_means = simulate_gene_average_expression(adata=adata, mean_adjust_ratio=mean_adjust_ratio)

    simulated_vars, var_threshold, var_evaluation= simulate_gene_variances_advanced(adata=adata, var_adjust_ratio=var_adjust_ratio)
    # Fit the marginal model
    model_params = fit_marginal_model_with_simulated_params(
        adata, 
        simulated_means, 
        simulated_vars, 
        maxiter=500, 
        n_jobs=-1
    )

    model_params['simulation_evaluation'] = {
        'variance': var_evaluation,
    }

    return model_params

def run_three_D_simulation_tissue(adata, ref_adatas):
    """Run the simulation of the spatial transcriptomics data in one whole slice model.""" 

    simulated_means = simulate_gene_average_expression(adata)

    simulated_vars, var_threshold, var_evaluation = threeD_simulate_gene_variances_advanced(ref_adatas, adata)
    # Fit the marginal model
    model_params = fit_marginal_model_with_simulated_params(
        adata, 
        simulated_means, 
        simulated_vars, 
        maxiter=500, 
        n_jobs=-1
    )

    model_params['simulation_evaluation'] = {
        'variance': var_evaluation,
    }

    return model_params

def combine_models(global_params, domain_params, alpha=0.1):
    """Combine global and domain-specific model parameters."""
    combined_params = {}
    for key in global_params:
        if key in ['genes']:
            combined_params[key] = global_params[key]
        elif key == 'marginal_param1':  
            global_genes = global_params['genes'].values()
            domain_genes = domain_params['genes'].values()
            
            combined_marginal_param1 = []
            for i, gene in enumerate(global_genes):
                if gene in domain_genes:  
                    domain_idx = list(domain_genes).index(gene)
                    # Using a weighted average of global and domain-specific parameters
                    combined_param = alpha * np.array(global_params[key][i]) + (1 - alpha) * np.array(domain_params[key][domain_idx])
                else:  
                    combined_param = global_params[key][i]
                
                # Ensure that the parameters are within valid ranges
                combined_param[0] = min(max(combined_param[0], 0), 1)  # pi 的范围是 [0, 1]
                combined_param[1] = max(combined_param[1], 1e-8)       # r 的最小值 1e-8，防止负值
                combined_param[2] = max(combined_param[2], 1e-8)       # mu 的最小值 1e-8
                
                combined_marginal_param1.append(combined_param)
            
            combined_params[key] = combined_marginal_param1
        else:
            combined_params[key] = global_params[key]

    # If the global and domain-specific models are inconsistent, use the domain-specific model
    for i, (global_model, domain_model) in enumerate(zip(global_params['model_selected'], domain_params['model_selected'])):
        if global_model != domain_model:
            print(f"Warning: Inconsistent model types for gene {i}. Using domain model {domain_model}.")
            
            # Use Domain model
            combined_params['model_selected'][i] = domain_model
            domain_param = domain_params['marginal_param1'][i]

            
            if domain_model == 'Poisson':
                combined_params['marginal_param1'][i][2] = domain_param[2]

            elif domain_model == 'NB':
                combined_params['marginal_param1'][i][1] = domain_param[1]
                combined_params['marginal_param1'][i][2] = domain_param[2]

            elif domain_model == 'ZIP':
                combined_params['marginal_param1'][i][0] = domain_param[0]
                combined_params['marginal_param1'][i][2] = domain_param[2]

            elif domain_model == 'ZINB':
                combined_params['marginal_param1'][i][0] = domain_param[0]
                combined_params['marginal_param1'][i][1] = domain_param[1]
                combined_params['marginal_param1'][i][2] = domain_param[2]

    return combined_params


def simulation_slice(adata, var_adjust_ratio = None, mean_adjust_ratio = None,threeD = False, ref_adatas = None):
    num_genes = adata.shape[1]
    
    # 动态调整 percent_top
    if num_genes < 50:
        percent_top = [10, 20]
    elif num_genes < 100:
        percent_top = [50, 100]
    else:
        percent_top = [50, 100, 200]
    
    # 计算 QC 指标
    sc.pp.calculate_qc_metrics(adata, percent_top=percent_top, inplace=True)
    adata = adata.copy()

    if threeD:
        model_params = run_three_D_simulation_tissue(adata, ref_adatas)
    else:
        model_params = run_simulation_tissue(adata = adata,var_adjust_ratio=var_adjust_ratio, mean_adjust_ratio=mean_adjust_ratio)

    simulator = SimulatorSRT(adata, model_params)

    simulated_simulator = simulator_remain_simulate_count(simulator, adata, num_cores=8, verbose=True)

    simulated_counts = simulated_simulator.simCounts

    if simulated_counts.shape != adata.shape:
        if simulated_counts.shape == (adata.shape[1], adata.shape[0]):
            simulated_counts = simulated_counts.T  
        else:
            raise ValueError("Cannot adjust simulated_counts shape to match adata shape")

    simulated_adata = ad.AnnData(
        X=simulated_counts,
        obs=adata.obs.copy(),
        var=adata.var.copy(),
        obsm={'spatial': adata.obsm['spatial']}
    )

    simulated_adata.obs['total_counts'] = simulated_adata.X.sum(axis=1)
    simulated_adata.obs['n_genes'] = (simulated_adata.X > 0).sum(axis=1)

    return simulated_adata

def simulation_annotations(adata_with_annotation, type_key = "CellType"):
    adata = adata_with_annotation.copy()
    unique_ground_truths = adata.obs[type_key].unique()

    global_model_params = run_simulation_tissue(adata)

    split_adatas = {}
    domain_params = {}

    for ground_truth in unique_ground_truths:
        
        mask = adata.obs[type_key] == ground_truth
        
        new_adata = ad.AnnData(
            X=adata[mask].X.copy(),
            obs=adata[mask].obs.copy(),
            var=adata.var.copy(),
            uns=adata.uns.copy(),
            obsm=adata[mask].obsm.copy() if adata.obsm is not None else None,
            varm=adata.varm.copy() if adata.varm is not None else None,
            layers=adata[mask].layers.copy() if adata.layers is not None else None
        )
        
        
        new_adata.obs_names_make_unique()
        
        split_adatas[ground_truth] = new_adata
        domain_params[ground_truth] = run_simulation_tissue(new_adata)


    simulated_adatas = {}
    alpha = 0.1

    for ground_truth, split_adata in split_adatas.items():
        print(f"Simulating Ground Truth: {ground_truth}")
    
        combined_params = combine_models(global_model_params, domain_params[ground_truth], alpha)
        simulatorSRT = SimulatorSRT(split_adata, combined_params)
        
        simulated_SimulatorSRT = simulator_remain_simulate_count(simulatorSRT, split_adata, num_cores=8, verbose=True)
        simulated_counts = simulated_SimulatorSRT.simCounts
        
        if simulated_counts.shape != split_adata.shape:
            print(f"Warning: simulated_counts shape {simulated_counts.shape} does not match adata shape {split_adata.shape}")
            if simulated_counts.shape == (split_adata.shape[1], split_adata.shape[0]):
                simulated_counts = simulated_counts.T
            elif simulated_counts.shape != split_adata.shape:
                raise ValueError("Cannot adjust simulated_counts shape to match adata shape")
        
        simulated_adata = ad.AnnData(
            X=simulated_counts,
            obs=split_adata.obs.copy(),
            var=split_adata.var.copy(),
            obsm={'spatial': split_adata.obsm['spatial']}
        )
        simulated_adata = simulated_adata[simulated_adata.obs_names.isin(split_adata.obs_names)]
        simulated_adata.obs['total_counts'] = simulated_adata.X.sum(axis=1)
        simulated_adata.obs['n_genes'] = (simulated_adata.X > 0).sum(axis=1)

        simulated_adatas[ground_truth] = simulated_adata


    merged_simulated_adata = ad.concat(
        list(simulated_adatas.values()),
        axis=0,
        join='outer',
        merge='same',
        label=type_key,
        keys=list(simulated_adatas.keys())
    )


    merged_simulated_adata.obs_names_make_unique()

    return merged_simulated_adata


def after_simulation_alter(adata, resolution_factor=None, method='hexagonal', sequencing_depth=1.0,modified_sparsity = None, dropout_rate = None, gene_subsample_rate = None, 
                     noise_level = None, sparsity_cell_type_col = None, highly_expressed = False, 
                     background_noise_level = None, zero_prop_increase = None, cell_type_col = None):
    
    simulated_adata = adata.copy()

    if gene_subsample_rate is not None:
        simulated_adata = subsample_genes(simulated_adata, subsampling_rate=gene_subsample_rate, highly_expressed=highly_expressed)
    if modified_sparsity is not None:
        simulated_adata = increase_sparsity(simulated_adata, modified_sparsity, cell_type_col=sparsity_cell_type_col)
    if dropout_rate is not None:
        simulated_adata = simulate_low_quality_data(simulated_adata, target_depth_factor=dropout_rate,target_zero_increase=zero_prop_increase,verbose=False)
    if noise_level is not None:
        simulated_adata = add_poisson_noise(adata = simulated_adata, noise_level=noise_level, background_noise_level=background_noise_level)
    if resolution_factor is not None:
        simulated_adata = batch_process_slice(adata, resolution_factor, method, sequencing_depth)
    simulated_adata.X = np.round(simulated_adata.X).astype(int)
    return simulated_adata
    

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the simulation of the spatial transcriptomics data in one whole slice model.')
    parser.add_argument('--h5ad_file', type=str, help='The input file path of the spatial transcriptomics data.')
    parser.add_argument('--output_dir', type=str, help='The output file path of the simulated spatial transcriptomics data.')
    args = parser.parse_args()

    adata = sc.read_h5ad(args.h5ad_file)
    simulated_adata = simulation_slice(adata)

    simulated_adata.write(args.output_dir)