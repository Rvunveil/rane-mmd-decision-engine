"""
Recalculation Chain & P&L Engine for Rane (Madras) MMD Decision Engine
Team 11.59 · Xovate'26
Implements Section 7 financial, landed cost, and division formulas.
"""

import os
import yaml
import math
from typing import Any
from engine.scenario import Scenario
from engine.results import Results
from engine.inventory import evaluate_inventory, evaluate_containers
from engine.actions import evaluate_actions

BASELINE_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "baseline.yaml")
ASSUMPTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "assumptions.yaml")

def load_config(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

# Calibrated FY25 baseline commodity prices
BASELINE_PRICES = {
    "copper": 9369.4,       # USD/t
    "nickel": 16552.9,      # USD/t
    "aluminium": 2526.0,    # USD/t
    "resin": 1437.0,        # USD/t (1.437 USD/kg * 1000)
    "rubber": 140197.0,     # INR/t (14019.7 INR/100kg * 10)
    "steel_hr": 60441.8,    # INR/t (Domestic)
    "steel_cr": 69066.0,    # INR/t (Domestic)
}

FX_BASELINE = 84.5648 # FY25 RBI average reference rate


def compute_landed_costs(scenario: Scenario, assumptions: dict) -> tuple[dict[str, dict[str, Any]], dict[str, float]]:
    """
    Computes landed cost per tonne for all 7 inputs at Baseline and Active Scenario.
    Also calibrates baseline tonnes per input so baseline material spend == ₹1,223.0 Cr.
    """
    mat_cfg = assumptions.get("materials", {})
    landed_results = {}
    annual_tonnes = {}

    fx_base = FX_BASELINE
    fx_scn = scenario.fx_inr_usd
    tariff_pct = scenario.tariff_pct

    for mat_id, cfg in mat_cfg.items():
        base_price_orig = BASELINE_PRICES.get(mat_id, 50000.0)
        curr = cfg.get("currency", "USD")
        duty_pct = float(cfg.get("base_duty_pct", 0.0))
        handling_inr = float(cfg.get("handling_per_t_inr", 1500.0))
        is_import = cfg.get("import_dependent", True)
        freight_usd_t = float(cfg.get("inbound_freight_usd_t", 0.0))
        domestic_freight_inr = float(cfg.get("domestic_freight_per_t_inr", 0.0))

        # Base Raw Material Cost (INR / tonne with base duty)
        if curr == "USD":
            base_price_inr = base_price_orig * fx_base
            landed_base = base_price_inr * (1.0 + duty_pct / 100.0)
            base_freight_inr = freight_usd_t * fx_base
        else:
            base_price_inr = base_price_orig
            landed_base = base_price_inr * (1.0 + duty_pct / 100.0)
            base_freight_inr = domestic_freight_inr

        # Calibrate annual tonnes from spend share
        spend_cr = float(cfg.get("spend_cr", 100.0))
        tonnes = (spend_cr * 1e7) / landed_base
        annual_tonnes[mat_id] = tonnes

        # Scenario Raw Material Cost (INR / tonne)
        shock_pct = float(scenario.price_shock_pct.get(mat_id, 0.0))

        if curr == "USD":
            fx_ratio = fx_scn / fx_base
            effective_duty = duty_pct + tariff_pct
            scn_price_inr = (base_price_orig * (1.0 + shock_pct / 100.0)) * fx_scn
            landed_scn = scn_price_inr * (1.0 + effective_duty / 100.0)
            scn_freight_inr = freight_usd_t * scenario.freight_multiplier * fx_scn
        else:
            scn_price_inr = base_price_orig * (1.0 + shock_pct / 100.0)
            landed_scn = scn_price_inr * (1.0 + duty_pct / 100.0)
            scn_freight_inr = domestic_freight_inr * (1.0 + (scenario.freight_multiplier - 1.0) * 0.2)

        delta_pct = ((landed_scn - landed_base) / landed_base) * 100.0

        landed_results[mat_id] = {
            "name": cfg.get("name", mat_id),
            "currency": curr,
            "base_material_inr_t": landed_base,
            "scenario_material_inr_t": landed_scn,
            "base_freight_inr_t": base_freight_inr,
            "scenario_freight_inr_t": scn_freight_inr,
            "base_landed_inr_t": landed_base + base_freight_inr + handling_inr,
            "scenario_landed_inr_t": landed_scn + scn_freight_inr + handling_inr,
            "delta_pct": delta_pct,
            "annual_tonnes": tonnes,
            "base_spend_cr": spend_cr,
            "import_dependent": is_import
        }

    return landed_results, annual_tonnes


def run_all(scenario: Scenario, assumptions: dict = None) -> Results:
    """
    Core Pure-Python Recalculation Engine.
    Instantly computes entire P&L, Landed Costs, Division Costs,
    Inventory Runways, Container metrics, and Prescriptive Action Matrix.
    """
    baseline_cfg = load_config(BASELINE_PATH)
    if assumptions is None:
        assumptions = load_config(ASSUMPTIONS_PATH)

    fin = baseline_cfg.get("financials", {})
    base_rev = float(fin.get("revenue_cr", 3421.0))
    base_ebitda = float(fin.get("ebitda_cr", 297.7))
    base_material = float(fin.get("material_spend_cr", 1223.0))
    base_freight = float(fin.get("ocean_freight_spend_cr", 25.0))
    tax_rate = float(assumptions.get("financial_params", {}).get("tax_rate_pct", 25.17)) / 100.0
    contrib_margin = float(assumptions.get("financial_params", {}).get("contribution_margin_pct", 28.0)) / 100.0
    fixed_da_interest = float(assumptions.get("financial_params", {}).get("fixed_da_interest_cr", 247.458))

    # 1. Compute Landed Costs per tonne and Calibrated Tonnes
    landed_map, tonnes_map = compute_landed_costs(scenario, assumptions)

    # 2. Material Spend Delta
    demand_mult = 1.0 + (scenario.demand_volume_pct / 100.0)
    scn_material_spend = sum(
        tonnes_map[mat] * demand_mult * landed_map[mat]["scenario_material_inr_t"]
        for mat in landed_map
    ) / 1e7

    # Calibrated baseline spend with volume
    base_spend_vol = base_material * demand_mult
    delta_material = scn_material_spend - base_spend_vol

    # 3. Ocean Freight Spend Delta
    fx_ratio = scenario.fx_inr_usd / FX_BASELINE
    delta_freight = base_freight * (scenario.freight_multiplier * fx_ratio - 1.0) * demand_mult
    scn_freight_spend = base_freight + delta_freight

    # 4. OEM Pass-Through & Recovery
    pass_pct = scenario.oem_pass_through_pct / 100.0
    total_cost_delta = delta_material + delta_freight
    
    # Recovery in Cr
    full_recovery = pass_pct * total_cost_delta
    # Working capital cash gap caused by customer recovery lag
    working_capital_gap = full_recovery * (scenario.pass_through_lag_days / 365.0)

    if getattr(scenario, "in_year_mode", False):
        recovery = full_recovery * ((365.0 - scenario.pass_through_lag_days) / 365.0)
    else:
        recovery = full_recovery

    # 5. Volume & Revenue Impact
    scn_revenue = base_rev * demand_mult
    volume_delta_cr = (scn_revenue - base_rev) * contrib_margin
    lost_contrib = -volume_delta_cr if volume_delta_cr < 0 else 0.0

    # 6. EBITDA, PBT, Tax, PAT
    scn_ebitda = base_ebitda - delta_material - delta_freight + recovery + volume_delta_cr
    ebitda_margin = (scn_ebitda / scn_revenue) * 100.0 if scn_revenue > 0 else 0.0

    scn_pbt = scn_ebitda - fixed_da_interest
    if scn_pbt > 0:
        scn_tax = scn_pbt * tax_rate
        scn_pat = scn_pbt - scn_tax
    else:
        scn_tax = 0.0
        scn_pat = scn_pbt # Negative PAT equals PBT without current-period tax credit

    # 7. Division Cost Breakdown
    divisions_cfg = assumptions.get("divisions", {})
    division_costs = {}
    raw_div_spends = {}
    for div_id, dcfg in divisions_cfg.items():
        dname = dcfg.get("name", div_id)
        dweights = dcfg.get("weights", {})
        d_mat_share = float(dcfg.get("material_cost_share_pct", 25.0)) / 100.0
        base_div_spend = base_material * d_mat_share

        # Weighted landed cost change for this division
        weighted_delta_pct = sum(
            weight * landed_map.get(mid, {}).get("delta_pct", 0.0)
            for mid, weight in dweights.items()
        )
        scn_div_spend = base_div_spend * demand_mult * (1.0 + weighted_delta_pct / 100.0)
        raw_div_spends[div_id] = (dname, base_div_spend, scn_div_spend, weighted_delta_pct)

    # Reconcile division spends so sum(divisions) matches scn_material_spend identically
    raw_total = sum(item[2] for item in raw_div_spends.values())
    scaling = (scn_material_spend / raw_total) if raw_total > 0 else 1.0

    for div_id, (dname, base_div_spend, scn_div_spend, weighted_delta_pct) in raw_div_spends.items():
        reconciled_scn_spend = scn_div_spend * scaling
        denom = base_div_spend * demand_mult
        division_costs[div_id] = {
            "name": dname,
            "base_spend_cr": base_div_spend,
            "scenario_spend_cr": reconciled_scn_spend,
            "delta_cr": reconciled_scn_spend - denom,
            "delta_pct": ((reconciled_scn_spend - denom) / denom) * 100.0 if denom > 0 else 0.0
        }

    # 8. Inventory Runway & Inbound Containers
    inv_summary, worst_days, worst_days_mat, worst_margin, worst_margin_mat = evaluate_inventory(scenario, assumptions, tonnes_map)
    containers, avg_payload, avg_freight_t = evaluate_containers(scenario, assumptions)

    # 9. Prescriptive Action Matrix
    actions = evaluate_actions(scenario, delta_material, delta_freight, base_material, base_freight)
    top_act = actions[0] if actions else {}

    return Results(
        scenario_name=scenario.name,
        revenue_cr=scn_revenue,
        ebitda_cr=scn_ebitda,
        ebitda_margin_pct=ebitda_margin,
        pbt_cr=scn_pbt,
        tax_cr=scn_tax,
        pat_cr=scn_pat,
        material_spend_cr=scn_material_spend,
        ocean_freight_spend_cr=scn_freight_spend,
        delta_material_cr=delta_material,
        delta_freight_cr=delta_freight,
        oem_recovery_cr=recovery,
        lost_contribution_cr=lost_contrib,
        working_capital_gap_cr=working_capital_gap,
        landed_costs=landed_map,
        division_costs=division_costs,
        inventory_summary=inv_summary,
        worst_days_of_cover=worst_days,
        worst_material_name=worst_days_mat,
        worst_runway_margin_days=worst_margin,
        worst_margin_material_name=worst_margin_mat,
        containers=containers,
        avg_container_payload_pct=avg_payload,
        avg_freight_per_tonne_inr=avg_freight_t,
        action_rankings=actions,
        top_action_id=top_act.get("id", ""),
        top_action_title=top_act.get("title", ""),
        top_action_short_name=top_act.get("short_name", top_act.get("title", "")[:24]),
        top_action_net_benefit_cr=top_act.get("net_benefit_cr", 0.0)
    )
