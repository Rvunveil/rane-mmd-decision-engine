# Rane (Madras) MMD Decision Engine · Team 11:59
**Event:** Xovate'26 Management Hackathon  
**Tagline:** *"See the shock. Measure it. Decide."*  
**Team 11:59:** Vikram T · Sayoni Dan · Trisha Pal  
**Institute:** Xavier Institute of Management & Entrepreneurship (XIME), Chennai  

---

## Executive Summary

Rane (Madras) Limited manufactures safety-critical automotive systems (steering linkages and gears, brake friction materials, engine valves, light-metal castings) across 17 plants in India and Mexico for global vehicle OEMs. Operating in a thin-margin environment (8.7% EBITDA margin), raw materials constitute the company's largest single cost driver (₹1,223 Cr annual spend).

A global supply chain disruption—such as the Red Sea/Bab el-Mandeb chokepoint collapse, a 4x container freight surge, or a 10% unhedged commodity price shock—threatens to inflict over **₹60 Cr in unrecovered cost erosion**, completely wiping out annual net profit (PAT ₹37.6 Cr).

The **MMD Decision Engine** is an autonomous enterprise cockpit developed for Rane's Materials Management Department (MMD). It unifies time-series commodity forecasting, driver-based P&L recalculation, dynamic inventory runway tracking, and a prescriptive action matrix with mathematical linear integer optimization to protect operating margins.

---

## One-Page Mathematical Formula Sheet

All calculations are executed in a pure-Python driver engine (`engine/chain.py`) ensuring zero tracebacks and instantaneous sub-second recalculation:

### 1. Landed Cost per Tonne
$$\text{Landed}_i = \text{BasePrice}_i \times (1 + \text{Shock}_i) \times \left(\frac{\text{FX}_{\text{scn}}}{\text{FX}_{\text{base}}}\right)^{\mathbb{I}_{\text{USD}}} \times (1 + \text{Duty}_i + \text{Tariff}) + \text{Freight}_i \times \text{Multiplier} + \text{Handling}_i$$
*Note: Steel HR, Steel CR, and Kottayam Rubber are domestic inputs quoted in ₹/t and are not subjected to FX conversion.*

### 2. Material Spend Delta
$$\Delta \text{Material} = \sum_{i=1}^7 \left[ \text{Tonnes}_i \times (1 + \text{Demand}\%) \times \text{ScenarioMaterialCost}_i \right] - \text{BaseSpend} \times (1 + \text{Demand}\%)$$

### 3. Inbound Ocean Freight Delta
$$\Delta \text{Freight} = \text{BaseOceanFreight (₹25 Cr)} \times \left( \text{FreightMultiplier} \times \frac{\text{FX}_{\text{scn}}}{\text{FX}_{\text{base}}} - 1 \right) \times (1 + \text{Demand}\%)$$

### 4. OEM Pass-Through Recovery & Working Capital Cash Gap
$$\text{Recovery} = \text{PassThrough}\% \times (\Delta \text{Material} + \Delta \text{Freight})$$
$$\text{Working Capital Cash Gap} = \text{Recovery} \times \frac{\text{PassThroughLagDays (Default: 75 days)}}{365}$$

### 5. P&L Statement (EBITDA & PAT)
$$\text{Scenario EBITDA} = \text{Base EBITDA (₹297.7 Cr)} - \Delta \text{Material} - \Delta \text{Freight} + \text{Recovery} + (\Delta \text{Revenue} \times \text{ContributionMargin 28\%})$$
$$\text{PBT} = \text{Scenario EBITDA} - \text{Fixed D\&A / Interest (₹247.46 Cr)}$$
$$\text{PAT} = \begin{cases} \text{PBT} \times (1 - 0.2517) & \text{if } \text{PBT} > 0 \\ \text{PBT} & \text{if } \text{PBT} \le 0 \end{cases}$$

### 6. Inventory Runway & Reorder Point (ROP)
$$\text{Daily Usage} = \frac{\text{Calibrated Annual Tonnes}}{365}, \quad \text{Effective LT} = \text{Supplier LT} + \text{Shipping Delay}$$
$$\text{Safety Stock} = z \times \sigma_{\text{daily}} \times \sqrt{\text{Effective LT}}, \quad \text{ROP} = (\text{Daily Usage} \times \text{Effective LT}) + \text{Safety Stock}$$
$$\text{Status} = \begin{cases} \text{RED (Stock-out Risk)} & \text{if Days of Cover} < \text{Effective LT} \\ \text{AMBER (Watch / Reorder)} & \text{if Stock} \le \text{ROP} \\ \text{GREEN (Covered / Safe)} & \text{otherwise} \end{cases}$$

---

## System Architecture

