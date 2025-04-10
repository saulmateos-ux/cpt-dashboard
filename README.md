# CPT Code Financial Dashboard

This Streamlit dashboard provides a visual analysis of CPT code financial data by healthcare provider partners.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Place your Excel file "Collections by CPT Code Georgia - merged.xlsx" in the same directory as the app.py file.

3. Run the Streamlit app:
```bash
streamlit run app.py
```

## Features

- Interactive partner selection
- Detailed CPT code metrics table
- Visual representation of financial averages
- Responsive design with full-width tables

## Data Requirements

The Excel file should contain the following columns:
- Partner Account
- CPT Code 1
- Total Amounts Repaid 1 + 2
- Invoice Amount
- Medicare
- Medicaid
- Description 