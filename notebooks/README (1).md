# Notebooks

This folder contains Jupyter notebooks that demonstrate and test the core statistical modules located in `src/`.

## Purpose

These notebooks serve two main goals:

1. **Testing & Validation** — Verify that all modules in `src/` work correctly.
2. **Education & Examples** — Show practical usage of statistical methods on both synthetic and realistic business scenarios.

## Notebooks

### 1. `01_test_src_package.ipynb`
**Focus:** Basic to advanced usage of all six core modules.

**Covers:**
- Bootstrap confidence intervals (percentile vs basic)
- Hypothesis testing (t-tests, chi-square, permutation tests)
- Empirical Bayes and shrinkage methods (with visualization)
- LASSO feature selection
- Survival analysis (Kaplan-Meier + Log-rank test)

**Best for:** Quickly checking that the `src` package is working and understanding the API of each module.

### 2. `02_real_world_examples.ipynb`
**Focus:** Practical business and research applications.

**Covers:**
- E-commerce: Bootstrap CI for Average Order Value
- A/B Testing: Permutation test for conversion rates
- Retail Analytics: James-Stein shrinkage for store performance
- Customer Churn: LASSO for feature selection
- Subscription Business: Survival analysis for customer lifetime

**Best for:** Seeing how these statistical tools can be applied to real business problems.

## How to Use

1. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Open the notebooks using Jupyter Notebook, JupyterLab, or VS Code.

3. Run the cells from top to bottom.

> **Note:** The notebooks use `sys.path.append('..')` so they can import from the `src/` folder when run from inside `notebooks/`.

## Requirements

- Python 3.8+
- All packages listed in `requirements.txt` (including `lifelines`, `matplotlib`, `scikit-learn`, etc.)

## Contributing

When adding new notebooks:
- Follow the existing naming convention (`XX_description.ipynb`)
- Include clear markdown explanations
- Add both code and interpretation of results
- Update this README

---

These notebooks are meant to be living documentation for the statistical methods implemented in this repository.
