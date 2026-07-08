"""
hypothesis_testing.py
Core reusable module for classical hypothesis testing.

Includes t-tests, z-tests, chi-square, and permutation tests.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional


def one_sample_t_test(
    data: np.ndarray,
    popmean: float = 0.0,
    alternative: str = "two-sided"
) -> Tuple[float, float]:
    """
    One-sample t-test.

    Returns
    -------
    (t_stat, p_value)
    """
    t_stat, p_value = stats.ttest_1samp(data, popmean=popmean, alternative=alternative)
    return t_stat, p_value


def two_sample_t_test(
    sample1: np.ndarray,
    sample2: np.ndarray,
    equal_var: bool = True,
    alternative: str = "two-sided"
) -> Tuple[float, float]:
    """
    Two-sample t-test (independent samples).
    """
    t_stat, p_value = stats.ttest_ind(sample1, sample2, equal_var=equal_var, alternative=alternative)
    return t_stat, p_value


def paired_t_test(
    sample1: np.ndarray,
    sample2: np.ndarray,
    alternative: str = "two-sided"
) -> Tuple[float, float]:
    """
    Paired (dependent) t-test.
    """
    t_stat, p_value = stats.ttest_rel(sample1, sample2, alternative=alternative)
    return t_stat, p_value


def z_test(
    data: np.ndarray,
    popmean: float = 0.0,
    popstd: Optional[float] = None,
    alternative: str = "two-sided"
) -> Tuple[float, float]:
    """
    One-sample z-test (known population standard deviation).
    """
    if popstd is None:
        raise ValueError("popstd must be provided for z-test")

    n = len(data)
    sample_mean = np.mean(data)
    z_stat = (sample_mean - popmean) / (popstd / np.sqrt(n))

    if alternative == "two-sided":
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    elif alternative == "greater":
        p_value = 1 - stats.norm.cdf(z_stat)
    elif alternative == "less":
        p_value = stats.norm.cdf(z_stat)
    else:
        raise ValueError("alternative must be 'two-sided', 'greater', or 'less'")

    return z_stat, p_value


def permutation_test(
    sample1: np.ndarray,
    sample2: np.ndarray,
    statistic: callable = np.mean,
    n_permutations: int = 10000,
    random_state: Optional[int] = None
) -> Tuple[float, float]:
    """
    Permutation test for difference in means (or other statistic).

    Returns
    -------
    (observed_stat, p_value)
    """
    rng = np.random.default_rng(random_state)
    observed = statistic(sample1) - statistic(sample2)
    combined = np.concatenate([sample1, sample2])
    n1 = len(sample1)

    count = 0
    for _ in range(n_permutations):
        rng.shuffle(combined)
        perm1 = combined[:n1]
        perm2 = combined[n1:]
        perm_stat = statistic(perm1) - statistic(perm2)
        if abs(perm_stat) >= abs(observed):
            count += 1

    p_value = (count + 1) / (n_permutations + 1)  # conservative p-value
    return observed, p_value


def chi_square_test(
    observed: np.ndarray,
    expected: Optional[np.ndarray] = None
) -> Tuple[float, float, float]:
    """
    Chi-square goodness-of-fit or independence test.

    Returns
    -------
    (chi2_stat, p_value, dof)
    """
    chi2_stat, p_value, dof, _ = stats.chi2_contingency(observed)
    return chi2_stat, p_value, dof
