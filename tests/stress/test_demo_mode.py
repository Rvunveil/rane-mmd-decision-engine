"""
Demo Mode Unit and Integration Tests (Section 4)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine
"""

import os
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from demo.player import (
    load_demo_config, load_storyboard, start_demo, stop_demo, _apply_step
)
from engine.state import init_canonical_state, get_current_scenario

ROOT = Path(__file__).resolve().parent.parent.parent
TIMELINE_PATH = ROOT / "demo_out" / "demo_timeline.json"


def test_DM01_storyboard_structure():
    """DM01: Storyboard loads all 12 planned steps with required schema."""
    steps = load_storyboard()
    assert len(steps) == 12, f"Expected 12 steps, found {len(steps)}"
    for idx, s in enumerate(steps, 1):
        assert s["id"] == idx
        assert "title" in s
        assert "caption" in s
        assert "page" in s
        assert len(s["caption"]) > 15


def test_DM02_feature_flag_and_env_override(monkeypatch):
    """DM02: MMD_DEMO=0 environment variable completely disables demo mode."""
    cfg = load_demo_config()
    assert cfg.get("enabled") is True

    monkeypatch.setenv("MMD_DEMO", "0")
    cfg_disabled = load_demo_config()
    assert cfg_disabled.get("enabled") is False


def test_DM03_step_execution_and_timeline_logging():
    """DM03: Executing steps updates scenario state and records valid timeline JSON."""
    state = {}
    init_canonical_state(state)

    # Step 1: Base case
    _apply_step(1)
    scn = get_current_scenario()
    assert scn.name == "Base case"
    assert scn.shipping_delay_days == 0

    # Step 3: Red Sea / Hormuz shock
    _apply_step(3)
    scn_shock = get_current_scenario()
    assert scn_shock.name == "Red Sea / Hormuz crisis"
    assert scn_shock.shipping_delay_days == 18
    assert abs(scn_shock.freight_multiplier - 2.73) < 0.01

    # Verify timeline file written
    assert TIMELINE_PATH.exists()
    with open(TIMELINE_PATH, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    assert len(timeline) >= 2
    last_entry = timeline[-1]
    assert last_entry["step"] == 3
    assert last_entry["shipping_delay_days"] == 18
    assert "ebitda_cr" in last_entry
    assert last_entry["ebitda_cr"] < 297.7  # Shock should lower EBITDA


def test_DM04_app_loads_with_demo_hook():
    """DM04: Main app entrypoint loads smoothly with demo hook imported."""
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception
