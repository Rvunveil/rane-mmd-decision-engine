"""
Assumptions, Data Trace, Formula Sheet & About Team 11.59
Team 11.59 · Xovate'26 Management Hackathon
"""

import os
import streamlit as st
import pandas as pd
import yaml
from engine.data_loader import clean_container_freight_data
from ui.components import page_header, section, explain_box, data_badge
from ui.charts import plot_freight_redating_trace

page_header("Assumptions, Data Trace & About", "Complete data lineage, deliberate fixes, formula sheet & institutional credits", "Governance")

tab_trace, tab_assumptions, tab_formulas, tab_about = st.tabs([
    "🔍 Data Trace & Judgement Fixes",
    "⚙️ Model Assumptions & Parameters",
    "📐 Official Formula Sheet",
    "👥 About Team 11.59 & Credits"
])

# ==============================================================================
# TAB 1: DATA TRACE & DELIBERATE DATA-JUDGEMENT FIXES
# ==============================================================================
with tab_trace:
    section("🚢 Deliberate Data-Judgement Fix: Container Freight Weekly Re-Dating", "Correcting spreadsheet error where 165 weekly values were labelled as consecutive days")
    
    st.markdown(
        """
        **The Problem in Raw Data:**  
        In `Weekly Container freight rate index worldwide.xlsx`, 165 observations were erroneously labelled with consecutive daily dates from **12 Jan 2023 to 25 Jun 2023**.  
        However, the file's own internal text description explicitly stated:
        > *"Container freight rates oscillated dramatically between January 2023 and March 2026. Freight rates slumped to their lowest level on the 26th of October 2023 ($1,342)... hitting over $5,900 in July 2024... and stood at $2,172 on March 19, 2026."*
        
        **Team 11.59 Analytical Fix:**  
        We re-dated the 165 points as a **weekly series ending on 19 March 2026** (7-day intervals backwards).  
        Notice how all key anchors now match the descriptive reality exactly:
        - **October 2023 Low:** $1,342 (Points 42-45 fall in late October 2023).
        - **July 2024 Red Sea Peak:** $5,937 (Point 79 falls in mid-July 2024).
        - **March 19, 2026 Baseline:** $2,172 (Matches the official handout baseline figure).
        """
    )

    raw_freight, fixed_freight = clean_container_freight_data()
    fig_trace = plot_freight_redating_trace(raw_freight, fixed_freight)
    st.plotly_chart(fig_trace, use_container_width=True)

    st.markdown("---")
    
    section("📋 Comprehensive Data Quality Audit Matrix", "Audit findings and engineering transformations across all 12 raw files")
    
    trace_matrix = [
        {
            "Dataset File": "Weekly Container freight rate...xlsx",
            "Observed Data Issue": "Consecutive days Jan-Jun 2023 despite description citing Jan 2023 - Mar 2026",
            "Team 11.59 Engineering Fix": "Weekly re-dating backwards from 19 Mar 2026; validated Oct 2023 low ($1342) and Jul 2024 peak ($5937)",
            "Model Impact": "Accurate Red Sea freight multiplier (2.73x) and baseline ocean freight ($2,172)"
        },
        {
            "Dataset File": "Forex Exchange Rate (inr - usd).xlsx",
            "Observed Data Issue": "Duplicate dates, ~49 non-numeric strings ('ND', '-'), irregular daily gaps",
            "Team 11.59 Engineering Fix": "Coerced to numeric, deduplicated by date, chronological sort, monthly resampled",
            "Model Impact": "Accurate FY25 baseline average (84.56) and latest currency stress (94.60)"
        },
        {
            "Dataset File": "Aluminium Price.xlsx",
            "Observed Data Issue": "Horizontal 5-year wide matrix blocks (2014-2026) with reversed months (Dec down to Jan)",
            "Team 11.59 Engineering Fix": "Unwrapped wide matrix into tidy monthly chronological series using LME cash-settlement USD/t",
            "Model Impact": "Clean 155-month continuous series for AutoARIMA/AutoETS forecasting"
        },
        {
            "Dataset File": "Steel_Price_Dataset_2021-2026.xlsx",
            "Observed Data Issue": "Ministry of Steel HRC and CRC series; contains data-quality flags and indicative notes",
            "Team 11.59 Engineering Fix": "Preserved domestic INR/t without FX distortion; surfaced data flags in tool",
            "Model Impact": "Prevents catastrophic double-FX conversion on domestic Indian steel coils"
        },
        {
            "Dataset File": "Resin Price Dataset...xlsx",
            "Observed Data Issue": "Only 17 irregular points with large gaps; ±40% volatility swings",
            "Team 11.59 Engineering Fix": "Multiplied USD/kg × 1000 to USD/t; deployed robust median naive with empirical confidence bounds",
            "Model Impact": "Labelled as 'TOO SHORT TO FORECAST' to prevent ARIMA overfitting"
        },
        {
            "Dataset File": "Natural Rubber Yearly Trends...xlsx",
            "Observed Data Issue": "Annual Kottayam RSS-4 prices (2005-2025) in ₹/100kg; footer rows contain averages",
            "Team 11.59 Engineering Fix": "Filtered footer rows, converted ₹/100kg × 10 to ₹/t; damped annual trend with monthly interpolation",
            "Model Impact": "Labelled as 'ANNUAL SERIES'; aligned unit basis to ₹/t"
        },
        {
            "Dataset File": "Rane financials (Statista 2021-2025)",
            "Observed Data Issue": "Statista figures (FY25 Rev ₹3,863 Cr, PAT ₹107.5 Cr) contradict official handout (₹3,421 Cr, ₹37.6 Cr)",
            "Team 11.59 Engineering Fix": "Handout baseline strictly governs P&L simulation; Statista retained as historical trend context",
            "Model Impact": "100% mathematical fidelity to hackathon handout and acceptance tests"
        }
    ]
    st.dataframe(pd.DataFrame(trace_matrix), hide_index=True, use_container_width=True)

