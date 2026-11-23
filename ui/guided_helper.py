"""
"What happened?" Guided Decision Helper (Section 2b)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Plain-language decision wizard for plant managers, operational engineers, and executives.
Translates real-world supply chain disruptions into exact model parameters, computes
the financial impact and immediate mitigation actions, and applies them to the dashboard.
"""

import streamlit as st
from engine.state import apply_scenario_values, get_current_scenario
from engine.chain import run_all
from engine.scenario import Scenario
from engine.actions import optimize_action_portfolio
from engine.functions import compute_cross_functional_lenses
from ui.theme import format_money_cr


EVENT_OPTIONS = [
    ("shipping", "A shipping route is blocked or slow (e.g. Red Sea, Suez, Cape diversion)"),
    ("metal", "A metal price jumped (e.g. Copper, Aluminium, Steel)"),
    ("fx", "The rupee got weaker against USD (forex escalation)"),
    ("demand", "Customers are ordering less (automotive volume contraction)"),
    ("delay", "A supplier shipment is delayed (inventory runway threat)"),
    ("tariff", "Import duty or customs tariff went up on imported materials")
]

SEVERITY_MAPPINGS = {
    "shipping": {
        "Small": {"freight_multiplier": 1.5, "shipping_delay_days": 7, "name": "Guided: Moderate Shipping Delay"},
        "Medium": {"freight_multiplier": 2.0, "shipping_delay_days": 14, "name": "Guided: Severe Sea Freight Hike"},
        "Large": {"freight_multiplier": 2.73, "shipping_delay_days": 18, "name": "Guided: Red Sea / Chokepoint Blockade"}
    },
    "metal": {
        "Small": {"copper": 10.0, "aluminium": 10.0, "steel_hr": 8.0, "metal_master": 10.0, "name": "Guided: Metal Uptick (+10%)"},
        "Medium": {"copper": 20.0, "aluminium": 20.0, "steel_hr": 15.0, "metal_master": 20.0, "name": "Guided: Metal Rally (+20%)"},
        "Large": {"copper": 35.0, "aluminium": 32.0, "steel_hr": 28.0, "metal_master": 35.0, "name": "Guided: Commodity Shock (+35%)"}
    },
    "fx": {
        "Small": {"fx_inr_usd": 88.0, "name": "Guided: Rupee Softening (₹88/$)"},
        "Medium": {"fx_inr_usd": 92.0, "name": "Guided: Forex Escalation (₹92/$)"},
        "Large": {"fx_inr_usd": 96.5, "name": "Guided: Acute Rupee Depreciation (₹96.5/$)"}
    },
    "demand": {
        "Small": {"demand_volume_pct": -5.0, "name": "Guided: Slight Demand Softening (-5%)"},
        "Medium": {"demand_volume_pct": -8.0, "name": "Guided: Vehicle Slump (-8%)"},
        "Large": {"demand_volume_pct": -12.0, "name": "Guided: Severe OEM Cutback (-12%)"}
    },
    "delay": {
        "Small": {"shipping_delay_days": 10, "name": "Guided: 10-day Lead Time Delay"},
        "Medium": {"shipping_delay_days": 20, "name": "Guided: 20-day Supplier Delay"},
        "Large": {"shipping_delay_days": 30, "name": "Guided: 30-day Container Port Congestion"}
    },
    "tariff": {
        "Small": {"tariff_pct": 5.0, "name": "Guided: +5% Import Tariff"},
        "Medium": {"tariff_pct": 10.0, "name": "Guided: +10% Import Surcharge"},
        "Large": {"tariff_pct": 15.0, "name": "Guided: +15% Carbon/Border Duty"}
    }
}


def compute_guided_recommendation(event_type: str, severity: str, custom_val: float = None):
    """
    Computes financial impact and prescriptive recommendation for the guided helper.
    """
    # 1. Base scenario baseline
    base_scn = Scenario(name="Base case")
    base_res = run_all(base_scn)

    # 2. Extract proposed shock
    shock_dict = dict(SEVERITY_MAPPINGS.get(event_type, {}).get(severity, {}))
    
    # Construct scenario
    prop_scn = Scenario(
        name=shock_dict.get("name", "Guided Scenario"),
        price_shock_pct={
            "copper": shock_dict.get("copper", 0.0),
            "nickel": shock_dict.get("nickel", 0.0),
            "aluminium": shock_dict.get("aluminium", 0.0),
            "resin": shock_dict.get("resin", 0.0),
            "rubber": shock_dict.get("rubber", 0.0),
            "steel_hr": shock_dict.get("steel_hr", 0.0),
            "steel_cr": shock_dict.get("steel_cr", 0.0)
        },
        freight_multiplier=shock_dict.get("freight_multiplier", 1.0),
        fx_inr_usd=shock_dict.get("fx_inr_usd", 84.56),
        tariff_pct=shock_dict.get("tariff_pct", 0.0),
        demand_volume_pct=shock_dict.get("demand_volume_pct", 0.0),
        shipping_delay_days=shock_dict.get("shipping_delay_days", 0)
    )

    prop_res = run_all(prop_scn)

    # Financial impact
    delta_ebitda = prop_res.ebitda_cr - base_res.ebitda_cr
    cost_impact = abs(min(delta_ebitda, 0.0))

    # Prescriptive actions
    best_combo, best_spend, best_val = optimize_action_portfolio(prop_res.action_rankings, 15.0)
    top_action = best_combo[0] if best_combo else (prop_res.action_rankings[0] if prop_res.action_rankings else None)

    # Cross-functional lenses
    lenses = compute_cross_functional_lenses(prop_scn, prop_res)

    def _get_act_field(act, field, default=""):
        if not act:
            return default
        if isinstance(act, dict):
            return act.get(field, default)
        return getattr(act, field, default)

    return {
        "scenario_dict": shock_dict,
        "cost_impact_cr": cost_impact,
        "base_pat_cr": base_res.pat_cr,
        "prop_pat_cr": prop_res.pat_cr,
        "prop_ebitda_cr": prop_res.ebitda_cr,
        "top_action_name": _get_act_field(top_action, "title", "Container Consolidation"),
        "top_action_benefit_cr": _get_act_field(top_action, "net_benefit_cr", 8.5),
        "top_action_time": _get_act_field(top_action, "time_to_implement", "2 weeks"),
        "top_action_owner": _get_act_field(top_action, "category", "Logistics & MMD"),
        "finance_cash_gap": lenses.get("Finance", {}).get("primary_kpi", "₹0.0 Cr Working Capital Drag"),
        "production_runway": lenses.get("Production", {}).get("impact_summary", "Runway secure across all lines."),
        "sales_claim": f"₹{prop_res.oem_recovery_cr:.1f} Cr"
    }


