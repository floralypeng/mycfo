# MyCFO

Manage Your Wealth Like a Business.

MyCFO is a personal CFO platform designed for financially sophisticated individuals and families.

## Current Features

- Transaction ingestion
- Cash flow analysis
- Transaction categorization

## Roadmap

- Monthly cash flow statements
- Balance sheet tracking
- Portfolio monitoring
- Real estate tracking
- AI-generated financial insights
- Daily CFO briefing

## Project Structure

```text
Personal-finance-agent/
│
├── app.py                     # Streamlit dashboard
├── consolidate_transactions.py # ETL & transaction normalization
├── balance_sheet.py
├── cashflow.py
├── expense_summary.py
├── projection_scenarios.py
│
├── data/
│   ├── assets.csv
│   ├── liabilities.csv
│   ├── reference/
│   │     └── merchant_rules.csv
│   ├── bank_raw/              # Ignored
│   └── processed/             # Generated outputs
```
