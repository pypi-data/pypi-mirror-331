import numpy as np
import warnings
warnings.filterwarnings('ignore')
import anndata
import pandas as pd
from scipy import sparse as sp
from scipy import stats
from var_model_fit import fit_gig, calculate_aic
from var_preprocess import extract_data, get_initial_params, fit_simple_ig
from var_evaluation import evaluate_fit
from var_sim_helper import assess_tail_discreteness, simulate_gig, interpolate_tail_data
import scanpy as sc

class GIG_VarianceSimulator:
    def __init__(self):
        self.alpha = None
        self.beta = None
        self.theta = None
        self.k = None
        self.lambda_ = None
        self.threshold = None
        self.tail_data = None
        self.original_order = None
        self.original_data = None
        self.random_state = None
        self.model_type = None  # 'IG' or 'GIG'

    def fit(self, adata, percentile):
        """fit GIG and IG model"""
        try:
            if sp.issparse(adata.X):
                X = adata.X.toarray()
            else:
                X = adata.X

            self.original_data = extract_data(X)
            if not np.all(np.isfinite(self.original_data)):
                raise ValueError("Data contains non-finite values")

            self.original_order = np.argsort(self.original_data)
            sorted_data = np.sort(self.original_data)

            # simple IG fit
            ig_params = fit_simple_ig(sorted_data)

            best_score = 0
            best_evaluation = None
            chosen_threshold = None

            current_threshold = np.percentile(sorted_data, percentile)
            main_data = sorted_data[sorted_data <= current_threshold]
            tail_data = sorted_data[sorted_data > current_threshold]

            try:
                ig_aic = calculate_aic(-len(main_data) * np.log(stats.invgamma.pdf(main_data,
                                                                                ig_params['alpha'],
                                                                                scale=ig_params['scale'])).sum(), 2)

                # Pre-calculated the IG model; if it is good enough, we will choose it directly
                tem_main = stats.invgamma.rvs(ig_params['alpha'], scale=ig_params['scale'],
                                              size=len(main_data), random_state=self.random_state)
                tem_main = np.clip(tem_main, np.min(self.original_data), np.max(self.original_data))
                tem_main = np.sort(tem_main)
                tem_tail = np.sort(tail_data)

                tem_data = np.concatenate([tem_main, tem_tail])

                tem_evaluation = evaluate_fit(self.original_data, tem_data, percentile)
                # if the IG model is good enough, we will choose it directly
                if tem_evaluation["Correlation"] > 0.98 and tem_evaluation["KS Statistic"] < 0.05:
                    model_type = 'IG'
                    alpha = ig_params['alpha']
                    theta = ig_params['scale']
                    print("Choosing IG model in percentile, because is good enough", percentile)

                else:
                    # use IG model as initial guess
                    initial_guess = [ig_params['alpha'], 1, ig_params['scale'], 0.001, 0.001]
                    gig_params, gig_likelihood = fit_gig(main_data,initial_guess=initial_guess)
                    gig_aic = calculate_aic(gig_likelihood, 5)

                    if gig_aic < ig_aic:
                        model_type = 'IG'
                        alpha = ig_params['alpha']
                        theta = ig_params['scale']
                        
                    else:
                        model_type = 'GIG'
                        alpha = gig_params[0]
                        beta = gig_params[1]
                        theta = gig_params[2]
                        k = gig_params[3]
                        lambda_ = gig_params[4]
                       
                n_main = len(main_data)
                n_tail = len(tail_data)

                if model_type == 'IG':
                    new_main = stats.invgamma.rvs(alpha, scale=theta,
                                                  size=n_main, random_state=self.random_state)
                else:
                    new_main = simulate_gig(n_main, alpha, beta, theta, k, lambda_)

                # deal with tail data
                tail_type = assess_tail_discreteness(tail_data)
                if tail_type == 'discrete':
                    new_tail = self.random_state.choice(tail_data, size=n_tail, replace=True)
                else:
                    new_tail = interpolate_tail_data(tail_data, n_tail)

                # combine main and tail data
                new_samples = np.concatenate([new_main, new_tail])
                new_samples = np.clip(new_samples, np.min(self.original_data),
                                      np.max(self.original_data))

                evaluation = evaluate_fit(self.original_data, new_samples, percentile)

                score = (
                         evaluation["Relative Error"] +
                         evaluation["KS Statistic"] +
                         (1 - evaluation["Correlation"]))

                if score > best_score:
                    best_score = score
                    best_evaluation = evaluation
                    chosen_threshold = percentile
                    if model_type == 'IG':
                        self.alpha = alpha
                        self.theta = theta
                    else:
                        self.alpha = alpha
                        self.beta = beta
                        self.theta = theta
                        self.k = k
                        self.lambda_ = lambda_
                    self.model_type = model_type
                    self.threshold = chosen_threshold
                    self.tail_data = tail_data

            except Exception as e:
                raise
            if best_evaluation is None:
                raise ValueError("No valid fit found")

            return self, best_evaluation

        except Exception as e:
            print(f"Fitting failed: {str(e)}")
            # Fallback to simple IG
            ig_params = fit_simple_ig(self.original_data)
            self.model_type = 'IG'
            self.alpha = ig_params['alpha']
            self.theta = ig_params['scale']
            return self, {"Verdict": "Fallback to single component IG"}

    def simulate(self, n_samples ,tail_process=False):
        """simulate gene variances based on fitted model"""
        try:
            if self.threshold is None:
                print("Warning: Threshold is None, using default value of 95.")
                self.threshold = 95

            n_main = int(n_samples * self.threshold / 100)
            n_tail = n_samples - n_main

            # Generate main data
            if self.model_type == 'IG':
                new_main = stats.invgamma.rvs(self.alpha, scale=self.theta,
                                              size=n_main, random_state=self.random_state)
            else:
                new_main = simulate_gig(n_main, self.alpha, self.beta, self.theta, self.k, self.lambda_)

            # Generate tail data
            if tail_process:
                tail_type = assess_tail_discreteness(self.tail_data)
                if tail_type == 'discrete':
                    new_tail = self.random_state.choice(self.tail_data, size=n_tail, replace=True)
                else:
                    new_tail = interpolate_tail_data(self.tail_data, n_tail)
            else:
                # remain the same tail data
                new_tail = self.tail_data

            # Combine main and tail data
            new_samples = np.concatenate([new_main, new_tail])
            new_samples = np.clip(new_samples, np.min(self.original_data),
                                  np.max(self.original_data))
            new_samples = np.sort(new_samples)

            simulated_data = np.zeros_like(new_samples)
            simulated_data[self.original_order] = new_samples

            return simulated_data

        except Exception as e:
            return self.random_state.choice(self.original_data, size=n_samples, replace=True)

    def fit_and_simulate(self, adata, n_iterations=3,tail_process=False):
            print(f"Starting fit and simulate process...")
            """fit and simulate gene variances(main process)"""
            best_overall_simulation = None
            best_overall_evaluation = None
            best_overall_score = float('-inf')
            best_overall_threshold = None
            best_overall_params = None
            # pre-defined thresholds
            thresholds = [95,90,96,99,98,97,92]
            best_threshold_evaluation = None  

            for threshold in thresholds:
                best_threshold_simulation = None
                best_threshold_score = float('-inf')
                best_threshold_params = None

                for iteration in range(n_iterations):
                    self.random_state = np.random.RandomState(iteration)
                    self.threshold = threshold

                    try:
                        self, evaluation = self.fit(adata, threshold)
                        simulated_values = self.simulate(adata.n_vars,tail_process=tail_process)
                        final_evaluation = evaluate_fit(self.original_data, simulated_values,percentile=threshold)
                        print(final_evaluation)
                        weight = [0.5, 1, 2]
                        score = (weight[0] * (1 - final_evaluation["Relative Error"]) +
                                weight[1] * (1 - final_evaluation["KS Statistic"]) +
                                weight[2] * final_evaluation["Correlation"])

                        if score > best_threshold_score:
                            best_threshold_score = score
                            best_threshold_simulation = simulated_values
                            best_threshold_evaluation = final_evaluation  
                            best_threshold_params = {
                                'threshold': self.threshold,
                                'alpha': self.alpha,
                                'beta': self.beta if hasattr(self, 'beta') else None,
                                'theta': self.theta,
                                'k': self.k if hasattr(self, 'k') else None,
                                'lambda_': self.lambda_ if hasattr(self, 'lambda_') else None,
                                'model_type': self.model_type
                            }

                    except Exception as e:
                        continue
                
                if best_overall_evaluation and best_threshold_evaluation["KS Statistic"] < 0.06 and best_threshold_evaluation["Correlation"] > 0.95:
                    print(f"Early stopping at threshold {threshold}")
                    break

                if best_threshold_score > best_overall_score:
                    best_overall_score = best_threshold_score
                    best_overall_simulation = best_threshold_simulation
                    best_overall_evaluation = best_threshold_evaluation  
                    best_overall_threshold = threshold
                    best_overall_params = best_threshold_params
                print(f"Threshold {threshold} finished")
                print(f"Best score: {best_overall_score:.3f}")

            self.threshold = best_overall_threshold
            self.model_type = best_overall_params['model_type']
            self.alpha = best_overall_params['alpha']
            self.theta = best_overall_params['theta']

            if self.model_type == 'GIG':
                self.beta = best_overall_params['beta']
                self.k = best_overall_params['k']
                self.lambda_ = best_overall_params['lambda_']

            

            return best_overall_simulation, best_overall_evaluation