```
mmd-decision-engine/
├── .streamlit/config.toml             # Bloomberg/SaaS theme configuration
├── app.py                             # Navigation root and shared state
├── pages/
│   ├── 0_Command_Centre.py            # Early Warning Shock Radar & Active Summary
│   ├── 1_Forecast.py                  # Module 1: statsforecast 3/6/12M projections with bands
│   ├── 2_Scenario_Simulator.py        # Module 2: Presets, side-by-side comparison & tornado chart
│   ├── 3_Profit_Chain.py              # Module 3: Landed cost/t, division mix & EBITDA/PAT waterfall
│   ├── 4_Containers_Inventory.py      # Module 4: 40ft container payloads & stock-out runway alerts
│   ├── 5_Action_Matrix.py             # Module 5: Re-ranking mitigation matrix, ripple & 0-1 optimizer
│   └── 6_Assumptions_Data_Trace_About.py # Data trace, assumptions ledger & team profile
├── engine/                            # Pure-Python mathematical and analytical engines
│   ├── data_loader.py                 # Data cleaning, unit conversions & re-dating
│   ├── scenario.py                    # Frozen Scenario dataclass & presets
│   ├── results.py                     # High-density typed Results dataclass
│   ├── forecast.py                    # statsforecast pool & empirical fallbacks
│   ├── signals.py                     # Chokepoints, GSCPI, Brent & Forex radar
│   ├── chain.py                       # P&L recalculation and division allocation
│   ├── inventory.py                   # Runway, safety stock, and container payloads
│   └── actions.py                     # Mitigation catalogue, ranking & 0-1 optimizer
├── ui/                                # Presentation tokens, Plotly charts, and styles
├── config/                            # Baseline, assumptions, presets, and actions YAMLs
├── data/                              # Raw, processed, and pre-computed fallback tables
├── tests/                             # Section 8 acceptance tests & Streamlit smoke tests
├── ASSUMPTIONS.md                     # Comprehensive assumption documentation
├── DATA_TRACE.md                      # Complete data lineage & reconciliation log
└── DEMO_SCRIPT.md                     # 15-minute presentation script & judge Q&A guide
```

---

## Quickstart & Local Execution

The application is completely self-contained and operates 100% offline without external API dependencies:

```bash
# 1. Clone the repository
git clone https://github.com/Team1159/mmd-decision-engine.git
cd mmd-decision-engine

# 2. Set up virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Execute the full test suite (Acceptance + Data Loaders + Streamlit Smoke)
pytest -v

# 4. Launch the Streamlit Application
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Reference Repositories & Credits (Section 10)

In accordance with hackathon instructions, key architectural patterns and open-source libraries were studied, adapted, and credited:

1. **Forecasting (Module 1):**
   - [Nixtla/statsforecast](https://github.com/Nixtla/statsforecast) — Core automated time-series forecasting engine (AutoETS, AutoARIMA, AutoTheta, prediction intervals).
   - [ParBproject/commodity-price-forecaster](https://github.com/ParBproject/commodity-price-forecaster) — Rolling-origin backtesting pattern and commodity calibration structure.

2. **Scenario Simulator (Module 2):**
   - [streamlit/demos (`forecasting-app`)](https://github.com/streamlit/demos) — Frozen dataclass scenario architecture, session state persistence, and slider grouping.
   - [kanzmajdalawi/supply-chain-Monte-Carlo](https://github.com/kanzmajdalawi/supply-chain-Monte-Carlo) — Supply chain parameter dataclasses and tornado sensitivity structure.
   - [sanoojcools/workforce-scenario-engine](https://github.com/sanoojcools/workforce-scenario-engine) — Driver-based scenario execution and sensitivity fanning.

3. **Profit Chain & Landed Cost (Module 3):**
   - [Arthur0349/netback-calculator](https://github.com/Arthur0349/netback-calculator) — Pure landed-cost calculation core and Plotly waterfall bridges.
   - [lorenzobosio/financial-analytics-dashboard](https://github.com/lorenzobosio/financial-analytics-dashboard) — Driver-based P&L simulation and EBIT bridge waterfalls.
   - [DavidMaco/pvis](https://github.com/DavidMaco/pvis) — FX pass-through, tariff scaling, and landed cost model.

4. **Containers & Inventory (Module 4):**
   - [samirsaci/inventory-stochastic](https://github.com/samirsaci/inventory-stochastic) — Stochastic safety stock sizing and lead-time variance simulation.
   - [kritikab01/mrp-lot-sizing-analyzer](https://github.com/kritikab01/mrp-lot-sizing-analyzer) — Bill of materials to inventory runway and reorder point alerts.

5. **Action Matrix (Module 5):**
   - [coin-or/pulp](https://github.com/coin-or/pulp) — Prescriptive action portfolio optimization under capital limits.
   - [brianwendr/decision-analytics-toolkit](https://github.com/brianwendr/decision-analytics-toolkit) — Multi-criteria decision ranking and sensitivity re-ranking.
   - [shuklasamyak1/supply-chain-command-center](https://github.com/shuklasamyak1/supply-chain-command-center) — Disruption penalty modeling and freight-shock mitigation.

6. **UI & Presentation Shell:**
   - [thed700/streamlit](https://github.com/thed700/streamlit) — Multipage layout, custom tokens, and KPI card architecture.
   - [datawithdon/supply-chain-dashboard](https://github.com/datawithdon/supply-chain-dashboard) — KPI strip design and supply chain visualization templates.
   - [paolocarner/fair-monte-carlo-risk-analysis](https://github.com/paolocarner/fair-monte-carlo-risk-analysis) — Preset management and clean test-first testing structure.
