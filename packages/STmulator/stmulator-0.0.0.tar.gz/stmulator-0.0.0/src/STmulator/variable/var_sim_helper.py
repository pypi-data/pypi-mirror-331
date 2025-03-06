import numpy as np
from scipy import stats
from var_distribution import gig_pdf

def assess_tail_discreteness(tail_data):
    """assess the discreteness of tail data"""
    sorted_tail = np.sort(tail_data)
    differences = np.diff(sorted_tail)
    cv = np.std(differences) / np.mean(differences)

    if cv > 2.0:
        return 'discrete'
    elif cv < 1.0:
        return 'smooth'
    else:
        return 'mixed'


def simulate_gig(n_samples, alpha, beta, theta, k, lambda_):
    def adaptive_proposal(size):
        if k < 1 and lambda_ < 1:
            return stats.invgamma.rvs(alpha, scale=theta, size=size)
        else:
            return stats.gamma.rvs(alpha, scale=1 / theta, size=size)

    def calculate_acceptance_ratio(x):
        proposal_pdf = stats.invgamma.pdf(x, alpha, scale=theta)
        target_pdf = gig_pdf(x, alpha, beta, theta, k, lambda_)
        return target_pdf / np.maximum(proposal_pdf, 1e-300)

    accepted_samples = []
    max_attempts = 100
    attempt = 0

    while len(accepted_samples) < n_samples and attempt < max_attempts:
        proposed = adaptive_proposal(n_samples * 2)
        acceptance_ratio = calculate_acceptance_ratio(proposed)
        acceptance_prob = acceptance_ratio / np.max(acceptance_ratio)

        accepted = proposed[np.random.random(len(proposed)) < acceptance_prob]
        accepted_samples.extend(accepted[:n_samples - len(accepted_samples)])
        attempt += 1

    if len(accepted_samples) < n_samples:
        # Fallback to proposal distribution
        remaining = n_samples - len(accepted_samples)
        accepted_samples.extend(adaptive_proposal(remaining))

    return np.array(accepted_samples[:n_samples])


def interpolate_tail_data(tail_data, n_tail):
    return np.interp(
        np.linspace(0, 1, n_tail),
        np.linspace(0, 1, len(tail_data)),
        np.sort(tail_data)
    )