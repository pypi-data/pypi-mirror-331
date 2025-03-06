import numpy as np
import scanpy as sc
import scipy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import autocast, GradScaler
from geomloss import SamplesLoss  


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
to_dense = lambda X: X.toarray() if scipy.sparse.issparse(X) else X
to_tensor = lambda arr: torch.tensor(arr, dtype=torch.float32, device=device)

def preprocess_data(adata):
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    return to_tensor(to_dense(adata.X))

def compute_3d_coords(coords_2d: torch.Tensor, z_value: float) -> torch.Tensor:
    z_coords = torch.full((coords_2d.shape[0], 1), z_value, device=coords_2d.device)
    return torch.cat([coords_2d, z_coords], dim=1)

class ModifiedOTLoss(nn.Module):
    def __init__(self, pi_13, pi_23, reg=0.1, blur=0.05):  # Add blur parameter
        super().__init__()
        self.pi_13 = pi_13.detach().clone()  
        self.pi_23 = pi_23.detach().clone()
        self.reg = reg
        self.blur = blur  # Blur for Sinkhorn
        self.sinkhorn_loss = SamplesLoss("sinkhorn", p=2, blur=self.blur, debias=True) # Initialize Sinkhorn loss

    def normalize_data(self, x):
        if x.requires_grad:
            return (x - x.mean()) / (x.std() + 1e-8)
        else:
            with torch.no_grad():
                return (x - x.mean()) / (x.std() + 1e-8)

    def forward(self, pred_C, A, B):
        A = A.detach()
        B = B.detach()

        pred_C_norm = self.normalize_data(pred_C)
        A_norm = self.normalize_data(A)
        B_norm = self.normalize_data(B)
        
        # Use Sinkhorn loss instead of efficient_distance
        loss_A = self.sinkhorn_loss(self.pi_13.sum(dim=1), A_norm, self.pi_13.sum(dim=0), pred_C_norm)
        loss_B = self.sinkhorn_loss(self.pi_23.sum(dim=1), B_norm, self.pi_23.sum(dim=0), pred_C_norm)

        # L2 regularization
        l2_reg = 0.01 * torch.norm(pred_C_norm, p=2)

        total_loss = loss_A + loss_B + l2_reg

        if torch.isnan(total_loss) or torch.isinf(total_loss):
            print("Warning: Loss is nan or inf")
            return torch.tensor(1.0, requires_grad=True, device=device)

        return total_loss

class ExpressionOptimizer(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.3),
            nn.Linear(256, input_dim)
        )

    def forward(self, x):
        return self.net(x)

def train_expression_optimizer(init_expression, expressionA, expressionB, 
                             pi_13_tensor, pi_23_tensor, n_epochs=1500, blur=0.05): #add blur


    model = ExpressionOptimizer(init_expression.shape[1]).to(device)
    criterion = ModifiedOTLoss(pi_13_tensor, pi_23_tensor, reg=0.1, blur=blur) #pass blur
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)


    scaler = GradScaler('cuda')

    scheduler = optim.lr_scheduler.OneCycleLR(optimizer, max_lr=0.001,
                                           steps_per_epoch=1, epochs=n_epochs)

    best_loss = float('inf')
    patience_counter = 0
    best_model_state = None

    for epoch in range(n_epochs):
        model.train()
        optimizer.zero_grad()

        with autocast('cuda'):
            pred_expressionC = model(init_expression)
            loss = criterion(pred_expressionC, expressionA, expressionB)

        # backward + optimize
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        scheduler.step()

        # early stopping
        if loss.item() < best_loss:
            best_loss = loss.item()
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1

        if patience_counter > 100:
            print(f"Early stopping at epoch {epoch}")
            break

        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.6f}, Best Loss: {best_loss:.6f}")

    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    return model

def optimize_intermediate_slice(slice1, slice2, slice3, pi_13, pi_23, blur=0.05):
    # preprocess
    for adata in [slice1, slice2, slice3]:
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

    common_genes = np.intersect1d(np.intersect1d(
        slice1.var_names, slice2.var_names), slice3.var_names)
    slice1 = slice1[:, common_genes]
    slice2 = slice2[:, common_genes]
    slice3 = slice3[:, common_genes]

    expressionA = to_tensor(to_dense(slice1.X)).requires_grad_(False)
    expressionB = to_tensor(to_dense(slice2.X)).requires_grad_(False)
    init_expressionC = to_tensor(to_dense(slice3.X)).requires_grad_(False)


    pi_13_tensor = to_tensor(pi_13.toarray()).requires_grad_(False)
    pi_23_tensor = to_tensor(pi_23.toarray()).requires_grad_(False)


    temp_adata = slice1.copy()
    sc.pp.highly_variable_genes(temp_adata, n_top_genes=min(1000, len(common_genes)))
    gene_mask = temp_adata.var.highly_variable.values

    # initialize expressionC
    initial_expressionC = torch.zeros_like(init_expressionC)


    with torch.no_grad():
        for gene_idx in range(expressionA.shape[1]):
            contrib_A = pi_13_tensor.T @ expressionA[:, gene_idx]
            contrib_B = pi_23_tensor.T @ expressionB[:, gene_idx]
            weights = pi_13_tensor.sum(0) + pi_23_tensor.sum(0)
            valid_mask = weights > 1e-6
            initial_expressionC[valid_mask, gene_idx] = (
                contrib_A[valid_mask] + contrib_B[valid_mask]
            ) / weights[valid_mask]


    important_genes = initial_expressionC[:, gene_mask].clone().requires_grad_(False)

    print("Starting optimized OT training...")
    model = train_expression_optimizer(
        important_genes,
        expressionA[:, gene_mask],
        expressionB[:, gene_mask],
        pi_13_tensor,
        pi_23_tensor,
        blur=blur  # Pass blur to the training function
    )

    with torch.no_grad(), autocast('cuda'):
        optimized_genes = model(important_genes)
        final_expressionC = initial_expressionC.clone()
        final_expressionC[:, gene_mask] = optimized_genes.float()  # 确保数据类型一致

    optimized_slice = slice3.copy()
    optimized_slice.X = final_expressionC.cpu().numpy()

    del model, important_genes, optimized_genes
    torch.cuda.empty_cache()

    return optimized_slice



