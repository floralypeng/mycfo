import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/bank_raw")

OUTPUT_FILE = Path("data/processed/master_transactions.csv")
MONTHLY_CASHFLOW_FILE = Path("data/processed/monthly_cash_flow.csv")
UNCATEGORIZED_FILE = Path("data/processed/uncategorized_merchants.csv")

MERCHANT_RULES_FILE = Path("data/reference/merchant_rules.csv")

def classify_credit_card_transaction(transaction_type, description):
    desc = str(description).lower()

    if "autopay" in desc or "thank you" in desc:
        return "transfer"

    mapping = {
        "Sale": "expense",
        "Fee": "expense",
        "Payment": "transfer",
        "Return": "refund",
        "Adjustment": "adjustment",
    }

    return mapping.get(transaction_type, "unknown")
def classify_cashflow(description, amount, account_type=None, transaction_type=None):
    desc = str(description).lower()

    if pd.isna(amount):
        return "unknown"

    transfer_keywords = [
        "transfer",
        "xfer",
        "ach trnsfr",
        "ach transfer",
        "online banking transfer",
        "online transfer",
        "chase credit crd",
        "autopaybus",
        "autopay",
        "thank you",
        "payment thank you",
        "automatic payment",
        "web pymt",
        "credit crd",
        "american express",
        "payment to chk",
        "bill payment",
        "alliant cu",
        "travis credit un",
        "oceanair fcu",
        "cbc fcu",
    ]

    mortgage_keywords = [
        "unitedwholesale",
        "select portfolio",
        "regions mortgage",
        "loandepot",
        "mortgage",
        "mort ",
        "loan paymt",
        "home lending",
    ]

    investment_keywords = [
        "schwab",
        "fidelity",
        "vanguard",
        "etrade",
        "e*trade",
        "robinhood",
        "morgan stanley",
        "brokerage",
        "fid bkg svc",
        "moomoo",
    ]

    income_keywords = [
        "payroll",
        "salary",
        "direct deposit",
        "airbnb",
        "rental income",
    ]

    asset_sale_keywords = [
        "escrow",
        "title",
        "realty",
        "proceeds",
        "wire deposit",
        "closing",
        "home sale",
    ]

    refund_keywords = [
        "refund",
        "return",
        "reversal",
        "franchise tax bd",
        "tax refund",
    ]

    # Transfers first
    if any(k in desc for k in transfer_keywords):
        return "transfer"

    # Internal transfer to spouse
    if "ning zhan" in desc:
        return "transfer"

    # Zelle
    if "zelle payment to" in desc or "zelle to" in desc:
        return "expense"

    if "zelle payment from" in desc or "zelle from" in desc:
        return "refund"

    if any(k in desc for k in mortgage_keywords):
        return "mortgage"

    if any(k in desc for k in investment_keywords):
        return "investment"

    if any(k in desc for k in asset_sale_keywords) or amount > 50000:
        return "asset_sale"

    if any(k in desc for k in refund_keywords):
        return "refund"

    if any(k in desc for k in income_keywords):
        return "income"

    if amount > 0:
        return "unknown_inflow"

    if amount < 0:
        return "expense"

    return "unknown"

def load_merchant_rules():
    if not MERCHANT_RULES_FILE.exists():
        return pd.DataFrame(
            columns=[
                "keyword",
                "merchant",
                "mycfo_category",
                "mycfo_subcategory",
            ]
        )

    rules = pd.read_csv(MERCHANT_RULES_FILE)
    rules["keyword"] = rules["keyword"].astype(str).str.upper()
    return rules


merchant_rules_df = load_merchant_rules()

merchant_rules = {}

for _, row in merchant_rules_df.sort_values(
    "keyword",
    key=lambda s: s.str.len(),
    ascending=False
).iterrows():
    merchant_rules[row["keyword"]] = (
        row["merchant"],
        row["mycfo_category"],
        row["mycfo_subcategory"],
    )

def categorize_mycfo(description):
    desc = str(description).upper()

    for keyword, values in merchant_rules.items():
        if keyword in desc:
            return values

    return ("Unknown", "Unknown", "Unknown")