def simulate_gene_variances_advanced(adata, n_iterations=5, var_adjust_ratio=None):
    simulator = GIG_VarianceSimulator()
    try:
        simulated_values, final_evaluation = simulator.fit_and_simulate(adata, n_iterations)
        result_dict = dict(zip(adata.var_names, simulated_values))
        
        # 打印原始参数
        if simulator.model_type == 'GIG':
            params_str = []
            if simulator.alpha is not None:
                params_str.append(f"alpha: {simulator.alpha:.3f}")
            if simulator.beta is not None:
                params_str.append(f"beta: {simulator.beta:.3f}")
            if simulator.theta is not None:
                params_str.append(f"theta: {simulator.theta:.3f}")
            if simulator.k is not None:
                params_str.append(f"k: {simulator.k:.3f}")
            if simulator.lambda_ is not None:
                params_str.append(f"lambda: {simulator.lambda_:.3f}")
            print("GIG parameters - " + ", ".join(params_str))
        else:
            params_str = []
            if simulator.alpha is not None:
                params_str.append(f"alpha: {simulator.alpha:.3f}")
            if simulator.theta is not None:
                params_str.append(f"theta: {simulator.theta:.3f}")
            print("IG parameters - " + ", ".join(params_str))

        
        if var_adjust_ratio is not None:
            positive_key = ['beta', 'theta', 'lambda_']
            negative_key = ["alpha", 'k']
            for key in positive_key:
                if key in simulator.__dict__ and simulator.__dict__[key] is not None:
                    simulator.__dict__[key] = simulator.__dict__[key] * var_adjust_ratio
            for key in negative_key:
                if key in simulator.__dict__ and simulator.__dict__[key] is not None:
                    simulator.__dict__[key] = simulator.__dict__[key] / var_adjust_ratio
            
            # 打印调整后的参数
            if simulator.model_type == 'GIG':
                params_str = []
                if simulator.alpha is not None:
                    params_str.append(f"alpha: {simulator.alpha:.3f}")
                if simulator.beta is not None:
                    params_str.append(f"beta: {simulator.beta:.3f}")
                if simulator.theta is not None:
                    params_str.append(f"theta: {simulator.theta:.3f}")
                if simulator.k is not None:
                    params_str.append(f"k: {simulator.k:.3f}")
                if simulator.lambda_ is not None:
                    params_str.append(f"lambda: {simulator.lambda_:.3f}")
                print("Adjusted GIG parameters - " + ", ".join(params_str))
            
            else:
                params_str = []
                if simulator.alpha is not None:
                    params_str.append(f"alpha: {simulator.alpha:.3f}")
                if simulator.theta is not None:
                    params_str.append(f"theta: {simulator.theta:.3f}")
                print("Adjusted IG parameters - " + ", ".join(params_str))

            # generate new simulated values
            new_simulator = GIG_VarianceSimulator()
            for attr in ['alpha', 'beta', 'theta', 'k', 'lambda_', 'threshold', 'model_type']:
                if hasattr(simulator, attr):
                    setattr(new_simulator, attr, getattr(simulator, attr))
            new_simulator.original_data = simulator.original_data
            new_simulator.original_order = simulator.original_order
            new_simulator.random_state = simulator.random_state

            new_simulated_values = new_simulator.simulate(adata.n_vars)
            new_result_dict = dict(zip(adata.var_names, new_simulated_values))
            return new_result_dict, new_simulator.threshold, final_evaluation
        
        return result_dict, simulator.threshold, final_evaluation
        
    except Exception as e:
        print(f"Simulation failed: {str(e)}")
        raise

