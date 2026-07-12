# Statistical-Inference

**Implementations of modern statistical methods from classical and frequentist theory in Python.**

This repository showcases clean, practical implementations of statistical techniques — from foundational methods to real-world applications in data science, A/B testing, and predictive modeling.

## Topics
`statistics`, `statistical-inference`, `frequentist-statistics`, `bootstrap`, `empirical-bayes`, `james-stein`, `hypothesis-testing`, `survival-analysis`, `lasso`, `shrinkage`, `machine-learning`, `pycaret`, `statsmodels`, `statistical-learning`

## Repository Structure

```bash
Statistical-Inference/
├── src/                          # Core reusable modules
│   ├── bootstrap.py              # Bootstrap resampling, confidence intervals, percentile methods
│   ├── hypothesis_testing.py     # Classical tests, p-values, multiple testing correction
│   ├── empirical_bayes.py        # Shrinkage estimators, James-Stein, empirical Bayes methods
│   ├── shrinkage.py              # Ridge, Lasso-related shrinkage techniques
│   ├── lasso.py                  # LASSO regression, coordinate descent, regularization paths
│   └── survival.py               # Survival analysis basics (Kaplan-Meier, Cox models, etc.)
├── examples/                     # Real-world case studies & applications
│   ├── RKZ_Regulierungsstatistik/      # Hierarchical KPI scoring & regulatory statistics
│   ├── Cross_Selling_BamS/             # ML-driven cross-selling prediction
│   ├── Hypothesis_Testing/             # A/B testing and classical hypothesis tests
│   ├── Weekend_Users_Hypo_Test/        # User behavior hypothesis testing
│   └── Weighted_Temperature/           # Weighted statistical modeling
├── notebooks/
│   ├── README.md
│   ├── 01_test_src_package.ipynb       # Validation of src/ modules
│   └── 02_real_world_examples.ipynb    # End-to-end demonstrations
├── Automation_monthly_run/       # Scheduled automation & reporting scripts
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## About

This project provides **clean, well-tested, and reusable Python implementations** of key statistical inference methods used in modern data analysis and machine learning. The focus is on both classical frequentist approaches and modern shrinkage/regularization techniques that improve robustness in high-dimensional or small-sample settings.

Methods are implemented from scratch (or with minimal dependencies) to promote understanding, while also demonstrating practical usage with `statsmodels`, `scikit-learn`, and `pycaret`.

## Installation

```bash
git clone https://github.com/Shahabed/Statistical-Inference.git
cd Statistical-Inference
pip install -r requirements.txt
```

**Core dependencies** (see requirements.txt):
- numpy, pandas, matplotlib, seaborn
- scipy, statsmodels
- scikit-learn, pycaret (optional for examples)

## Usage

### Using the Core Modules (`src/`)

Each module in `src/` can be imported directly:

```python
from src.bootstrap import bootstrap_ci
from src.hypothesis_testing import t_test, multiple_testing_correction
from src.empirical_bayes import james_stein_estimator
from src.lasso import lasso_path
# etc.
```

**Example: Bootstrap Confidence Interval**
```python
import numpy as np
from src.bootstrap import bootstrap_ci

data = np.random.normal(0, 1, 1000)
ci_lower, ci_upper = bootstrap_ci(data, np.mean, n_boot=10000)
print(f"95% CI for mean: [{ci_lower:.3f}, {ci_upper:.3f}]")
```

See individual module docstrings and the notebooks for full examples and parameter details.

### Running Notebooks

```bash
jupyter notebook notebooks/
```

- `01_test_src_package.ipynb` — Unit tests / validation of the core implementations
- `02_real_world_examples.ipynb` — Complete pipelines on real datasets

### Real-World Examples

Explore the `examples/` folder for production-style case studies:
- Regulatory statistics and hierarchical modeling
- Cross-selling prediction with machine learning
- Classic and modern hypothesis testing scenarios
- Weighted statistical models

## Key Methods Implemented

| Module                | Techniques Covered                          | Typical Use Case                     |
|-----------------------|---------------------------------------------|--------------------------------------|
| `bootstrap.py`        | Non-parametric bootstrap, CI, bias correction | Small samples, complex statistics   |
| `hypothesis_testing.py` | t-tests, chi-square, permutation tests, FDR | A/B testing, group comparisons      |
| `empirical_bayes.py`  | James-Stein estimator, shrinkage            | High-dimensional means estimation   |
| `shrinkage.py`        | Ridge, general shrinkage estimators         | Multicollinear or noisy data        |
| `lasso.py`            | LASSO, regularization path, cross-validation| Feature selection, sparse models    |
| `survival.py`         | Kaplan-Meier, Nelson-Aalen, basic Cox       | Time-to-event analysis              |

## Why This Repository?

Many statistical libraries exist, but this project emphasizes:
- **Transparency**: Code is readable and commented.
- **Educational value**: Good for learning how the methods work under the hood.
- **Practicality**: Ready-to-use functions with sensible defaults.
- **Real data**: Examples drawn from actual business/regulatory/ scientific problems.


## Contributing

Contributions are welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

For major changes, open an issue first to discuss.


## Acknowledgments

- Inspired by classic statistical literature (Efron, Hastie, Tibshirani, etc.)
- Built on top of excellent scientific Python ecosystem (`numpy`, `scipy`, `statsmodels`, `scikit-learn`)
- Real-world examples contributed from various data science projects

---
