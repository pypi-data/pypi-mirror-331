from interpolation_gene_expression import GeneExpressionReordererOptimized
from interpolation_spatial import spatial_interpolation
from simulator import simulation_slice


def run_interpolation(
    adjacent_adatas, 
    reference_adatas=None, 
    method='sequencing',
    inter_pos=[0.5],
    spatial_params=None,
    simulation_params=None,
    reorderer_params=None,
    optimization_params=None
):
    if not sorted(inter_pos) == inter_pos:
        inter_pos = sorted(inter_pos)
    
    adata1 = adjacent_adatas[0]
    adata2 = adjacent_adatas[1]
    
    _spatial_params = {'s': 0.7}
    if spatial_params:
        _spatial_params.update(spatial_params)
    
    _simulation_params = {}
    if simulation_params:
        _simulation_params.update(simulation_params)
    
    _reorderer_params = {
        'n_top_genes': 2000,
        'n_jobs': 8,
        'k_neighbors': 15
    }
    if reorderer_params:
        _reorderer_params.update(reorderer_params)
    
    _optimization_params = {
        'method': 'hierarchical',
        'n_clusters': 25,
        'local_iter': 5,
        'temp': 1.0,
        'structure_weight': 0.3
    }
    if optimization_params:
        _optimization_params.update(optimization_params)
    
    all_adatas = [adata1, adata2]
    all_pis = {}
    
    if reference_adatas is None:
        ref_adatas = [adata1, adata2]
    else:
        ref_adatas = reference_adatas.copy()
    
    binary_tree = generate_binary_tree(inter_pos)
    processed_positions = set([0.0, 1.0])
    
    for level in binary_tree:
        for pos in level:
            if pos in processed_positions:
                continue
                
            processed_positions.add(pos)
            
            left_idx = find_nearest_left_position(pos, all_adatas)
            right_idx = find_nearest_right_position(pos, all_adatas)
            
            left_adata = all_adatas[left_idx]
            right_adata = all_adatas[right_idx]
            
            _, _, interpolation_adata, pi_left, pi_right, _ = spatial_interpolation(
                [left_adata, right_adata], 
                method=method,
                **_spatial_params
            )
            
            modeling_adata = simulation_slice(
                interpolation_adata, 
                threeD=True, 
                ref_adatas=ref_adatas,
                **_simulation_params
            )
            
            reorderer = GeneExpressionReordererOptimized(
                left_adata, 
                right_adata, 
                modeling_adata, 
                pi_left, 
                pi_right, 
                **_reorderer_params
            )
            
            optimized_adata = reorderer.optimize(**_optimization_params)
            
            insert_position = find_insert_position(pos, all_adatas)
            all_adatas.insert(insert_position, optimized_adata)
            
            all_pis[f"{left_idx}_{insert_position}"] = pi_left
            all_pis[f"{right_idx}_{insert_position}"] = pi_right
            
            ref_adatas.append(optimized_adata)
    
    return all_adatas, all_pis

def generate_binary_tree(positions):
    positions = [0.0] + positions + [1.0]
    positions = sorted(list(set(positions)))
    
    tree = []
    queue = [(0, len(positions) - 1)]
    
    while queue:
        level = []
        new_queue = []
        
        for left, right in queue:
            if right - left <= 1:
                continue
                
            mid = (left + right) // 2
            level.append(positions[mid])
            new_queue.append((left, mid))
            new_queue.append((mid, right))
        
        if level:
            tree.append(level)
        queue = new_queue
    
    remaining = set(positions[1:-1]) - set(sum(tree, []))
    if remaining:
        tree.append(list(remaining))
    
    return tree

def find_nearest_left_position(pos, adatas):
    positions = [0.0]
    for i, adata in enumerate(adatas):
        if hasattr(adata, 'position') and adata.position < pos:
            positions.append((i, adata.position))
    
    positions.sort(key=lambda x: x[1], reverse=True)
    return positions[0][0] if len(positions) > 0 else 0

def find_nearest_right_position(pos, adatas):
    positions = [(len(adatas)-1, 1.0)]
    for i, adata in enumerate(adatas):
        if hasattr(adata, 'position') and adata.position > pos:
            positions.append((i, adata.position))
    
    positions.sort(key=lambda x: x[1])
    return positions[0][0] if len(positions) > 0 else len(adatas) - 1

def find_insert_position(pos, adatas):
    for i, adata in enumerate(adatas):
        if hasattr(adata, 'position') and adata.position > pos:
            return i
    return len(adatas)


