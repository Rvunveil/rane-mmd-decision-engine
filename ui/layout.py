"""
Shared Layout, Sidebar and Session State Management (Section 3)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Enforces:
- 3a: Canonical state via engine.state
- 3b: Decouples widgets from value= parameter; prevents dual key/value Streamlit warnings
- 3c: Preset changes through apply_scenario_values()
- 3d: Clean compact summary on Control Room; interactive sliders on other module pages
"""

import os
import streamlit as st
import yaml
from ui.theme import COLOR_BRAND_PRIMARY
from engine.state import (
    init_canonical_state,
    get_current_scenario,
    apply_scenario_values,
    apply_preset_by_name,
    reset_to_base
)

def load_yaml(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def page_setup(title: str = "MMD Decision Engine · Team 11:59"):
    """Inject styling, initialize canonical state, and configure page."""
    st.set_page_config(
        page_title=title,
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject global stylesheet
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    init_canonical_state()


def render_sidebar(is_control_room: bool = False):
    """
    Renders standardized interactive sidebar.
    Rule 3d: On Control Room, shows a compact read-only summary card plus presets.
    On module pages, renders full interactive sliders synchronized with canonical state.
    """
    init_canonical_state()
    branding = load_yaml("config/branding.yaml")
    scn = st.session_state["scn"]
    active = get_current_scenario()

    with st.sidebar:
        # 1. Branding Header
        st.markdown(
            f"""
            <div style="padding-bottom: 0.75rem; border-bottom: 1px solid #C9D1D5; margin-bottom: 0.75rem;">
                <div style="font-size: 0.7rem; font-weight: 700; color: #2F5D7C; letter-spacing: 0.08em; text-transform: uppercase;">
                    {branding.get('event', 'Xovate 26 Hackathon')}
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #1D262C; line-height: 1.2;">
                    {branding.get('short_name', 'MMD Decision Engine')}
                </div>
                <div style="font-size: 0.75rem; color: #536471; font-style: italic;">
                    "{branding.get('tagline', 'See the shock. Measure it. Decide.')}"
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. Preset Selector
        preset_map = {
            "Base case": "base_case",
            "Today's market (Live Data)": "todays_market",
            "Red Sea / Hormuz crisis": "red_sea_hormuz",
            "Metal shock": "metal_shock",
            "Tariff & FX escalation": "tariff_fx",
            "Demand recession": "demand_recession"
        }
        preset_options = list(preset_map.keys())

        current_name = scn.get("name", "Base case")
        idx = 0
        for i, opt in enumerate(preset_options):
            if opt.lower().startswith(current_name.lower()[:8]):
                idx = i
                break

        selected_preset = st.selectbox(
            ":material/bolt: Quick Shock Scenario Preset",
            options=preset_options,
            index=idx,
            key="sb_preset_select",
            help="Select a calibrated crisis preset or fine-tune individual shock sliders."
        )

        selected_key = preset_map[selected_preset]
        if selected_key != "base_case" and current_name == "Base case" and selected_preset != "Base case":
            apply_preset_by_name(selected_key)
            st.rerun()

        # 3. Rule 3d: Sidebar mode
        if is_control_room:
            # Compact read-only summary on Control Room
            st.markdown(
                f"""
                <div style="background: #F8F9F9; border: 1px solid #C9D1D5; padding: 10px; border-radius: 4px; font-size: 0.8rem; margin: 10px 0;">
                    <div style="font-weight: 700; color: #1D262C; margin-bottom: 6px;">Active Scenario: <span style="color:#2F5D7C;">{active.name}</span></div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-variant-numeric: tabular-nums; color: #536471; font-size: 0.75rem;">
                        <div>Metals: <b>{scn.get('metal_master', 0.0):+.0f}%</b></div>
                        <div>Freight: <b>{scn.get('freight_multiplier', 1.0):.2f}x</b></div>
                        <div>Delay: <b>+{scn.get('shipping_delay_days', 0)}d</b></div>
                        <div>USD/INR: <b>₹{scn.get('fx_inr_usd', 84.56):.2f}</b></div>
                        <div>Pass-Thru: <b>{scn.get('oem_pass_through_pct', 50.0):.0f}%</b></div>
                        <div>Demand: <b>{scn.get('demand_volume_pct', 0.0):+.0f}%</b></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption("ℹ️ Full scenario sliders are accessible directly on the Control Deck above, or deep-dive in **Module 2 (Scenario Simulator)**.")
        else:
            # Interactive Sliders for Module Pages (Rule 3b: no value= with key=)
            st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#536471; margin:0.75rem 0 0.25rem 0;'>FINE-TUNE SHOCK PARAMETERS</div>", unsafe_allow_html=True)

            # Pre-populate sidebar slider keys if missing
            if "sb_freight" not in st.session_state:
                st.session_state["sb_freight"] = float(scn.get("freight_multiplier", 1.0))
                st.session_state["sb_delay"] = int(scn.get("shipping_delay_days", 0))
                st.session_state["sb_fx"] = float(scn.get("fx_inr_usd", 84.56))
                st.session_state["sb_pass_through"] = float(scn.get("oem_pass_through_pct", 50.0))
                st.session_state["sb_demand"] = float(scn.get("demand_volume_pct", 0.0))

            def _on_sb_slider_change():
                apply_scenario_values({
                    "freight_multiplier": st.session_state.get("sb_freight", 1.0),
                    "shipping_delay_days": st.session_state.get("sb_delay", 0),
                    "fx_inr_usd": st.session_state.get("sb_fx", 84.56),
                    "oem_pass_through_pct": st.session_state.get("sb_pass_through", 50.0),
                    "demand_volume_pct": st.session_state.get("sb_demand", 0.0),
                    "name": "Custom"
                })

            with st.expander(":material/local_shipping: Freight & Maritime Logistics", expanded=False):
                st.slider("Container Freight (x)", 0.5, 4.0, step=0.05, key="sb_freight", on_change=_on_sb_slider_change)
                st.slider("Shipping Delay (Days)", 0, 45, step=1, key="sb_delay", on_change=_on_sb_slider_change)

            with st.expander(":material/currency_exchange: Forex & Currency", expanded=False):
                st.slider("USD/INR Exchange Rate", 80.0, 105.0, step=0.25, key="sb_fx", on_change=_on_sb_slider_change)

            with st.expander(":material/handshake: Commercial Pass-Through & Volume", expanded=False):
                st.slider("OEM Cost Pass-Through (%)", 0.0, 100.0, step=5.0, key="sb_pass_through", on_change=_on_sb_slider_change)
                st.slider("Vehicle Demand Volume Δ (%)", -30.0, 30.0, step=1.0, key="sb_demand", on_change=_on_sb_slider_change)

        # 4. Quick Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(":material/restart_alt: Reset Base", use_container_width=True):
                reset_to_base()
                st.rerun()
        with col_btn2:
            if st.button(":material/bookmark: Save", use_container_width=True):
                st.session_state.setdefault("saved_scenarios", {})[active.name] = active
                st.toast(f"Saved scenario '{active.name}'")

        # 5. Team Footer
        st.markdown(
            f"""
            <div style="margin-top: 1.5rem; padding-top: 0.75rem; border-top: 1px solid #C9D1D5; font-size: 0.75rem; color: #536471;">
                <b>{branding.get('team_name', 'Team 11:59')}</b><br>
                Vikram T · Sayoni Dan · Trisha Pal<br>
                <i>{branding.get('institute', 'XIME Chennai')}</i>
            </div>
            """,
            unsafe_allow_html=True
        )

    return get_current_scenario()