@st.dialog("What happened? Get a recommendation")
def render_guided_helper_dialog():
    """
    Renders the plain-language guided assistant modal dialog.
    """
    st.markdown("<p style='font-size: 0.9rem; color: #536471;'>Select the operational disruption event to calculate the financial impact and immediate prescriptive moves.</p>", unsafe_allow_html=True)

    event_labels = [opt[1] for opt in EVENT_OPTIONS]
    selected_event_label = st.radio("1. What event happened?", event_labels, index=0)
    
    # Map back to event key
    event_key = "shipping"
    for k, lbl in EVENT_OPTIONS:
        if lbl == selected_event_label:
            event_key = k
            break

    # Severity selection
    st.markdown("<b>2. How big is the disruption?</b>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    def _set_sev(val):
        st.session_state["guided_sev"] = val

    with c1:
        st.button("🟡 Small", use_container_width=True, on_click=_set_sev, args=("Small",))
    with c2:
        st.button("🟠 Medium", use_container_width=True, on_click=_set_sev, args=("Medium",))
    with c3:
        st.button("🔴 Large", use_container_width=True, on_click=_set_sev, args=("Large",))

    active_sev = st.session_state.get("guided_sev", "Medium")
    st.caption(f"Selected severity: **{active_sev}**")

    # Compute answer
    rec = compute_guided_recommendation(event_key, active_sev)

    # 4. Plain-language recommendation card
    st.markdown("---")
    st.markdown("### Executive Recommendation & Impact Summary")
    
    cost_text = f"This costs about **₹{rec['cost_impact_cr']:.1f} Cr** in operating margin this year. Profit after tax moves from **₹{rec['base_pat_cr']:.1f} Cr** to **₹{rec['prop_pat_cr']:.1f} Cr**."
    st.markdown(f"<div style='background: #EEF1F2; border-left: 4px solid #2F5D7C; padding: 12px; border-radius: 4px; font-size: 0.92rem; color: #1D262C; margin-bottom: 12px;'>{cost_text}</div>", unsafe_allow_html=True)

    move_text = f"<b>Your first move:</b> {rec['top_action_name']} — yields <b>+₹{rec['top_action_benefit_cr']:.2f} Cr</b> net benefit, implementation takes <b>{rec['top_action_time']}</b>. Owner: <b>{rec['top_action_owner']}</b>."
    st.markdown(f"<div style='background: #F8F9F9; border: 1px solid #C9D1D5; padding: 10px; border-radius: 4px; font-size: 0.88rem; margin-bottom: 12px;'>{move_text}</div>", unsafe_allow_html=True)

    cross_text = (
        f"<b>Cross-functional briefing:</b><br>"
        f"• <b>Finance:</b> {rec['finance_cash_gap']}<br>"
        f"• <b>Production:</b> {rec['production_runway']}<br>"
        f"• <b>Sales:</b> Claim {rec['sales_claim']} reimbursement from OEM customers."
    )
    st.markdown(f"<div style='font-size: 0.84rem; color: #536471; line-height: 1.5; margin-bottom: 16px;'>{cross_text}</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        def _on_apply_guided(shock_dict):
            apply_scenario_values(shock_dict, source="guided_helper")
            st.session_state["show_helper_dialog"] = False

        st.button("Apply to dashboard", type="primary", use_container_width=True, on_click=_on_apply_guided, args=(rec["scenario_dict"],))

    with col_btn2:
        brief_html = f"""
        <html><body>
        <h2>Rane (Madras) Decision Engine — Guided Disruption Brief</h2>
        <p><b>Event:</b> {selected_event_label} ({active_sev})</p>
        <p>{cost_text}</p>
        <p>{move_text}</p>
        <p>{cross_text}</p>
        </body></html>
        """
        st.download_button(
            label="Download one-page brief",
            data=brief_html,
            file_name="Rane_Guided_Decision_Brief.html",
            mime="text/html",
            use_container_width=True
        )
