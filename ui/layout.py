"""
Shared Layout, Sidebar and Session State Management for Rane MMD Decision Engine
Team 11.59 · Xovate'26
"""

import os
import streamlit as st
import yaml
from ui.theme import COLOR_BRAND_PRIMARY

def load_yaml(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def page_setup(title: str = "MMD Decision Engine · Team 11.59"):
    """Inject styling, initialize state, and configure page."""
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

    # Initialize session state for scenario
    from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario
    
    if "base_scenario" not in st.session_state:
        presets = get_default_presets()
        st.session_state.base_scenario = presets["base_case"]
        st.session_state.active_scenario = presets["base_case"]
        st.session_state.saved_scenarios = []
        st.session_state.active_preset_name = "Base case"
        st.session_state.todays_market_scenario = None


def render_sidebar():
    """
    Renders standardized interactive sidebar with grouped sliders.
    Returns: active Scenario object
    """
    from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario

    branding = load_yaml("config/branding.yaml")
    presets = get_default_presets()

    with st.sidebar:
        # 1. Branding Header
        st.markdown(
            f"""
            <div style="padding-bottom: 0.75rem; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem;">
                <div style="font-size: 0.7rem; font-weight: 700; color: #0284C7; letter-spacing: 0.08em; text-transform: uppercase;">
                    {branding.get('event', 'Xovate 26 Hackathon')}
                </div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; line-height: 1.2;">
                    {branding.get('short_name', 'MMD Decision Engine')}
                </div>
                <div style="font-size: 0.75rem; color: #64748B; font-style: italic;">
                    "{branding.get('tagline', 'See the shock. Measure it. Decide.')}"
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. Preset Selector
        preset_options = [
            "Base case",
            "Today's market (Live Data)",
            "Red Sea / Hormuz crisis",
            "Metal shock",
            "Tariff & FX escalation",
            "Demand recession"
        ]

        # Check if active preset matches
        current_name = st.session_state.get("active_preset_name", "Base case")
        idx = preset_options.index(current_name) if current_name in preset_options else 0

        selected_preset = st.selectbox(
            "⚡ Quick Shock Scenario Preset",
            options=preset_options,
            index=idx,
            help="Select a calibrated crisis preset or fine-tune individual shock sliders below."
        )

        if selected_preset != st.session_state.get("active_preset_name"):
            st.session_state.active_preset_name = selected_preset
            if selected_preset == "Base case":
                st.session_state.active_scenario = presets["base_case"]
            elif selected_preset == "Red Sea / Hormuz crisis":
                st.session_state.active_scenario = presets["red_sea_hormuz"]
            elif selected_preset == "Metal shock":
                st.session_state.active_scenario = presets["metal_shock"]
            elif selected_preset == "Tariff & FX escalation":
                st.session_state.active_scenario = presets["tariff_fx"]
            elif selected_preset == "Demand recession":
                st.session_state.active_scenario = presets["demand_recession"]
            elif selected_preset == "Today's market (Live Data)":
                if st.session_state.todays_market_scenario is None:
                    st.session_state.todays_market_scenario = compute_todays_market_scenario()
                st.session_state.active_scenario = st.session_state.todays_market_scenario
            st.rerun()

        active = st.session_state.active_scenario

        # 3. Interactive Shock Sliders (Grouped in Expanders)
        st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#475569; margin:0.75rem 0 0.25rem 0;'>FINE-TUNE SHOCK PARAMETERS</div>", unsafe_allow_html=True)

        # Group A: Material Price Shocks (%)
        with st.expander("📦 Material Prices (% Shock)", expanded=(selected_preset != "Base case")):
            cu_shock = st.slider("Copper Cathode (%)", -30.0, 100.0, float(active.price_shock_pct.get("copper", 0.0)), 1.0, key="sl_cu")
            ni_shock = st.slider("Nickel Metal (%)", -30.0, 100.0, float(active.price_shock_pct.get("nickel", 0.0)), 1.0, key="sl_ni")
            al_shock = st.slider("Aluminium LME (%)", -30.0, 100.0, float(active.price_shock_pct.get("aluminium", 0.0)), 1.0, key="sl_al")
            resin_shock = st.slider("Phenolic Resin (%)", -30.0, 100.0, float(active.price_shock_pct.get("resin", 0.0)), 1.0, key="sl_res")
            rub_shock = st.slider("Natural Rubber (%)", -30.0, 100.0, float(active.price_shock_pct.get("rubber", 0.0)), 1.0, key="sl_rub")
            hr_shock = st.slider("Steel HR Coil (%)", -30.0, 100.0, float(active.price_shock_pct.get("steel_hr", 0.0)), 1.0, key="sl_hr")
            cr_shock = st.slider("Steel CR Coil (%)", -30.0, 100.0, float(active.price_shock_pct.get("steel_cr", 0.0)), 1.0, key="sl_cr")

        # Group B: Freight & Shipping
        with st.expander("🚢 Freight & Maritime Logistics", expanded=False):
            freight_mult = st.slider(
                "40ft Container Freight Mult (x)",
                0.5, 4.0, float(active.freight_multiplier), 0.05,
                help="1.0x = $2,172 baseline; 2.73x = Jul 2024 Red Sea peak ($5,937)"
            )
            ship_delay = st.slider(
                "Shipping Delay (Days)",
                0, 45, int(active.shipping_delay_days), 1,
                help="Cape of Good Hope rerouting adds 14-21 days vs Suez Canal"
            )

        # Group C: Currency & Tariffs
        with st.expander("💱 Forex & Import Tariffs", expanded=False):
            fx_val = st.slider(
                "USD/INR Exchange Rate",
                80.0, 105.0, float(active.fx_inr_usd), 0.25,
                help="FY25 average = 84.56; Latest 2026 = ~94.6"
            )
            tariff_val = st.slider(
                "Customs Tariff / Surcharge (%)",
                0.0, 25.0, float(active.tariff_pct), 0.5,
                help="Additional import duty imposed on raw metals & resins"
            )

        # Group D: Commercial & Demand
        with st.expander("🤝 Commercial & Volume", expanded=False):
            pass_through = st.slider(
                "OEM Cost Pass-Through (%)",
                0.0, 100.0, float(active.oem_pass_through_pct), 5.0,
                help="Default 50% per handout; index contract raises to 75-100%"
            )
            lag_days = st.slider(
                "Pass-Through Recovery Lag (Days)",
                0, 120, int(active.pass_through_lag_days), 5,
                help="Handout specifies 60 to 90 days lag for OEM price adjustments"
            )
            demand_vol = st.slider(
                "Vehicle Demand Volume Δ (%)",
                -30.0, 30.0, float(active.demand_volume_pct), 1.0,
                help="ACMA FY20 slowdown benchmark = -11.7%"
            )

        # Build active scenario from current slider values
        new_scenario = Scenario(
            name="Custom Active Scenario" if selected_preset == "Base case" and (
                cu_shock != 0 or freight_mult != 1.0 or ship_delay != 0
            ) else selected_preset,
            price_shock_pct={
                "copper": cu_shock,
                "nickel": ni_shock,
                "aluminium": al_shock,
                "resin": resin_shock,
                "rubber": rub_shock,
                "steel_hr": hr_shock,
                "steel_cr": cr_shock
            },
            freight_multiplier=freight_mult,
            fx_inr_usd=fx_val,
            tariff_pct=tariff_val,
            demand_volume_pct=demand_vol,
            shipping_delay_days=ship_delay,
            oem_pass_through_pct=pass_through,
            pass_through_lag_days=lag_days
        )
        st.session_state.active_scenario = new_scenario

        # 4. Quick Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("↺ Reset Base", use_container_width=True):
                st.session_state.active_preset_name = "Base case"
                st.session_state.active_scenario = presets["base_case"]
                st.rerun()
        with col_btn2:
            if st.button("💾 Save Scenario", use_container_width=True):
                if len(st.session_state.saved_scenarios) < 3:
                    st.session_state.saved_scenarios.append(new_scenario)
                    st.toast(f"Saved scenario '{new_scenario.name}'!")
                else:
                    st.warning("Max 3 saved scenarios reached.")

        # 5. Team Footer
        st.markdown(
            f"""
            <div style="margin-top: 1.5rem; padding-top: 0.75rem; border-top: 1px solid #E2E8F0; font-size: 0.75rem; color: #64748B;">
                <b>{branding.get('team_name', 'Team 11.59')}</b><br>
                Vikram T · Sayoni Dan · Trisha Pal<br>
                <i>{branding.get('institute', 'XIME Chennai')}</i>
            </div>
            """,
            unsafe_allow_html=True
        )

    return st.session_state.active_scenario
