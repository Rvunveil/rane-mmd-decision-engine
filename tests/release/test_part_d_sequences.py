"""
Part D: Automated AppTest Suite — Scripted State Sequences
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

9 Scripted Sequences where state bugs typically hide:
1. preset → slider → preset → Reset
2. page switch mid-change
3. guided helper apply → sidebar change → Control Room chip
4. "Use forecast as scenario" → Scenario page → Profit Chain
5. demo start → page switch → stop → manual slider
6. demo start → Reset during demo
7. save → load during demo
8. Simple view on → preset → off
9. 20 rapid alternating preset clicks
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
from demo.player import start_demo, stop_demo, is_demo_running


def test_seq_1_preset_slider_preset_reset():
    """Seq 1: preset → slider → preset → Reset."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()
    assert not at.exception

    # 1. Preset: Red Sea
    chip_rs = next(b for b in at.button if b.label == "Red Sea / Hormuz")
    chip_rs.click().run()
    assert not at.exception
    assert abs(at.session_state["scn"]["freight_multiplier"] - 2.73) < 0.05

    # 2. Slider change
    slider_fr = next(s for s in at.slider if s.key == "deck_freight")
    slider_fr.set_value(3.5).run()
    assert not at.exception
    assert abs(at.session_state["scn"]["freight_multiplier"] - 3.5) < 0.01

    # 3. Preset: Metal shock
    chip_ms = next(b for b in at.button if b.label == "Metal shock")
    chip_ms.click().run()
    assert not at.exception
    assert at.session_state["scn"]["copper"] == 35.0

    # 4. Reset
    btn_reset = next(b for b in at.button if ":material/restart_alt: Reset" in b.label)
    btn_reset.click().run()
    assert not at.exception
    assert at.session_state["scn"]["freight_multiplier"] == 1.0
    assert at.session_state["scn"]["copper"] == 0.0


def test_seq_2_page_switch_mid_change():
    """Seq 2: Lever change on Simulator carried over to Profit Chain."""
    state = {}
    init_canonical_state(state)
    apply_scenario_values({"copper": 25.0, "freight_multiplier": 2.2}, state=state)

    # Load Simulator with modified state
    at_sim = AppTest.from_file(os.path.join(BASE_DIR, "pages/2_Scenario_Simulator.py"), default_timeout=30)
    for k, v in state.items():
        at_sim.session_state[k] = v
    at_sim.run()
    assert not at_sim.exception

    # Further modify on Simulator
    apply_scenario_values({"shipping_delay_days": 12}, state=at_sim.session_state)
    at_sim.run()
    assert not at_sim.exception

    # Switch to Profit Chain
    at_chain = AppTest.from_file(os.path.join(BASE_DIR, "pages/3_Profit_Chain.py"), default_timeout=30)
    for k, v in at_sim.session_state.items():
        at_chain.session_state[k] = v
    at_chain.run()
    assert not at_chain.exception
    assert at_chain.session_state["scn"]["copper"] == 25.0
    assert at_chain.session_state["scn"]["freight_multiplier"] == 2.2
    assert at_chain.session_state["scn"]["shipping_delay_days"] == 12


