"""
Module 2: What-if Scenario Simulator
Team 11.59 · Xovate'26
"""

import streamlit as st
import pandas as pd
from engine.scenario import Scenario, get_default_presets, compute_todays_market_scenario
from engine.chain import run_all
from ui.components import page_header, kpi_strip, section, insight, explain_box, status_badge
from ui.charts import plot_tornado_sensitivity
from ui.theme import format_money_cr, format_pct

# 1. State & Calculations
presets = get_default_presets()
base_scn = presets["base_case"]
active_scn = st.session_state.get("active_scenario", base_scn)
saved_scns = st.session_state.get("saved_scenarios", [])

results = run_all(active_scn)
base_results = run_all(base_scn)

page_header("What-if Scenario Simulator", "Preset crisis calibrations, sensitivity tornado & multi-scenario comparison", "Module 2")
kpi_strip(results, base_results)

# 2. Preset Selection & Evidence Cards
section("⚡ Calibrated Crisis Presets", "Empirically sized from historical shocks in the dataset")

preset_cols = st.columns(5)
preset_keys = [
    ("base_case", "Base case", "FY25 Baseline"),
    ("red_sea_hormuz", "Red Sea / Hormuz", "Freight 2.7x, 18d delay"),
    ("metal_shock", "Metal Shock", "Base metals +30%+"),
    ("tariff_fx", "Tariff & FX", "FX 96.5, Tariff 10%"),
    ("demand_recession", "Demand Recession", "ACMA -11.7% volume")
]

for col, (k, title, sub) in zip(preset_cols, preset_keys):
    with col:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(sub)
            if st.button("Load Preset", key=f"btn_p_{k}", use_container_width=True):
                st.session_state.active_preset_name = presets[k].name
                st.session_state.active_scenario = presets[k]
                st.rerun()

# 3. Side-by-Side Comparison Matrix
section("📋 Multi-Scenario P&L Comparison Matrix", "Side-by-side benchmark of Baseline, Active, and Saved Scenarios")

comparison_list = [("Base Case (Handout)", base_results)]
if active_scn.name != "Base case":
    comparison_list.append((f"Active: {active_scn.name}", results))

for idx, s in enumerate(saved_scns):
    comparison_list.append((f"Saved #{idx+1}: {s.name}", run_all(s)))

comp_rows = []
metrics = [
    ("Revenue (₹ Cr)", lambda r: f"₹{r.revenue_cr:,.1f}"),
    ("Raw Material Spend (₹ Cr)", lambda r: f"₹{r.material_spend_cr:,.1f}"),
    ("Material Spend Δ vs Base", lambda r: f"{r.delta_material_cr:+.1f} Cr"),
    ("Ocean Freight Spend (₹ Cr)", lambda r: f"₹{r.ocean_freight_spend_cr:,.1f}"),
    ("Ocean Freight Δ vs Base", lambda r: f"{r.delta_freight_cr:+.1f} Cr"),
    ("OEM Pass-Through Recovery", lambda r: f"+₹{r.oem_recovery_cr:,.1f} Cr"),
    ("Working Capital Cash Gap", lambda r: f"₹{r.working_capital_gap_cr:,.1f} Cr"),
    ("Scenario EBITDA (₹ Cr)", lambda r: f"₹{r.ebitda_cr:,.1f}"),
    ("EBITDA Margin (%)", lambda r: f"{r.ebitda_margin_pct:.1f}%"),
    ("Net Profit / PAT (₹ Cr)", lambda r: f"₹{r.pat_cr:,.1f}"),
    ("Worst Days of Cover", lambda r: f"{r.worst_days_of_cover:.0f} days ({r.worst_material_name})"),
    ("Top Recommended Action", lambda r: r.top_action_title[:24] + "..."),
    ("Top Action Net Benefit", lambda r: f"+₹{r.top_action_net_benefit_cr:,.1f} Cr")
]

for label, func in metrics:
    row_dict = {"Financial & Operating Metric": label}
    for scn_label, res_obj in comparison_list:
        row_dict[scn_label] = func(res_obj)
    comp_rows.append(row_dict)

st.dataframe(pd.DataFrame(comp_rows), hide_index=True, use_container_width=True)

# 4. Tornado Sensitivity Analysis
section("🌪️ Tornado Sensitivity Chart: What Hurts EBITDA Most?", "Independent univariate stress testing from Base Case")

