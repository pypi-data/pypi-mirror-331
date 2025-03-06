import scanpy as sc
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import scipy
from paste2 import PASTE2, projection
from var_cal import simulate_gene_variances_advanced
import anndata as ad
from scipy.sparse import csr_matrix
from scipy.spatial import distance_matrix, cKDTree
from scipy.optimize import linear_sum_assignment
from simulator import simulation_slice
from ot_optimization import optimize_intermediate_slice


def alignment_paste(adata1,adata2):
    adata1 = adata1.copy()
    adata2 = adata2.copy()
    com_genes = list(set(adata1.var_names) & set(adata2.var_names))
    
    adata1 = adata1[:,com_genes]
    adata2 = adata2[:,com_genes]


    pi_AB = PASTE2.partial_pairwise_align(adata1, adata2, s=0.7)
    pis = [pi_AB]
    slices = [adata1,adata2]

    aligned_slices = projection.partial_stack_slices_pairwise(slices, pis)

    return aligned_slices,pi_AB

def generate_sequencing_grid(midpoints, method='hexagonal'):
    """
    Generate a regular sequencing grid that covers the area of midpoints.
    Returns both the grid coordinates and the optimal mapping to midpoints.
    """
    x_min, y_min = np.min(midpoints, axis=0)
    x_max, y_max = np.max(midpoints, axis=0)
    
    # Add margin to ensure coverage
    margin = 0.1  # 10% margin
    width = x_max - x_min
    height = y_max - y_min
    x_min -= margin * width
    x_max += margin * width
    y_min -= margin * height
    y_max += margin * height
    
    # Estimate appropriate spacing based on point density
    area = (x_max - x_min) * (y_max - y_min)
    n_points = len(midpoints)
    estimated_spacing = np.sqrt(area / n_points)
    
    if method == 'hexagonal':
        # Use estimated spacing or adjust based on your data scale
        x_spacing = estimated_spacing
        y_spacing = x_spacing * np.sqrt(3)/2
        
        # Generate regular hexagonal grid
        grid_points = []
        y = y_min
        row = 0
        while y <= y_max:
            x = x_min + (row % 2) * (x_spacing/2)  # offset every other row
            while x <= x_max:
                grid_points.append([x, y])
                x += x_spacing
            y += y_spacing
            row += 1
        
        grid_points = np.array(grid_points)
    else:
        # Square grid if needed
        x_coords = np.arange(x_min, x_max + estimated_spacing, estimated_spacing)
        y_coords = np.arange(y_min, y_max + estimated_spacing, estimated_spacing)
        xx, yy = np.meshgrid(x_coords, y_coords)
        grid_points = np.column_stack((xx.ravel(), yy.ravel()))
    
    # Find optimal subset of grid points
    tree = cKDTree(grid_points)
    distances, nearest_grid = tree.query(midpoints)
    
    # Select grid points that are closest to any midpoint
    used_indices = np.unique(nearest_grid)
    selected_grid = grid_points[used_indices]
    
    # If we need more points, add nearest unused grid points
    if len(selected_grid) < len(midpoints):
        unused_mask = np.ones(len(grid_points), dtype=bool)
        unused_mask[used_indices] = False
        unused_points = grid_points[unused_mask]
        
        if len(unused_points) > 0:
            unused_tree = cKDTree(unused_points)
            _, additional_indices = unused_tree.query(midpoints, k=1)
            additional_points = unused_points[np.unique(additional_indices)]
            selected_grid = np.vstack([selected_grid, 
                                     additional_points[:len(midpoints)-len(selected_grid)]])
    
    # Ensure we have exactly the right number of points
    if len(selected_grid) > len(midpoints):
        # Keep the grid points closest to any midpoint
        tree = cKDTree(selected_grid)
        distances, _ = tree.query(midpoints)
        importance = np.zeros(len(selected_grid))
        for i, dist in enumerate(distances):
            importance[_[i]] += 1/max(dist, 1e-10)
        selected_indices = np.argsort(importance)[-len(midpoints):]
        selected_grid = selected_grid[selected_indices]
    
    return selected_grid

def calculate_weighted_expression(point, source_coords, source_expr):
    """Calculate weighted expression based on spatial distances."""
    distances = np.sqrt(np.sum((source_coords - point)**2, axis=1))
    distances = np.maximum(distances, 1e-10)
    weights = 1 / distances
    weights = weights / np.sum(weights)
    return np.average(source_expr, weights=weights, axis=0)

