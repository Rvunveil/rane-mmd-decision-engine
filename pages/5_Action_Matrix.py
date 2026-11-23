"""
Module 5: Prescriptive Action Matrix & Cross-Functional Ripple
Team 11:59 · Xovate'26
"""

import streamlit as st
import pandas as pd
from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all
from engine.actions import optimize_action_bundle
from engine.triggers import evaluate_andon_triggers
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge
from ui.theme import format_money_cr, format_pct

presets = get_default_presets()
base_scn = presets["base_case"]
active_scn = st.session_state.get("active_scenario", base_scn)

results = run_all(active_scn)
base_results = run_all(base_scn)

page_header("Prescriptive Action Matrix", "Dynamic decision ranking, 6-function ripple matrix & PuLP capital optimizer", "Module 5")
kpi_strip(results, base_results)

# 1. Dynamic Ranked Actions Table
section("📋 Dynamic Ranked Mitigation Matrix", "Actions dynamically re-rank based on active commodity shocks and shipping delays")

act_rows = []
for act in results.action_rankings:
    net_val = act["net_benefit_cr"]
    badge_type = "green" if net_val > 5.0 else ("amber" if net_val >= 0 else "red")
    
    act_rows.append({
        "Rank": f"#{act['rank']}",
        "Action Title": act["title"],
        "Category": act["category"],
        "Time to Execute": act["time_to_implement"],
        "Cost (₹ Cr)": f"₹{act['cost_cr']:.2f} Cr",
        "Gross Benefit": f"₹{act['benefit_cr']:.2f} Cr",
        "Net ₹ Impact": f"+₹{net_val:.2f} Cr" if net_val >= 0 else f"-₹{-net_val:.2f} Cr",
        "Cash Budget Req": f"₹{act['cash_budget_cr']:.1f} Cr"
    })

st.dataframe(pd.DataFrame(act_rows), hide_index=True, use_container_width=True)

# Andon Trigger Playbook Linkage (N7)
with st.expander("🚨 View Active Andon Trigger Playbook Status (N7)", expanded=False):
    andon_triggers = evaluate_andon_triggers(active_scn, results)
    trig_cols = st.columns(len(andon_triggers))
    for col, t in zip(trig_cols, andon_triggers):
        with col:
            st.markdown(f"**{t['id']}**")
            st.markdown(status_badge(t["status"], t["status"].lower()), unsafe_allow_html=True)
            st.caption(f"{t['name']}<br>Action: **{t['playbook_action']}**", unsafe_allow_html=True)

# 2. Before / After Decision Impact
col_ba1, col_ba2 = st.columns([1.2, 1.0])

top_action = results.action_rankings[0] if results.action_rankings else None

with col_ba1:
    section("⚡ Decision Impact: Before vs After Top Action", f"Implementing Rank #1 ({top_action['title']})")
    if top_action:
        ba_data = [
            {
                "Decision Dimension": "Operating EBITDA",
                "Unmitigated Scenario": format_money_cr(results.ebitda_cr),
                "After Top Action": format_money_cr(results.ebitda_cr + top_action['net_benefit_cr']),
                "Net Benefit": f"+{format_money_cr(top_action['net_benefit_cr'])}"
            },
            {
                "Decision Dimension": "EBITDA Margin",
                "Unmitigated Scenario": f"{results.ebitda_margin_pct:.1f}%",
                "After Top Action": f"{((results.ebitda_cr + top_action['net_benefit_cr']) / results.revenue_cr)*100.0:.1f}%",
                "Net Benefit": f"+{((top_action['net_benefit_cr']) / results.revenue_cr)*100.0:.1f}%"
            },
            {
                "Decision Dimension": "Net Profit (PAT)",
                "Unmitigated Scenario": format_money_cr(results.pat_cr),
                "After Top Action": format_money_cr(results.pat_cr + top_action['net_benefit_cr'] * 0.7483),
                "Net Benefit": f"+{format_money_cr(top_action['net_benefit_cr'] * 0.7483)}"
            },
            {
                "Decision Dimension": "Cash Capital Required",
                "Unmitigated Scenario": "₹ 0.0 Cr",
                "After Top Action": f"₹ {top_action['cash_budget_cr']:.1f} Cr",
                "Net Benefit": "Capex / Opex Allocation"
            }
        ]
        st.dataframe(pd.DataFrame(ba_data), hide_index=True, use_container_width=True)

