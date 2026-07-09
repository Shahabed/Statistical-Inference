# RKZ Regulierungsstatistik - Performance KPI System

This project implements a hierarchical performance scoring system for retail regulation (Regulierungsstatistik).

## Overview

The system calculates Key Performance Indicators (KPIs) across multiple aggregation levels:
- OGR (Object Group)
- HKD (Main Customer)
- HKDFIL (Main Customer Branch)
- OBJ (Object)
- EH (Individual Unit)

Key metrics include:
- Overstock rate (Remissionsquote)
- Sellout rate (Abverkaufsquote)
- Custom performance score (RKZ)

## Key Features

- Multi-level hierarchical aggregation
- Target-based performance scoring
- Flop-20 adjustment mechanism
- Integration with SQL Server data sources
- Support for different VGK (sales classes)

## Technologies Used

- Python (pandas, numpy, pyodbc, sqlalchemy)
- QuTiP (for related quantum simulations in earlier versions)
- Statistical modeling and parameter estimation

## Project Structure

- `rkz_main_python_version.py`: Main calculation script
- Data processing and KPI computation pipeline

## Business Context

This system is used for regulatory reporting and performance evaluation in the retail sector, particularly for calculating fair performance metrics across different organizational levels.

## Note

This project was developed as part of operational analytics work and involves complex business logic for fair KPI calculation across hierarchical retail structures.