def normalize_chase_credit_card(file_path):
    df = pd.read_csv(file_path)

    normalized = pd.DataFrame()
    normalized["transaction_date"] = pd.to_datetime(df["Transaction Date"])
    normalized["post_date"] = pd.to_datetime(df["Post Date"])
    normalized["description"] = df["Description"]
    normalized["category"] = df["Category"]
    normalized["type"] = df["Type"]
    normalized["amount"] = df["Amount"]

    normalized["transaction_class"] = normalized.apply(
    lambda row: classify_credit_card_transaction(
        row["type"],
        row["description"]
    ),
    axis=1,
)

    normalized["source_file"] = file_path.name
    normalized["account_type"] = "credit_card"
    normalized["institution"] = "Chase"

    return normalized


def normalize_amex_credit_card(file_path):
    df = pd.read_csv(file_path)

    normalized = pd.DataFrame()
    normalized["transaction_date"] = pd.to_datetime(df["Date"])
    normalized["post_date"] = pd.to_datetime(df["Date"])
    normalized["description"] = df["Description"]
    normalized["category"] = df["Category"]
    normalized["type"] = "Sale"
    normalized["amount"] = -df["Amount"].abs()
    normalized["transaction_class"] = normalized.apply(
        lambda row: classify_credit_card_transaction(
            row["type"],
            row["description"],
        ),
        axis=1,
    )
    
    normalized["source_file"] = file_path.name
    normalized["account_type"] = "credit_card"
    normalized["institution"] = "Amex"

    return normalized


