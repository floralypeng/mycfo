import pandas as pd

df = pd.read_csv("data/transactions.csv")

def categorize(desc):
    desc = desc.lower()

    if "starbucks" in desc:
        return "Dining"
    elif "costco" in desc:
        return "Shopping"
    elif "amazon" in desc:
        return "Shopping"
    elif "netflix" in desc:
        return "Entertainment"
    elif "payroll" in desc:
        return "Income"
    return "Other"

df["Category"] = df["Description"].apply(categorize)

income = df[df["Amount"] > 0]["Amount"].sum()
expense = abs(df[df["Amount"] < 0]["Amount"].sum())
net = income - expense

print(df)
print()
print(f"Income: ${income:,.2f}")
print(f"Expense: ${expense:,.2f}")
print(f"Net Cash Flow: ${net:,.2f}")

summary = df.groupby("Category")["Amount"].sum()
print()
print(summary)