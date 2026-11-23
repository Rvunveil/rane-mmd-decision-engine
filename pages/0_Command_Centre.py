"""
Materials Control Room (Master Home) · Rane (Madras) MMD Decision Engine
Team 11:59 · Xovate'26 Management Hackathon
"See the shock coming, measure what it costs, decide what to do."
"""

import streamlit as st
import pandas as pd
from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario
from engine.chain import run_all
from engine.signals import get_shock_radar_signals, get_market_tape
from engine.exposure import compute_exposure_map, plot_exposure_map
from engine.risk import run_profit_at_risk_monte_carlo
from engine.timeline import compute_cash_recovery_timeline
from engine.buy_signal import compute_buy_signals
from engine.triggers import evaluate_andon_triggers
from engine.functions import compute_cross_functional_lenses
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge
from ui.charts import plot_profit_at_risk_distribution, plot_cash_timeline_trough, plot_inventory_runway
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

# Novel Engine Computations
exposure_data = compute_exposure_map(active_scn)
risk_data = run_profit_at_risk_monte_carlo(active_scn, num_paths=1500, seed=42)
timeline_data = compute_cash_recovery_timeline(active_scn, results)
buy_signals = compute_buy_signals(active_scn, results)
andon_triggers = evaluate_andon_triggers(active_scn, results)
func_lenses = compute_cross_functional_lenses(active_scn, results)

