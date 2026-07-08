"""
shrinkage.py
Core reusable module for Shrinkage Estimators.

Includes Ridge-like shrinkage and positive-part James-Stein.
"""

import numpy as np
from typing import Optional


def ridge_shrinkage(
    estimates: np.ndarray,
    shrinkage_intensity: float = 0.5
) -> np.ndarray:
    """
    Simple ridge-style shrinkage toward zero.

    Parameters
    ----------
    estimates : np.ndarray
        Vector of estimates.
    shrinkage_intensity : float
        Between 0 and 1. Higher value = more shrinkage toward 0.

    Returns
    -------
    shrunk : np.ndarray
    """
    return (1 - shrinkage_intensity) * estimates


def positive_part_james_stein(
    observations: np.ndarray,
    known_variance: Optional[float] = None
) -> np.ndarray:
    """
    Positive-part James-Stein estimator (always shrinks, never expands).

    Recommended over classical James-Stein in practice.
    """
    n = len(observations)
    grand_mean = np.mean(observations)

    if known_variance is None:
        s2 = np.var(observations, ddof=1)
    else:
        s2 = known_variance

    sum_sq = np.sum((observations - grand_mean)**2)
    shrinkage = max(0, 1 - (n - 2) * s2 / sum_sq)

    return grand_mean + shrinkage * (observations - grand_mean)
