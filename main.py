
import pandas as pd
import numpy as np

from dataclass import ProcurementConfig, ModelData
from model import solve_price_saa
from postprocess_order import extract_order_matrices
from plots import (plot_order_placement_bar, 
                   plot_price_distribution_band, 
                   plot_price_and_orders, 
                   plot_price_and_orders_deterministic)




# scalar parameters
h = 5
b = 20
I_0 = 0
B_0 = 0

# Load Excel file
file_path = "pidsg25-02.xlsx"
xls = pd.ExcelFile(file_path)

# Load data sheets
demand_df = pd.read_excel(xls, sheet_name="demand", index_col=0)
price_df_s1 = pd.read_excel(xls, sheet_name="p1normal", index_col=0)
price_df_s2 = pd.read_excel(xls, sheet_name="p2normal", index_col=0)
supplier_df = pd.read_excel(xls, sheet_name="supplier")
capacity_df = pd.read_excel(xls, sheet_name="capacity", index_col=0)

# --- 1. Fixed deterministic demand
fixed_demand = demand_df["Actual"].dropna().values
T = len(fixed_demand)
S = supplier_df["supplier"].tolist()
N = price_df_s1.shape[1]

# --- 2. Supplier lead times
lead_time = dict(zip(supplier_df["supplier"], supplier_df["lead_time"]))
lead_time_s2 = int(lead_time["s2"])

# --- 3. Optional raw orders for s2 (order_time: quantity)
raw_orders_s2 = {
    **{i: 4886.83127572017 for i in range(6)},
    **{i: 2764.92 if i == 6 else 2767.36 for i in range(6, 12)}
}


enforce_fixed_orders = True  # Toggle
fixed_orders_s2 = {
    (t, t + lead_time_s2): q
    for t, q in raw_orders_s2.items()
    if t + lead_time_s2 < T
} if enforce_fixed_orders else None



print("Fixed orders with arrival time:", fixed_orders_s2)

# --- 4. Construct price samples [(t,s) -> price] for each sample
price_samples = []
for i in range(N):
    sample_prices = {}
    for t in range(T):
        sample_prices[(t, 's1')] = price_df_s1.iloc[t, i]
        sample_prices[(t, 's2')] = price_df_s2.iloc[t, i]
    price_samples.append(sample_prices)

# --- 5. Supplier order costs
order_cost = dict(zip(supplier_df["supplier"], supplier_df["order_cost"]))

# --- 6. Time-supplier capacities
capacity_dict = {(t, s): capacity_df.loc[t + 1, s] for t in range(T) for s in S}

# --- 7. Solve the price uncertainty SAA problem
obj_val, df_result = solve_price_saa(
    fixed_demand=fixed_demand,
    price_samples=price_samples[:5],
    order_cost=order_cost,
    lead_time=lead_time,
    capacity_dict=capacity_dict,
    h=h,
    b=b,
    I_0=I_0,
    B_0=B_0,
    fixed_orders_s2=fixed_orders_s2
)

# --- 8. Postprocess and plot
print("Objective Value:", obj_val)
print(df_result)

order_placed, order_arr = extract_order_matrices(df_result)

plot_order_placement_bar(order_placed, start_date="2025-04-01")
plot_price_distribution_band(price_df_s1, price_df_s2, start_date="2025-04-01")
plot_price_and_orders(price_df_s1, order_placed, supplier='s1', start_date="2025-04-01")
plot_price_and_orders(price_df_s2, order_placed, supplier='s2', start_date="2025-04-01")

mean_price_s2 = price_df_s2.iloc[:, 0].values
plot_price_and_orders_deterministic(mean_price_s2, order_placed, supplier='s2', start_date="2025-04-01")

print("Raw orders:", raw_orders_s2)
print("Enforced fixed_orders_s2 (with arrival):", fixed_orders_s2)

