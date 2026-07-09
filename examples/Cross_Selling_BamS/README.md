# Cross-Selling Prediction (BamS → BILD)

Machine learning project to predict successful cross-selling of BILD subscriptions to existing BamS readers.

## Project Goal

Predict the probability that a BamS subscriber will convert to a BILD subscription when contacted through marketing campaigns. The model helps prioritize customers with higher conversion likelihood.

## Key Results

- Built using **Random Forest** and ensemble methods via **PyCaret**
- Successfully handled severe class imbalance
- Model was used to generate scoring for real marketing campaigns
- In the 2024 Oscars context (separate project), similar modeling techniques correctly identified strong performers

## Features Used

- Historical subscription behavior
- Contact history and campaign response
- Digital subscription patterns (MSD & SD)
- Customer demographics and opt-in status
- Previous BamS subscription duration and engagement

## Technologies

- Python
- PyCaret (AutoML)
- scikit-learn
- pandas, numpy
- Oracle & SQL Server data integration

## Project Components

- `modeling_script.py`: Model training and optimization pipeline
- `inference_script.py`: Scoring pipeline for new customers
- Feature engineering from multiple data sources (AboMart + CRM DWH)

## Business Impact

The model supports data-driven customer selection for cross-selling campaigns, improving conversion rates and marketing efficiency.

## Note

This project combines machine learning with complex data integration from multiple enterprise systems (SQL Server and Oracle).
