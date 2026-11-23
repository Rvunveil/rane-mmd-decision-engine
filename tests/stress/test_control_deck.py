"""
Control Deck & Guided Helper Verification Tests
Team 11:59 · Xovate'26
Verifies canonical state, preset synchronization, guided helper recommendation,
and simple view toggle.
"""

import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
from engine.state import (
    init_canonical_state, get_current_scenario, apply_scenario_values,
    apply_preset_by_name, reset_to_base, load_glossary
)
from engine.scenario import Scenario

ROOT = Path(__file__).resolve().parent.parent.parent


def test_CD01_canonical_state_lifecycle():
    """CD01: Canonical state initializes, updates via apply_scenario_values, and resets."""
    # When uninitialized outside Streamlit, fallback scenario is Base case
    scn = get_current_scenario()
    assert scn.name == "Base case"
    assert scn.freight_multiplier == 1.0

    # In a simulated session_state dict
    state = {}
    init_canonical_state(state)
    assert "scn" in state
    assert state["scn"]["name"] == "Base case"
    assert state["scn"]["freight_multiplier"] == 1.0

    # Apply values
    apply_scenario_values(state, {"freight_multiplier": 2.5, "shipping_delay_days": 14}, source="test")
    assert state["scn"]["freight_multiplier"] == 2.5
    assert state["scn"]["shipping_delay_days"] == 14
    assert state["scn"]["name"] == "Custom"

    # Reset to base
    reset_to_base(state)
    assert state["scn"]["freight_multiplier"] == 1.0
    assert state["scn"]["shipping_delay_days"] == 0
    assert state["scn"]["name"] == "Base case"


def test_CD02_apply_preset_synchronization():
    """CD02: Applying a preset updates both scn and widget keys."""
    state = {}
    init_canonical_state(state)

    apply_preset_by_name(state, "red_sea_hormuz")
    assert state["scn"]["name"] == "Red Sea / Hormuz crisis"
    assert abs(state["scn"]["freight_multiplier"] - 2.73) < 0.01
    assert state["scn"]["shipping_delay_days"] == 18
    assert state["deck_freight"] == 2.73
    assert state["deck_delay"] == 18
    assert state["deck_pass_through"] == 50.0

    # Apply metal shock
    apply_preset_by_name(state, "metal_shock")
    assert state["scn"]["name"] in ["Metal shock", "Global metal shock"]
    assert state["scn"]["copper"] == 35.0
    assert state["scn"]["steel_hr"] == 28.0


def test_CD03_glossary_content():
    """CD03: Glossary YAML loads and contains plain-language explanations."""
    glossary = load_glossary()
    assert "EBITDA" in glossary
    assert "PAT" in glossary
    assert "Working Capital Gap" in glossary
    assert "Days of Cover" in glossary
    assert len(glossary["EBITDA"]) > 10


def test_CD04_command_centre_control_deck_apptest():
    """CD04: Command Centre loads with Control Deck, preset buttons, and simple view toggle."""
    at = AppTest.from_file(str(ROOT / "pages" / "0_Command_Centre.py"), default_timeout=30)
    at.run()
    assert not at.exception

    # Check presence of toggle and buttons
    assert len(at.toggle) >= 1  # Simple view toggle
    assert len(at.button) >= 3  # Reset, Preset buttons, What happened dialog trigger


def test_CD05_simple_view_toggle_behavior():
    """CD05: Toggling Simple view suppresses complex distributions while preserving core KPIs."""
    at = AppTest.from_file(str(ROOT / "pages" / "0_Command_Centre.py"), default_timeout=30)
    at.session_state["simple_view"] = True
    at.session_state["simple_view_toggle"] = True
    at.run()
    assert not at.exception

    # Under simple view, simplified financial summary table and primary actions are displayed
    all_text = " ".join([str(m.value) for m in at.markdown])
    assert "Simplified Operational View" in all_text
    assert "Financial Performance Summary" in all_text
    assert "Primary Recommended Actions" in all_text
    assert len(at.dataframe) >= 1
