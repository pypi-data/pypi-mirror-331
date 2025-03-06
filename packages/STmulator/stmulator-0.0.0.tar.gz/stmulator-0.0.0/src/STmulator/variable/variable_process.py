import anndata as ad
import numpy as np
import scipy.sparse as sp
from scipy.stats import poisson, bernoulli
from sklearn.utils import shuffle
from typing import Optional, Union
import warnings
import scanpy as sc
import alphashape
from shapely.geometry import Point, Polygon, MultiPolygon
import torch
from tqdm import tqdm
import time
from scipy.spatial import cKDTree
from scipy import sparse

def increase_sparsity(adata: ad.AnnData, sparsity_factor: float = 2.0,
                      cell_type_col: Optional[str] = None) -> ad.AnnData:
    """Increases sparsity by systematically adding zeros, simulating capture efficiency or biological variation."""
    if sparsity_factor < 1.0:
        raise ValueError("Sparsity factor must be greater than or equal to 1.0")

    X = adata.X.copy()
    if sp.issparse(X):
        X = X.toarray()  # Convert to dense array for easier manipulation

    n_genes = X.shape[1]

    if cell_type_col and cell_type_col in adata.obs.columns:
        cell_types = adata.obs[cell_type_col].unique()
        for cell_type in cell_types:
            cell_type_mask = adata.obs[cell_type_col] == cell_type
            for i in range(n_genes):
                gene_data = X[cell_type_mask, i]
                non_zero_indices = np.where(gene_data > 0)[0]
                n_non_zero = len(non_zero_indices)
                if n_non_zero == 0:
                    continue

                n_zeros_to_add = int(n_non_zero * (sparsity_factor - 1))

                if n_zeros_to_add > 0:
                    if n_zeros_to_add >= n_non_zero:
                        n_zeros_to_add = n_non_zero - 1
                        if n_zeros_to_add <= 0:
                            continue
                    cell_type_means = adata[cell_type_mask].obs.groupby(cell_type_col).apply(
                        lambda group: np.mean(X[group.index, i])
                    )
                    cell_type_probs = 1 / (cell_type_means + 1e-6)
                    cell_type_probs = cell_type_probs / cell_type_probs.sum()
                    probs = np.array([cell_type_probs[adata.obs[cell_type_col][j]] for j in np.where(cell_type_mask)[0][non_zero_indices]])
                    probs = probs / probs.sum() if probs.sum() > 0 else None  # Handle potential zero probability

                    indices_to_zero = np.random.choice(
                        non_zero_indices, size=min(n_zeros_to_add, len(non_zero_indices)), replace=False, p=probs
                    )
                    X[np.where(cell_type_mask)[0][indices_to_zero], i] = 0
    else:
        for i in range(n_genes):
            gene_data = X[:, i]
            non_zero_indices = np.where(gene_data > 0)[0]
            n_non_zero = len(non_zero_indices)
            if n_non_zero == 0:
                continue

            n_zeros_to_add = int(n_non_zero * (sparsity_factor - 1))

            if n_zeros_to_add > 0:
                if n_zeros_to_add >= n_non_zero:
                    n_zeros_to_add = n_non_zero - 1
                    if n_zeros_to_add <= 0:
                        continue

                sorted_indices = np.argsort(gene_data[non_zero_indices])
                indices_to_zero = non_zero_indices[sorted_indices[:n_zeros_to_add]]
                X[indices_to_zero, i] = 0


    adata_new = ad.AnnData(X=X, obs=adata.obs.copy(), var=adata.var.copy(), obsm=adata.obsm.copy(), uns=adata.uns.copy())
    if sp.issparse(adata.X):
        adata_new.X = sp.csr_matrix(adata_new.X)
    return adata_new


def subsample_genes(adata: ad.AnnData, subsampling_rate: float = 0.8,
                    highly_expressed: bool = False) -> ad.AnnData:
    """Subsamples genes, simulating limited sequencing depth, biological variability, or specific pathway focus."""
    if not (0.0 < subsampling_rate <= 1.0):
        raise ValueError("Subsampling rate must be between 0.0 and 1.0")

    n_genes = adata.shape[1]
    n_genes_to_keep = int(n_genes * subsampling_rate)

    if highly_expressed:
        gene_means = np.array(adata.X.mean(axis=0)).flatten()
        probs = gene_means / np.sum(gene_means)  # Ensure probabilities sum to 1
        selected_indices = np.random.choice(n_genes, size=n_genes_to_keep, replace=False, p=probs)
        selected_genes = adata.var_names[selected_indices]
    else:
        selected_genes = np.random.choice(adata.var_names, size=n_genes_to_keep, replace=False)

    return adata[:, selected_genes].copy()

    
