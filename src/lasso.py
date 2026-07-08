"""
lasso.py
Core reusable module for LASSO and related regularization methods.

Note: For full LASSO with coordinate descent, use scikit-learn.
This module provides a simple implementation + helper functions.
"""

import numpy as np
from typing import Tuple, Optional
from sklearn.linear_model import Lasso


def soft_threshold(x: float, lambda_: float) -> float:
    """
    Soft-thresholding operator (used in LASSO coordinate descent).
    """
    if x > lambda_:
        return x - lambda_
    elif x < -lambda_:
        return x + lambda_
    else:
        return 0.0


def simple_lasso_coordinate_descent(
    X: np.ndarray,
    y: np.ndarray,
    alpha: float = 1.0,
    max_iter: int = 1000,
    tol: float = 1e-4
) -> np.ndarray:
    """
    Simple LASSO via coordinate descent (for educational purposes).

    For production use, prefer sklearn.linear_model.Lasso.
    """
    n_samples, n_features = X.shape
    beta = np.zeros(n_features)
    X = X - np.mean(X, axis=0)  # center
    y = y - np.mean(y)

    for _ in range(max_iter):
        beta_old = beta.copy()
        for j in range(n_features):
            residual = y - X @ beta + X[:, j] * beta[j]
            rho = X[:, j].T @ residual
            beta[j] = soft_threshold(rho, alpha) / (X[:, j].T @ X[:, j])

        if np.max(np.abs(beta - beta_old)) < tol:
            break

    return beta


def fit_lasso_sklearn(
    X: np.ndarray,
    y: np.ndarray,
    alpha: float = 1.0,
    **kwargs
) -> Tuple[np.ndarray, object]:
    """
    Convenience wrapper around sklearn Lasso.
    """
    model = Lasso(alpha=alpha, **kwargs)
    model.fit(X, y)
    return model.coef_, model
