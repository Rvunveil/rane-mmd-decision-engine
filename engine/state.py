"""
Canonical Scenario State Architecture & Control Sync (Section 3 / P0 Fix)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Enforces:
- P0: Single canonical state dictionary st.session_state["scn"] holding every lever.
- P0: apply_scenario_values() NEVER writes widget keys directly; sets _sync_widgets = True.
- P0: sync_widgets_from_scn() runs at the very top of app.py to safely synchronize widgets before creation.
- P0: All scenario modifications use callbacks (on_click/on_change) or rerun-safe patterns.
- Decouples widgets from value= parameter; prevents dual key/value Streamlit warnings.
"""

import os
import yaml
from typing import Any
import streamlit as st
from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_PATH = os.path.join(BASE_DIR, "config", "glossary.yaml")

DEFAULT_SCN_DICT = {
    "name": "Base case",
    "copper": 0.0,
    "nickel": 0.0,
    "aluminium": 0.0,
    "resin": 0.0,
    "rubber": 0.0,
    "steel_hr": 0.0,
    "steel_cr": 0.0,
    "metal_master": 0.0,
    "freight_multiplier": 1.0,
    "shipping_delay_days": 0,
    "fx_inr_usd": 84.56,
    "oem_pass_through_pct": 50.0,
    "demand_volume_pct": 0.0,
    "tariff_pct": 0.0,
    "pass_through_lag_days": 75,
    "in_year_mode": False
}

# Standalone fallback state store for testing outside active Streamlit runtime
_FALLBACK_STATE: dict[str, Any] = {}

# Widget key mapping for top-of-script synchronization
WIDGET_KEY_MAPPING = {
    "deck_metal": lambda scn: float(scn.get("metal_master", 0.0)),
    "deck_freight": lambda scn: float(scn.get("freight_multiplier", 1.0)),
    "deck_delay": lambda scn: int(scn.get("shipping_delay_days", 0)),
    "deck_fx": lambda scn: float(scn.get("fx_inr_usd", 84.56)),
    "deck_pass_through": lambda scn: float(scn.get("oem_pass_through_pct", 50.0)),
    "deck_demand": lambda scn: float(scn.get("demand_volume_pct", 0.0)),
    "sb_freight": lambda scn: float(scn.get("freight_multiplier", 1.0)),
    "sb_delay": lambda scn: int(scn.get("shipping_delay_days", 0)),
    "sb_fx": lambda scn: float(scn.get("fx_inr_usd", 84.56)),
    "sb_pass_through": lambda scn: float(scn.get("oem_pass_through_pct", 50.0)),
    "sb_demand": lambda scn: float(scn.get("demand_volume_pct", 0.0)),
    "fine_copper": lambda scn: float(scn.get("copper", scn.get("metal_master", 0.0))),
    "fine_aluminium": lambda scn: float(scn.get("aluminium", scn.get("metal_master", 0.0))),
    "fine_nickel": lambda scn: float(scn.get("nickel", scn.get("metal_master", 0.0))),
    "fine_steel_hr": lambda scn: float(scn.get("steel_hr", scn.get("metal_master", 0.0))),
    "fine_steel_cr": lambda scn: float(scn.get("steel_cr", scn.get("metal_master", 0.0))),
    "fine_resin": lambda scn: float(scn.get("resin", 0.0)),
    "fine_rubber": lambda scn: float(scn.get("rubber", 0.0)),
}


def _get_state_store():
    """Returns Streamlit session_state if running in app, else fallback dict."""
    try:
        _ = st.session_state
        return st.session_state
    except Exception:
        return _FALLBACK_STATE


def load_glossary() -> dict[str, str]:
    """Loads plain-language definitions from config/glossary.yaml with multi-case keys."""
    lookup = {}
    if os.path.exists(GLOSSARY_PATH):
        try:
            with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
                for k, v in raw.items():
                    lookup[k] = v
                    lookup[k.lower()] = v
                    lookup[k.upper()] = v
                    lookup[k.title()] = v
                    clean_space = k.replace("_", " ")
                    lookup[clean_space] = v
                    lookup[clean_space.lower()] = v
                    lookup[clean_space.title()] = v
                    lookup[clean_space.capitalize()] = v
                lookup["Days of Cover"] = lookup.get("days_of_cover", "")
                lookup["Working Capital Gap"] = lookup.get("working_capital_gap", "")
        except Exception:
            pass
    return lookup


def init_canonical_state(state: dict[str, Any] | None = None):
    """Initializes canonical state structures and sets up initial widget keys."""
    if state is None:
        state = _get_state_store()
    if "scn" not in state:
        state["scn"] = dict(DEFAULT_SCN_DICT)
    if "saved_scenarios" not in state:
        state["saved_scenarios"] = {}
    if "simple_view" not in state:
        state["simple_view"] = False
    if "show_helper_dialog" not in state:
        state["show_helper_dialog"] = False
    if "base_scenario" not in state:
        state["base_scenario"] = get_default_presets()["base_case"]
    if "active_scenario" not in state:
        state["active_scenario"] = get_current_scenario(state)
    if "_sync_widgets" not in state:
        state["_sync_widgets"] = False

    # Initialize each widget key from scn once if missing
    scn = state["scn"]
    for widget_key, getter in WIDGET_KEY_MAPPING.items():
        if widget_key not in state:
            state[widget_key] = getter(scn)