def test_seq_3_guided_helper_sidebar_deck_chip():
    """Seq 3: Guided helper apply → sidebar change → Control Room chip."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()
    assert not at.exception

    # 1. Simulate guided helper apply
    apply_scenario_values({"freight_multiplier": 2.0, "shipping_delay_days": 14, "name": "Guided Shipping"}, state=at.session_state)
    at.run()
    assert not at.exception
    assert at.session_state["scn"]["freight_multiplier"] == 2.0

    # 2. Sidebar lever change
    apply_scenario_values({"shipping_delay_days": 21}, state=at.session_state)
    at.run()
    assert not at.exception
    assert at.session_state["scn"]["shipping_delay_days"] == 21

    # 3. Control room chip click
    chip_tf = next(b for b in at.button if b.label == "Tariff & FX")
    chip_tf.click().run()
    assert not at.exception
    assert at.session_state["scn"]["tariff_pct"] == 10.0


def test_seq_4_forecast_to_simulator_to_profit_chain():
    """Seq 4: 'Use forecast as scenario' → Scenario page → Profit Chain."""
    state = {}
    init_canonical_state(state)

    # Simulate forecast calibration shock apply
    forecast_shocks = {
        "copper": 14.2,
        "aluminium": 9.8,
        "freight_multiplier": 1.45,
        "name": "Q3-FY27 Forecast Scenario"
    }
    apply_scenario_values(forecast_shocks, state=state)

    # 1. Load Scenario Simulator
    at_sim = AppTest.from_file(os.path.join(BASE_DIR, "pages/2_Scenario_Simulator.py"), default_timeout=30)
    for k, v in state.items():
        at_sim.session_state[k] = v
    at_sim.run()
    assert not at_sim.exception
    assert at_sim.session_state["scn"]["copper"] == 14.2

    # 2. Load Profit Chain
    at_chain = AppTest.from_file(os.path.join(BASE_DIR, "pages/3_Profit_Chain.py"), default_timeout=30)
    for k, v in at_sim.session_state.items():
        at_chain.session_state[k] = v
    at_chain.run()
    assert not at_chain.exception
    assert at_chain.session_state["scn"]["freight_multiplier"] == 1.45


def test_seq_5_demo_start_page_switch_stop_slider():
    """Seq 5: demo start → page switch → stop → manual slider."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()

    # 1. Start demo
    start_demo(at.session_state)
    at.run()
    assert not at.exception
    assert is_demo_running(at.session_state)

    # 2. Switch page while demo active
    at_chain = AppTest.from_file(os.path.join(BASE_DIR, "pages/3_Profit_Chain.py"), default_timeout=30)
    for k, v in at.session_state.items():
        at_chain.session_state[k] = v
    at_chain.run()
    assert not at_chain.exception

    # 3. Stop demo
    stop_demo(at_chain.session_state)
    at_chain.run()
    assert not at_chain.exception
    assert not is_demo_running(at_chain.session_state)

    # 4. Manual slider change
    apply_scenario_values({"freight_multiplier": 2.1}, state=at_chain.session_state)
    at_chain.run()
    assert not at_chain.exception
    assert at_chain.session_state["scn"]["freight_multiplier"] == 2.1


def test_seq_6_demo_start_reset_during_demo():
    """Seq 6: demo start → Reset during demo."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()

    start_demo(at.session_state)
    at.run()
    assert is_demo_running(at.session_state)

    # Click Reset
    btn_reset = next(b for b in at.button if ":material/restart_alt: Reset" in b.label)
    btn_reset.click().run()
    assert not at.exception
    # Demo should be halted and state reset to base
    assert at.session_state["scn"]["freight_multiplier"] == 1.0


def test_seq_7_save_load_during_demo():
    """Seq 7: save → load during demo."""
    state = {}
    init_canonical_state(state)
    presets = get_default_presets()
    state["saved_scenarios"]["CustomSave"] = presets["metal_shock"]

    # Start demo
    start_demo(state)
    assert is_demo_running(state)

    # Load saved scenario
    loaded = state["saved_scenarios"]["CustomSave"]
    apply_scenario_values({
        "name": loaded.name,
        "copper": loaded.price_shock_pct.get("copper", 0.0),
        "freight_multiplier": loaded.freight_multiplier
    }, state=state)
    assert state["scn"]["copper"] == 35.0


def test_seq_8_simple_view_toggle_preset_cycle():
    """Seq 8: Simple view on → preset → off."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()

    if len(at.toggle) > 0:
        tog = at.toggle[0]
        # Turn ON
        tog.set_value(True).run()
        assert not at.exception
        assert at.session_state.get("simple_view") is True

        # Click preset
        chip = next(b for b in at.button if b.label == "Today's market")
        chip.click().run()
        assert not at.exception

        # Turn OFF
        tog.set_value(False).run()
        assert not at.exception
        assert at.session_state.get("simple_view") is False


def test_seq_9_twenty_rapid_alternating_preset_clicks():
    """Seq 9: 20 rapid alternating preset clicks (Red Sea ↔ Metal Shock)."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()
    assert not at.exception

    chip_rs = next(b for b in at.button if b.label == "Red Sea / Hormuz")
    chip_ms = next(b for b in at.button if b.label == "Metal shock")

    for i in range(20):
        if i % 2 == 0:
            chip_rs.click().run()
            assert not at.exception, f"Exception on rapid click {i} (Red Sea)"
        else:
            chip_ms.click().run()
            assert not at.exception, f"Exception on rapid click {i} (Metal Shock)"

    # Final state must equal Metal Shock
    assert at.session_state["scn"]["copper"] == 35.0
    assert not at.exception
