import numpy as np
import scipy.sparse as sp
import scanpy as sc
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from tqdm import tqdm
from joblib import Parallel, delayed
import numba as nb
from numba.typed import List

class GeneExpressionReordererOptimized:
    def __init__(self, adata1, adata2, adata3, pi_13, pi_23, n_top_genes=1000, spatial_sigma=1.0, use_spatial_consistency=True, spatial_weight=0.5, n_jobs=4, k_neighbors=30):
        self.n_jobs = n_jobs
        self.common_genes = self._get_common_genes(adata1, adata2, adata3, n_top_genes)
        self.adata3_raw = adata3[:, self.common_genes].copy()
        
        if sp.issparse(self.adata3_raw.X):
            self.original_counts = self.adata3_raw.X.toarray().astype(np.int32)
        else:
            self.original_counts = self.adata3_raw.X.copy().astype(np.int32)
        
        self.calc_layers = self._create_calc_layers(adata1, adata2, adata3)
        self.transport_plans = self._prepare_transport_plans(pi_13, pi_23)
        self.spatial_prob_matrix, self.spatial_neighbors = self._compute_spatial_prob_matrix(adata3, sigma=spatial_sigma, k=k_neighbors)
        self.ref_gene_expr = self._precompute_reference_gene_expr()
        self.transported_expr = self._precompute_transported_expr()
        self.gene_sums = np.sum(self.original_counts, axis=0) + 1e-10
        self.use_spatial_consistency = use_spatial_consistency
        self.spatial_weight = spatial_weight

    def _get_common_genes(self, adata1, adata2, adata3, n_top_genes):
        common = adata1.var_names.intersection(adata2.var_names).intersection(adata3.var_names)
        if len(common) > n_top_genes:
            adata1_sub = adata1[:, common].copy()
            adata2_sub = adata2[:, common].copy()
            adata3_sub = adata3[:, common].copy()
            sc.pp.normalize_total(adata1_sub)
            sc.pp.normalize_total(adata2_sub)
            sc.pp.normalize_total(adata3_sub)
            sc.pp.log1p(adata1_sub)
            sc.pp.log1p(adata2_sub)
            sc.pp.log1p(adata3_sub)
            var1 = np.var(adata1_sub.X.toarray() if sp.issparse(adata1_sub.X) else adata1_sub.X, axis=0)
            var2 = np.var(adata2_sub.X.toarray() if sp.issparse(adata2_sub.X) else adata2_sub.X, axis=0)
            var3 = np.var(adata3_sub.X.toarray() if sp.issparse(adata3_sub.X) else adata3_sub.X, axis=0)
            avg_var = (var1 + var2 + var3) / 3
            top_indices = np.argsort(avg_var)[-n_top_genes:]
            common = np.array(list(common))[top_indices]
        return list(common)

    def _create_calc_layers(self, adata1, adata2, adata3):
        layers = []
        for adata in [adata1, adata2, adata3]:
            adata_subset = adata[:, self.common_genes].copy()
            sc.pp.normalize_total(adata_subset, target_sum=1e4)
            sc.pp.log1p(adata_subset)
            if sp.issparse(adata_subset.X):
                layers.append(adata_subset.X.toarray().astype(np.float32))
            else:
                layers.append(adata_subset.X.astype(np.float32))
        return layers

    def _prepare_transport_plans(self, pi_13, pi_23):
        n_cells1 = self.calc_layers[0].shape[0]
        n_cells2 = self.calc_layers[1].shape[0]
        n_cells3 = self.calc_layers[2].shape[0]
        if sp.issparse(pi_13):
            pi_13 = pi_13.toarray()
        if sp.issparse(pi_23):
            pi_23 = pi_23.toarray()
        if pi_13.shape == (n_cells1, n_cells3):
            pi_13 = pi_13.T
        if pi_23.shape == (n_cells2, n_cells3):
            pi_23 = pi_23.T
        return {'pi_13': pi_13, 'pi_23': pi_23}

    def _compute_spatial_prob_matrix(self, adata, sigma=1.0, k=30):
        coords = adata.obsm['spatial']
        n_cells = coords.shape[0]
        nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree').fit(coords)
        distances, indices = nbrs.kneighbors(coords)
        rows = []
        cols = []
        data = []
        for i in range(n_cells):
            for j in range(1, indices.shape[1]):
                idx = indices[i, j]
                dist = distances[i, j]
                prob = np.exp(-dist**2 / (2 * sigma**2))
                rows.append(i)
                cols.append(idx)
                data.append(prob)
        prob_matrix = sp.csr_matrix((data, (rows, cols)), shape=(n_cells, n_cells))
        row_sums = prob_matrix.sum(axis=1).A.ravel()
        prob_matrix = prob_matrix.multiply(1 / (row_sums + 1e-10)).tocsr()
        
        # 使用 Numba 的 typed.List 替代 Python 的 list
        spatial_neighbors = List()
        for i in range(n_cells):
            _, cols = prob_matrix[i].nonzero()
            spatial_neighbors.append(np.array(cols, dtype=np.int32))
        return prob_matrix, spatial_neighbors

    def _precompute_reference_gene_expr(self):
        ref_expr = [np.empty((len(self.common_genes), layer.shape[0]), dtype=np.float32) for layer in self.calc_layers[:2]]
        for dataset_idx, layer in enumerate(self.calc_layers[:2]):
            for gene_idx in range(len(self.common_genes)):
                gene_expr = layer[:, gene_idx].copy()
                gene_expr /= (np.sum(gene_expr) + 1e-10)
                ref_expr[dataset_idx][gene_idx] = gene_expr
        return ref_expr

    def _precompute_transported_expr(self):
        transported = [np.empty((len(self.common_genes), self.calc_layers[2].shape[0]), dtype=np.float32) for _ in range(2)]
        for gene_idx in range(len(self.common_genes)):
            transported[0][gene_idx] = self.transport_plans['pi_13'] @ self.ref_gene_expr[0][gene_idx]
            transported[1][gene_idx] = self.transport_plans['pi_23'] @ self.ref_gene_expr[1][gene_idx]
        return transported

    @staticmethod
    @nb.njit(fastmath=True)
    def _compute_alignment_loss_incremental(gene_counts, transported1, transported2, pos1, pos2, total_sum):
        old_val1 = gene_counts[pos1]
        old_val2 = gene_counts[pos2]
        old_expr1 = old_val1 / total_sum
        old_expr2 = old_val2 / total_sum
        new_expr1 = old_val2 / total_sum
        new_expr2 = old_val1 / total_sum
        diff1_old = abs(old_expr1 - transported1[pos1]) + abs(old_expr2 - transported1[pos2])
        diff2_old = abs(old_expr1 - transported2[pos1]) + abs(old_expr2 - transported2[pos2])
        diff1_new = abs(new_expr1 - transported1[pos1]) + abs(new_expr2 - transported1[pos2])
        diff2_new = abs(new_expr1 - transported2[pos1]) + abs(new_expr2 - transported2[pos2])
        return (diff1_new + diff2_new) - (diff1_old + diff2_old)

    @staticmethod
    @nb.njit(fastmath=True, parallel=True)
    def _compute_spatial_loss_incremental(gene_counts, transported1, transported2, spatial_neighbors, pos1, pos2, total_sum, spatial_weight, n_cells):
        old_val1 = gene_counts[pos1]
        old_val2 = gene_counts[pos2]
        new_val1 = old_val2
        new_val2 = old_val1
        affected = np.unique(np.concatenate((np.array([pos1, pos2]), spatial_neighbors[pos1], spatial_neighbors[pos2])))
        delta_loss = 0.0
        for idx in nb.prange(len(affected)):
            i = affected[idx]
            neighbors = spatial_neighbors[i]
            if len(neighbors) == 0:
                continue
            current_i = gene_counts[i] / total_sum
            current_diff = np.abs(current_i - gene_counts[neighbors]/total_sum)
            ref_diff1 = np.abs(transported1[i] - transported1[neighbors])
            ref_diff2 = np.abs(transported2[i] - transported2[neighbors])
            old_contribution = np.mean(np.abs(current_diff - ref_diff1)) + np.mean(np.abs(current_diff - ref_diff2))
            new_i = new_val1/total_sum if i == pos1 else (new_val2/total_sum if i == pos2 else current_i)
            new_neighbors = []
            for n in neighbors:
                new_neighbors.append(new_val1/total_sum if n == pos1 else (new_val2/total_sum if n == pos2 else gene_counts[n]/total_sum))
            new_diff = np.abs(new_i - np.array(new_neighbors))
            new_contribution = np.mean(np.abs(new_diff - ref_diff1)) + np.mean(np.abs(new_diff - ref_diff2))
            delta_loss += (new_contribution - old_contribution)
        return delta_loss * spatial_weight / n_cells

    def _compute_gene_alignment_loss(self, gene_idx, current_counts=None):
        if current_counts is None:
            gene_counts = self.original_counts[:, gene_idx]
        else:
            gene_counts = current_counts
        gene_expr = gene_counts.astype(np.float32) / (np.sum(gene_counts) + 1e-10)
        transported_expr1 = self.transported_expr[0][gene_idx]
        transported_expr2 = self.transported_expr[1][gene_idx]
        diff1 = np.sum(np.abs(gene_expr - transported_expr1))
        diff2 = np.sum(np.abs(gene_expr - transported_expr2))
        spatial_consistency = 0
        if self.use_spatial_consistency:
            for i in range(len(gene_expr)):
                neighbors = self.spatial_neighbors[i]
                if len(neighbors) > 0:
                    local_diff = np.abs(gene_expr[i] - np.mean(gene_expr[neighbors]))
                    spatial_consistency += local_diff
        total_loss = diff1 + diff2 + self.spatial_weight * spatial_consistency
        return total_loss

    def _optimize_gene_cluster(self, gene_idx, cluster_indices, local_iter, temp, structure_weight):
        gene_counts = self.optimized_counts[:, gene_idx].copy()
        n_cells = len(cluster_indices)
        if n_cells < 2:
            return gene_counts
        total_sum = self.gene_sums[gene_idx]
        transported1 = self.transported_expr[0][gene_idx]
        transported2 = self.transported_expr[1][gene_idx]
        for _ in range(max(1, local_iter * n_cells // 5)):
            pos1, pos2 = np.random.choice(cluster_indices, 2, replace=False)
            delta_alignment = self._compute_alignment_loss_incremental(gene_counts, transported1, transported2, pos1, pos2, total_sum)
            delta_spatial = 0.0
            if self.use_spatial_consistency:
                delta_spatial = self._compute_spatial_loss_incremental(gene_counts, transported1, transported2, self.spatial_neighbors, pos1, pos2, total_sum, self.spatial_weight, gene_counts.shape[0])
            delta_total = delta_alignment + structure_weight * delta_spatial
            if delta_total < 0 or np.random.random() < np.exp(-delta_total / temp):
                gene_counts[pos1], gene_counts[pos2] = gene_counts[pos2], gene_counts[pos1]
        return gene_counts

    def _optimize_hierarchical(self, n_clusters=30, local_iter=3, boundary_iter=2, temp=1.0, structure_weight=0.5):
        coords = self.adata3_raw.obsm['spatial']
        n_clusters = min(n_clusters, coords.shape[0] // 15)
        clustering = KMeans(n_clusters=n_clusters, random_state=0).fit(coords)
        clusters = clustering.labels_
        self.optimized_counts = self.original_counts.copy()
        gene_vars = np.var(self.calc_layers[2], axis=0)
        top_gene_indices = np.argsort(gene_vars)[-min(80, len(self.common_genes)):]
        for cluster_id in tqdm(range(n_clusters), desc="Cluster optimization"):
            cluster_mask = clusters == cluster_id
            cluster_indices = np.where(cluster_mask)[0]
            if len(cluster_indices) <= 1:
                continue
            results = Parallel(n_jobs=self.n_jobs, backend="threading")(delayed(self._optimize_gene_cluster)(gene_idx, cluster_indices, local_iter, temp, structure_weight) for gene_idx in top_gene_indices)
            for i, gene_idx in enumerate(top_gene_indices):
                self.optimized_counts[cluster_indices, gene_idx] = results[i][cluster_indices]
        if sp.issparse(self.adata3_raw.X):
            self.adata3_raw.X = sp.csr_matrix(self.optimized_counts)
        else:
            self.adata3_raw.X = self.optimized_counts
        self._update_calc_layer()
        return self.adata3_raw

    def _update_calc_layer(self):
        norm_counts = self.optimized_counts.astype(np.float32)
        row_sums = norm_counts.sum(axis=1, keepdims=True)
        norm_counts = np.divide(norm_counts, row_sums, where=row_sums!=0) * 1e4
        self.calc_layers[2] = np.log1p(norm_counts)

    def evaluate_alignment(self, gene_indices=None):
        if gene_indices is None:
            gene_indices = range(len(self.common_genes))
        gene_losses = {}
        total_loss = 0
        for gene_idx in gene_indices:
            loss = self._compute_gene_alignment_loss(gene_idx)
            gene_losses[self.common_genes[gene_idx]] = loss
            total_loss += loss
        return total_loss, gene_losses

    def optimize(self, method='hierarchical', **kwargs):
        if method == 'hierarchical':
            return self._optimize_hierarchical(**kwargs)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
