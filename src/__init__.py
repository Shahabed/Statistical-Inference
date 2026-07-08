"""
Statistical-Inference Core Package

This package contains reusable modules for classical and modern statistical methods.

Usage:
    from src import bootstrap
    from src import hypothesis_testing
    from src.empirical_bayes import james_stein_estimator
"""

from . import bootstrap
from . import hypothesis_testing
from . import empirical_bayes
from . import shrinkage
from . import lasso
from . import survival

__all__ = [
    "bootstrap",
    "hypothesis_testing",
    "empirical_bayes",
    "shrinkage",
    "lasso",
    "survival",
]
