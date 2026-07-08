"""
empirical_bayes.py
Core reusable module for Empirical Bayes methods.

Includes James-Stein estimator and simple shrinkage toward a grand mean.
"""

import numpy as np
from typing import Tuple, Optional


def james_stein_estimator(
    observations: np.ndarray,
    known_variance: Optional[float] = None
) -> np.ndarray:
    """
    James-Stein shrinkage estimator.

    Shrinks individual observations toward the grand mean.

    Parameters
    ----------
    observations : np.ndarray
        Vector of observations (e.g., sample means).
    known_variance : float or None
        If provided, uses known variance. Otherwise estimates from data.

    Returns
    -------
    shrunk_estimates : np.ndarray
    """
    n = len(observations)
    grand_mean = np.mean(observations)

    if known_variance is None:
        # Estimate variance from data (assumes equal variance)
        s2 = np.var(observations, ddof=1)
    else:
        s2 = known_variance

    # James-Stein shrinkage factor
    shrinkage = max(0, 1 - (n - 2) * s2 / np.sum((observations - grand_mean)**2))

    shrunk = grand_mean + shrinkage * (observations - grand_mean)
    return shrunk


def empirical_bayes_shrinkage(
    group_means: np.ndarray,
    group_sizes: np.ndarray,
    within_variance: float
) -> np.ndarray:
    """
    Simple Empirical Bayes shrinkage for group means.

    Assumes normal model with known within-group variance.

    Returns
    -------
    shrunk_means : np.ndarray
    """
    grand_mean = np.average(group_means, weights=group_sizes)
    between_variance = np.var(group_means, ddof=1)

    shrinkage_factors = between_variance / (between_variance + within_variance / group_sizes)
    shrunk_means = grand_mean + shrinkage_factors * (group_means - grand_mean)

    return shrunk_means
