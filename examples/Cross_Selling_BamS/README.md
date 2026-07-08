### Cross-Selling Prediction for BamS → BILD
Machine learning pipeline to predict successful cross-selling of BILD subscriptions to existing BamS customers.

**Key Techniques**:
- Multi-source data integration (AboMart + CRM DWH)
- Feature engineering (subscription history, contact points, digital subscriptions, age, etc.)
- Handling severe class imbalance
- PyCaret AutoML + Random Forest
- Threshold optimization for business-relevant metrics (Jaccard, APC)
- Production-ready scoring script

**Results**: High AUC (~0.91), optimized decision threshold for campaign selection.