@st.cache_data
def compute_tornado_data() -> list[dict]:
    factors = [
        ("Copper Price Shock (-15% vs +35%)", {"copper": -15.0}, {"copper": 35.0}, 1.0, 84.56, 50.0, 0.0),
        ("Steel HR Coil Shock (-10% vs +30%)", {"steel_hr": -10.0}, {"steel_hr": 30.0}, 1.0, 84.56, 50.0, 0.0),
        ("Aluminium Shock (-10% vs +30%)", {"aluminium": -10.0}, {"aluminium": 30.0}, 1.0, 84.56, 50.0, 0.0),
        ("Ocean Freight Multiplier (0.8x vs 2.73x)", {}, {}, 0.8, 84.56, 50.0, 0.0), # high freight = adverse
        ("USD/INR Depreciation (82.0 vs 96.0)", {}, {}, 1.0, 82.0, 50.0, 0.0),       # high FX = adverse
        ("OEM Cost Pass-Through (75% vs 25%)", {"copper": 15, "steel_hr": 15}, {"copper": 15, "steel_hr": 15}, 1.0, 84.56, 75.0, 0.0),
        ("Vehicle Demand Volume (-12% vs +5%)", {}, {}, 1.0, 84.56, 50.0, -12.0)
    ]

    tornado_rows = []
    base_res = run_all(Scenario())
    b_val = base_res.ebitda_cr

    # Factor 1: Copper
    scn_low = run_all(Scenario(price_shock_pct={"copper": 35.0}))
    scn_high = run_all(Scenario(price_shock_pct={"copper": -15.0}))
    tornado_rows.append({"factor": "Copper Price (-15% vs +35%)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    # Factor 2: Steel HR
    scn_low = run_all(Scenario(price_shock_pct={"steel_hr": 30.0}))
    scn_high = run_all(Scenario(price_shock_pct={"steel_hr": -10.0}))
    tornado_rows.append({"factor": "Steel HR Coil (-10% vs +30%)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    # Factor 3: Aluminium
    scn_low = run_all(Scenario(price_shock_pct={"aluminium": 30.0}))
    scn_high = run_all(Scenario(price_shock_pct={"aluminium": -10.0}))
    tornado_rows.append({"factor": "Aluminium LME (-10% vs +30%)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    # Factor 4: Ocean Freight
    scn_low = run_all(Scenario(freight_multiplier=2.73))
    scn_high = run_all(Scenario(freight_multiplier=0.8))
    tornado_rows.append({"factor": "Ocean Freight (0.8x vs 2.73x)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    # Factor 5: FX
    scn_low = run_all(Scenario(fx_inr_usd=96.0))
    scn_high = run_all(Scenario(fx_inr_usd=82.0))
    tornado_rows.append({"factor": "USD/INR Forex (82.0 vs 96.0)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    # Factor 6: OEM Pass-Through
    scn_low = run_all(Scenario(price_shock_pct={"copper": 15, "steel_hr": 15, "aluminium": 15}, oem_pass_through_pct=25.0))
    scn_high = run_all(Scenario(price_shock_pct={"copper": 15, "steel_hr": 15, "aluminium": 15}, oem_pass_through_pct=75.0))
    tornado_rows.append({"factor": "OEM Pass-Through (25% vs 75%)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    # Factor 7: Demand
    scn_low = run_all(Scenario(demand_volume_pct=-12.0))
    scn_high = run_all(Scenario(demand_volume_pct=5.0))
    tornado_rows.append({"factor": "Vehicle Demand (-12% vs +5%)", "low_ebitda": scn_low.ebitda_cr, "high_ebitda": scn_high.ebitda_cr, "base_ebitda": b_val})

    return tornado_rows

tornado_data = compute_tornado_data()
fig_tornado = plot_tornado_sensitivity(tornado_data)
st.plotly_chart(fig_tornado, use_container_width=True)

insight(
    "The <b>Tornado Sensitivity Analysis</b> clearly reveals that <b>Steel HR & CR Coils</b> and <b>Aluminium</b> "
    "wield the largest single-factor swing on operating profit due to their combined 72% spend share. "
    "Furthermore, negotiating OEM pass-through from 50% to 75% recaptures over <b>₹30 Cr</b> of margin under heavy shock."
)

explain_box(
    "Scenario Simulation & Tornado Sensitivities",
    "Univariate stress tests isolate one shock variable at a time against Baseline EBITDA (₹297.7 Cr)",
    "Calibrated parameters: Steel HR (₹342 Cr spend), Aluminium (₹269 Cr spend), Red Sea Freight Multiplier (2.73x from Jul 2024 peak)."
)
