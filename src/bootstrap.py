"""
bootstrap.py
Core reusable module for Bootstrap and Jackknife methods.

Author: Grok (for Statistical-Inference repo)
"""

import numpy as np
from typing import Callable, Tuple, Optional
from scipy.stats import norm


def bootstrap_statistic(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_bootstrap: int = 10000,
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    Perform bootstrap resampling and compute the statistic for each resample.

    Parameters
    ----------
    data : np.ndarray
        Original sample data.
    statistic : callable
        Function that takes a sample and returns a scalar statistic.
    n_bootstrap : int
        Number of bootstrap samples.
    random_state : int or None
        Seed for reproducibility.

    Returns
    -------
    bootstrap_stats : np.ndarray
        Array of bootstrap statistic values.
    """
    rng = np.random.default_rng(random_state)
    n = len(data)
    bootstrap_stats = np.empty(n_bootstrap)

    for i in range(n_bootstrap):
        resample = rng.choice(data, size=n, replace=True)
        bootstrap_stats[i] = statistic(resample)

    return bootstrap_stats


def bootstrap_confidence_interval(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float],
    n_bootstrap: int = 10000,
    confidence_level: float = 0.95,
    method: str = "percentile",
    random_state: Optional[int] = None
) -> Tuple[float, float]:
    """
    Compute bootstrap confidence interval for a statistic.

    Parameters
    ----------
    data : np.ndarray
        Original sample.
    statistic : callable
        Statistic function.
    n_bootstrap : int
        Number of bootstrap replicates.
    confidence_level : float
        Desired confidence level (e.g. 0.95).
    method : str
        'percentile' or 'basic'.
    random_state : int or None

    Returns
    -------
    (lower, upper) : tuple
        Confidence interval bounds.
    """
    boot_stats = bootstrap_statistic(data, statistic, n_bootstrap, random_state)
    alpha = 1 - confidence_level

    if method == "percentile":
        lower = np.percentile(boot_stats, 100 * alpha / 2)
        upper = np.percentile(boot_stats, 100 * (1 - alpha / 2))
    elif method == "basic":
        original_stat = statistic(data)
        lower = 2 * original_stat - np.percentile(boot_stats, 100 * (1 - alpha / 2))
        upper = 2 * original_stat - np.percentile(boot_stats, 100 * alpha / 2)
    else:
        raise ValueError("method must be 'percentile' or 'basic'")

    return lower, upper


def jackknife_estimate(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float]
) -> Tuple[float, float]:
    """
    Jackknife estimate of bias and standard error.

    Returns
    -------
    (jackknife_estimate, jackknife_se) : tuple
    """
    n = len(data)
    jackknife_stats = np.empty(n)

    for i in range(n):
        jackknife_sample = np.delete(data, i)
        jackknife_stats[i] = statistic(jackknife_sample)

    original_stat = statistic(data)
    jackknife_estimate = n * original_stat - (n - 1) * np.mean(jackknife_stats)
    jackknife_se = np.sqrt((n - 1) / n * np.sum((jackknife_stats - np.mean(jackknife_stats))**2))

    return jackknife_estimate, jackknife_se
