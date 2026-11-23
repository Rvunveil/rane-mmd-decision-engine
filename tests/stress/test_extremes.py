"""
Level 3 Tests (H01-H04, H11, H12): Extreme Boundary Stress & Assumptions Modification.
Team 11.59 · Xovate'26
"""

import pytest
import math
import copy
from engine.scenario import Scenario
from engine.chain import run_all
import tests.oracle as oracle

def test_H01_all_sliders_to_maximum():
    """H01: All sliders to MAX simultaneously: no crash, no NaN, huge loss handled gracefully."""
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    scn_max = Scenario(
        price_shock_pct={m: 100.0 for m in materials},
        freight_multiplier=4.0,
        fx_inr_usd=105.0,
        tariff_pct=25.0,
        demand_volume_pct=-30.0,
        shipping_delay_days=45,
        oem_pass_through_pct=0.0,
        pass_through_lag_days=120
    )
    res = run_all(scn_max)

    assert not math.isnan(res.ebitda_cr)
    assert not math.isnan(res.pat_cr)
    assert not math.isinf(res.ebitda_cr)
    assert not math.isinf(res.pat_cr)
    assert res.ebitda_cr < 0  # Severe loss
    assert res.pat_cr < 0
    assert res.material_spend_cr > 0
    assert len(res.action_rankings) == 10


def test_H02_all_sliders_to_minimum():
    """H02: All sliders to MIN simultaneously: profit rises sensibly, no div-by-zero, positive costs."""
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    scn_min = Scenario(
        price_shock_pct={m: -30.0 for m in materials},
        freight_multiplier=0.5,
        fx_inr_usd=80.0,
        tariff_pct=0.0,
        demand_volume_pct=30.0,
        shipping_delay_days=0,
        oem_pass_through_pct=100.0,
        pass_through_lag_days=0
    )
    res = run_all(scn_min)

    assert not math.isnan(res.ebitda_cr)
    assert not math.isnan(res.pat_cr)
    assert res.ebitda_cr > 297.7  # Profit increases significantly
    assert res.material_spend_cr > 0
    assert res.revenue_cr > 3421.0


def test_H03_pass_through_100pct_with_max_shocks():
    """H03: Pass-through 100% with every price/freight shock at max: recovery exactly offsets cost delta."""
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    scn = Scenario(
        price_shock_pct={m: 100.0 for m in materials},
        freight_multiplier=4.0,
        fx_inr_usd=105.0,
        tariff_pct=25.0,
        demand_volume_pct=0.0,
        oem_pass_through_pct=100.0
    )
    res = run_all(scn)

    # Cost shock total
    total_cost_delta = res.delta_material_cr + res.delta_freight_cr
    # Recovery should exactly equal total cost delta
    assert abs(res.oem_recovery_cr - total_cost_delta) < 1e-4
    # EBITDA should equal base EBITDA (297.7) because volume delta is 0
    assert abs(res.ebitda_cr - 297.7) < 0.01


def test_H04_demand_volume_extremes():
    """H04: Demand volume -30% and -100%: no division by zero, days of cover handled safely."""
    # -30% (slider minimum)
    scn_neg30 = Scenario(demand_volume_pct=-30.0)
    res_neg30 = run_all(scn_neg30)
    assert res_neg30.revenue_cr == 3421.0 * 0.70
    assert res_neg30.worst_days_of_cover > 0
    assert not math.isnan(res_neg30.worst_days_of_cover)

    # Extreme -100% (zero volume edge case)
    scn_zero = Scenario(demand_volume_pct=-100.0)
    res_zero = run_all(scn_zero)
    assert res_zero.revenue_cr == 0.0
    assert not math.isnan(res_zero.ebitda_cr)


def test_H11_edit_assumptions_and_reset():
    """H11: Edit assumptions (tax 30%, custom params): moves PAT but not EBITDA; reset restores baseline."""
    base_res = run_all(Scenario())
    assumptions = oracle.get_oracle_assumptions()

    # Modify tax rate to 30.0%
    modified_assumptions = copy.deepcopy(assumptions)
    modified_assumptions["financial_params"]["tax_rate_pct"] = 30.0

    mod_res = run_all(Scenario(), assumptions=modified_assumptions)
    # EBITDA must be invariant to tax rate change
    assert abs(mod_res.ebitda_cr - base_res.ebitda_cr) < 1e-4
    # PAT must be lower due to higher tax rate
    assert mod_res.pat_cr < base_res.pat_cr

    # Reset / run with original assumptions restores exact baseline
    restored_res = run_all(Scenario(), assumptions=assumptions)
    assert abs(restored_res.pat_cr - base_res.pat_cr) < 1e-4


def test_H12_invalid_assumptions_resilience():
    """H12: Graceful handling of edge assumptions without crashing."""
    assumptions = oracle.get_oracle_assumptions()

    # Empty materials dict fallback
    bad_assumptions = copy.deepcopy(assumptions)
    bad_assumptions["materials"] = {}
    res = run_all(Scenario(), assumptions=bad_assumptions)
    assert not math.isnan(res.ebitda_cr)
    assert res.revenue_cr == 3421.0