def add_poisson_noise(adata: ad.AnnData, noise_level: float = 0.3,
                        background_noise_level: Optional[float] = None) -> ad.AnnData:
    """Adds Poisson noise to all values, simulating stochasticity in mRNA transcription, degradation, and technical noise."""
    X = adata.X.copy()
    if sp.issparse(X):
        X = X.toarray()

    if background_noise_level is None:
        background_noise_level = 0.1 * noise_level

    n_genes = X.shape[1]
    for i in range(n_genes):
        gene_data = X[:, i]
        non_zero_mask = gene_data > 0

        # Noise for non-zero values
        if np.any(non_zero_mask):  # Check for any non-zero values
            gene_mean = np.mean(gene_data[non_zero_mask])
            lambda_non_zero = gene_mean * noise_level
            noise_non_zero = poisson.rvs(mu=lambda_non_zero, size=np.sum(non_zero_mask))
            gene_data[non_zero_mask] += noise_non_zero

        # Noise for zero values
        lambda_zero = background_noise_level
        noise_zero = poisson.rvs(mu=lambda_zero, size=np.sum(~non_zero_mask))
        gene_data[~non_zero_mask] += noise_zero

        X[:, i] = gene_data  # Update the gene data in the matrix

    adata_new = ad.AnnData(X=X, obs=adata.obs.copy(), var=adata.var.copy(), obsm=adata.obsm.copy(), uns=adata.uns.copy())
    if sp.issparse(adata.X):
        adata_new.X = sp.csr_matrix(adata_new.X)
    return adata_new

import numpy as np
import scipy.sparse as sparse
import anndata as ad

def simulate_low_quality_data(
    adata,
    target_depth_factor=0.3,
    target_zero_increase=0.2,  
    celltype_specific_effects=None,  
    min_gene_expression=0.5,  
    verbose=True,  
):
    # Step 1: Poisson downsampling
    X = adata.X.copy()
    if sparse.issparse(X):
        X = X.toarray()
    
    original_zero_rate = np.mean(X == 0)
    
    if verbose:
        print(f"Original zero rate: {original_zero_rate:.2%}")
    
    for i in range(X.shape[0]):
        original_total = X[i].sum()
        new_total = np.random.poisson(original_total * target_depth_factor)
        if new_total > 0:
            # Calculate probabilities
            probs = X[i].astype(np.float64) / original_total.astype(np.float64)
            
            # Explicit correction for floating-point precision issues
            if not np.isclose(probs.sum(), 1.0, atol=1e-12):
                probs[-1] = 1.0 - probs[:-1].sum()
            probs = np.clip(probs, 0, 1)  # Ensure probabilities are in [0, 1]
            
            # Ensure sum is exactly 1.0 after adjustments and clipping
            probs_sum = probs.sum()
            if probs_sum > 0:
                probs = probs / probs_sum
            else:
                probs = np.ones_like(probs) / len(probs)  # Uniform if all zeros
            
            # Generate new counts using multinomial sampling
            X[i] = np.random.multinomial(new_total, probs)
        else:
            X[i] = np.zeros_like(X[i])  # No counts if new total is zero
    
    # Step 2: Logistic dropout
    gene_means = np.mean(X, axis=0)
    log_means = np.log1p(gene_means)
    
    if verbose:
        print("Calibrating dropout to achieve target zero rate...")
    
    def logistic_dropout(log_means, beta0, beta1):
        """Logistic dropout function."""
        return 1 / (1 + np.exp(-beta1 * (log_means - beta0)))
    
    def find_logistic_params(original_zero_rate, target_zero_rate):
        beta0 = 0.5  
        beta1 = 5 
        for _ in range(100):  
            dropout_probs = logistic_dropout(log_means, beta0, beta1)
            simulated_zero_rate = np.mean(np.random.rand(*X.shape) < dropout_probs)
            if simulated_zero_rate < target_zero_rate:
                beta0 -= 0.05  
            else:
                beta0 += 0.05 
        return beta0, beta1
    
    target_zero_rate = original_zero_rate + target_zero_increase
    target_zero_rate = np.clip(target_zero_rate, 0, 0.95)  # Prevent exceeding 95%
    
    beta0, beta1 = find_logistic_params(original_zero_rate, target_zero_rate)
    dropout_probs = logistic_dropout(log_means, beta0, beta1)
    dropout_mask = np.random.rand(*X.shape) < dropout_probs
    X[dropout_mask] = 0

    # Step 3: Cell type-specific effects (Optional)
    if celltype_specific_effects:
        for celltype, params in celltype_specific_effects.items():
            if celltype not in adata.obs:
                raise ValueError(f"Cell type '{celltype}' not found in adata.obs.")
            ct_mask = adata.obs[celltype] == celltype
            ct_beta0, ct_beta1 = find_logistic_params(
                original_zero_rate, 
                original_zero_rate + params.get("zero_increase", 0)
            )
            ct_probs = logistic_dropout(log_means, ct_beta0, ct_beta1)
            ct_dropout_mask = np.random.rand(*X[ct_mask].shape) < ct_probs
            X[ct_mask][ct_dropout_mask] = 0

    # Step 4: Apply minimum gene expression threshold
    X[X < min_gene_expression] = 0
    
    # Step 5: Calculate and report achieved zero rate
    simulated_zero_rate = np.mean(X == 0)
    if verbose:
        print(f"Target zero rate: {target_zero_rate:.2%}")
        print(f"Achieved zero rate: {simulated_zero_rate:.2%}")

    # Step 6: Return the modified AnnData object
    return ad.AnnData(
        X=sparse.csr_matrix(X) if sparse.issparse(adata.X) else X,
        obs=adata.obs.copy(),
        var=adata.var.copy()
    )


