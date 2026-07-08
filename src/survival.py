"""
survival.py
Core reusable module for Survival Analysis.

Includes Kaplan-Meier estimator and basic survival functions.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from lifelines import KaplanMeierFitter


def kaplan_meier_estimator(
    durations: np.ndarray,
    event_observed: np.ndarray,
    timeline: Optional[np.ndarray] = None
) -> pd.DataFrame:
    """
    Kaplan-Meier survival curve estimation.

    Parameters
    ----------
    durations : array-like
        Observed times (event or censoring).
    event_observed : array-like
        1 if event occurred, 0 if censored.
    timeline : array-like or None
        Time points to evaluate at.

    Returns
    -------
    km_table : pd.DataFrame
        Columns: timeline, survival_probability, etc.
    """
    kmf = KaplanMeierFitter()
    kmf.fit(durations, event_observed=event_observed, timeline=timeline)

    return kmf.survival_function_.reset_index()


def kaplan_meier_median_survival(
    durations: np.ndarray,
    event_observed: np.ndarray
) -> float:
    """
    Estimate median survival time from Kaplan-Meier.
    """
    kmf = KaplanMeierFitter()
    kmf.fit(durations, event_observed=event_observed)
    return kmf.median_survival_time_


def log_rank_test(
    durations_A: np.ndarray,
    event_A: np.ndarray,
    durations_B: np.ndarray,
    event_B: np.ndarray
) -> Tuple[float, float]:
    """
    Log-rank test for comparing two survival curves.
    """
    from lifelines.statistics import logrank_test

    results = logrank_test(durations_A, durations_B, event_observed_A=event_A, event_observed_B=event_B)
    return results.test_statistic, results.p_value
