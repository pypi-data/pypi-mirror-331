import numpy as np
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')
from var_preprocess import get_initial_params
from var_distribution import gig_pdf

def calculate_aic(log_likelihood, n_params):
    """calculate AIC score"""
    return 2 * n_params - 2 * log_likelihood

def fit_gig(data, initial_guess=None):
    """fit generalized inverse gaussian distribution with enhanced robustness"""
    def negative_log_likelihood(params):
        alpha, beta, theta, k, lambda_ = params
        
        # 自适应正则化强度
        mean_param = np.mean([alpha, beta, k, lambda_])
        penalty = 0.01 * (alpha ** 2 + beta ** 2 + k ** 2 + lambda_ ** 2) / mean_param
        
        try:
            pdf_values = gig_pdf(data, alpha, beta, theta, k, lambda_)
            pdf_values = np.maximum(pdf_values, 1e-300)
            return -np.sum(np.log(pdf_values)) + penalty
        except:
            return np.inf

    # 根据数据特征设置参数边界
    data_mean = np.mean(data)
    data_median = np.median(data)
    data_std = np.std(data)
    data_range = np.ptp(data)
    
    bounds = [
        (0.1, max(100, data_std * 2)),  # alpha
        (0.1, max(50, data_std)),       # beta
        (max(0.1, data_mean - 2*data_std), data_mean + 2*data_std),  # theta
        (0, max(100, data_range/10)), # k
        (0, min(25, data_std))          # lambda
    ]

    if initial_guess is None:
        initial_guess = get_initial_params(data)

    # 生成多样化的初始猜测
    def generate_initial_guesses(data):
        guesses = []
        
        # 基本统计量
        q25, q75 = np.percentile(data, [25, 75])
        iqr = q75 - q25
        skew = np.mean((data - data_mean) ** 3) / (data_std ** 3)
        
        # 基于数据特征的猜测
        base_guesses = [
            [1.0, 1.0, data_mean, 1.0, 0.5],
            [0.5, 0.5, data_median, 0.5, 0.1],
            [2.0, 1.0, (data_mean + data_median)/2, 1.0, 0.3],
            [1.5, 0.8, q75, 0.8, 0.2],
            [0.8, 1.2, q25, 1.2, 0.4],
        ]
        guesses.extend(base_guesses)
        
        # 基于数据分布特征的猜测
        if skew > 0:  # 右偏分布
            guesses.extend([
                [2.0, 0.5, data_mean + data_std, 0.5, 0.1],
                [1.5, 0.3, q75 + iqr/2, 0.3, 0.2],
            ])
        else:  # 左偏分布
            guesses.extend([
                [0.5, 2.0, data_mean - data_std, 2.0, 0.1],
                [0.3, 1.5, q25 - iqr/2, 1.5, 0.2],
            ])
        
        # 添加一些随机扰动的猜测
        for _ in range(3):
            rand_factor = np.random.uniform(0.8, 1.2, 5)
            guesses.append([
                max(0.1, base_guesses[0][0] * rand_factor[0]),
                max(0.1, base_guesses[0][1] * rand_factor[1]),
                base_guesses[0][2] * rand_factor[2],
                max(0.1, base_guesses[0][3] * rand_factor[3]),
                max(0, min(25, base_guesses[0][4] * rand_factor[4]))
            ])
        
        return guesses

    best_fit = None
    best_likelihood = np.inf
    initial_guesses = generate_initial_guesses(data)
    
    # 优化设置
    options = {
        'maxiter': 1000,
        'ftol': 1e-6,
        'gtol': 1e-5
    }

    for guess in initial_guesses:
        try:
            result = minimize(
                negative_log_likelihood,
                guess,
                bounds=bounds,
                method='L-BFGS-B',
                options=options
            )

            if result.success and result.fun < best_likelihood:
                best_likelihood = result.fun
                best_fit = result.x
                
        except:
            continue

    if best_fit is None:
        # raise value error but not print
        raise ValueError('Using IG directly')

    return best_fit, best_likelihood