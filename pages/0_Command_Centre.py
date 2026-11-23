"""
Materials Control Room (Master Home) · Rane (Madras) MMD Decision Engine
Team 11:59 · Xovate'26 Management Hackathon
"See the shock coming, measure what it costs, decide what to do."
"""

import streamlit as st
import pandas as pd
from engine.state import (
    init_canonical_state,
    get_current_scenario,
    get_default_presets,
    load_glossary
)
from engine.chain import run_all
from engine.signals import get_shock_radar_signals, get_market_tape
from engine.exposure import compute_exposure_map, plot_exposure_map
from engine.risk import run_profit_at_risk_monte_carlo
from engine.timeline import compute_cash_recovery_timeline
from engine.buy_signal import compute_buy_signals
from engine.triggers import evaluate_andon_triggers
from engine.functions import compute_cross_functional_lenses
from ui.control_deck import render_control_deck
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge
from ui.charts import plot_profit_at_risk_distribution, plot_cash_timeline_trough, plot_inventory_runway
from ui.theme import format_money_cr, format_pct

# 1. State & Calculations
init_canonical_state()
active_scn = get_current_scenario()
presets = get_default_presets()
base_scn = presets["base_case"]
glossary = load_glossary()

results = run_all(active_scn)
base_results = run_all(base_scn)

# Novel Engine Computations
exposure_data = compute_exposure_map(active_scn)
risk_data = run_profit_at_risk_monte_carlo(active_scn, num_paths=2000, seed=42)
timeline_data = compute_cash_recovery_timeline(active_scn, results)
buy_signals = compute_buy_signals(active_scn, results)
andon_triggers = evaluate_andon_triggers(active_scn, results)
func_lenses = compute_cross_functional_lenses(active_scn, results)

# ==============================================================================
# 1. COMPACT EXECUTIVE HEADER (T6: NO GRADIENT HERO)
# ==============================================================================
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #C9D1D5; padding-bottom: 6px; margin-bottom: 8px;">
        <div>
            <span style="font-size: 1.35rem; font-weight: 700; color: #1D262C; letter-spacing: -0.01em;">Rane (Madras) Materials Control Room</span>
            <span style="font-size: 0.82rem; color: #536471; margin-left: 12px; font-style: italic;">"See the shock coming, measure what it costs, decide what to do."</span>
        </div>
        <div style="font-size: 0.8rem; color: #536471;">
            <span style="background: #2F5D7C; color: #FFF; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.72rem;">Team 11:59</span> · XIME Chennai · FY25 Baseline
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 2. LIVE COMMODITY & FREIGHT MARKET TAPE (T1: COMPUTED DYNAMICALLY FROM DATA)
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
# 3. INTERACTIVE CONTROL DECK (SECTION 2a)
# ==============================================================================
render_control_deck()

# ==============================================================================
# 4. STANDARD TOP KPI STRIP
# ==============================================================================
kpi_strip(results, base_results)

# Contextual Alert Banner
if active_scn.name != "Base case":
    ebitda_diff = results.ebitda_cr - base_results.ebitda_cr
    if ebitda_diff < -30:
        insight(
            f"Under active scenario <b>'{active_scn.name}'</b>, raw material & freight shocks threaten to erode "
            f"<b>{format_money_cr(abs(ebitda_diff))}</b> of operating EBITDA. Net profit moves to <b>{format_money_cr(results.pat_cr)}</b>. "
            f"Deployment of <b>'{results.top_action_title}'</b> is recommended to recover <b>+{format_money_cr(results.top_action_net_benefit_cr)}</b>.",
            is_warning=True
        )
    else:
        insight(
            f"Active scenario <b>'{active_scn.name}'</b> operates within calibrated tolerance. "
            f"Operating EBITDA margin: <b>{results.ebitda_margin_pct:.1f}%</b>. Minimum inventory coverage: <b>{results.worst_days_of_cover:.0f} days</b>."
        )

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 5. HERO ROW: INBOUND EXPOSURE MAP (N2) & ANDON RISK BOARD (N7)
# ==============================================================================
col_map, col_andon = st.columns([1.55, 1.15])

