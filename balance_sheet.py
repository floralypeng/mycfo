import pandas as pd

assets = pd.read_csv("data/assets.csv")
liabilities = pd.read_csv("data/liabilities.csv")

total_assets = assets["value"].sum()
total_liabilities = liabilities["balance"].sum()

net_worth = total_assets - total_liabilities

print()
print("===== BALANCE SHEET =====")

print()
print(f"Total Assets:      ${total_assets:,.0f}")
print(f"Total Liabilities: ${total_liabilities:,.0f}")
print(f"Net Worth:         ${net_worth:,.0f}")

print()
print("Asset Breakdown")

asset_breakdown = (
    assets.groupby("asset_type")["value"]
    .sum()
    .sort_values(ascending=False)
)

print(asset_breakdown)

print()
print("Liability Breakdown")

liability_breakdown = (
    liabilities.groupby("liability_type")["balance"]
    .sum()
)

print(liability_breakdown)

asset_breakdown_pct = (
    assets.groupby("asset_type")["value"]
    .sum()
    / total_assets
    * 100
)

print()
print("Asset Allocation (%)")
print(asset_breakdown_pct.round(1))
latest_date = assets["last_updated"].max()
print(assets[["name","value","last_updated"]])
latest_date = assets["last_updated"].max()

print()
print(f"Snapshot Date: {latest_date}")