"""
Independent Calculation Oracle for Rane (Madras) MMD Decision Engine
Team 11.59 · Xovate'26

NON-NEGOTIABLE RULE:
This module contains ZERO imports from engine/*.
All calculations are pure hand-arithmetic implemented directly from Section 7 / Section 2
formulas and config/*.yaml values. It acts as the hostile, independent test oracle.
"""

import os
import yaml
import math
from typing import Any

# Locate config files directly relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE_FILE = os.path.join(BASE_DIR, "config", "baseline.yaml")
ASSUMPTIONS_FILE = os.path.join(BASE_DIR, "config", "assumptions.yaml")

def load_yaml(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

# Baseline reference values from config/baseline.yaml
def get_oracle_baseline() -> dict:
    raw = load_yaml(BASELINE_FILE)
    fin = raw.get("financials", {})
    return {
        "revenue_cr": float(fin.get("revenue_cr", 3421.0)),
        "ebitda_cr": float(fin.get("ebitda_cr", 297.7)),
        "material_spend_cr": float(fin.get("material_spend_cr", 1223.0)),
        "ocean_freight_spend_cr": float(fin.get("ocean_freight_spend_cr", 25.0)),
        "pat_cr": float(fin.get("pat_cr", 37.6)),
    }

def get_oracle_assumptions() -> dict:
    return load_yaml(ASSUMPTIONS_FILE)

# Baseline prices calibrated in FY25
ORACLE_BASELINE_PRICES = {
    "copper": 9369.4,       # USD/t
    "nickel": 16552.9,      # USD/t
    "aluminium": 2526.0,    # USD/t
    "resin": 1437.0,        # USD/t
    "rubber": 140197.0,     # INR/t
    "steel_hr": 60441.8,    # INR/t
    "steel_cr": 69066.0,    # INR/t
}

ORACLE_FX_BASE = 84.5648

def oracle_compute_landed_costs(
    shocks: dict[str, float] = None,
    fx_inr_usd: float = ORACLE_FX_BASE,
    freight_mult: float = 1.0,
    tariff_pct: float = 0.0,
    assumptions: dict = None
) -> tuple[dict[str, dict[str, Any]], dict[str, float]]:
    """
    Computes landed costs per tonne and calibrated tonnes completely independently.
    """
    if shocks is None:
        shocks = {}
    if assumptions is None:
        assumptions = get_oracle_assumptions()

    mats = assumptions.get("materials", {})
    landed_map = {}
    tonnes_map = {}

    for mat_id, cfg in mats.items():
        base_price = ORACLE_BASELINE_PRICES.get(mat_id, 10000.0)
        spend_cr = float(cfg.get("spend_cr", 100.0))
        is_import = cfg.get("import_dependent", True)
        base_duty = float(cfg.get("base_duty_pct", 0.0)) / 100.0
        handling_t = float(cfg.get("handling_per_t_inr", 1000.0))
        freight_usd = float(cfg.get("inbound_freight_usd_t", 0.0))
        domestic_freight_t = float(cfg.get("domestic_freight_per_t_inr", 0.0))
        shock = float(shocks.get(mat_id, 0.0)) / 100.0

        if is_import:
            # Base material cost (INR / tonne with base duty)
            base_mat_inr = base_price * ORACLE_FX_BASE * (1.0 + base_duty)
            base_landed_inr = base_mat_inr + (freight_usd * ORACLE_FX_BASE) + handling_t
            cal_tonnes = (spend_cr * 1e7) / base_mat_inr

            # Scenario landed cost
            scn_price_usd = base_price * (1.0 + shock)
            scn_mat_inr = scn_price_usd * fx_inr_usd * (1.0 + base_duty + (tariff_pct / 100.0))
            scn_freight_inr = (freight_usd * freight_mult) * fx_inr_usd
            scn_landed_inr = scn_mat_inr + scn_freight_inr + handling_t
        else:
            # Domestic
            base_mat_inr = base_price * (1.0 + base_duty)
            base_landed_inr = base_mat_inr + domestic_freight_t + handling_t
            cal_tonnes = (spend_cr * 1e7) / base_mat_inr

            # Scenario
            scn_price_inr = base_price * (1.0 + shock)
            scn_mat_inr = scn_price_inr * (1.0 + base_duty)
            scn_freight_inr = domestic_freight_t * (1.0 + (freight_mult - 1.0) * 0.2)
            scn_landed_inr = scn_mat_inr + scn_freight_inr + handling_t

        delta_pct = ((scn_landed_inr - base_landed_inr) / base_landed_inr) * 100.0

        landed_map[mat_id] = {
            "base_material_inr_t": base_mat_inr,
            "base_landed_inr_t": base_landed_inr,
            "scenario_material_inr_t": scn_mat_inr,
            "scenario_freight_inr_t": scn_freight_inr,
            "scenario_landed_inr_t": scn_landed_inr,
            "delta_pct": delta_pct,
            "is_import": is_import
        }
        tonnes_map[mat_id] = cal_tonnes

    return landed_map, tonnes_map


def oracle_calculate(
    shocks: dict[str, float] = None,
    freight_mult: float = 1.0,
    fx_inr_usd: float = ORACLE_FX_BASE,
    tariff_pct: float = 0.0,
    demand_volume_pct: float = 0.0,
    pass_through_pct: float = 50.0,
    lag_days: int = 75,
    in_year_mode: bool = False,
    contrib_margin_pct: float = None,
    assumptions_override: dict = None
) -> dict[str, Any]:
    """
    Pure arithmetic oracle calculator for all P&L metrics.
    """
    if shocks is None:
        shocks = {}
    base_fin = get_oracle_baseline()
    assumptions = assumptions_override if assumptions_override else get_oracle_assumptions()

    fin_params = assumptions.get("financial_params", {})
    tax_rate = float(fin_params.get("tax_rate_pct", 25.17)) / 100.0
    fixed_da = float(fin_params.get("fixed_da_interest_cr", 247.458))
    if contrib_margin_pct is None:
        contrib_margin = float(fin_params.get("contribution_margin_pct", 28.0)) / 100.0
    else:
        contrib_margin = contrib_margin_pct / 100.0

    demand_mult = 1.0 + (demand_volume_pct / 100.0)

    # 1. Landed costs & material spend
    landed_map, tonnes_map = oracle_compute_landed_costs(
        shocks=shocks,
        fx_inr_usd=fx_inr_usd,
        freight_mult=freight_mult,
        tariff_pct=tariff_pct,
        assumptions=assumptions
    )

    scn_material_spend = sum(
        tonnes_map[m] * demand_mult * landed_map[m]["scenario_material_inr_t"]
        for m in landed_map
    ) / 1e7

    base_material_spend_vol = base_fin["material_spend_cr"] * demand_mult
    delta_material = scn_material_spend - base_material_spend_vol

    # 2. Freight delta
    fx_ratio = fx_inr_usd / ORACLE_FX_BASE
    delta_freight = base_fin["ocean_freight_spend_cr"] * (freight_mult * fx_ratio - 1.0) * demand_mult
    scn_freight_spend = base_fin["ocean_freight_spend_cr"] + delta_freight

    # 3. Recovery & cash gap
    pass_pct = pass_through_pct / 100.0
    total_cost_delta = delta_material + delta_freight

    full_recovery = pass_pct * total_cost_delta
    cash_gap = full_recovery * (lag_days / 365.0)

    if in_year_mode:
        recovery = full_recovery * ((365.0 - lag_days) / 365.0)
    else:
        recovery = full_recovery

    # 4. Revenue & Lost contribution
    scn_revenue = base_fin["revenue_cr"] * demand_mult
    volume_delta_cr = (scn_revenue - base_fin["revenue_cr"]) * contrib_margin
    lost_contrib = -volume_delta_cr if volume_delta_cr < 0 else 0.0

    # 5. EBITDA
    scn_ebitda = base_fin["ebitda_cr"] - delta_material - delta_freight + recovery + volume_delta_cr
    ebitda_margin = (scn_ebitda / scn_revenue) * 100.0 if scn_revenue > 0 else 0.0

    # 6. PBT & PAT
    scn_pbt = scn_ebitda - fixed_da
    if scn_pbt > 0:
        scn_tax = scn_pbt * tax_rate
        scn_pat = scn_pbt - scn_tax
    else:
        scn_tax = 0.0
        scn_pat = scn_pbt

    # 7. Division breakdown
    div_costs = {}
    raw_divs = {}
    for div_id, dcfg in assumptions.get("divisions", {}).items():
        d_share = float(dcfg.get("material_cost_share_pct", 25.0)) / 100.0
        base_div = base_fin["material_spend_cr"] * d_share
        dweights = dcfg.get("weights", {})
        weighted_delta_pct = sum(
            weight * landed_map.get(mid, {}).get("delta_pct", 0.0)
            for mid, weight in dweights.items()
        )
        scn_div = base_div * demand_mult * (1.0 + weighted_delta_pct / 100.0)
        raw_divs[div_id] = (base_div, scn_div, weighted_delta_pct)

    raw_total = sum(v[1] for v in raw_divs.values())
    scaling = (scn_material_spend / raw_total) if raw_total > 0 else 1.0

    for div_id, (base_div, scn_div, weighted_delta_pct) in raw_divs.items():
        reconciled_div = scn_div * scaling
        denom = base_div * demand_mult
        div_costs[div_id] = {
            "base_spend_cr": base_div,
            "scenario_spend_cr": reconciled_div,
            "delta_cr": reconciled_div - denom,
            "delta_pct": ((reconciled_div - denom) / denom) * 100.0 if denom > 0 else 0.0
        }

    return {
        "revenue_cr": scn_revenue,
        "ebitda_cr": scn_ebitda,
        "ebitda_margin_pct": ebitda_margin,
        "pbt_cr": scn_pbt,
        "tax_cr": scn_tax,
        "pat_cr": scn_pat,
        "material_spend_cr": scn_material_spend,
        "ocean_freight_spend_cr": scn_freight_spend,
        "delta_material_cr": delta_material,
        "delta_freight_cr": delta_freight,
        "oem_recovery_cr": recovery,
        "full_recovery_cr": full_recovery,
        "working_capital_gap_cr": cash_gap,
        "lost_contribution_cr": lost_contrib,
        "landed_map": landed_map,
        "tonnes_map": tonnes_map,
        "division_costs": div_costs
    }


def oracle_inventory_item(mat_id: str, added_delay_days: int = 0, assumptions: dict = None) -> dict[str, Any]:
    """
    Computes days of cover, safety stock, and ROP for a single material independently.
    """
    if assumptions is None:
        assumptions = get_oracle_assumptions()
    
    cfg = assumptions.get("materials", {}).get(mat_id, {})
    _, tonnes_map = oracle_compute_landed_costs(assumptions=assumptions)
    
    tonnes_yr = tonnes_map.get(mat_id, 1000.0)
    daily_usage = tonnes_yr / 365.0
    stock_tonnes = float(cfg.get("stock_on_hand_tonnes", 500.0))
    days_of_cover = stock_tonnes / daily_usage if daily_usage > 0 else 999.0
    
    supplier_lt = int(cfg.get("supplier_lead_time_days", 30))
    is_import = cfg.get("import_dependent", True)
    effective_lt = supplier_lt + (added_delay_days if is_import else 0)
    
    sigma_pct = float(cfg.get("daily_usage_sigma_pct", 15.0)) / 100.0
    sigma_daily = daily_usage * sigma_pct
    z = float(cfg.get("service_level_z", 1.65))
    safety_stock = z * sigma_daily * math.sqrt(max(effective_lt, 1))
    rop = (daily_usage * effective_lt) + safety_stock
    
    margin_days = days_of_cover - effective_lt
    if days_of_cover < effective_lt:
        status = "Stock-out Risk"
    elif stock_tonnes <= rop:
        status = "Watch / Reorder"
    else:
        status = "Covered / Safe"
        
    return {
        "stock_tonnes": stock_tonnes,
        "daily_usage": daily_usage,
        "days_of_cover": days_of_cover,
        "effective_lt": effective_lt,
        "safety_stock": safety_stock,
        "rop": rop,
        "margin_days": margin_days,
        "status": status
    }


def oracle_containers(freight_mult: float = 1.0, fx: float = ORACLE_FX_BASE, delay_days: int = 0) -> list[dict[str, Any]]:
    """
    Calculates container shipments independently.
    """
    assumptions = get_oracle_assumptions()
    shipments = assumptions.get("container_logistics", {}).get("sample_inbound_shipments", [])
    max_payload = 26.0
    current_freight_inr = 2172.0 * freight_mult * fx
    
    results = []
    for s in shipments:
        cargo_t = float(s.get("cargo_tonnes", 20.0))
        payload_pct = min((cargo_t / max_payload) * 100.0, 100.0)
        freight_t = current_freight_inr / cargo_t if cargo_t > 0 else 0.0
        base_eta = int(s.get("eta_days", 20))
        is_delayed = "Bottleneck" in s.get("status", "") or "Disrupted" in s.get("route", "")
        effective_eta = base_eta + (delay_days if is_delayed else 0)
        results.append({
            "id": s.get("id"),
            "cargo_tonnes": cargo_t,
            "payload_pct": payload_pct,
            "freight_per_t_inr": freight_t,
            "effective_eta": effective_eta
        })
    return results


def oracle_breakeven_uniform_shock(pass_through_pct: float = 50.0) -> float:
    """
    Finds uniform shock where PAT = 0 (EBITDA = fixed_da = 247.458).
    Required EBITDA drop = 297.70 - 247.458 = 50.242 Cr.
    At pass_through_pct: net drop = (1 - pass_pct) * 1223.0 * shock.
    shock = 50.242 / (1223.0 * (1 - pass_pct))
    """
    assumptions = get_oracle_assumptions()
    fixed_da = float(assumptions.get("financial_params", {}).get("fixed_da_interest_cr", 247.458))
    base_ebitda = 297.70
    base_mat = 1223.0
    target_drop = base_ebitda - fixed_da
    pass_pct = pass_through_pct / 100.0
    unrecovered_fraction = 1.0 - pass_pct
    if unrecovered_fraction <= 0:
        return 999.0
    return (target_drop / (base_mat * unrecovered_fraction)) * 100.0