def generate_intermediate_slice(adata1, adata2, pi_AB, method='sequencing'):
    """
    Generate an intermediate slice between two spatial transcriptomics slices.
    
    Parameters:
    -----------
    adata1 : AnnData
        First slice data
    adata2 : AnnData
        Second slice data
    pi_AB : numpy.ndarray
        Alignment matrix between slices
    method : str
        Method for generating coordinates ('sequencing' or 'imaging')
        
    Returns:
    --------
    adata3 : AnnData
        Generated intermediate slice
    pi_13 : scipy.sparse.csr_matrix
        Alignment matrix between slice1 and intermediate slice
    pi_23 : scipy.sparse.csr_matrix
        Alignment matrix between slice2 and intermediate slice
    valid_pairs : list
        List of valid spot pairs used for generating the intermediate slice
    """
    
    # Filter spots with no alignments
    mask1 = pi_AB.sum(axis=1) > 0
    mask2 = pi_AB.sum(axis=0) > 0
    original_indices1 = np.where(mask1)[0]
    original_indices2 = np.where(mask2)[0]

    # Valid pairs (i,j) in original indices where pi_AB[i,j] > 0
    valid_rows, valid_cols = np.nonzero(pi_AB)
    valid = np.isin(valid_rows, original_indices1) & np.isin(valid_cols, original_indices2)
    valid_pairs = list(zip(valid_rows[valid], valid_cols[valid]))

    # Compute midpoints for valid pairs
    coords1 = adata1.obsm['spatial'][[i for i, j in valid_pairs]]
    coords2 = adata2.obsm['spatial'][[j for i, j in valid_pairs]]
    midpoints = (coords1 + coords2) / 2

    if method == 'sequencing':
        # Generate grid-based coordinates
        adjusted_coords = generate_sequencing_grid(midpoints, method='hexagonal')
        
        cost_matrix = distance_matrix(midpoints, adjusted_coords)
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        valid_pairs = [valid_pairs[i] for i in row_ind]
        
    else:  # imaging-based
        noise_scale = 0.05 * np.std(midpoints, axis=0)
        adjusted_coords = midpoints + np.random.normal(0, noise_scale, midpoints.shape)

    common_genes = np.intersect1d(adata1.var_names, adata2.var_names)


    X1 = adata1[:, common_genes].X
    X2 = adata2[:, common_genes].X

    if isinstance(X1, csr_matrix):
        X1 = X1.toarray()
    if isinstance(X2, csr_matrix):
        X2 = X2.toarray()

    # Create alignment matrices
    n1 = adata1.n_obs
    n2 = adata2.n_obs
    n3 = len(adjusted_coords)

    # Initialize alignment matrices
    pi_13 = csr_matrix((n1, n3), dtype=np.float32)
    pi_23 = csr_matrix((n2, n3), dtype=np.float32)

    # Fill alignment matrices with 1s for valid pairs
    for k in range(n3): 
        i, j = valid_pairs[k]
        pi_13[i, k] = 1
        pi_23[j, k] = 1

    X3 = np.zeros((n3, len(common_genes)))

    for k in range(n3):
        i, j = valid_pairs[k]
        # average expression for valid pairs
        X3[k] = (X1[i] + X2[j]) / 2

    adata3 = ad.AnnData(
        X=X3,
        obs=pd.DataFrame(index=[f'spot_{i}' for i in range(n3)]),
        var=pd.DataFrame(index=common_genes),
        obsm={'spatial': adjusted_coords},
    )

    return adata3, pi_13, pi_23, valid_pairs


def reverse_transformations(adata, original_target_sum=None):

    adata_reversed = adata.copy()

    # Step 1: Reverse log1p (X = exp(X) - 1)
    if scipy.sparse.issparse(adata_reversed.X):
        adata_reversed.X = adata_reversed.X.expm1()  # Sparse expm1
    else:
        adata_reversed.X = np.expm1(adata_reversed.X)

    # Step 2: Reverse normalization (X = X * (original_library_size / target_sum))
    if original_target_sum is not None:
        if scipy.sparse.issparse(adata_reversed.X):
            normalized_sums = np.array(adata_reversed.X.sum(axis=1)).flatten()  # Sum per cell
        else:
            normalized_sums = np.sum(adata_reversed.X, axis=1)
        scaling_factors = normalized_sums / original_target_sum
    else:
        print("WARNING: original_target_sum not provided. Inferring from data; results may be less accurate.")
        if scipy.sparse.issparse(adata_reversed.X):
            scaling_factors = np.array(adata_reversed.X.sum(axis=1)).flatten() / 1e4
        else:
            scaling_factors = np.sum(adata_reversed.X, axis=1) / 1e4

    # Apply scaling factors to reverse normalization
    if scipy.sparse.issparse(adata_reversed.X):
        scaling_matrix = scipy.sparse.diags(1 / scaling_factors)  # Reverse normalization
        adata_reversed.X = scaling_matrix @ adata_reversed.X
    else:
        adata_reversed.X = adata_reversed.X / scaling_factors[:, np.newaxis]

    # Step 3: Round to integers
    if scipy.sparse.issparse(adata_reversed.X):
        adata_reversed.X.data = np.round(adata_reversed.X.data)
    else:
        adata_reversed.X = np.round(adata_reversed.X)
    adata_reversed.layers['raw_counts'] = adata_reversed.X.copy()

    return adata_reversed



def simulate_intermediate_slice(adata1, adata2, pi_AB, method='sequencing',output = 'raw'):
    aligned_slices,pi_12 = alignment_paste(adata1, adata2)
    adata1 = aligned_slices[0]
    adata2 = aligned_slices[1]

    adata3, pi_13, pi_23, valid_pairs = generate_intermediate_slice(adata1, adata2, pi_12, method=method)

    simulated_initial_adata3 = simulation_slice(adata3, threeD = True, ref_adatas = [adata1,adata2])


    optimized_slice = optimize_intermediate_slice(adata1.copy(), adata2.copy(), adata3.copy(), pi_13, pi_23)
    
    if output == 'raw':
        adata_reversed = reverse_transformations(optimized_slice, original_target_sum=1e4)
        return adata_reversed, pi_13, pi_23, valid_pairs
    else:       
        return simulated_initial_adata3, pi_13, pi_23, valid_pairs