# ==============================================================================
# TAB 2: MODEL ASSUMPTIONS & PARAMETERS
# ==============================================================================
with tab_assumptions:
    section("⚙️ Transparent Assumption Ledger", "All parameters not present in raw datasets are explicitly documented, justified, and labelled")
    
    st.markdown(
        """
        The official hackathon dataset does not provide internal plant inventory balances, division bills-of-materials (BOM), 
        or corporate tax provisions. In strict accordance with the prompt, Team 11.59 established sensible, industry-standard 
        assumptions calibrated against auto-component manufacturing benchmarks.
        """
    )

    assumptions_list = [
        {"Parameter": "Tax Rate", "Value": "25.17%", "Source Tag": "TEAM ASSUMPTION", "Rationale": "Corporate tax rate in India under Section 115BAA (22% + 10% surcharge + 4% cess)."},
        {"Parameter": "Fixed D&A + Interest", "Value": "₹ 247.46 Cr", "Source Tag": "HANDOUT DERIVED", "Rationale": "EBITDA (₹297.7 Cr) - PBT (₹37.6 / (1 - 0.2517) = ₹50.24 Cr) = ₹247.46 Cr."},
        {"Parameter": "Contribution Margin", "Value": "28.0%", "Source Tag": "INDUSTRY BENCHMARK", "Rationale": "Tier-1 auto component average contribution margin on vehicle build volumes."},
        {"Parameter": "Working Capital Interest", "Value": "9.5% p.a.", "Source Tag": "INDUSTRY BENCHMARK", "Rationale": "Short-term bank borrowing rate for automotive working capital facilities."},
        {"Parameter": "Raw Material Spend Split", "Value": "Steels 50%, Al 22%, Cu 10%, Ni 6%, Resin 6%, Rubber 6%", "Source Tag": "TEAM ASSUMPTION", "Rationale": "Reflects Rane's product lines: Steering linkages & valves (steel/nickel), light-metal castings (Al), friction/brake pads (resin/rubber/copper)."},
        {"Parameter": "Division Mix", "Value": "Steering 42%, Castings 28%, Friction 16%, Valves 14%", "Source Tag": "TEAM ASSUMPTION", "Rationale": "Calibrated against Rane Group operating divisions in India and Mexico."},
        {"Parameter": "Safety Stock Service Level", "Value": "95.0% (z = 1.65)", "Source Tag": "OPERATIONS STANDARD", "Rationale": "Target stock availability for safety-critical automotive parts."},
        {"Parameter": "Container Max Payload", "Value": "26.0 tonnes / 40ft", "Source Tag": "LOGISTICS STANDARD", "Rationale": "Standard payload limit for dry 40ft high-cube ocean containers."}
    ]
    st.dataframe(pd.DataFrame(assumptions_list), hide_index=True, use_container_width=True)

