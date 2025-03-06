import numpy as np
import scipy.special as special
from scipy import stats


def generalized_gamma(alpha, k, lambda_):
    """Generalized gamma function"""
    try:
        log_gamma = np.log(special.gamma(alpha)) - lambda_ * np.log(1 + k)
        return np.exp(log_gamma)
    except:
        return special.gamma(alpha)


def gig_pdf(x, alpha, beta, theta, k, lambda_):
    """Generalized Inverse Gaussian PDF calculation"""
    try:
        log_pdf = (np.log(beta) +
                  alpha * beta * np.log(theta) -
                  (alpha * beta + 1) * np.log(x) -
                  lambda_ * np.log((theta / x) ** beta + k) -
                  (theta / x) ** beta -
                  np.log(generalized_gamma(alpha, k, lambda_)))
        return np.exp(log_pdf)
    except:
        return np.zeros_like(x)