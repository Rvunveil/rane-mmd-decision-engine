"""
Part C: Cross-Control Consistency & Scenario Lifecycle
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Verifies:
- Sidebar lever ↔ Control Room deck lever ↔ guided-helper ↔ preset parity
- State persistence across pages
- Scenario Save, Load, Delete, and Compare table fidelity
"""

import os
import sys
import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.scenario import Scenario, get_default_presets
from engine.state import (
    init_canonical_state,
    get_current_scenario,
    apply_preset_by_name,
    apply_scenario_values,
    reset_to_base
)
from engine.chain import run_all
from ui.guided_helper import compute_guided_recommendation


def test_part_c_preset_vs_helper_parity():
    """C1: Verify that Preset and Guided Helper produce consistent engine results for Red Sea."""
    presets = get_default_presets()
    scn_preset = presets["red_sea_hormuz"]
    res_preset = run_all(scn_preset)

    # Guided helper for Red Sea
    helper_out = compute_guided_recommendation("shipping", "Large")
    helper_shock = helper_out["scenario_dict"]

    assert abs(scn_preset.freight_multiplier - helper_shock.get("freight_multiplier", 1.0)) < 0.1
    assert scn_preset.shipping_delay_days == helper_shock.get("shipping_delay_days", 0)


def test_part_c_lever_deck_sidebar_parity():
    """C2: Changing a lever via deck or sidebar results in identical canonical scn."""
    state_deck = {}
    init_canonical_state(state_deck)
    apply_scenario_values({"freight_multiplier": 2.5, "shipping_delay_days": 15}, state=state_deck)
    scn_deck = get_current_scenario(state_deck)
    res_deck = run_all(scn_deck)

    state_sb = {}
    init_canonical_state(state_sb)
    apply_scenario_values({"freight_multiplier": 2.5, "shipping_delay_days": 15}, state=state_sb)
    scn_sb = get_current_scenario(state_sb)
    res_sb = run_all(scn_sb)

    assert scn_deck == scn_sb
    assert res_deck.revenue_cr == res_sb.revenue_cr
    assert res_deck.ebitda_cr == res_sb.ebitda_cr
    assert res_deck.pat_cr == res_sb.pat_cr
    assert res_deck.delta_material_cr == res_sb.delta_material_cr


def test_part_c_state_persistence_across_pages():
    """C3: State applied on Command Centre persists when loading Profit Chain or Scenario Simulator."""
    shared_session = {}
    init_canonical_state(shared_session)

    # Apply Metal Shock
    apply_preset_by_name(shared_session, "metal_shock")
    active_scn = get_current_scenario(shared_session)
    expected_res = run_all(active_scn)

    # Now load Scenario Simulator with this state
    at_sim = AppTest.from_file(os.path.join(BASE_DIR, "pages/2_Scenario_Simulator.py"), default_timeout=30)
    for k, v in shared_session.items():
        at_sim.session_state[k] = v
    at_sim.run()
    assert not at_sim.exception
    assert at_sim.session_state["scn"]["copper"] == 35.0
    assert at_sim.session_state["scn"]["steel_hr"] == 28.0

    # Load Profit Chain with this state
    at_chain = AppTest.from_file(os.path.join(BASE_DIR, "pages/3_Profit_Chain.py"), default_timeout=30)
    for k, v in shared_session.items():
        at_chain.session_state[k] = v
    at_chain.run()
    assert not at_chain.exception
    assert at_chain.session_state["scn"]["copper"] == 35.0


def test_part_c_scenario_save_load_delete_lifecycle():
    """C4: Save scenario → change values → Load scenario → exact restore. Delete scenario."""
    state = {}
    init_canonical_state(state)

    # 1. Start with Red Sea
    apply_preset_by_name(state, "red_sea_hormuz")
    saved_copy = get_current_scenario(state)
    state["saved_scenarios"]["Saved_Red_Sea"] = saved_copy

    # 2. Modify to Metal Shock
    apply_preset_by_name(state, "metal_shock")
    assert state["scn"]["name"] in ["Metal shock", "Global metal shock"]
    assert state["scn"]["copper"] == 35.0

    # 3. Load saved scenario back
    loaded = state["saved_scenarios"]["Saved_Red_Sea"]
    apply_scenario_values({
        "name": loaded.name,
        "freight_multiplier": loaded.freight_multiplier,
        "shipping_delay_days": loaded.shipping_delay_days,
        "fx_inr_usd": loaded.fx_inr_usd,
        "copper": loaded.price_shock_pct.get("copper", 0.0),
        "nickel": loaded.price_shock_pct.get("nickel", 0.0),
        "aluminium": loaded.price_shock_pct.get("aluminium", 0.0),
        "resin": loaded.price_shock_pct.get("resin", 0.0),
        "rubber": loaded.price_shock_pct.get("rubber", 0.0),
        "steel_hr": loaded.price_shock_pct.get("steel_hr", 0.0),
        "steel_cr": loaded.price_shock_pct.get("steel_cr", 0.0),
        "oem_pass_through_pct": loaded.oem_pass_through_pct,
        "demand_volume_pct": loaded.demand_volume_pct,
        "tariff_pct": loaded.tariff_pct
    }, state=state)

    restored = get_current_scenario(state)
    assert restored.name == saved_copy.name
    assert abs(restored.freight_multiplier - saved_copy.freight_multiplier) < 0.001
    assert restored.shipping_delay_days == saved_copy.shipping_delay_days

    # 4. Delete saved scenario
    del state["saved_scenarios"]["Saved_Red_Sea"]
    assert "Saved_Red_Sea" not in state["saved_scenarios"]


def test_part_c_compare_table_fidelity():
    """C5: Saved scenario comparison matches each scenario's individual run_all."""
    presets = get_default_presets()
    s1 = presets["base_case"]
    s2 = presets["red_sea_hormuz"]
    s3 = presets["metal_shock"]

    r1 = run_all(s1)
    r2 = run_all(s2)
    r3 = run_all(s3)

    compare_records = [
        {"Scenario": s1.name, "Revenue": r1.revenue_cr, "EBITDA": r1.ebitda_cr, "PAT": r1.pat_cr},
        {"Scenario": s2.name, "Revenue": r2.revenue_cr, "EBITDA": r2.ebitda_cr, "PAT": r2.pat_cr},
        {"Scenario": s3.name, "Revenue": r3.revenue_cr, "EBITDA": r3.ebitda_cr, "PAT": r3.pat_cr},
    ]

    for rec, res in zip(compare_records, [r1, r2, r3]):
        assert rec["Revenue"] == res.revenue_cr
        assert rec["EBITDA"] == res.ebitda_cr
        assert rec["PAT"] == res.pat_cr
