"""
Scenario Dataclass and Preset Definitions for Rane MMD Decision Engine
Team 11:59 · Xovate'26
"""

from dataclasses import dataclass, field
import os
import yaml
import pandas as pd

DEFAULT_PRESETS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "presets.yaml")

@dataclass(frozen=True)
class Scenario:
    name: str = "Base case"
    price_shock_pct: dict[str, float] = field(default_factory=lambda: {
        "copper": 0.0,
        "nickel": 0.0,
        "aluminium": 0.0,
        "resin": 0.0,
        "rubber": 0.0,
        "steel_hr": 0.0,
        "steel_cr": 0.0
    })
    freight_multiplier: float = 1.0     # 1.0 = USD 2,172 / 40ft
    fx_inr_usd: float = 84.5648         # FY25 RBI avg reference rate
    tariff_pct: float = 0.0
    demand_volume_pct: float = 0.0
    shipping_delay_days: int = 0
    oem_pass_through_pct: float = 50.0  # Official handout default
    pass_through_lag_days: int = 75     # 60–90 days lag per case
    in_year_mode: bool = False


def get_default_presets() -> dict[str, Scenario]:
    """Loads calibrated presets from presets.yaml"""
    if os.path.exists(DEFAULT_PRESETS_PATH):
        with open(DEFAULT_PRESETS_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        presets = {}
        for key, p in data.items():
            presets[key] = Scenario(
                name=p.get("name", key),
                price_shock_pct=p.get("price_shock_pct", {}),
                freight_multiplier=float(p.get("freight_multiplier", 1.0)),
                fx_inr_usd=float(p.get("fx_inr_usd", 84.5648)),
                tariff_pct=float(p.get("tariff_pct", 0.0)),
                demand_volume_pct=float(p.get("demand_volume_pct", 0.0)),
                shipping_delay_days=int(p.get("shipping_delay_days", 0)),
                oem_pass_through_pct=float(p.get("oem_pass_through_pct", 50.0)),
                pass_through_lag_days=int(p.get("pass_through_lag_days", 75))
            )
        return presets

    # Fallback if yaml not found
    return {
        "base_case": Scenario(),
        "red_sea_hormuz": Scenario(
            name="Red Sea / Hormuz crisis",
            price_shock_pct={"copper": 12.0, "nickel": 8.0, "aluminium": 18.0, "resin": 10.0, "rubber": 5.0, "steel_hr": 6.0, "steel_cr": 6.0},
            freight_multiplier=2.73,
            shipping_delay_days=18
        )
    }


def compute_todays_market_scenario() -> Scenario:
    """
    Computes 'Today's market' preset dynamically from live processed data
    by measuring the percentage change between latest available price/rate
    and the FY25 baseline average.
    """
    proc_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    
    # 1. FX
    fx_path = os.path.join(proc_dir, "fx_daily.csv")
    if os.path.exists(fx_path):
        df_fx = pd.read_csv(fx_path)
        df_fx['date'] = pd.to_datetime(df_fx['date'])
        fy25_fx = df_fx[(df_fx['date'] >= '2024-04-01') & (df_fx['date'] <= '2025-03-31')]['rate'].mean()
        latest_fx = df_fx.iloc[-1]['rate']
    else:
        fy25_fx, latest_fx = 84.5648, 94.60

    # 2. Materials
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    shocks = {}
    for mat in materials:
        csv_p = os.path.join(proc_dir, f"{mat}.csv")
        if os.path.exists(csv_p):
            df = pd.read_csv(csv_p)
            df['ds'] = pd.to_datetime(df['ds'])
            fy25_sub = df[(df['ds'] >= '2024-04-01') & (df['ds'] <= '2025-03-31')]
            if not fy25_sub.empty:
                fy25_val = fy25_sub['y'].mean()
            else:
                fy25_val = df.iloc[0]['y']
            
            latest_val = df.iloc[-1]['y']
            pct_change = ((latest_val - fy25_val) / fy25_val) * 100.0
            shocks[mat] = round(pct_change, 1)
        else:
            shocks[mat] = 0.0

    return Scenario(
        name="Today's market (Live Data)",
        price_shock_pct=shocks,
        freight_multiplier=1.0, # Handout specifies baseline $2,172 is 19 Mar 2026 freight rate
        fx_inr_usd=round(latest_fx, 2),
        tariff_pct=0.0,
        demand_volume_pct=0.0,
        shipping_delay_days=5,
        oem_pass_through_pct=50.0,
        pass_through_lag_days=75
    )
