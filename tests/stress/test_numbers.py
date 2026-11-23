"""
Level 1 (E01) & Level 2 (M01-M17) Numerical Correctness Tests vs Independent Oracle.
Team 11:59 · Xovate'26
"""

import pytest
from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario
from engine.chain import run_all, compute_landed_costs
import tests.oracle as oracle

TOLERANCE = 0.50  # ±0.5 Cr tolerance as specified in prompt

def test_E01_fresh_start_base_case():
    """E01: Fresh start, Base case."""
    scn = Scenario()
    res = run_all(scn)
    base_oracle = oracle.oracle_calculate()

    assert abs(res.revenue_cr - 3421.0) < TOLERANCE
    assert abs(res.ebitda_cr - 297.7) < TOLERANCE
    assert abs(res.pat_cr - 37.6) < TOLERANCE
    assert abs(res.delta_material_cr - 0.0) < TOLERANCE
    assert abs(res.delta_freight_cr - 0.0) < TOLERANCE
    assert abs(res.ebitda_cr - base_oracle["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - base_oracle["pat_cr"]) < TOLERANCE


def test_M01_all_10pct_pass_50pct():
    """M01: All 7 inputs +10%, pass 50%."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks=shocks, pass_through_pct=50.0)

    assert abs(res.ebitda_cr - 236.55) < TOLERANCE
    assert abs(res.pat_cr - (-10.91)) < TOLERANCE
    assert abs(res.delta_material_cr - 122.30) < TOLERANCE
    assert abs(res.oem_recovery_cr - 61.15) < TOLERANCE
    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < 0.01
    assert abs(res.pat_cr - orc["pat_cr"]) < 0.01


def test_M02_all_10pct_pass_0pct():
    """M02: All +10%, pass 0%."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, oem_pass_through_pct=0.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks=shocks, pass_through_pct=0.0)

    assert abs(res.ebitda_cr - 175.40) < TOLERANCE
    assert abs(res.pat_cr - (-72.05)) < TOLERANCE
    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < 0.01


def test_M03_all_10pct_pass_100pct():
    """M03: All +10%, pass 100%."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, oem_pass_through_pct=100.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks=shocks, pass_through_pct=100.0)

    assert abs(res.ebitda_cr - 297.70) < TOLERANCE
    assert abs(res.pat_cr - 37.60) < TOLERANCE
    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < 0.01


def test_M04_freight_2x_only():
    """M04: Freight x2.0 only."""
    scn = Scenario(freight_multiplier=2.0, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(freight_mult=2.0, pass_through_pct=50.0)

    assert abs(res.delta_freight_cr - 25.0) < TOLERANCE
    assert abs(res.ebitda_cr - 285.20) < TOLERANCE
    assert abs(res.pat_cr - 28.25) < TOLERANCE
    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < 0.01


def test_M05_fx_10pct_only():
    """M05: FX +10% only (FX_base x 1.10)."""
    new_fx = oracle.ORACLE_FX_BASE * 1.10
    scn = Scenario(fx_inr_usd=new_fx, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(fx_inr_usd=new_fx, pass_through_pct=50.0)

    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - orc["pat_cr"]) < TOLERANCE
    assert abs(res.delta_freight_cr - orc["delta_freight_cr"]) < TOLERANCE
    assert abs(res.delta_material_cr - orc["delta_material_cr"]) < TOLERANCE


def test_M06_demand_minus_12pct_only():
    """M06: Demand -12% only."""
    scn = Scenario(demand_volume_pct=-12.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(demand_volume_pct=-12.0)

    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - orc["pat_cr"]) < TOLERANCE
    assert abs(res.lost_contribution_cr - orc["lost_contribution_cr"]) < TOLERANCE


def test_M07_copper_10pct_only():
    """M07: Copper +10% only."""
    scn = Scenario(price_shock_pct={"copper": 10.0}, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks={"copper": 10.0}, pass_through_pct=50.0)

    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - orc["pat_cr"]) < TOLERANCE
    assert abs(res.delta_material_cr - orc["delta_material_cr"]) < TOLERANCE


def test_M08_steel_hr_10pct_and_fx_invariance():
    """M08: Steel HR +10% only; domestic steel landed cost must NOT change when FX changes."""
    scn = Scenario(price_shock_pct={"steel_hr": 10.0}, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks={"steel_hr": 10.0}, pass_through_pct=50.0)

    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - orc["pat_cr"]) < TOLERANCE

    # Invariance check: changing FX must not change steel HR landed cost
    scn_fx = Scenario(price_shock_pct={"steel_hr": 10.0}, fx_inr_usd=95.0, oem_pass_through_pct=50.0)
    res_fx = run_all(scn_fx)
    assert abs(res.landed_costs["steel_hr"]["scenario_landed_inr_t"] - res_fx.landed_costs["steel_hr"]["scenario_landed_inr_t"]) < 1e-4


def test_M09_all_10pct_freight_2x_fx_10pct():
    """M09: All +10% + freight x2 + FX +10%, pass 50%."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    new_fx = oracle.ORACLE_FX_BASE * 1.10
    scn = Scenario(price_shock_pct=shocks, freight_multiplier=2.0, fx_inr_usd=new_fx, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks=shocks, freight_mult=2.0, fx_inr_usd=new_fx, pass_through_pct=50.0)

    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - orc["pat_cr"]) < TOLERANCE
    assert abs(res.delta_freight_cr - orc["delta_freight_cr"]) < TOLERANCE
    assert abs(res.delta_material_cr - orc["delta_material_cr"]) < TOLERANCE


def test_M10_all_10pct_demand_minus_12pct():
    """M10: All +10% + demand -12%, pass 50%."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, demand_volume_pct=-12.0, oem_pass_through_pct=50.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks=shocks, demand_volume_pct=-12.0, pass_through_pct=50.0)

    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < TOLERANCE
    assert abs(res.pat_cr - orc["pat_cr"]) < TOLERANCE


def test_M11_in_year_recovery_mode():
    """M11: All +10%, pass 50%, IN-YEAR mode, lag 75d."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, oem_pass_through_pct=50.0, pass_through_lag_days=75, in_year_mode=True)
    res = run_all(scn)
    orc = oracle.oracle_calculate(shocks=shocks, pass_through_pct=50.0, lag_days=75, in_year_mode=True)

    assert abs(res.ebitda_cr - 223.99) < TOLERANCE
    assert abs(res.pat_cr - (-23.46)) < TOLERANCE
    assert abs(res.oem_recovery_cr - 48.59) < TOLERANCE
    assert abs(res.working_capital_gap_cr - 12.57) < TOLERANCE
    assert abs(res.ebitda_cr - orc["ebitda_cr"]) < 0.01


def test_M12_breakeven_uniform_shock():
    """M12: Breakeven uniform shock where PAT = 0 at pass 50%."""
    be_shock = oracle.oracle_breakeven_uniform_shock(pass_through_pct=50.0)
    assert abs(be_shock - 8.22) < 0.10

    # Plug it back into engine
    shocks = {k: be_shock for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, oem_pass_through_pct=50.0)
    res = run_all(scn)
    assert abs(res.pat_cr - 0.0) < 0.30


def test_M13_tariff_10pct_only():
    """M13: Tariff +10% only (must affect imported inputs only)."""
    scn = Scenario(tariff_pct=10.0)
    res = run_all(scn)
    orc = oracle.oracle_calculate(tariff_pct=10.0)

    assert abs(res.delta_material_cr - orc["delta_material_cr"]) < TOLERANCE

    # Check imported vs domestic landed cost delta
    for mid, lc in res.landed_costs.items():
        if lc["import_dependent"]:
            assert lc["delta_pct"] > 0
        else:
            assert lc["delta_pct"] == 0.0


def test_M14_waterfall_reconciliation():
    """M14: Waterfall reconciliation: Sum of bars = EBITDA change exactly (±0.01)."""
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn = Scenario(price_shock_pct=shocks, freight_multiplier=2.0, fx_inr_usd=90.0, demand_volume_pct=-10.0, oem_pass_through_pct=50.0)
    res = run_all(scn)

    ebitda_change = res.ebitda_cr - 297.7
    # Waterfall components: -delta_material - delta_freight + recovery + volume_delta
    vol_delta = (res.revenue_cr - 3421.0) * 0.28
    components_sum = -res.delta_material_cr - res.delta_freight_cr + res.oem_recovery_cr + vol_delta
    assert abs(ebitda_change - components_sum) < 0.01


def test_M15_division_cost_totals():
    """M15: Division cost totals: Sum of divisions = total material spend for base and M09."""
    # Base
    res_base = run_all(Scenario())
    div_sum_base = sum(d["scenario_spend_cr"] for d in res_base.division_costs.values())
    assert abs(div_sum_base - res_base.material_spend_cr) < 0.50

    # M09
    shocks = {k: 10.0 for k in oracle.ORACLE_BASELINE_PRICES}
    scn_m09 = Scenario(price_shock_pct=shocks, freight_multiplier=2.0, fx_inr_usd=oracle.ORACLE_FX_BASE * 1.10, oem_pass_through_pct=50.0)
    res_m09 = run_all(scn_m09)
    div_sum_m09 = sum(d["scenario_spend_cr"] for d in res_m09.division_costs.values())
    assert abs(div_sum_m09 - res_m09.material_spend_cr) < 0.50


def test_M16_landed_cost_per_tonne_invariance():
    """M16: Imported rows move with FX and freight; domestic rows don't move with FX."""
    res_base = run_all(Scenario())
    res_fx = run_all(Scenario(fx_inr_usd=100.0))

    for mid in ["rubber", "steel_hr", "steel_cr"]:
        base_lc = res_base.landed_costs[mid]["scenario_material_inr_t"]
        fx_lc = res_fx.landed_costs[mid]["scenario_material_inr_t"]
        assert abs(base_lc - fx_lc) < 1e-4

    for mid in ["copper", "nickel", "aluminium", "resin"]:
        base_lc = res_base.landed_costs[mid]["scenario_material_inr_t"]
        fx_lc = res_fx.landed_costs[mid]["scenario_material_inr_t"]
        assert fx_lc > base_lc


def test_M17_todays_market_preset():
    """M17: Today's market preset: shocks computed from actual processed data."""
    todays_scn = compute_todays_market_scenario()
    assert todays_scn.name == "Today's market (Live Data)"
    # Copper price in latest data is around $14,508 vs ~9,369 baseline (+54.8%)
    assert todays_scn.price_shock_pct["copper"] > 40.0
    # Steel HR coil is around +27%
    assert todays_scn.price_shock_pct["steel_hr"] > 20.0
    # FX is around 94.6 vs 84.56 baseline
    assert todays_scn.fx_inr_usd > 90.0