def generate_grid(spatial_coords_np, resolution_factor=1.0, method='hexagonal'):
    x_min, y_min = np.min(spatial_coords_np, axis=0)
    x_max, y_max = np.max(spatial_coords_np, axis=0)
    
    base_spots = len(spatial_coords_np)
    target_spots = int(base_spots * resolution_factor)
    
    if method == 'square':
        x_bins = np.linspace(x_min, x_max, int(np.sqrt(target_spots)))
        y_bins = np.linspace(y_min, y_max, int(np.sqrt(target_spots)))
        x_centers = (x_bins[:-1] + x_bins[1:]) / 2
        y_centers = (y_bins[:-1] + y_bins[1:]) / 2
        grid_x, grid_y = np.meshgrid(x_centers, y_centers)
        grid_coords = np.column_stack((grid_x.ravel(), grid_y.ravel()))
    
    elif method == 'hexagonal':
        spacing = np.sqrt((x_max - x_min) * (y_max - y_min) / target_spots)
        hex_centers = []
        for i in range(int((y_max - y_min) / spacing) + 1):
            for j in range(int((x_max - x_min) / spacing) + 1):
                x = x_min + j * spacing + (i % 2) * spacing / 2
                y = y_min + i * spacing * np.sqrt(3) / 2
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    hex_centers.append([x, y])
        grid_coords = np.array(hex_centers)
    
    else:
        raise ValueError(f"Unsupported grid generation method: {method}")
    
    return grid_coords


def generate_within_shape(spatial_coords_np, grid_coords_np, alpha=0.01):
    alpha_shape = alphashape.alphashape(spatial_coords_np, alpha)
    if isinstance(alpha_shape, MultiPolygon):
        polygons = list(alpha_shape.geoms)
    else:
        polygons = [alpha_shape]
    
    mask = np.array([
        any(polygon.contains(Point(p))) for p in grid_coords_np
    ])
    
    return grid_coords_np[mask]

def assign_gt_labels(spatial_coords_np, gt_labels, target_coords_np, mode='high'):
    tree = cKDTree(spatial_coords_np)
    
    if mode == 'high':
        k = min(5, len(spatial_coords_np))
        distances, indices = tree.query(target_coords_np, k=k)
        
        distances = torch.tensor(distances, dtype=torch.float32, device="cuda")
        indices = torch.tensor(indices, dtype=torch.long, device="cuda")

        weights = torch.exp(-distances**2 / (2 * torch.mean(distances, dim=1, keepdim=True)**2))
        weights = weights / torch.sum(weights, dim=1, keepdim=True)

        original_labels = np.array(gt_labels)
        target_gt_labels = np.array([
            np.random.choice(original_labels[indices[i].cpu().numpy()], p=weights[i].cpu().numpy())
            for i in range(len(target_coords_np))
        ])
        
        return target_gt_labels, None  

    else:
        k = min(10, len(spatial_coords_np))
        distances, indices = tree.query(target_coords_np, k=k)

        original_labels = np.array(gt_labels)
        unique_labels = np.unique(original_labels)

        gt_label_fractions = np.zeros((len(target_coords_np), len(unique_labels)))

        for i, neighbors in enumerate(indices):
            neighbor_labels = original_labels[neighbors]
            unique, counts = np.unique(neighbor_labels, return_counts=True)
            fractions = counts / counts.sum()
            
            for j, label in enumerate(unique_labels):
                if label in unique:
                    gt_label_fractions[i, j] = fractions[np.where(unique == label)[0][0]]

        gt_label_fractions_df = pd.DataFrame(gt_label_fractions, columns=unique_labels)

        return None, gt_label_fractions_df  


