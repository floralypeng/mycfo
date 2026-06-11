income = [
    ("Ning Salary", 30000),
    ("Friess Rent", 8000),
    ("Monroe Airbnb", 10000),
]
expenses = [
    ("Mortgage", 25000),
    ("Rent", 7500),
    ("Fencing", 1100),
    ("Groceries", 200),
    ("Restaurants", 500),
    ("Entertainment", 300),
    ("Utilities", 400),
    ("summer camps", 6000),
    ("Travel", 1500),
]

total_income = 0
for category, amount in income:
    print(f"Income - {category}: ${amount}")
    total_income += amount

print("----------------")

total_expenses = 0
for category, amount in expenses:
    print(f"Expense - {category}: ${amount}")
    total_expenses += amount

print("----------------")

net_cash_flow = total_income - total_expenses

print(f"Total Income: ${total_income}")
print(f"Total Expenses: ${total_expenses}")
print(f"Net Cash Flow: ${net_cash_flow}")