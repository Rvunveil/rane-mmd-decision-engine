"""
Level 2 Tests (M21-M23): Prescriptive Action Matrix, Re-ranking & Ripple Effects.
Team 11:59 · Xovate'26
"""

import pytest
from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all
from engine.actions import evaluate_actions, optimize_action_bundle

def test_M21_action_matrix_hand_calc():
    """M21: Verify hand calculations for 3 actions in Base and Red Sea / Hormuz."""
    # 1. Base case
    res_base = run_all(Scenario())
    actions_base = {a["id"]: a for a in res_base.action_rankings}

    # ACT-07: Container Consolidation (B10 calibrated: 25.0 * (1 - 89.7/98.0) = 2.1173 Cr)
    exp_benefit_07 = 25.0 * (1.0 - (89.7 / 98.0))
    exp_cost_07 = 1.2
    assert abs(actions_base["ACT-07"]["cost_cr"] - exp_cost_07) < 1e-4
    assert abs(actions_base["ACT-07"]["benefit_cr"] - exp_benefit_07) < 1e-4
    assert abs(actions_base["ACT-07"]["net_benefit_cr"] - (exp_benefit_07 - exp_cost_07)) < 1e-4

    # ACT-01: Commodity Hedge (No shock at base)
    # Cost = 1.2 Cr; Benefit = 0.0 Cr; Net = -1.2 Cr
    assert abs(actions_base["ACT-01"]["cost_cr"] - 1.2) < 1e-4
    assert abs(actions_base["ACT-01"]["benefit_cr"] - 0.0) < 1e-4
    assert abs(actions_base["ACT-01"]["net_benefit_cr"] - (-1.2)) < 1e-4

    # ACT-05: Air-Freight Bridge (No delay at base)
    # Cost = 4.8 Cr; Benefit = 0.0 Cr; Net = -4.8 Cr
    assert abs(actions_base["ACT-05"]["cost_cr"] - 4.8) < 1e-4
    assert abs(actions_base["ACT-05"]["benefit_cr"] - 0.0) < 1e-4
    assert abs(actions_base["ACT-05"]["net_benefit_cr"] - (-4.8)) < 1e-4

    # 2. Red Sea / Hormuz crisis preset
    presets = get_default_presets()
    res_crisis = run_all(presets["red_sea_hormuz"])
    actions_crisis = {a["id"]: a for a in res_crisis.action_rankings}

    # ACT-05: Air-Freight Bridge under Red Sea (delay = 18 days >= 12 days)
    # Cost = 4.8 Cr; Benefit = 14.5 Cr; Net = 9.7 Cr
    assert abs(actions_crisis["ACT-05"]["cost_cr"] - 4.8) < 1e-4
    assert abs(actions_crisis["ACT-05"]["benefit_cr"] - 14.5) < 1e-4
    assert abs(actions_crisis["ACT-05"]["net_benefit_cr"] - 9.7) < 1e-4


def test_M22_action_reranking_under_crisis():
    """M22: Ranking changes dynamically between Base and Red Sea/Hormuz crisis."""
    res_base = run_all(Scenario())
    presets = get_default_presets()
    res_crisis = run_all(presets["red_sea_hormuz"])

    base_ranks = {a["id"]: a["rank"] for a in res_base.action_rankings}
    crisis_ranks = {a["id"]: a["rank"] for a in res_crisis.action_rankings}

    # ACT-05 (Air Freight) must jump significantly in rank under crisis
    assert crisis_ranks["ACT-05"] < base_ranks["ACT-05"]

    # ACT-06 (Cape of Good Hope Reroute) must also improve in rank
    assert crisis_ranks["ACT-06"] < base_ranks["ACT-06"]

    # Top action must differ between Base and Crisis
    assert res_base.top_action_id != res_crisis.top_action_id


def test_M23_ripple_matrix_and_suppliers():
    """M23: Ripple matrix covers >=4 functions for every action; suppliers listed."""
    res = run_all(Scenario())
    for act in res.action_rankings:
        # Cross-functional ripple effects
        impacts = act["function_impacts"]
        assert len(impacts) >= 4, f"Action {act['id']} has fewer than 4 function impacts: {list(impacts.keys())}"
        for func, desc in impacts.items():
            assert len(str(desc).strip()) > 0, f"Action {act['id']} has empty impact description for {func}"

        # Affected suppliers
        suppliers = act["affected_suppliers"]
        assert len(suppliers) >= 1, f"Action {act['id']} has no listed suppliers"
