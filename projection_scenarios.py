import pandas as pd
import matplotlib.pyplot as plt

assets = pd.read_csv("data/assets.csv")
liabilities = pd.read_csv("data/liabilities.csv")

stock_value = assets[assets["asset_type"].isin(["Brokerage", "Retirement"])]["value"].sum()
real_estate_value = assets[assets["asset_type"] == "Real Estate"]["value"].sum()
cash_value = assets[assets["asset_type"] == "Cash"]["value"].sum()
total_liabilities = liabilities["balance"].sum()

scenarios = {
    "Base Case": {
        "stock_growth": 0.15,
        "real_estate_growth": 0.04
    },
    "Aggressive": {
        "stock_growth": 0.20,
        "real_estate_growth": 0.08
    },
    "Conservative": {
        "stock_growth": 0.08,
        "real_estate_growth": 0.02
    }
}

years = list(range(0, 11))
results = []

for scenario_name, assumptions in scenarios.items():
    for year in years:
        projected_stocks = stock_value * ((1 + assumptions["stock_growth"]) ** year)
        projected_real_estate = real_estate_value * ((1 + assumptions["real_estate_growth"]) ** year)

        projected_assets = projected_stocks + projected_real_estate + cash_value
        projected_net_worth = projected_assets - total_liabilities

        results.append({
            "year": year,
            "scenario": scenario_name,
            "projected_net_worth": projected_net_worth
        })

df = pd.DataFrame(results)

print(df)

for scenario_name in scenarios.keys():
    scenario_df = df[df["scenario"] == scenario_name]
    plt.plot(
        scenario_df["year"],
        scenario_df["projected_net_worth"] / 1_000_000,
        label=scenario_name
    )

plt.title("10-Year Net Worth Projection")
plt.xlabel("Year")
plt.ylabel("Net Worth ($M)")
plt.legend()
plt.grid(True)

plt.savefig("data/processed/net_worth_projection.png")
plt.show()