# ==============================================================================
# 1. LIVE COMMODITY & FREIGHT MARKET TAPE (T1: COMPUTED DYNAMICALLY FROM DATA)
# ==============================================================================
tape_items = get_market_tape()
tape_html = "".join([
    f'<div class="mmd-tape-item">'
    f'<span class="mmd-tape-label">{item["label"]}:</span> '
    f'<span class="mmd-tape-val">{item["formatted_val"]}</span> '
    f'<span class="mmd-tape-chg-{"up" if item["is_up"] else "down"}">{item["formatted_chg"]}</span>'
    f'{item["sparkline_svg"]}'
    f'</div>'
    for item in tape_items
])
st.markdown(f'<div class="mmd-market-tape">{tape_html}</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. MASTER HERO BANNER
# ==============================================================================
st.markdown(
    """
    <div class="mmd-hero-banner">
        <div class="mmd-hero-tag">Xovate'26 Management Hackathon · Automotive Supply Chain Cockpit</div>
        <h1 class="mmd-hero-heading">Rane (Madras) Materials Control Room</h1>
        <div class="mmd-hero-tagline">"See the shock coming, measure what it costs, decide what to do."</div>
        <div style="font-size: 0.88rem; color: #E2E8F0; line-height: 1.5; max-width: 900px;">
            A unified trading-desk control room engineered for the Materials Management Department (MMD), 
            Finance, and Plant Operations. Integrates global maritime trade lane exposure, 2,000-path Monte Carlo profit-at-risk, 
            prescriptive mitigation playbooks, and OEM price-recovery tracking.
        </div>
        <div class="mmd-hero-meta">
            <span><b>Team:</b> Team 11:59</span>
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

# ==============================================================================
# 5. HERO ROW: INBOUND EXPOSURE MAP (N2) & ANDON RISK BOARD (N7)
# ==============================================================================
col_map, col_andon = st.columns([1.6, 1.0])

with col_map:
    section("🌐 Inbound Trade Lane Exposure Map", "Global maritime corridors, chokepoints, active vessels, and spend-at-risk")
    fig_map = plot_exposure_map(exposure_data)
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; background:#F8FAFC; padding:8px 12px; border-radius:6px; border:1px solid #E2E8F0;">
            <span><b>Total Spend at Risk:</b> <span style="color:#DC2626; font-weight:700;">₹{exposure_data['total_spend_at_risk_cr']:.1f} Cr</span></span>
            <span><b>Tracked Inbound Lanes:</b> 6 Trade Corridors</span>
            <span><b>Vessel Pipeline:</b> 6 Inbound Shipments</span>
            <span><b>Active Chokepoint Alert:</b> {"Red Sea / Cape Reroute (+18d)" if active_scn.shipping_delay_days > 0 else "Normal Maritime Transit"}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_andon:
    section("🚨 Andon Trigger Playbook", "7 mission-critical operational triggers with green/amber/red status lights")
    for t in andon_triggers:
        status = t["status"]
        css_card = "mmd-andon-red" if status == "RED" else ("mmd-andon-amber" if status == "AMBER" else "mmd-andon-green")
        badge_html = status_badge(status, status.lower())
        
        st.markdown(
            f"""
            <div class="mmd-andon-card {css_card}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b>{t['name']}</b>
                    {badge_html}
                </div>
                <div style="font-size:0.75rem; color:#475569; margin-top:2px;">
                    <b>Current:</b> {t['current_value_formatted']} &nbsp;|&nbsp; <b>Owner:</b> {t['owner']}
                </div>
                <div style="font-size:0.75rem; margin-top:4px; font-style:italic;">
                    <b>Playbook:</b> {t['mitigation_sop'][:110]}…
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 6. ROW: MONTE CARLO PROFIT-AT-RISK (N3) & DECISIONS NOW (N6)
# ==============================================================================
col_risk, col_decisions = st.columns([1.2, 1.2])

with col_risk:
    section("🎲 Monte Carlo Profit-at-Risk (2,000 Paths)", "Multivariate joint disruption simulation for EBITDA, PAT, and loss probability")
    fig_risk = plot_profit_at_risk_distribution(risk_data)
    st.plotly_chart(fig_risk, use_container_width=True)

    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1:
        st.metric("P10 EBITDA", f"₹{risk_data['p10_ebitda_cr']:.1f} Cr", help="10th percentile (stress outcome)")
    with r_col2:
        st.metric("P50 EBITDA", f"₹{risk_data['p50_ebitda_cr']:.1f} Cr", help="Median expected EBITDA")
    with r_col3:
        st.metric("P90 EBITDA", f"₹{risk_data['p90_ebitda_cr']:.1f} Cr", help="90th percentile (favourable outcome)")
    with r_col4:
        st.metric("P(PAT < 0)", f"{risk_data['prob_loss_pat_pct']:.1f}%", help="Probability of net annual operating loss")

with col_decisions:
    section("⚡ Decisions Now: Top Mitigation Actions", "Prescriptive ranking based on net ₹ Cr benefit and time to execute")
    for act in results.action_rankings[:3]:
        with st.container(border=True):
            a_col1, a_col2 = st.columns([2.2, 1.0])
            with a_col1:
                st.markdown(f"**#{act['rank']} {act['title']}**")
                st.caption(f"Category: {act['category']} · Time: {act['time_to_implement']} · Budget: ₹{act['cash_budget_cr']:.1f} Cr")
            with a_col2:
                st.markdown(f"<div style='text-align:right; font-weight:700; color:#059669; font-size:1.1rem;'>+₹{act['net_benefit_cr']:.1f} Cr</div>", unsafe_allow_html=True)
                st.caption(f"Cost: ₹{act['cost_cr']:.1f} Cr")

    # Buy Timing Signals Strip
    st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#1E293B; margin-top:0.75rem; margin-bottom:0.35rem;'>COMMODITY BUY-TIMING SIGNALS:</div>", unsafe_allow_html=True)
    sig_cols = st.columns(len(buy_signals))
    for col, (mat_id, sig) in zip(sig_cols, buy_signals.items()):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #E2E8F0; border-radius:6px; padding:6px; text-align:center; background:#FFFFFF;">
                    <div style="font-size:0.7rem; font-weight:700; color:#64748B; text-transform:uppercase;">{mat_id[:6]}</div>
                    <div class="{sig['badge_class']}" style="margin:4px 0;">{sig['signal']}</div>
                    <div style="font-size:0.65rem; color:#475569;">Save: ₹{sig['expected_saving_cr']:.1f}Cr</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 7. CROSS-FUNCTIONAL IMPACT LENSES STRIP (N8)
# ==============================================================================
section("👥 Cross-Functional Department Lenses", "Enterprise ripple effect across all 7 operational leadership domains")

dept_cols = st.columns(7)
for col, (dept, lens) in zip(dept_cols, func_lenses.items()):
    with col:
        badge = status_badge(lens["status"], lens["status"].lower())
        st.markdown(
            f"""
            <div style="border:1px solid #E2E8F0; border-radius:6px; padding:8px; background:#F8FAFC; min-height:165px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#0F172A;">{dept}</span>
                    {badge}
                </div>
                <div style="font-size:0.85rem; font-weight:700; color:#0284C7; margin-bottom:4px;">{lens['primary_kpi']}</div>
                <div style="font-size:0.7rem; color:#475569; line-height:1.3; margin-bottom:6px;">{lens['impact_summary'][:85]}…</div>
                <div style="font-size:0.65rem; color:#059669; font-weight:600;">{lens['prescriptive_action'][:45]}…</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 8. ROW: 12-MONTH CASH TIMELINE (N4) & DYNAMIC INVENTORY RUNWAY (N1)
# ==============================================================================
col_time, col_runway = st.columns([1.2, 1.2])

with col_time:
    section("⏳ 12-Month Cash Deficit Trough & OEM Recovery", "Month-by-month cash lag showing peak deficit trough and borrowing interest cost")
    fig_timeline = plot_cash_timeline_trough(timeline_data)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.caption(
        f"Peak Cash Deficit: **₹{timeline_data['max_cumulative_deficit_cr']:.1f} Cr** at {timeline_data['trough_month_name']} · "
        f"Annual Working Capital Interest Drag: **₹{timeline_data['financing_interest_cost_cr']:.2f} Cr** (at {timeline_data['working_capital_interest_rate_pct']:.1f}% p.a.)"
    )

with col_runway:
    section("📊 Dynamic Inventory Runway Strip", "Plant days-of-cover vs effective lead time (including maritime delays)")
    fig_runway = plot_inventory_runway(results.inventory_summary)
    st.plotly_chart(fig_runway, use_container_width=True)
    
    st.caption(
        f"Critical Runway Alert: **{results.worst_material_name}** at **{results.worst_days_of_cover:.0f} days of cover** "
        f"(Margin: {results.worst_runway_margin_days:+.1f} days vs Effective Lead Time)."
    )

# ==============================================================================
# 9. DECISION BRIEF EXPORT FOR MANAGING DIRECTOR
# ==============================================================================
st.markdown("---")
d_col1, d_col2 = st.columns([2.0, 1.0])
with d_col1:
    st.markdown("#### 📄 Executive Decision Brief for Managing Director")
    st.markdown("Download an auditable, board-ready 1-page HTML memo summarizing active scenario impact and mitigation mandate.")

with d_col2:
    brief_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>MMD Executive Decision Brief · Rane (Madras)</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 30px; color: #0F172A; max-width: 900px; margin: auto; }}
            h1 {{ color: #0F172A; border-bottom: 2px solid #0284C7; padding-bottom: 8px; }}
            .kpi-row {{ display: flex; gap: 15px; margin: 20px 0; }}
            .kpi-box {{ background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; flex: 1; }}
            .kpi-label {{ font-size: 11px; color: #64748B; text-transform: uppercase; font-weight: bold; }}
            .kpi-val {{ font-size: 20px; font-weight: bold; color: #0F172A; margin-top: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }}
            th, td {{ border: 1px solid #CBD5E1; padding: 8px 12px; text-align: left; }}
            th {{ background: #F1F5F9; font-weight: bold; }}
            .action-rec {{ background: #ECFDF5; border-left: 4px solid #059669; padding: 12px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <h1>RANE (MADRAS) LIMITED · EXECUTIVE DECISION BRIEF</h1>
        <div style="font-size: 12px; color: #64748B; margin-bottom: 15px;">
            Date: 23 November 2026 · Author: Team 11:59 (Xovate'26) · Target: Managing Director & MMD Committee
        </div>

        <p><b>ACTIVE OPERATIONAL SCENARIO:</b> {active_scn.name}</p>

        <div class="kpi-row">
            <div class="kpi-box"><div class="kpi-label">Revenue</div><div class="kpi-val">₹{results.revenue_cr:,.1f} Cr</div></div>
            <div class="kpi-box"><div class="kpi-label">EBITDA (Margin)</div><div class="kpi-val">₹{results.ebitda_cr:.1f} Cr ({results.ebitda_margin_pct:.1f}%)</div></div>
            <div class="kpi-box"><div class="kpi-label">Net Profit (PAT)</div><div class="kpi-val">₹{results.pat_cr:.1f} Cr</div></div>
            <div class="kpi-box"><div class="kpi-label">Working Capital Gap</div><div class="kpi-val">₹{results.working_capital_gap_cr:.1f} Cr</div></div>
        </div>

        <h3>1. Supply Chain Exposure & Spend at Risk</h3>
        <p>Total spend at risk across global inbound lanes stands at <b>₹{exposure_data['total_spend_at_risk_cr']:.1f} Cr</b>. Minimum inventory coverage is <b>{results.worst_days_of_cover:.0f} days</b> for {results.worst_material_name}.</p>

        <h3>2. Top Prescriptive Mitigation Actions</h3>
        <table>
            <tr><th>Rank</th><th>Action Title</th><th>Category</th><th>Time to Implement</th><th>Budget</th><th>Net ₹ Benefit</th></tr>
            <tr><td>#1</td><td>{results.action_rankings[0]['title']}</td><td>{results.action_rankings[0]['category']}</td><td>{results.action_rankings[0]['time_to_implement']}</td><td>₹{results.action_rankings[0]['cash_budget_cr']:.1f} Cr</td><td><b>+₹{results.action_rankings[0]['net_benefit_cr']:.1f} Cr</b></td></tr>
            <tr><td>#2</td><td>{results.action_rankings[1]['title']}</td><td>{results.action_rankings[1]['category']}</td><td>{results.action_rankings[1]['time_to_implement']}</td><td>₹{results.action_rankings[1]['cash_budget_cr']:.1f} Cr</td><td><b>+₹{results.action_rankings[1]['net_benefit_cr']:.1f} Cr</b></td></tr>
            <tr><td>#3</td><td>{results.action_rankings[2]['title']}</td><td>{results.action_rankings[2]['category']}</td><td>{results.action_rankings[2]['time_to_implement']}</td><td>₹{results.action_rankings[2]['cash_budget_cr']:.1f} Cr</td><td><b>+₹{results.action_rankings[2]['net_benefit_cr']:.1f} Cr</b></td></tr>
        </table>

        <div class="action-rec">
            <b>DECISION MANDATE:</b> Approve deployment of Rank #1 ({results.action_rankings[0]['title']}) with immediate budgetary sanction of ₹{results.action_rankings[0]['cash_budget_cr']:.1f} Cr to protect operating margin and prevent assembly line starvation.
        </div>
    </body>
    </html>
    """
    st.download_button(
        label="📥 Download Executive Brief (HTML)",
        data=brief_html,
        file_name=f"Rane_Decision_Brief_{active_scn.name.replace(' ', '_')}.html",
        mime="text/html",
        use_container_width=True
    )

explain_box(
    "Materials Control Room Architecture",
    "Unified Trading Desk = Inbound Exposure Map + 2,000-Path Monte Carlo VaR + 7-Trigger Andon Playbook + 12M Cash Timeline + Function Lenses",
    "Calibrated FY25 Handout (₹3,421 Cr Rev / ₹297.7 Cr EBITDA) · Live Data Feeds · Deterministic Arithmetic"
)