with col_map:
    section("🌐 Inbound Trade Lane Exposure Map", "Global maritime corridors, chokepoint transit delays, and spend-at-risk")
    fig_map = plot_exposure_map(exposure_data)
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; background:#F8F9F9; padding:8px 12px; border-radius:4px; border:1px solid #C9D1D5; color:#1D262C;">
            <span><b>Spend at Risk:</b> <span style="color:#C2382B; font-weight:700;">₹{exposure_data['total_spend_at_risk_cr']:.1f} Cr</span> (annual spend on amber/red lanes)</span>
            <span><b>Tracked Corridors:</b> 6 Inbound Lanes</span>
            <span><b>Active Delay:</b> {"+" + str(active_scn.shipping_delay_days) + " days" if active_scn.shipping_delay_days > 0 else "On schedule"}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_andon:
    section("🚨 Andon Trigger Board", "7 operational trigger thresholds with green/amber/red indicator lights")
    for t in andon_triggers:
        status = t["status"]
        css_card = "mmd-andon-red" if status == "RED" else ("mmd-andon-amber" if status == "AMBER" else "mmd-andon-green")
        badge_html = status_badge(status, status.lower())
        
        st.markdown(
            f"""
            <div class="mmd-andon-card {css_card}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; font-size:0.82rem;">{t['name']}</span>
                    {badge_html}
                </div>
                <div style="font-size:0.75rem; color:#536471; margin-top:2px; font-variant-numeric:tabular-nums;">
                    <b>Current:</b> {t.get('current_value_formatted', '')} &nbsp;|&nbsp; <b>Threshold:</b> {t.get('threshold_label', t.get('threshold_rule', 'N/A'))} &nbsp;|&nbsp; <b>Owner:</b> {t.get('owner', 'MMD')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.expander(":material/menu_book: Mitigation Playbook & Operational SOPs", expanded=False):
        for t in andon_triggers:
            if t["status"] != "GREEN":
                st.markdown(f"**{t['name']} ({t['status']}):** {t['mitigation_sop']}")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 6. ROW: MONTE CARLO PROFIT-AT-RISK & DECISIONS NOW
# ==============================================================================
is_simple = st.session_state.get("simple_view", False) or st.session_state.get("simple_view_toggle", False)

if not is_simple:
    col_risk, col_decisions = st.columns([1.2, 1.2])

    with col_risk:
        section("🎲 Profit-at-Risk Monte Carlo (2,000 Paths)", "Multivariate joint disruption simulation: EBITDA, PAT, and loss probability")
        fig_risk = plot_profit_at_risk_distribution(risk_data)
        st.plotly_chart(fig_risk, use_container_width=True)

        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            st.metric("P10 EBITDA", f"₹{risk_data['p10_ebitda_cr']:.1f} Cr", help="Pessimistic 10th percentile outcome")
        with r_col2:
            st.metric("P50 EBITDA", f"₹{risk_data['p50_ebitda_cr']:.1f} Cr", help="Median expected EBITDA")
        with r_col3:
            st.metric("P90 EBITDA", f"₹{risk_data['p90_ebitda_cr']:.1f} Cr", help="Optimistic 90th percentile outcome")
        with r_col4:
            st.metric("P(PAT < 0)", f"{risk_data['prob_loss_pat_pct']:.1f}%", help="Probability of net operating loss")

    with col_decisions:
        section("⚡ Decisions Now: Top Mitigation Actions", "Prescriptive ranking based on net ₹ Cr operating benefit and time to execute")
        for act in results.action_rankings[:3]:
            with st.container(border=True):
                a_col1, a_col2 = st.columns([2.3, 1.0])
                with a_col1:
                    st.markdown(f"**#{act['rank']} {act['title']}**")
                    st.caption(f"Category: {act['category']} · Timeframe: {act['time_to_implement']} · Budget: ₹{act['cash_budget_cr']:.1f} Cr")
                with a_col2:
                    st.markdown(f"<div style='text-align:right; font-weight:700; color:#1E8A4C; font-size:1.05rem; font-variant-numeric:tabular-nums;'>+₹{act['net_benefit_cr']:.1f} Cr</div>", unsafe_allow_html=True)
                    st.caption(f"Cost: ₹{act['cost_cr']:.1f} Cr")

        # Commodity Buy-Timing Signals Strip (Section 6: Full Material Names)
        st.markdown("<div style='font-size:0.78rem; font-weight:700; color:#1D262C; margin-top:0.6rem; margin-bottom:0.35rem;'>COMMODITY BUY-TIMING SIGNALS:</div>", unsafe_allow_html=True)
        sig_cols = st.columns(len(buy_signals))
        
        full_names = {
            "copper": "Copper",
            "aluminium": "Aluminium",
            "nickel": "Nickel",
            "steel_hr": "Steel HR",
            "resin": "Resin",
            "rubber": "Rubber"
        }

        for col, (mat_id, sig) in zip(sig_cols, buy_signals.items()):
            with col:
                st.markdown(
                    f"""
                    <div style="border:1px solid #C9D1D5; border-radius:4px; padding:6px; text-align:center; background:#FFFFFF;">
                        <div style="font-size:0.72rem; font-weight:600; color:#1D262C;">{full_names.get(mat_id, mat_id.title())}</div>
                        <div class="{sig['badge_class']}" style="margin:3px 0; font-size:0.7rem; padding:2px 4px;">{sig['signal']}</div>
                        <div style="font-size:0.68rem; color:#536471; font-variant-numeric:tabular-nums;">Save: ₹{sig['expected_saving_cr']:.1f}Cr</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
else:
    section("⚡ Simplified Operational View", "Essential financial metrics and primary action priorities")
    s_col1, s_col2 = st.columns([1.2, 1.2])
    with s_col1:
        st.markdown("#### Financial Performance Summary")
        p_table = {
            "Line Item": ["Revenue", "Raw Material Cost", "Ocean Freight", "Operating Profit (EBITDA)", "Net Profit (PAT)"],
            "Active Outcome": [
                format_money_cr(results.revenue_cr),
                format_money_cr(results.material_spend_cr),
                format_money_cr(results.ocean_freight_spend_cr),
                format_money_cr(results.ebitda_cr),
                format_money_cr(results.pat_cr)
            ],
            "vs Baseline": [
                format_pct((results.revenue_cr - base_results.revenue_cr) / base_results.revenue_cr * 100, plus_sign=True),
                format_money_cr(results.delta_material_cr, show_sign=True),
                format_money_cr(results.delta_freight_cr, show_sign=True),
                format_money_cr(results.ebitda_cr - base_results.ebitda_cr, show_sign=True),
                format_money_cr(results.pat_cr - base_results.pat_cr, show_sign=True)
            ]
        }
        st.dataframe(pd.DataFrame(p_table), hide_index=True, use_container_width=True)

    with s_col2:
        st.markdown("#### Primary Recommended Actions")
        for act in results.action_rankings[:3]:
            st.markdown(f"• **{act['title']}**: +₹{act['net_benefit_cr']:.1f} Cr net benefit ({act['time_to_implement']})")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 7. CROSS-FUNCTIONAL IMPACT LENSES STRIP (N8 / SECTION 6)
# ==============================================================================
section("👥 Cross-Functional Department Lenses", "Enterprise ripple effect across all 7 operational leadership domains")

dept_cols = st.columns(7)
for col, (dept, lens) in zip(dept_cols, func_lenses.items()):
    with col:
        badge = status_badge(lens["status"], lens["status"].lower())
        st.markdown(
            f"""
            <div style="border:1px solid #C9D1D5; border-radius:4px; padding:8px; background:#F8F9F9; min-height:120px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#1D262C;">{dept}</span>
                    {badge}
                </div>
                <div style="font-size:0.82rem; font-weight:700; color:#2F5D7C; margin-bottom:4px; font-variant-numeric:tabular-nums;">{lens['primary_kpi']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.popover(f":material/info: {dept} Detail"):
            st.markdown(f"**Impact Summary:** {lens['impact_summary']}")
            st.markdown(f"**Action Required:** {lens['prescriptive_action']}")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 8. ROW: 12-MONTH CASH TIMELINE (N4) & DYNAMIC INVENTORY RUNWAY (N1)
# ==============================================================================
col_time, col_runway = st.columns([1.2, 1.2])

with col_time:
    section("⏳ 12-Month Projected Cash Deficit Profile", "Working capital deficit trough caused by OEM settlement lag")
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
    st.markdown("#### :material/description: Executive Decision Brief for Managing Director")
    st.markdown("<span style='font-size:0.85rem; color:#536471;'>Generate an audit-ready, 1-page HTML memo summarizing scenario financial exposure, cash trough, and action approvals.</span>", unsafe_allow_html=True)

with d_col2:
    brief_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>MMD Executive Decision Brief · Rane (Madras)</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 30px; color: #1D262C; max-width: 900px; margin: auto; background: #FFFFFF; }}
            h1 {{ color: #1D262C; border-bottom: 2px solid #2F5D7C; padding-bottom: 8px; font-size: 22px; }}
            .kpi-row {{ display: flex; gap: 15px; margin: 20px 0; }}
            .kpi-box {{ background: #F8F9F9; border: 1px solid #C9D1D5; padding: 12px; border-radius: 4px; flex: 1; }}
            .kpi-label {{ font-size: 11px; color: #536471; text-transform: uppercase; font-weight: bold; }}
            .kpi-val {{ font-size: 18px; font-weight: bold; color: #1D262C; margin-top: 4px; font-variant-numeric: tabular-nums; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }}
            th, td {{ border: 1px solid #C9D1D5; padding: 8px 12px; text-align: left; }}
            th {{ background: #EEF1F2; font-weight: bold; }}
            .action-rec {{ background: #EEF1F2; border-left: 4px solid #2F5D7C; padding: 12px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <h1>RANE (MADRAS) LIMITED · EXECUTIVE DECISION BRIEF</h1>
        <div style="font-size: 12px; color: #536471; margin-bottom: 15px;">
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
        label=":material/download: Download Decision Brief",
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

# Footer
st.markdown(
    """
    <div style="text-align: center; font-size: 0.75rem; color: #8E9AA2; margin-top: 2rem; border-top: 1px solid #C9D1D5; padding-top: 10px;">
        Xovate'26 Management Hackathon · Team 11:59 · Vikram T, Sayoni Dan, Trisha Pal · XIME Chennai
    </div>
    """,
    unsafe_allow_html=True
)
