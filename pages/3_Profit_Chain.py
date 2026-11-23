"""
Module 3: Live Recalculation Chain & P&L Impact
Team 11.59 · Xovate'26
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge
from ui.charts import plot_ebitda_waterfall
from ui.theme import format_money_cr, format_pct, format_inr_t, COLOR_BRAND_PRIMARY, COLOR_STATUS_RED, COLOR_STATUS_GREEN

presets = get_default_presets()
base_scn = presets["base_case"]
active_scn = st.session_state.get("active_scenario", base_scn)

results = run_all(active_scn)
base_results = run_all(base_scn)

page_header("Live Recalculation Chain", "Landed cost/t, division allocations, cash-gap & EBITDA/PAT waterfall bridge", "Module 3")
kpi_strip(results, base_results)

# 1. Landed Cost per Tonne Breakdown
section("📦 Landed Cost per Tonne Breakdown (All 7 Inputs)", "Pure driver calculations linking spot commodity price, FX, duties, and freight")

landed_rows = []
for mat_id, item in results.landed_costs.items():
    landed_rows.append({
        "Material Name": item["name"],
        "Sourcing": "Import" if item["import_dependent"] else "Domestic",
        "Currency": item["currency"],
        "Annual Volume (Tonnes)": f"{item['annual_tonnes']:,.0f} t",
        "Base RM Cost (₹/t)": f"₹{item['base_material_inr_t']:,.0f}",
        "Scenario RM Cost (₹/t)": f"₹{item['scenario_material_inr_t']:,.0f}",
        "Freight (₹/t)": f"₹{item['scenario_freight_inr_t']:,.0f}",
        "Base Landed (₹/t)": f"₹{item['base_landed_inr_t']:,.0f}",
        "Scenario Landed (₹/t)": f"₹{item['scenario_landed_inr_t']:,.0f}",
        "Landed Δ (%)": f"{item['delta_pct']:+.1f}%"
    })

st.dataframe(pd.DataFrame(landed_rows), hide_index=True, use_container_width=True)

# 2. Division Line Cost Impact
col_div1, col_div2 = st.columns([1.2, 1.0])

with col_div1:
    section("🏭 Division Cost Allocation Impact", "Propagating raw material shock into Rane's 4 core manufacturing divisions")
    
    div_rows = []
    for d_id, d in results.division_costs.items():
        div_rows.append({
            "Division": d["name"],
            "Base Spend": f"₹{d['base_spend_cr']:.1f} Cr",
            "Scenario Spend": f"₹{d['scenario_spend_cr']:.1f} Cr",
            "Cost Δ (₹ Cr)": f"{d['delta_cr']:+.1f} Cr",
            "Cost Δ (%)": f"{d['delta_pct']:+.1f}%"
        })
    st.dataframe(pd.DataFrame(div_rows), hide_index=True, use_container_width=True)

with col_div2:
    # Division Cost Bar Chart
    d_names = [d["name"] for d in results.division_costs.values()]
    d_base = [d["base_spend_cr"] for d in results.division_costs.values()]
    d_scn = [d["scenario_spend_cr"] for d in results.division_costs.values()]
    
    fig_div = go.Figure()
    fig_div.add_trace(go.Bar(name="Base Spend", y=d_names, x=d_base, orientation='h', marker_color="#94A3B8"))
    fig_div.add_trace(go.Bar(name="Scenario Spend", y=d_names, x=d_scn, orientation='h', marker_color=COLOR_BRAND_PRIMARY))
    fig_div.update_layout(
        title="<b>Division Material Spend Comparison (₹ Cr)</b>",
        xaxis_title="₹ Crores",
        barmode='group',
        height=280,
        margin=dict(l=20, r=20, t=35, b=20)
    )
    st.plotly_chart(fig_div, use_container_width=True)

# 3. P&L Waterfall Bridge (EBITDA & PAT)
section("📊 EBITDA & Net Profit (PAT) Waterfall Bridge", "Transparent reconciliation from Baseline EBITDA to Scenario PAT")

fig_waterfall = plot_ebitda_waterfall(
    base_ebitda=base_results.ebitda_cr,
    delta_material=results.delta_material_cr,
    delta_freight=results.delta_freight_cr,
    recovery=results.oem_recovery_cr,
    lost_contrib=results.lost_contribution_cr,
    scenario_ebitda=results.ebitda_cr,
    scenario_pat=results.pat_cr
)
st.plotly_chart(fig_waterfall, use_container_width=True)

# 4. Working Capital Lag Cash Gap Callout
col_lag1, col_lag2 = st.columns([1.5, 1.0])

with col_lag1:
    section("⏳ Working Capital Recovery Cash Gap", "Commercial friction from OEM 60–90 day price adjustment lag")
    st.markdown(
        f"""
        Although the active contract pass-through is set to **{active_scn.oem_pass_through_pct:.0f}%**, 
        Tier-1 OEM contract renegotiations (e.g., Maruti Suzuki, Tata Motors) legally require a **{active_scn.pass_through_lag_days}-day settlement lag**.
        
        - **Total Monthly Shock Incurred:** {format_money_cr((results.delta_material_cr + results.delta_freight_cr) / 12.0)} / month
        - **Cumulative Working Capital Cash Deficit:** **{format_money_cr(results.working_capital_gap_cr)}**
        - **Financing Cost @ 9.5% Short-Term Debt:** **{format_money_cr(results.working_capital_gap_cr * 0.095)} / year**
        """
    )

with col_lag2:
    with st.container(border=True):
        st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#475569;'>CASH GAP FORMULA</div>", unsafe_allow_html=True)
        st.code(
            f"Cash Gap = (ΔMaterial + ΔFreight) × Pass% × (Lag / 365)\n"
            f"         = ₹{results.delta_material_cr + results.delta_freight_cr:.1f} Cr × {active_scn.oem_pass_through_pct/100:.2f} × ({active_scn.pass_through_lag_days}/365)\n"
            f"         = ₹{results.working_capital_gap_cr:.2f} Cr",
            language="text"
        )
        st.caption("Mitigation: Deploy ACT-02 (Index-linked contract) to compress lag from 75 to 30 days.")

insight(
    f"Gross material cost inflation under active scenario stands at <b>{format_money_cr(results.delta_material_cr)}</b>. "
    f"With <b>{active_scn.oem_pass_through_pct:.0f}% pass-through</b>, Rane recovers <b>+{format_money_cr(results.oem_recovery_cr)}</b>, "
    f"leaving a net unmitigated EBITDA reduction of <b>{format_money_cr(base_results.ebitda_cr - results.ebitda_cr)}</b>."
)

explain_box(
    "Live Recalculation Chain & Landed Cost",
    "Landed = BasePrice * (1 + Shock) * (FX/FX_base if USD else 1) * (1 + Duty + Tariff) + Freight + Handling",
    "P&L: EBITDA = Base EBITDA - ΔMaterial - ΔFreight + Recovery - Lost Contribution; PBT = EBITDA - Fixed D&A/Interest; PAT = PBT * (1 - 25.17%) if PBT > 0 else PBT."
)
