"""
Command Centre (Home) · Rane (Madras) MMD Decision Engine
Team 11.59 · Xovate'26
"""

import streamlit as st
import pandas as pd
from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario
from engine.chain import run_all
from engine.signals import get_shock_radar_signals
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge
from ui.theme import format_money_cr, format_pct

# 1. State & Calculations
if "active_scenario" not in st.session_state:
    presets = get_default_presets()
    st.session_state.base_scenario = presets["base_case"]
    st.session_state.active_scenario = presets["base_case"]

active_scn = st.session_state.active_scenario
presets = get_default_presets()
base_scn = presets["base_case"]

results = run_all(active_scn)
base_results = run_all(base_scn)

# 2. Hero Banner
st.markdown(
    """
    <div class="mmd-hero-banner">
        <div class="mmd-hero-tag">Xovate'26 Management Hackathon · Automotive Supply Chain Cockpit</div>
        <h1 class="mmd-hero-heading">Rane (Madras) MMD Decision Engine</h1>
        <div class="mmd-hero-tagline">"See the shock. Measure it. Decide."</div>
        <div style="font-size: 0.85rem; color: #E2E8F0; line-height: 1.5; max-width: 900px;">
            An autonomous, driver-based enterprise decision cockpit engineered for the Materials Management Department (MMD). 
            Empowers executive leadership to detect global supply chain bottlenecks, measure cross-functional P&L ripple, 
            and deploy prescriptive mitigation actions before line stoppages occur.
        </div>
        <div class="mmd-hero-meta">
            <span><b>Team:</b> Team 11.59</span>
            <span><b>Members:</b> Vikram T · Sayoni Dan · Trisha Pal</span>
            <span><b>Institute:</b> XIME Chennai</span>
            <span><b>Calibrated Baseline:</b> FY25 Official Handout (₹3,421 Cr Rev / ₹297.7 Cr EBITDA)</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. Standard Top KPI Strip
kpi_strip(results, base_results)

# 4. Critical Insight
if active_scn.name != "Base case":
    ebitda_diff = results.ebitda_cr - base_results.ebitda_cr
    if ebitda_diff < -30:
        insight(
            f"Under the active scenario <b>'{active_scn.name}'</b>, unmitigated material & freight shocks threaten to erode "
            f"<b>{format_money_cr(abs(ebitda_diff))}</b> of operating profit. Net profit drops to <b>{format_money_cr(results.pat_cr)}</b>. "
            f"Immediate execution of <b>'{results.top_action_title}'</b> is recommended to recover <b>+{format_money_cr(results.top_action_net_benefit_cr)}</b>.",
            is_warning=True
        )
    else:
        insight(
            f"Active scenario <b>'{active_scn.name}'</b> is within manageable operating tolerance. "
            f"EBITDA margin stands at <b>{results.ebitda_margin_pct:.1f}%</b>. Minimum inventory coverage is <b>{results.worst_days_of_cover:.0f} days</b>."
        )
else:
    insight(
        "Operating at calibrated <b>Base Case</b> (FY25 average pricing & RBI Forex rates). "
        "Select a crisis preset or fine-tune shock sliders in the sidebar to simulate geopolitical and commodity disruptions."
    )

st.markdown("<br>", unsafe_allow_html=True)

# 5. Two-Column Dashboard Layout
col_left, col_right = st.columns([1.6, 1.0])

with col_left:
    section("⚡ Early Warning Shock Radar", "Real-time indicators synthesized from live dataset signals")
    
    signals = get_shock_radar_signals()
    for s in signals:
        with st.container(border=True):
            r_col1, r_col2, r_col3 = st.columns([2.0, 1.2, 0.8])
            
            with r_col1:
                badge = status_badge(s['status'], s['color'])
                st.markdown(f"**{s['name']}** {badge}", unsafe_allow_html=True)
                st.caption(s['evidence'])
            
            with r_col2:
                st.markdown(f"<div style='font-size:0.75rem; color:#64748B;'>LATEST LEVEL</div>", unsafe_allow_html=True)
                st.markdown(f"**{s['current_val']}**")
                st.caption(f"Baseline: {s['baseline_val']}")
            
            with r_col3:
                rec_preset = s.get('recommended_preset')
                if rec_preset:
                    if st.button("Apply Preset", key=f"btn_{s['id']}", help=f"Simulate {rec_preset}"):
                        st.session_state.active_preset_name = rec_preset
                        if rec_preset == "Red Sea / Hormuz crisis":
                            st.session_state.active_scenario = presets["red_sea_hormuz"]
                        elif rec_preset == "Metal shock":
                            st.session_state.active_scenario = presets["metal_shock"]
                        elif rec_preset == "Tariff & FX escalation":
                            st.session_state.active_scenario = presets["tariff_fx"]
                        elif rec_preset == "Today's market (Live Data)":
                            if st.session_state.todays_market_scenario is None:
                                st.session_state.todays_market_scenario = compute_todays_market_scenario()
                            st.session_state.active_scenario = st.session_state.todays_market_scenario
                        st.rerun()

with col_right:
    section("📊 Active Scenario Summary", "P&L impact bridge vs official handout baseline")
    with st.container(border=True):
        st.markdown(f"#### {active_scn.name}")
        st.markdown(
            f"""
            - **Gross Material Shock Δ:** {format_money_cr(results.delta_material_cr)}
            - **Ocean Freight Shock Δ:** {format_money_cr(results.delta_freight_cr)}
            - **OEM Contract Pass-Through:** +{format_money_cr(results.oem_recovery_cr)} ({active_scn.oem_pass_through_pct:.0f}%)
            - **Working Capital Cash Gap:** {format_money_cr(results.working_capital_gap_cr)} ({active_scn.pass_through_lag_days} days lag)
            - **Scenario EBITDA:** **{format_money_cr(results.ebitda_cr)}** ({results.ebitda_margin_pct:.1f}%)
            - **Net Profit (PAT):** **{format_money_cr(results.pat_cr)}**
            """
        )
        if results.pat_cr < 0:
            st.error(f"⚠️ Net profit wiped out! Annual loss of {format_money_cr(abs(results.pat_cr))}.")
        else:
            st.success(f"✓ Profitable: Net margin at {(results.pat_cr / results.revenue_cr)*100.0:.2f}%.")

    section("🎯 Top Prescriptive Action", "Highest net ₹ impact recommendation for active scenario")
    with st.container(border=True):
        st.markdown(f"**Rank #1: {results.top_action_title}**")
        st.markdown(f"**Net ₹ Benefit:** +{format_money_cr(results.top_action_net_benefit_cr)}")
        
        # Display top 3 actions list
        st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#475569; margin-top:0.75rem;'>TOP 3 RECOMMENDED MITIGATIONS:</div>", unsafe_allow_html=True)
        for act in results.action_rankings[:3]:
            st.markdown(f"- **#{act['rank']} {act['title']}**: Net **+{format_money_cr(act['net_benefit_cr'])}** (Time: {act['time_to_implement']})")

explain_box(
    "Command Centre Synthesis",
    "P&L = Revenue - (Calibrated Material Spend + ΔMaterial) - (Ocean Freight + ΔFreight) + OEM Recovery - D&A/Tax",
    "Handout Baseline + UNCTAD/PortWatch Chokepoints + NY Fed GSCPI + RBI Forex + Ministry of Steel"
)
