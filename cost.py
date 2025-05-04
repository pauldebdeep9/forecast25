

def compute_fixed_order_cost_from_Y(df_result, order_cost):
    df_y = df_result[df_result['variable_name'].str.contains("if_make_order_arrive")].copy()
    df_y[['t', 's', 't_prime']] = df_y['variable_name'] \
        .str.extract(r"if_make_order_arrive\[(\d+),([a-zA-Z0-9_]+),(\d+)\]") \
        .astype({0: int, 2: int, 1: str})
    
    return sum(order_cost[s] * val for _, (_, s, _, val) in df_y[['t', 's', 't_prime', 'value']].iterrows())


def compute_procurement_cost_from_matrix(order_placed, price_sample):
    """
    Parameters:
    - order_placed: pd.DataFrame [T x S]
    - price_sample: dict {(t, s): price}

    Returns:
    - total procurement cost
    """
    cost = 0
    for (t, s), qty in order_placed.stack().items():
        cost += price_sample[(t, s)] * qty
    return cost


def compute_inventory_backlog_cost_from_df(df_result, h, b):
    df_i = df_result[df_result['variable_name'].str.contains("inventory")]
    df_b = df_result[df_result['variable_name'].str.contains("backlog")]
    return h * df_i['value'].sum(), b * df_b['value'].sum()
