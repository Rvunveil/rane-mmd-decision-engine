"""
Official Section 8 Acceptance Tests for Rane (Madras) MMD Decision Engine
Team 11:59 · Xovate'26
All tests written BEFORE engine code ("implement until green").
"""

import pytest
import math
from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario
from engine.chain import run_all

def test_acceptance_1_base_case():
    """
    Test 1: Official Handout Baseline
    Revenue: 3421, EBITDA: 297.7 (8.7%), PAT: 37.6, Material: 1223, Freight: 25 (within +-0.1)
    """
    presets = get_default_presets()
    base_scn = presets["base_case"]
    res = run_all(base_scn)

    assert math.isclose(res.revenue_cr, 3421.0, abs_tol=0.1), f"Revenue expected 3421.0, got {res.revenue_cr}"
    assert math.isclose(res.ebitda_cr, 297.7, abs_tol=0.1), f"EBITDA expected 297.7, got {res.ebitda_cr}"
    assert math.isclose(res.ebitda_margin_pct, 8.7, abs_tol=0.1), f"Margin expected 8.7%, got {res.ebitda_margin_pct}"
    assert math.isclose(res.pat_cr, 37.6, abs_tol=0.1), f"PAT expected 37.6, got {res.pat_cr}"
    assert math.isclose(res.material_spend_cr, 1223.0, abs_tol=0.1), f"Material spend expected 1223.0, got {res.material_spend_cr}"
    assert math.isclose(res.ocean_freight_spend_cr, 25.0, abs_tol=0.1), f"Freight spend expected 25.0, got {res.ocean_freight_spend_cr}"


def test_acceptance_2_ten_percent_shock_wipes_out_profit():
    """
    Test 2: 10% shock on all 7 inputs, 50% pass-through, annual
    EBITDA drop ~= 61.2 Cr, PAT ~= -10.9 Cr
    Matches '> 60 Cr shock wipes out profit'.
    """
    shock_10_scn = Scenario(
        name="10% Input Cost Shock",
        price_shock_pct={
            "copper": 10.0,
            "nickel": 10.0,
            "aluminium": 10.0,
            "resin": 10.0,
            "rubber": 10.0,
            "steel_hr": 10.0,
            "steel_cr": 10.0
        },
        freight_multiplier=1.0,
        fx_inr_usd=84.5648,
        tariff_pct=0.0,
        demand_volume_pct=0.0,
        shipping_delay_days=0,
        oem_pass_through_pct=50.0,
        pass_through_lag_days=75
    )
    res = run_all(shock_10_scn)
    ebitda_drop = 297.7 - res.ebitda_cr

    assert math.isclose(ebitda_drop, 61.15, abs_tol=0.3), f"EBITDA drop expected ~61.2 Cr, got {ebitda_drop}"
    assert math.isclose(res.pat_cr, -10.9, abs_tol=0.3), f"PAT expected ~ -10.9 Cr, got {res.pat_cr}"


def test_acceptance_3_monotonicity():
    """
    Test 3: Monotonicity
    - More shock -> lower EBITDA
    - More pass-through -> higher EBITDA
    - More delay -> lower days-of-cover margin
    """
    base_scn = Scenario(
        price_shock_pct={"copper": 0, "nickel": 0, "aluminium": 0, "resin": 0, "rubber": 0, "steel_hr": 0, "steel_cr": 0},
        freight_multiplier=1.0,
        fx_inr_usd=84.5648,
        oem_pass_through_pct=50.0,
        shipping_delay_days=0
    )
    res_base = run_all(base_scn)

    # 1. More shock -> lower EBITDA
    scn_shock_5 = Scenario(
        price_shock_pct={"copper": 5, "nickel": 5, "aluminium": 5, "resin": 5, "rubber": 5, "steel_hr": 5, "steel_cr": 5},
        freight_multiplier=1.0,
        fx_inr_usd=84.5648,
        oem_pass_through_pct=50.0
    )
    scn_shock_15 = Scenario(
        price_shock_pct={"copper": 15, "nickel": 15, "aluminium": 15, "resin": 15, "rubber": 15, "steel_hr": 15, "steel_cr": 15},
        freight_multiplier=1.0,
        fx_inr_usd=84.5648,
        oem_pass_through_pct=50.0
    )
    assert run_all(scn_shock_5).ebitda_cr < res_base.ebitda_cr
    assert run_all(scn_shock_15).ebitda_cr < run_all(scn_shock_5).ebitda_cr

    # 2. More pass-through -> higher EBITDA
    scn_pt_30 = Scenario(
        price_shock_pct={"copper": 10, "nickel": 10, "aluminium": 10, "resin": 10, "rubber": 10, "steel_hr": 10, "steel_cr": 10},
        oem_pass_through_pct=30.0
    )
    scn_pt_70 = Scenario(
        price_shock_pct={"copper": 10, "nickel": 10, "aluminium": 10, "resin": 10, "rubber": 10, "steel_hr": 10, "steel_cr": 10},
        oem_pass_through_pct=70.0
    )
    assert run_all(scn_pt_70).ebitda_cr > run_all(scn_pt_30).ebitda_cr

    # 3. More delay -> lower days-of-cover margin
    scn_delay_0 = Scenario(shipping_delay_days=0)
    scn_delay_20 = Scenario(shipping_delay_days=20)
    res_d0 = run_all(scn_delay_0)
    res_d20 = run_all(scn_delay_20)
    assert res_d20.worst_runway_margin_days < res_d0.worst_runway_margin_days


def test_acceptance_4_presets_and_todays_market():
    """
    Test 4: Every preset + 'Today's market' runs without exception;
    Today's market is computed dynamically from data.
    """
    presets = get_default_presets()
    for name, scn in presets.items():
        res = run_all(scn)
        assert res.ebitda_cr is not None
        assert not math.isnan(res.ebitda_cr)

    tm_scn = compute_todays_market_scenario()
    assert tm_scn is not None
    # Verify copper has large shock (~ +50% or more) and steel is positive
    assert tm_scn.price_shock_pct["copper"] > 40.0
    assert tm_scn.price_shock_pct["steel_hr"] > 15.0
    res_tm = run_all(tm_scn)
    assert res_tm.ebitda_cr < 297.7


def test_acceptance_6_action_reranking():
    """
    Test 6: Action ranking changes between Base case and Red Sea/Hormuz preset.
    """
    presets = get_default_presets()
    res_base = run_all(presets["base_case"])
    res_red_sea = run_all(presets["red_sea_hormuz"])

    base_top_action = res_base.top_action_id
    red_sea_top_action = res_red_sea.top_action_id

    assert base_top_action != red_sea_top_action, (
        f"Top action did not change between Base ({base_top_action}) "
        f"and Red Sea ({red_sea_top_action})"
    )