# ==============================================================================
# TAB 3: OFFICIAL FORMULA SHEET
# ==============================================================================
with tab_formulas:
    section("📐 Mathematical Formulations Reference", "Exact engine equations governing recalculation across all modules")

    st.markdown(
        r"""
        ### 1. Landed Cost per Tonne
        $$\text{Landed}_i = \text{BasePrice}_i \times (1 + \text{Shock}_i) \times \left(\frac{\text{FX}_{\text{scn}}}{\text{FX}_{\text{base}}}\right)^{\mathbb{I}_{\text{USD}}} \times (1 + \text{Duty}_i + \text{Tariff}) + \text{Freight}_i \times \text{Multiplier} + \text{Handling}_i$$
        
        ### 2. Calibrated Material Spend & Gross Shock
        $$\text{Tonnes}_i = \frac{\text{BaseSpend}_i \times 10^7}{\text{BaseMaterialCost}_i}$$
        $$\Delta \text{Material} = \sum_{i} \left[ \text{Tonnes}_i \times (1 + \text{Demand}\%) \times \text{ScenarioMaterialCost}_i \right] - \text{BaseSpend} \times (1 + \text{Demand}\%)$$

        ### 3. Ocean Freight Delta
        $$\Delta \text{Freight} = \text{BaseFreight} \times \left( \text{FreightMultiplier} \times \frac{\text{FX}_{\text{scn}}}{\text{FX}_{\text{base}}} - 1 \right) \times (1 + \text{Demand}\%)$$

        ### 4. OEM Pass-Through Recovery & Cash Gap
        $$\text{Recovery} = \text{PassThrough}\% \times (\Delta \text{Material} + \Delta \text{Freight})$$
        $$\text{Working Capital Cash Gap} = \text{Recovery} \times \frac{\text{RecoveryLagDays}}{365}$$

        ### 5. Operating Profit (EBITDA) & Net Profit (PAT)
        $$\text{EBITDA}_{\text{scn}} = \text{BaseEBITDA} - \Delta \text{Material} - \Delta \text{Freight} + \text{Recovery} + (\Delta \text{Revenue} \times \text{ContributionMargin})$$
        $$\text{PBT} = \text{EBITDA}_{\text{scn}} - \text{Fixed D\&A / Interest (₹247.46 Cr)}$$
        $$\text{PAT} = \begin{cases} \text{PBT} \times (1 - 0.2517) & \text{if } \text{PBT} > 0 \\ \text{PBT} & \text{if } \text{PBT} \le 0 \end{cases}$$

        ### 6. Inventory Runway & Reorder Point (ROP)
        $$\text{Daily Usage} = \frac{\text{Annual Tonnes}}{365}, \quad \text{Effective LT} = \text{Supplier LT} + \text{Shipping Delay}$$
        $$\text{Safety Stock} = z \times \sigma_{\text{daily}} \times \sqrt{\text{Effective LT}}, \quad \text{ROP} = (\text{Daily Usage} \times \text{Effective LT}) + \text{Safety Stock}$$
        $$\text{Status} = \begin{cases} \text{RED (Stock-out Risk)} & \text{if Days of Cover} < \text{Effective LT} \\ \text{AMBER (Watch/Reorder)} & \text{if Stock} \le \text{ROP} \\ \text{GREEN (Safe)} & \text{otherwise} \end{cases}$$
        """
    )

# ==============================================================================
# TAB 4: ABOUT TEAM 11.59 & CREDITS
# ==============================================================================
with tab_about:
    section("👥 Team 11.59 Profile", "Built for Xovate'26 Management Hackathon")
    
    st.markdown(
        """
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #0284C7; text-transform: uppercase;">Xovate'26 Management Hackathon</div>
            <h3 style="margin: 0.25rem 0 0 0; color: #0F172A;">Rane (Madras) MMD Decision Engine</h3>
            <div style="font-size: 0.85rem; color: #64748B; font-style: italic; margin-bottom: 0.5rem;">"See the shock. Measure it. Decide."</div>
            <p style="color: #475569; margin: 0; font-weight: 600;">Team 11.59 · Xavier Institute of Management & Entrepreneurship (XIME Chennai)</p>
            <div style="display: flex; gap: 2rem; margin-top: 1rem; flex-wrap: wrap;">
                <div>
                    <b>Vikram T</b><br>
                    <span style="font-size: 0.8rem; color: #64748B;">Lead Systems Architect & Financial Modelling</span>
                </div>
                <div>
                    <b>Sayoni Dan</b><br>
                    <span style="font-size: 0.8rem; color: #64748B;">Product Strategy & Supply Chain Analytics</span>
                </div>
                <div>
                    <b>Trisha Pal</b><br>
                    <span style="font-size: 0.8rem; color: #64748B;">Decision Matrix & UX Engineering</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section("📚 Open-Source Reference Architecture & Repositories", "Architectural patterns adapted and credited in accordance with Section 10")
    
    credits = [
        ("Nixtla statsforecast & utilsforecast", "https://github.com/Nixtla/statsforecast", "Core automated time-series forecasting (AutoARIMA, AutoETS, AutoTheta)."),
        ("streamlit/demos (forecasting-app)", "https://github.com/streamlit/demos", "Frozen dataclass scenario state, session management, and UI architecture."),
        ("netback-calculator & pvis", "https://github.com/Arthur0349/netback-calculator", "Landed-cost waterfall decomposition, driver-based P&L simulation, and Plotly bridges."),
        ("inventory-stochastic & mrp-lot-sizing", "https://github.com/samirsaci/inventory-stochastic", "Stochastic safety stock, lead-time variance, and service-level calculations."),
        ("COIN-OR PuLP", "https://github.com/coin-or/pulp", "Linear integer programming for action portfolio optimization under capital limits.")
    ]

    for name, url, desc in credits:
        st.markdown(f"- **[{name}]({url})**: {desc}")
