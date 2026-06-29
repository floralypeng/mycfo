# MyCFO

An AI-powered personal CFO that consolidates bank statements,
categorizes transactions, analyzes cash flow, and generates
financial insights.

## Features

- Multi-bank transaction import
- Merchant normalization
- Cash flow classification
- Expense categorization
- Balance sheet tracking
- AI financial insights (coming soon)

## Architecture

[project structure]

## Screenshots

(coming tomorrow)

## Future Roadmap

- Streamlit dashboard
- AI chat assistant
- Net worth tracking
- Portfolio analytics
  
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