def simulate_gene_average_expression(adata, pseudocount=1, n_simulations=1000, mean_adjust_ratio=None):
    # 确保 adata.X 是一个稠密矩阵
    if sp.issparse(adata.X):
        X = adata.X.toarray()
    else:
        X = adata.X

    # 计算基因的总表达量
    gene_totals = X.sum(axis=0)

    # 加上伪计数，计算基因的平均表达量
    gene_totals_pseudo = gene_totals + pseudocount
    gene_mean_expression = gene_totals_pseudo / adata.shape[0]

    # 计算总的平均表达量
    total_mean_expression = gene_mean_expression.sum()

    # 计算基因表达的概率
    gene_expression_probs = gene_mean_expression / total_mean_expression

    # 确保概率严格归一化，修正累积误差
    gene_expression_probs = gene_expression_probs / gene_expression_probs.sum()
    gene_expression_probs[-1] += 1.0 - gene_expression_probs.sum()  # 修正最后一个值

    # 检查概率是否有效
    gene_expression_probs = np.clip(gene_expression_probs, 0, 1)
    if not np.isclose(gene_expression_probs.sum(), 1.0):
        raise ValueError("Probabilities do not sum to 1 after normalization.")

    # 模拟的总读数数目
    total_reads = int(total_mean_expression * n_simulations)

    # 使用多项分布模拟计数
    simulated_counts = np.random.multinomial(total_reads, gene_expression_probs)

    # 计算模拟的平均表达值
    precise_mu = simulated_counts / n_simulations

    # 确保基因名称和结果匹配
    assert len(adata.var_names) == len(precise_mu), "Gene names and probabilities do not match!"

    if mean_adjust_ratio is not None:
        precise_mu = precise_mu * mean_adjust_ratio
    
    # 返回结果
    return dict(zip(adata.var_names, precise_mu))

