from typing import Optional
import pandas as pd
import numpy as np

# https://www.gurufocus.com/stock/AVGO/dcf
def intrinsic_value_gurufocus(
    E0: float,         # current EPS without NRI (per share)
    d: float,          # discount rate (e.g., 0.10 for 10%)
    g1: float,         # growth rate during growth stage (e.g., 0.12 for 12%)
    n: int = 10,       # years in growth stage
    g2: float = 0.04,  # terminal (stable) growth rate (e.g., 0.04 for 4%)
    m: int = 10        # years in terminal stage (often 10 in this method)
) -> float:
    """
    Compute intrinsic value per share using the GuruFocus DCF formula:
    
    Intrinsic Value = Future Earnings at Growth Stage + Terminal Value, where
      x = (1 + g1) / (1 + d)
      y = (1 + g2) / (1 + d)
      IV = E0 * x * (1 - x**n) / (1 - x) + E0 * (x**n) * y * (1 - y**m) / (1 - y)

    Notes:
      - E0 should be EPS without NRI.
      - d must be > g2 to ensure convergence (i.e., y < 1).
      - Returns a per-share intrinsic value.
    """
    if E0 < 0:
        raise ValueError("E0 (current EPS without NRI) should be non-negative.")
    if not (0 <= d < 1) or not (0 <= g1 < 1.5) or not (0 <= g2 < 1):
        raise ValueError("Use decimal rates (e.g., 0.10 for 10%). Check that 0<=rates<reasonable bounds.")
    if n <= 0 or m <= 0:
        raise ValueError("n and m must be positive integers.")
    if d <= g2:
        raise ValueError("Discount rate d must be greater than terminal growth g2 for convergence.")

    x = (1 + g1) / (1 + d)
    y = (1 + g2) / (1 + d)

    # Handle edge cases where x or y are ~1 to avoid division-by-zero noise
    def _series_sum(first_ratio: float, years: int) -> float:
        # sum of geometric series: r + r^2 + ... + r^years = r*(1 - r^years)/(1 - r)
        if abs(1 - first_ratio) < 1e-12:
            # when r ~ 1, sum ~ years * r  (limit as r->1)
            return years * first_ratio
        return first_ratio * (1 - first_ratio**years) / (1 - first_ratio)

    growth_stage = E0 * _series_sum(x, n)
    terminal_stage = E0 * (x**n) * _series_sum(y, m)

    return growth_stage + terminal_stage

def dcf_chatgpt(eps_ttm: float):
    growth_years_1_5 = 0.3  # 12% CAGR first 5 years
    growth_years_6_10 = 0.1  # 6% CAGR years 6-10
    terminal_growth = 0.025  # 2.5%

    # Discount rate (WACC proxy)
    discount_rate = 0.09  # 9%

    # Forecast eps_list
    years = list(range(1, 11))
    eps_list = []

    eps = eps_ttm
    for y in years:
        if y <= 5:
            eps *= (1 + growth_years_1_5)
        else:
            eps *= (1 + growth_years_6_10)
        eps_list.append(eps)

    # Discount cash flows
    discount_factors = [(1 / (1 + discount_rate) ** y) for y in years]
    pv_fcfs = [fcf * df for fcf, df in zip(eps_list, discount_factors)]

    # Terminal value
    terminal_value = eps_list[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_terminal = terminal_value * discount_factors[-1]

    # Enterprise value
    enterprise_value = sum(pv_fcfs) + pv_terminal

    # Put into dataframe
    df = pd.DataFrame({
        "Year": years,
        "EPS": eps_list,
        "PV of EPS": pv_fcfs
    })

    return df, enterprise_value

