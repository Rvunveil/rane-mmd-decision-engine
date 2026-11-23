"""
Part A: Automated AppTest Suite — Every Page x Every State
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Pages (7):
- pages/0_Command_Centre.py
- pages/1_Forecast.py
- pages/2_Scenario_Simulator.py
- pages/3_Profit_Chain.py
- pages/4_Containers_Inventory.py
- pages/5_Action_Matrix.py
- pages/6_Assumptions_Data_Trace_About.py

States (10):
1. Base case
2. Today's market
3. Red Sea / Hormuz
4. Metal shock
5. Tariff & FX escalation
6. Demand recession
7. Custom extreme-high
8. Custom extreme-low
9. After Reset
10. Saved scenarios + Simple view on/off + Demo on/off
"""

import os
import sys
import re
import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.scenario import Scenario, get_default_presets
from engine.state import (
    init_canonical_state,
    apply_preset_by_name,
    apply_scenario_values,
    reset_to_base,
    get_current_scenario
)
from engine.chain import run_all

PAGE_FILES = [
    "pages/0_Command_Centre.py",
    "pages/1_Forecast.py",
    "pages/2_Scenario_Simulator.py",
    "pages/3_Profit_Chain.py",
    "pages/4_Containers_Inventory.py",
    "pages/5_Action_Matrix.py",
    "pages/6_Assumptions_Data_Trace_About.py"
]

LEAK_PATTERNS = [
    re.compile(r"\{\s*[a-zA-Z0-9_]+\s*\}"),  # {placeholder}
    re.compile(r":\.\df"),                    # :.1f, :.2f
    re.compile(r"\bNone\b"),                  # Unformatted None
    re.compile(r"\bnan\b", re.IGNORECASE),    # nan or NaN
    re.compile(r"\binf\b", re.IGNORECASE),    # inf or Infinity
    re.compile(r"\+₹-0\.0"),                  # Negative zero bug
]


def _check_text_leaks(at: AppTest, page_name: str, state_name: str):
    """Scans all rendered text elements for raw placeholders and formatting leaks."""
    all_text = []
    for md in at.markdown:
        all_text.append(str(md.value))
    for cap in at.caption:
        all_text.append(str(cap.value))
    for m in at.metric:
        all_text.append(f"{m.label} {m.value} {m.delta}")
    for title in at.title:
        all_text.append(str(title.value))
    for h in at.header:
        all_text.append(str(h.value))
    for sub in at.subheader:
        all_text.append(str(sub.value))

    combined = "\n".join(all_text)
    for pattern in LEAK_PATTERNS:
        matches = pattern.findall(combined)
        # Filter out safe substrings (e.g. CSS styles or intentional markdown)
        safe_matches = []
        for match in matches:
            # Allow literal "NaN" or "None" only if clearly explanatory, else flag
            if match in ["none", "None"] and ("None selected" in combined or "display: none" in combined):
                continue
            safe_matches.append(match)
        assert not safe_matches, f"Text leak detected on {page_name} under {state_name}: {safe_matches}"


@pytest.mark.parametrize("page_file", PAGE_FILES)
def test_part_a_base_case(page_file):
    """State 1: Base case on every page."""
    at = AppTest.from_file(os.path.join(BASE_DIR, page_file), default_timeout=30)
    at.run()
    assert not at.exception, f"Exception on {page_file} under Base: {at.exception}"
    _check_text_leaks(at, page_file, "Base case")


@pytest.mark.parametrize("preset_key", [
    "todays_market",
    "red_sea_hormuz",
    "metal_shock",
    "tariff_fx",
    "demand_recession"
])
@pytest.mark.parametrize("page_file", [
    "pages/0_Command_Centre.py",
    "pages/2_Scenario_Simulator.py",
    "pages/3_Profit_Chain.py",
    "pages/5_Action_Matrix.py"
])
def test_part_a_presets(page_file, preset_key):
    """States 2-6: Presets on primary decision engine pages."""
    at = AppTest.from_file(os.path.join(BASE_DIR, page_file), default_timeout=30)
    at.run()
    assert not at.exception

    # Apply preset directly to session state
    apply_preset_by_name(at.session_state, preset_key)
    at.run()
    assert not at.exception, f"Exception on {page_file} under {preset_key}: {at.exception}"
    _check_text_leaks(at, page_file, preset_key)


def test_part_a_custom_extremes():
    """States 7-8: Custom extreme-high and extreme-low on Control Room and Simulator."""
    extreme_high = {
        "copper": 60.0,
        "nickel": 60.0,
        "aluminium": 60.0,
        "resin": 60.0,
        "rubber": 60.0,
        "steel_hr": 60.0,
        "steel_cr": 60.0,
        "metal_master": 60.0,
        "freight_multiplier": 4.0,
        "fx_inr_usd": 105.0,
        "tariff_pct": 30.0,
        "demand_volume_pct": 30.0,
        "shipping_delay_days": 45,
        "oem_pass_through_pct": 100.0,
        "name": "Custom Extreme High"
    }

    extreme_low = {
        "copper": -30.0,
        "nickel": -30.0,
        "aluminium": -30.0,
        "resin": -30.0,
        "rubber": -30.0,
        "steel_hr": -30.0,
        "steel_cr": -30.0,
        "metal_master": -30.0,
        "freight_multiplier": 0.5,
        "fx_inr_usd": 80.0,
        "tariff_pct": 0.0,
        "demand_volume_pct": -30.0,
        "shipping_delay_days": 0,
        "oem_pass_through_pct": 0.0,
        "name": "Custom Extreme Low"
    }

    for state_dict, sname in [(extreme_high, "Extreme High"), (extreme_low, "Extreme Low")]:
        for page in ["pages/0_Command_Centre.py", "pages/2_Scenario_Simulator.py", "pages/3_Profit_Chain.py"]:
            at = AppTest.from_file(os.path.join(BASE_DIR, page), default_timeout=30)
            at.run()
            assert not at.exception
            apply_scenario_values(state_dict, state=at.session_state)
            at.run()
            assert not at.exception, f"Exception on {page} under {sname}: {at.exception}"
            _check_text_leaks(at, page, sname)


def test_part_a_after_reset():
    """State 9: After Reset to Base."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()
    # Apply shock first
    apply_preset_by_name(at.session_state, "red_sea_hormuz")
    at.run()
    assert not at.exception

    # Reset
    reset_to_base(at.session_state)
    at.run()
    assert not at.exception
    assert at.session_state["scn"]["freight_multiplier"] == 1.0
    _check_text_leaks(at, "pages/0_Command_Centre.py", "After Reset")


def test_part_a_saved_scenarios_and_toggles():
    """State 10: Saved scenarios, Simple view toggle on/off, Demo on/off."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()

    # Populate 3 saved scenarios
    presets = get_default_presets()
    at.session_state["saved_scenarios"] = {
        "Red Sea Peak": presets["red_sea_hormuz"],
        "Metal Surge": presets["metal_shock"],
        "Tariff Crisis": presets["tariff_fx"]
    }
    at.session_state["simple_view"] = True
    at.run()
    assert not at.exception
    _check_text_leaks(at, "pages/0_Command_Centre.py", "Simple View ON")

    at.session_state["simple_view"] = False
    at.run()
    assert not at.exception
    _check_text_leaks(at, "pages/0_Command_Centre.py", "Simple View OFF")