def normalize_chase_checking(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    print("Checking columns:", list(df.columns))

    normalized = pd.DataFrame()
    normalized["transaction_date"] = pd.to_datetime(
        df["Posting Date"],
        format="%m/%d/%Y",
        errors="coerce",
    )
    normalized["post_date"] = normalized["transaction_date"]
    normalized["description"] = df["Description"]
    normalized["category"] = df["Type"]
    normalized["type"] = df["Details"]
    normalized["amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    normalized = normalized.dropna(subset=["transaction_date", "amount"])

    normalized["transaction_class"] = normalized.apply(
        lambda row: classify_cashflow(
            row["description"],
            row["amount"],
            account_type="checking",
            transaction_type=row["type"],
        ),
        axis=1,
    )

    normalized["source_file"] = file_path.name
    normalized["account_type"] = "checking"
    normalized["institution"] = "Chase"

    return normalized


def normalize_bofa_checking(file_path):
    df = pd.read_csv(
        file_path,
        skiprows=6,
        engine="python",
        on_bad_lines="skip",
    )

    df.columns = df.columns.str.strip()

    normalized = pd.DataFrame()
    normalized["transaction_date"] = pd.to_datetime(
        df["Date"],
        format="%m/%d/%Y",
        errors="coerce",
    )
    normalized["post_date"] = normalized["transaction_date"]
    normalized["description"] = df["Description"]

    normalized["amount"] = (
        df["Amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    normalized["amount"] = pd.to_numeric(
        normalized["amount"],
        errors="coerce",
    )

    normalized["category"] = "Uncategorized"
    normalized["type"] = "Checking"

    normalized = normalized.dropna(subset=["transaction_date", "amount"])

    normalized["transaction_class"] = normalized.apply(
        lambda row: classify_cashflow(
            row["description"],
            row["amount"],
            account_type="checking",
            transaction_type=row["type"],
        ),
        axis=1,
    )

    normalized["source_file"] = file_path.name
    normalized["account_type"] = "checking"
    normalized["institution"] = "BofA"

    return normalized


all_transactions = []

for file_path in RAW_DIR.glob("*"):
    if file_path.suffix.lower() != ".csv":
        continue

    print(f"Reading: {file_path.name}")

    if "Amex" in file_path.name:
        transactions = normalize_amex_credit_card(file_path)

    elif "BofA" in file_path.name:
        transactions = normalize_bofa_checking(file_path)

    elif "Checking" in file_path.name or "checking" in file_path.name:
        transactions = normalize_chase_checking(file_path)

    else:
        transactions = normalize_chase_credit_card(file_path)

    all_transactions.append(transactions)


master = pd.concat(all_transactions, ignore_index=True)
master = master.drop_duplicates()

master["month"] = master["transaction_date"].dt.strftime("%Y-%m")

master[["merchant", "mycfo_category", "mycfo_subcategory"]] = master[
    "description"
].apply(
    lambda x: pd.Series(categorize_mycfo(x))
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
master.to_csv(OUTPUT_FILE, index=False)

print()
print(f"Saved {len(master)} transactions to {OUTPUT_FILE}")

print()
print("Transaction Classes:")
print(master["transaction_class"].value_counts())

print()
print("===== AUTOPAY DEBUG =====")
print(
    master[
        master["description"].str.contains(
            "AUTOPAY PAYMENT",
            case=False,
            na=False,
        )
    ][
        [
            "description",
            "amount",
            "transaction_class",
            "account_type",
            "institution",
            "type",
        ]
    ]
)

# =========================
# CFO Cash Flow Statement
# =========================

operating_income = master[master["transaction_class"] == "income"]

expenses = master[
    (master["transaction_class"] == "expense")
    & (master["amount"] < 0)
]

mortgage = master[master["transaction_class"] == "mortgage"]
refunds = master[master["transaction_class"] == "refund"]
asset_sales = master[master["transaction_class"] == "asset_sale"]
transfers = master[master["transaction_class"] == "transfer"]
investments = master[master["transaction_class"] == "investment"]
unknown_inflows = master[master["transaction_class"] == "unknown_inflow"]

uncategorized = master[
    (master["mycfo_category"] == "Unknown") &
    (master["transaction_class"] == "expense")
]

uncategorized_summary = (
    uncategorized
    .groupby("description")
    .agg(
        total_amount=("amount", "sum"),
        transaction_count=("amount", "count"),
        first_date=("transaction_date", "min"),
        last_date=("transaction_date", "max"),
    )
    .sort_values("total_amount")
)

print()
print("===== Uncategorized Merchant Summary =====")
print(uncategorized_summary.head(100))

uncategorized_summary.to_csv(
    "data/processed/uncategorized_merchants.csv"
)

cash_flow = pd.DataFrame({
    "operating_income": operating_income.groupby("month")["amount"].sum(),
    "expenses": expenses.groupby("month")["amount"].sum(),
    "mortgage": mortgage.groupby("month")["amount"].sum(),
    "refunds": refunds.groupby("month")["amount"].sum(),
    "asset_sales": asset_sales.groupby("month")["amount"].sum(),
    "transfers": transfers.groupby("month")["amount"].sum(),
    "investments": investments.groupby("month")["amount"].sum(),
    "unknown_inflows": unknown_inflows.groupby("month")["amount"].sum(),
}).fillna(0)

cash_flow["operating_cashflow"] = (
    cash_flow["operating_income"]
    + cash_flow["refunds"]
    + cash_flow["expenses"]
    + cash_flow["mortgage"]
)

cash_flow["balance_sheet_movement"] = (
    cash_flow["asset_sales"]
    + cash_flow["transfers"]
    + cash_flow["investments"]
)

print()
print("===== Monthly CFO Cash Flow Statement =====")
print(cash_flow)

ytd_operating_cashflow = cash_flow["operating_cashflow"].sum()
months_count = cash_flow.index.nunique()
annualized_operating_cashflow = ytd_operating_cashflow / months_count * 12

print()
print(f"YTD Operating Cash Flow: ${ytd_operating_cashflow:,.0f}")
print(f"Annualized Operating Cash Flow: ${annualized_operating_cashflow:,.0f}")

cash_flow.to_csv(MONTHLY_CASHFLOW_FILE, index=True)
uncategorized_summary.to_csv(UNCATEGORIZED_FILE)

# =========================
# Expense Reporting
# =========================

print()
print("Monthly Expenses:")
print(expenses.groupby("month")["amount"].sum())

print()
print("Expense by MyCFO Subcategory:")
print(
    expenses.groupby(["mycfo_category", "mycfo_subcategory"])["amount"]
    .sum()
    .sort_values()
)

print()
print("Expense by MyCFO Category:")
print(
    expenses.groupby("mycfo_category")["amount"]
    .sum()
    .sort_values()
)

print()
print("Top 30 Merchants:")
top_merchants = (
    expenses.groupby("description")["amount"]
    .sum()
    .sort_values()
    .head(30)
)
print(top_merchants)