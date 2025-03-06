import numpy as np
from scipy import stats



# def cohens_d(x1, x2):
#     n1, n2 = len(x1), len(x2)
#     var1, var2 = np.var(x1, ddof=1), np.var(x2, ddof=1)
#     pooled_se = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
#     return (np.mean(x1) - np.mean(x2)) / pooled_se


def relative_error(x1, x2, method='mean', threshold=None):
    x1 = np.asarray(x1)
    x2 = np.asarray(x2)
    
    if x1.shape != x2.shape:
        raise ValueError("Arrays must have the same shape")
    
    # 应用阈值过滤
    if threshold is not None:
        mask = (np.abs(x1) > threshold) & (x1 != 0)
    else:
        mask = (x1 != 0)
    
    if not np.any(mask):
        return 0.0
        
    relative_errors = np.zeros_like(x1, dtype=float)
    relative_errors[mask] = np.abs(x1[mask] - x2[mask]) / np.abs(x1[mask])
    
    if method == 'mean':
        return np.mean(relative_errors[mask])
    elif method == 'median':
        return np.median(relative_errors[mask])
    elif method == 'max':
        return np.max(relative_errors[mask])
    else:
        raise ValueError("Unknown method")

def evaluate_fit(original, generated, percentile):
    
    # 计算相关性
    # 选择小于指定百分位数的数据
    threshold_orig = np.percentile(original, percentile)
    threshold_gen = np.percentile(generated, percentile)
    
    # 筛选数据
    filtered_orig = original[original <= threshold_orig]

    filtered_gen = generated[generated <= threshold_gen]

    # 确保数据长度相同
    min_length = min(len(filtered_orig), len(filtered_gen))
    filtered_orig = np.sort(filtered_orig)[:min_length]
    filtered_gen = np.sort(filtered_gen)[:min_length]
    rel_error = relative_error(filtered_orig, filtered_gen)

    ks_stat, _ = stats.ks_2samp(filtered_orig, filtered_gen)
    # 计算相关系数
    correlation = np.corrcoef(filtered_orig, filtered_gen)[0, 1]

    # 整理结果
    results = {
        "Relative Error": rel_error,
        "KS Statistic": ks_stat,
        "Correlation": correlation,
    }
    
    # 判断拟合质量
    fair = (rel_error < 0.2 and
            ks_stat < 0.2 and 
            correlation > 0.85)
    
    results["Verdict"] = "Fit" if fair else "Poor fit"
    
    return results