def sync_widgets_from_scn(state: dict[str, Any] | None = None, force: bool = False):
    """
    P0 CORE FIX: Copies canonical scn values into EVERY widget key.
    Must be called at the very top of app.py before any widget is created.
    """
    if state is None:
        state = _get_state_store()

    if "scn" not in state:
        init_canonical_state(state)

    if state.get("_sync_widgets", False) or force:
        scn = state["scn"]
        for widget_key, getter in WIDGET_KEY_MAPPING.items():
            state[widget_key] = getter(scn)
        state["_sync_widgets"] = False


def get_current_scenario(state: dict[str, Any] | None = None) -> Scenario:
    """Builds an immutable Scenario dataclass from canonical state."""
    if state is None:
        state = _get_state_store()
    s = state.get("scn", DEFAULT_SCN_DICT)
    
    master = float(s.get("metal_master", 0.0))
    cu = float(s.get("copper", master))
    ni = float(s.get("nickel", master))
    al = float(s.get("aluminium", master))
    fe_hr = float(s.get("steel_hr", master))
    fe_cr = float(s.get("steel_cr", master))
    res = float(s.get("resin", 0.0))
    rub = float(s.get("rubber", 0.0))

    return Scenario(
        name=s.get("name", "Custom"),
        price_shock_pct={
            "copper": cu,
            "nickel": ni,
            "aluminium": al,
            "resin": res,
            "rubber": rub,
            "steel_hr": fe_hr,
            "steel_cr": fe_cr
        },
        freight_multiplier=float(s.get("freight_multiplier", 1.0)),
        fx_inr_usd=float(s.get("fx_inr_usd", 84.56)),
        tariff_pct=float(s.get("tariff_pct", 0.0)),
        demand_volume_pct=float(s.get("demand_volume_pct", 0.0)),
        shipping_delay_days=int(s.get("shipping_delay_days", 0)),
        oem_pass_through_pct=float(s.get("oem_pass_through_pct", 50.0)),
        pass_through_lag_days=int(s.get("pass_through_lag_days", 75)),
        in_year_mode=bool(s.get("in_year_mode", False))
    )


def apply_scenario_values(values: dict[str, Any] | None = None, maybe_values: dict[str, Any] | None = None, source: str = "manual", state: dict[str, Any] | None = None):
    """
    P0 FIX: Updates canonical scn dictionary and sets _sync_widgets = True.
    NEVER writes widget keys directly to avoid StreamlitWidgetAlreadyInstantiatedError.
    """
    if maybe_values is not None:
        target_state = values
        vals = maybe_values
    else:
        target_state = state if state is not None else _get_state_store()
        vals = values or {}

    if "scn" not in target_state:
        target_state["scn"] = dict(DEFAULT_SCN_DICT)

    for k, v in vals.items():
        target_state["scn"][k] = v

    if not source.startswith("preset:") and "name" not in vals:
        target_state["scn"]["name"] = "Custom"

    # Set flag for top-of-script sync. Do NOT modify widget keys directly here.
    target_state["_sync_widgets"] = True
    target_state["active_scenario"] = get_current_scenario(target_state)

    # When testing offline with a plain dictionary (not active st.session_state),
    # immediately synchronize via sync_widgets_from_scn so mock-state unit tests see updated keys.
    try:
        is_st_session = (target_state is getattr(st, "session_state", None))
    except Exception:
        is_st_session = False

    if not is_st_session:
        sync_widgets_from_scn(target_state)


def apply_preset_by_name(preset_key_or_state: Any, preset_key_or_none: Any = None, state: dict[str, Any] | None = None):
    """
    Loads and activates a calibrated preset.
    Safe to use directly as a button callback: on_click=apply_preset_by_name, args=(preset_key,).
    """
    if isinstance(preset_key_or_state, str):
        preset_key = preset_key_or_state
        target_state = state if state is not None else _get_state_store()
    else:
        target_state = preset_key_or_state
        preset_key = preset_key_or_none or "base_case"

    if preset_key == "todays_market":
        scn = compute_todays_market_scenario()
    else:
        presets = get_default_presets()
        scn = presets.get(preset_key, presets["base_case"])

    new_vals = {
        "name": scn.name,
        "copper": scn.price_shock_pct.get("copper", 0.0),
        "nickel": scn.price_shock_pct.get("nickel", 0.0),
        "aluminium": scn.price_shock_pct.get("aluminium", 0.0),
        "resin": scn.price_shock_pct.get("resin", 0.0),
        "rubber": scn.price_shock_pct.get("rubber", 0.0),
        "steel_hr": scn.price_shock_pct.get("steel_hr", 0.0),
        "steel_cr": scn.price_shock_pct.get("steel_cr", 0.0),
        "metal_master": scn.price_shock_pct.get("copper", 0.0),
        "freight_multiplier": scn.freight_multiplier,
        "shipping_delay_days": scn.shipping_delay_days,
        "fx_inr_usd": scn.fx_inr_usd,
        "tariff_pct": scn.tariff_pct,
        "demand_volume_pct": scn.demand_volume_pct,
        "oem_pass_through_pct": scn.oem_pass_through_pct,
        "pass_through_lag_days": scn.pass_through_lag_days,
        "in_year_mode": scn.in_year_mode
    }
    apply_scenario_values(values=new_vals, source=f"preset:{preset_key}", state=target_state)


def reset_to_base(state: dict[str, Any] | None = None):
    """Restores canonical state to the calibrated base case. Safe as on_click callback."""
    apply_preset_by_name("base_case", state=state)
