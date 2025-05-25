
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from tempfile import NamedTemporaryFile

from dataclass import ProcurementConfig, ModelData
from model import solve_price_saa
from postprocess_order import extract_order_matrices

app = FastAPI()

@app.post("/optimize/")
async def optimize(file: UploadFile = File(...)):
    # Save uploaded Excel file
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # Load Excel sheets
    xls = pd.ExcelFile(tmp_path)
    demand_df = pd.read_excel(xls, sheet_name="demand", index_col=0)
    price_df_s1 = pd.read_excel(xls, sheet_name="p1normal", index_col=0)
    price_df_s2 = pd.read_excel(xls, sheet_name="p2normal", index_col=0)
    supplier_df = pd.read_excel(xls, sheet_name="supplier")
    capacity_df = pd.read_excel(xls, sheet_name="capacity", index_col=0)

    # Basic setup
    fixed_demand = demand_df["Actual"].dropna().values
    T = len(fixed_demand)
    S = supplier_df["supplier"].tolist()
    lead_time = dict(zip(supplier_df["supplier"], supplier_df["lead_time"]))
    lead_time_s2 = int(lead_time["s2"])

    raw_orders_s2 = {1: 125, 2: 125}
    enforce_fixed_orders = True
    fixed_orders_s2 = {
        (t, t + lead_time_s2): q
        for t, q in raw_orders_s2.items()
        if t + lead_time_s2 < T
    } if enforce_fixed_orders else None

    price_samples = []
    N = price_df_s1.shape[1]
    for i in range(N):
        sample_prices = {}
        for t in range(T):
            sample_prices[(t, 's1')] = price_df_s1.iloc[t, i]
            sample_prices[(t, 's2')] = price_df_s2.iloc[t, i]
        price_samples.append(sample_prices)

    order_cost = dict(zip(supplier_df["supplier"], supplier_df["order_cost"]))
    capacity_dict = {(t, s): capacity_df.loc[t + 1, s] for t in range(T) for s in S}

    # Optimization
    h, b, I_0, B_0 = 5, 50, 0, 0
    obj_val, df_result = solve_price_saa(
        fixed_demand=fixed_demand,
        price_samples=price_samples[:5],
        order_cost=order_cost,
        lead_time=lead_time,
        capacity_dict=capacity_dict,
        h=h, b=b, I_0=I_0, B_0=B_0,
        fixed_orders_s2=fixed_orders_s2
    )

    order_placed, order_arr = extract_order_matrices(df_result)

    return JSONResponse({
        "objective_value": obj_val,
        "orders_placed": order_placed.to_dict(),
        "orders_arrival": order_arr.to_dict(),
    })

