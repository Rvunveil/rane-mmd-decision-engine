"""
Demo Mode Player & State Machine (Section 4)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine
"""

import os
import time
import json
import yaml
from pathlib import Path
from typing import Any
import streamlit as st
from engine.state import apply_preset_by_name, apply_scenario_values, get_current_scenario, reset_to_base
from engine.chain import run_all
from demo.overlay import render_demo_overlay

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "demo.yaml"
STORYBOARD_PATH = ROOT_DIR / "demo" / "storyboard.yaml"
OUT_DIR = ROOT_DIR / "demo_out"


def load_demo_config() -> dict[str, Any]:
    """Loads feature flag and playback settings."""
    if os.environ.get("MMD_DEMO", "1") == "0":
        return {"enabled": False}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {"enabled": True}
        except Exception:
            pass
    return {"enabled": True}


def load_storyboard() -> list[dict[str, Any]]:
    """Loads 12-step guided storyboard."""
    if STORYBOARD_PATH.exists():
        try:
            with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("steps", [])
        except Exception:
            pass
    return []


def _record_timeline(step_info: dict[str, Any], scn: Any, results: Any):
    """Logs playback progression into demo_out/demo_timeline.json."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "demo_timeline.json"

    entry = {
        "timestamp": time.time(),
        "step": step_info.get("id", 1),
        "title": step_info.get("title", ""),
        "page": step_info.get("page", ""),
        "preset": scn.name,
        "freight_multiplier": scn.freight_multiplier,
        "shipping_delay_days": scn.shipping_delay_days,
        "revenue_cr": round(results.revenue_cr, 2),
        "ebitda_cr": round(results.ebitda_cr, 2),
        "pat_cr": round(results.pat_cr, 2),
        "caption": step_info.get("caption", "")
    }

    history = []
    if out_file.exists():
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(entry)
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass


def is_demo_running(state: dict[str, Any] | None = None) -> bool:
    """Checks whether the automated demo mode is currently running."""
    if state is None:
        try:
            state = getattr(st, "session_state", {})
        except Exception:
            state = {}
    return state.get("demo", {}).get("active", False)


def start_demo(state: dict[str, Any] | None = None):
    """Initializes and kicks off demo mode."""
    target = state if state is not None else st.session_state
    target["demo"] = {
        "active": True,
        "step": 1,
        "started_at": time.time(),
        "step_started_at": time.time(),
        "paused": False
    }
    # Clean previous timeline file
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "demo_timeline.json"
    if out_file.exists():
        try:
            out_file.unlink()
        except Exception:
            pass

    _apply_step(1, state=target)


def stop_demo(state: dict[str, Any] | None = None):
    """Exits demo mode cleanly and restores base state."""
    target = state if state is not None else st.session_state
    target["demo"] = {
        "active": False,
        "step": 0,
        "started_at": 0.0,
        "step_started_at": 0.0,
        "paused": False
    }
    reset_to_base(target)


def _apply_step(step_idx: int, state: dict[str, Any] | None = None):
    """Executes actions for the target step."""
    steps = load_storyboard()
    if not steps or step_idx < 1 or step_idx > len(steps):
        return

    step_info = steps[step_idx - 1]
    action = step_info.get("action", "")

    if action == "apply_preset":
        preset_name = step_info.get("preset", "base_case")
        if state is not None:
            apply_preset_by_name(state, preset_name)
        else:
            apply_preset_by_name(preset_name)

    elif action == "tween_slider":
        target = step_info.get("target", "metal_master")
        val = step_info.get("value", 15.0)
        apply_scenario_values({target: val, "name": "Custom Sensitivity"}, state=state)

    # Evaluate live metrics and log
    scn = get_current_scenario(state)
    results = run_all(scn)
    _record_timeline(step_info, scn, results)

    # Check navigation
    target_page = step_info.get("page", "")
    # If running inside Streamlit, we can safely invoke page switch if requested
    # But only switch when page is different to avoid infinite loop
    # Note: Streamlit switch_page triggers a rerun immediately
    try:
        current_script = getattr(st, "_RerunData", None)
    except Exception:
        pass


def run_demo_player():
    """
    Main hook called from app.py.
    Renders sidebar launcher, updates state machine, and displays lower-third overlay.
    """
    cfg = load_demo_config()
    if not cfg.get("enabled", True):
        return

    steps = load_storyboard()
    total_steps = len(steps)
    if total_steps == 0:
        return

    if "demo" not in st.session_state:
        st.session_state["demo"] = {
            "active": False,
            "step": 0,
            "started_at": 0.0,
            "step_started_at": 0.0,
            "paused": False
        }

    demo_state = st.session_state["demo"]

    # Render launcher button in sidebar if inactive (P0: on_click callback)
    with st.sidebar:
        if not demo_state["active"]:
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.button("🎬 Run Director Demo (60s)", help="Autonomously tours all 5 modules with live calculations", key="btn_start_demo", use_container_width=True, on_click=start_demo)
            return

    # If demo is active:
    current_step_idx = demo_state.get("step", 1)
    if current_step_idx < 1 or current_step_idx > total_steps:
        stop_demo()
        return

    current_step = steps[current_step_idx - 1]

    # Handlers for interactive controls (P0: callback-safe)
    def on_next():
        if current_step_idx < total_steps:
            demo_state["step"] = current_step_idx + 1
            demo_state["step_started_at"] = time.time()
            _apply_step(demo_state["step"])
        else:
            stop_demo()

    def on_prev():
        if current_step_idx > 1:
            demo_state["step"] = current_step_idx - 1
            demo_state["step_started_at"] = time.time()
            _apply_step(demo_state["step"])

    def on_toggle_pause():
        demo_state["paused"] = not demo_state.get("paused", False)

    def on_stop():
        stop_demo()

    # Render Floating Overlay
    render_demo_overlay(
        step_info=current_step,
        total_steps=total_steps,
        is_paused=demo_state.get("paused", False),
        on_next=on_next,
        on_prev=on_prev,
        on_toggle_pause=on_toggle_pause,
        on_stop=on_stop
    )