with col_ba2:
    section("🎯 Selected Action Specifications", "Operational scope and affected supplier base")
    if top_action:
        with st.container(border=True):
            st.markdown(f"**{top_action['title']}**")
            st.caption(f"**Category:** {top_action['category']} | **Time to Implement:** {top_action['time_to_implement']}")
            st.markdown(f"**Description:** {top_action['description']}")
            st.markdown(f"**Affected Supply Partners:** {', '.join(top_action['affected_suppliers'])}")

# 3. Cross-Functional Ripple Matrix
section("🌊 Cross-Functional Ripple Matrix (6 Enterprise Functions)", "Evaluating systemic organizational trade-offs across MMD, Finance, Production, HR, Quality, Logistics, and Sales")

selected_act_id = st.selectbox(
    "Inspect Functional Ripple for Action:",
    options=[a["id"] for a in results.action_rankings],
    format_func=lambda x: f"#{next((a['rank'] for a in results.action_rankings if a['id']==x), 1)}: {next((a['title'] for a in results.action_rankings if a['id']==x), x)}"
)

act_obj = next((a for a in results.action_rankings if a["id"] == selected_act_id), top_action)

if act_obj and "function_impacts" in act_obj:
    ripple_cols = st.columns(6)
    funcs = [
        ("MMD / Procurement", "MMD"),
        ("Finance", "Finance"),
        ("Production", "Production"),
        ("Quality", "Quality"),
        ("Logistics", "Logistics"),
        ("Sales & OEMs", "Sales")
    ]
    
    for c, (f_name, f_key) in zip(ripple_cols, funcs):
        f_info = act_obj["function_impacts"].get(f_key, {"status": "neutral", "reason": "No direct change"})
        st_icon = "🟢 POSITIVE" if f_info["status"] == "+" else ("🔴 STRAIN" if f_info["status"] == "-" else "⚪ NEUTRAL")
        b_color = "green" if f_info["status"] == "+" else ("red" if f_info["status"] == "-" else "neutral")
        
        with c:
            with st.container(border=True):
                st.markdown(f"**{f_name}**")
                st.markdown(status_badge(st_icon, b_color), unsafe_allow_html=True)
                st.caption(f_info["reason"])

# 4. PuLP Linear Programming Action Bundle Optimizer
section("🤖 PuLP Mathematical Optimization: Action Bundle under Cash Budget", "Solves integer linear program to find the highest total Net Benefit within capital limits")

col_opt1, col_opt2 = st.columns([1.0, 1.8])

with col_opt1:
    budget_slider = st.slider(
        "Available Cash Budget Constraint (₹ Cr)",
        0.0, 40.0, 15.0, 1.0,
        help="MMD discretionary cash reserve for hedging, air freight, near-shoring, and safety buffer investments"
    )

with col_opt2:
    chosen_actions, total_cash_used, total_net_rec = optimize_action_bundle(results.action_rankings, budget_slider)
    
    with st.container(border=True):
        st.markdown(f"**Optimal Portfolio Solution (Budget: ₹{budget_slider:.1f} Cr)**")
        st.markdown(
            f"- **Selected Actions Count:** {len(chosen_actions)} actions\n"
            f"- **Total Capital Deployed:** **₹{total_cash_used:.1f} Cr**\n"
            f"- **Total Maximized Net Benefit:** **+{format_money_cr(total_net_rec)}**"
        )
        if chosen_actions:
            chosen_names = ", ".join([f"**{a['id']}** ({a['title'][:20]}...)" for a in chosen_actions])
            st.caption(f"Recommended Bundle: {chosen_names}")
        else:
            st.caption("Budget too low to activate mitigation actions; 'Do Nothing' applies.")

insight(
    f"Under the active scenario, <b>'{top_action['title']}'</b> delivers the highest single net benefit of <b>+{format_money_cr(top_action['net_benefit_cr'])}</b>. "
    f"With a ₹{budget_slider:.0f} Cr cash budget, the <b>PuLP Optimizer</b> bundles {len(chosen_actions)} complementary actions to recover <b>+{format_money_cr(total_net_rec)}</b> of EBITDA."
)

explain_box(
    "Prescriptive Action Matrix & PuLP Optimization",
    "Net Benefit_i = Benefit_i(Scenario, ΔMaterial, ΔFreight, Delays) - Cost_i. PuLP Maximizes sum(x_i * Net_i) s.t. sum(x_i * Budget_i) <= Cash_Budget, x_i in {0,1}",
    "10 Mitigation Actions calibrated from automotive supplier best practices and OEM contract structures."
)