def distribute_counts_batch(spatial_coords_np, expression_matrix, target_coords_np, sequencing_depth_factor=1.0, mode='high', tree=None):
    spatial_coords = torch.tensor(spatial_coords_np, dtype=torch.float32, device="cuda")
    target_coords = torch.tensor(target_coords_np, dtype=torch.float32, device="cuda")
    expression_matrix = torch.tensor(expression_matrix, dtype=torch.float32, device="cuda")
    
    if mode == 'high':
        if tree is None:
            tree = cKDTree(spatial_coords_np)
        
        k = min(5, len(spatial_coords_np))
        distances, indices = tree.query(target_coords_np, k=k)
        
        distances = torch.tensor(distances, dtype=torch.float32, device="cuda")
        indices = torch.tensor(indices, dtype=torch.long, device="cuda")

        weights = torch.exp(-distances**2 / (2 * torch.mean(distances, dim=1, keepdim=True)**2))
        weights = weights / torch.sum(weights, dim=1, keepdim=True)

        predicted_counts = torch.zeros((len(target_coords), expression_matrix.shape[1]), device="cuda")

        batch_size = 1000
        for i in range(0, len(target_coords), batch_size):
            end_idx = min(i + batch_size, len(target_coords))
            batch_indices = indices[i:end_idx]
            batch_weights = weights[i:end_idx]
            batch_expression = expression_matrix[batch_indices]
            predicted_counts[i:end_idx] = torch.sum(batch_expression * batch_weights.unsqueeze(-1), dim=1)
    
    else:
        if tree is None:
            tree = cKDTree(target_coords_np)
        spot_assignments = tree.query(spatial_coords_np)[1]
        spot_assignments = torch.tensor(spot_assignments, dtype=torch.long, device="cuda")
        
        predicted_counts = torch.zeros((len(target_coords), expression_matrix.shape[1]), device="cuda")
        predicted_counts.scatter_add_(0, spot_assignments.unsqueeze(-1).expand(-1, expression_matrix.shape[1]), expression_matrix)
    
    total_original = torch.sum(expression_matrix, dim=0)
    target_total = total_original * sequencing_depth_factor
    scaling_factor = torch.where(torch.sum(predicted_counts, dim=0) > 0, target_total / torch.sum(predicted_counts, dim=0), torch.ones_like(total_original))
    predicted_counts *= scaling_factor
    
    return torch.poisson(predicted_counts)


def batch_process_slice(adata, resolution_factor=1.0, method='hexagonal', sequencing_depth=1.0, gt_key="cell_type"):
    spatial_coords_np = adata.obsm['spatial']
    expression_matrix = adata.X.toarray()
    
    has_gt = gt_key in adata.obs
    gt_labels = adata.obs[gt_key].values if has_gt else None

    grid_coords_np = generate_grid(spatial_coords_np, resolution_factor, method)
    grid_coords_np = generate_within_shape(spatial_coords_np, grid_coords_np)

    mode = 'high' if resolution_factor > 1 else 'low'
    target_gt_labels, gt_label_fractions = assign_gt_labels(spatial_coords_np, gt_labels, grid_coords_np, mode) if has_gt else (None, None)

    simulated_counts = distribute_counts_batch(spatial_coords_np, expression_matrix, grid_coords_np, sequencing_depth_factor=sequencing_depth, mode=mode)

    new_adata = sc.AnnData(X=simulated_counts.cpu().numpy(), var=adata.var)
    new_adata.obsm['spatial'] = grid_coords_np
    if has_gt:
        new_adata.obs = gt_label_fractions  

    return new_adata