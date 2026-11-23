"""
Module 4: Inbound Containers & Inventory Runway
Team 11.59 · Xovate'26
"""

import streamlit as st
import pandas as pd
from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge, data_badge
from ui.charts import plot_inventory_runway
from ui.theme import format_money_cr, format_days, format_inr_t

presets = get_default_presets()
base_scn = presets["base_case"]
active_scn = st.session_state.get("active_scenario", base_scn)

results = run_all(active_scn)
base_results = run_all(base_scn)

page_header("Containers & Inventory Model", "Inbound container payloads, freight ₹/t & dynamic stock-out runway alerts", "Module 4")
kpi_strip(results, base_results)

# 1. Dynamic Inventory Runway Chart
section("📊 Inventory Runway vs Effective Lead Time (Days of Cover)", "Visualising vulnerability: Red = Stock-out risk (< Effective LT); Amber = Reorder trigger (< ROP)")

fig_inv = plot_inventory_runway(results.inventory_summary)
st.plotly_chart(fig_inv, use_container_width=True)

# 2. Granular Inventory Policy Table
section("📋 Inventory Policy & Buffer Health Matrix", "Safety stock sizing (95% service level) and reorder points reacting to shipping delays")

inv_table_rows = []
for row in results.inventory_summary:
    status_pill = status_badge(row["status"], row["status_color"])
    inv_table_rows.append({
        "Material": row["material_name"],
        "Sourcing Origin": row["primary_origin"],
        "Stock on Hand": f"{row['stock_on_hand_tonnes']:,.0f} t",
        "Daily Usage": f"{row['daily_usage_tonnes']:.1f} t/day",
        "Days of Cover": f"{row['days_of_cover']:.1f} d",
        "Supplier Lead Time": f"{row['supplier_lead_time']} d",
        "Effective Lead Time": f"{row['effective_lead_time']} d",
        "Safety Stock": f"{row['safety_stock_tonnes']:,.0f} t",
        "Reorder Point (ROP)": f"{row['reorder_point_tonnes']:,.0f} t",
        "Runway Margin": f"{row['runway_margin_days']:+.1f} d",
        "Buffer Status": status_pill
    })

# Render HTML table for styled status pills
df_inv_display = pd.DataFrame(inv_table_rows)
st.write(df_inv_display.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. Inbound Container Shipments & Payload Utilisation
section("🚢 Inbound Container Tracking & Payload Efficiency " + data_badge("SAMPLE DATA"), "40ft container payload utilisation (%) and ocean freight landed cost per tonne")

col_cnt1, col_cnt2, col_cnt3 = st.columns(3)
with col_cnt1:
    st.metric("Avg Container Payload Utilisation", f"{results.avg_container_payload_pct:.1f}%", "Max: 26.0 tonnes / 40ft")
with col_cnt2:
    st.metric("Avg Inbound Freight Landed Cost", f"₹ {results.avg_freight_per_tonne_inr:,.0f} / t", f"Multiplier: {active_scn.freight_multiplier:.2f}x")
with col_cnt3:
    delay_sub = "Cape of Good Hope rerouting" if active_scn.shipping_delay_days > 0 else "Normal Suez & Gulf routing"
    st.metric("Active Maritime Shipping Delay", f"+{active_scn.shipping_delay_days} days", delay_sub)

container_table_rows = []
for c in results.containers:
    container_table_rows.append({
        "Shipment ID": c["id"],
        "Input Material": c["material"].capitalize(),
        "Origin Port": c["origin"],
        "Maritime Route": c["route"],
        "Carrier": c["carrier"],
        "Cargo Payload": f"{c['cargo_tonnes']:.1f} t",
        "Payload Utilisation": f"{c['payload_pct']:.1f}%",
        "Base ETA": f"{c['base_eta_days']} days",
        "Effective ETA": f"{c['effective_eta_days']} days",
        "Freight Landed Cost": f"₹ {c['freight_cost_per_tonne_inr']:,.0f} / t",
        "Transit Status": c["status"]
    })

st.dataframe(pd.DataFrame(container_table_rows), hide_index=True, use_container_width=True)

# 4. Critical Stock-Out Alert
stock_out_items = [r for r in results.inventory_summary if r["status"] == "Stock-out Risk"]
if stock_out_items:
    crit_names = ", ".join([r["material_name"] for r in stock_out_items])
    insight(
        f"<b>CRITICAL STOCK-OUT RISK DETECTED:</b> Inventory for <b>{crit_names}</b> will deplete before replacement vessels arrive "
        f"due to the active shipping delay of <b>+{active_scn.shipping_delay_days} days</b>. "
        "Recommend deploying <b>ACT-05 (Air-Freight Bridge)</b> or <b>ACT-09 (Production Re-sequencing)</b> immediately.",
        is_warning=True
    )
else:
    insight(
        f"Inventory buffer is stable. Worst runway margin is <b>{results.worst_runway_margin_days:+.1f} days</b> on <b>{results.worst_margin_material_name}</b>. "
        f"Container payload efficiency stands at <b>{results.avg_container_payload_pct:.1f}%</b>."
    )

explain_box(
    "Inventory & Container Formulations",
    "Days of Cover = Stock / Daily Usage; Effective LT = Supplier LT + Delay; Safety Stock = z × σ_daily × √Effective_LT; ROP = (Daily Usage × Effective_LT) + SS",
    "40ft Max Payload = 26.0 tonnes; Container Freight ₹/t = (2,172 × Multiplier × FX) / Cargo_tonnes."
)
