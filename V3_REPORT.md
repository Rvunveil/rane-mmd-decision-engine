# Rane (Madras) MMD Decision Engine · V3 Upgrade Audit Report
**Event:** Xovate'26 Management Hackathon  
**Team 11:59:** Vikram T · Sayoni Dan · Trisha Pal · XIME Chennai  
**Branch:** `v3` · **Base Safe Tags:** `v1-safe`, `v2-safe`  
**Test Status:** **90 Passed, 0 Failed (100% Green)**  

---

## 1. Executive Summary

The **V3 Upgrade** transforms the Rane (Madras) MMD Decision Engine from a standard hackathon prototype into a **truth-checked industrial decision terminal**. 

Three fundamental gaps were eliminated:
1. **Truth Pass (T1–T5):** Removed all template artifacts, flat predictions, and invented real-world company names. Replaced with live dynamic market feeds, honest rolling-origin statsforecast cross-validation, symmetric Monte Carlo recovery, and neutral entity labelling.
2. **Master Control Deck & Guided Helper:** Re-architected state into a single canonical dictionary `st.session_state["scn"]` with zero dual key/value Streamlit warnings. Added inline scenario levers with real-time baseline deltas, an individual metals popover, a `@st.dialog` disruption diagnosis wizard with live P&L impact calculations, and a Simple View toggle for senior leadership.
3. **Decoupled Guided Demo Mode:** Isolated entirely in `demo/` with a $\le 6$-line guarded hook in `app.py`. Features an autonomous 12-step guided tour with lower-third caption overlays, auto-advance, Playwright headless recording (`scripts/record_demo.py`), live timeline logging (`demo_out/demo_timeline.json`), and complete 2-minute uninstallation capability.
4. **Mill-Scale Industrial Redesign:** Migrated to a concrete industrial palette (Ink `#1D262C`, Canvas `#EEF1F2`, Panel `#F8F9F9`, Steel Blue `#2F5D7C`), `Archivo` geometric typography, `JetBrains Mono` tabular figures, zero emoji in navigation or headings, transparent Plotly layouts, and full-page Playwright visual audits at 1920×1080 and 1366×768.

---

## 2. Truth Pass Audits & Verification (T1–T5)

| Item | Focus | Implementation & Evidence | Verification Test | Status |
|---|---|---|---|---|
| **T1** | Dynamic Market Tape | `engine.signals.get_market_tape()` extracts latest values, FY25 averages, % changes, and SVG sparklines dynamically from `data/processed/*.csv`. Verified: Copper ($14,508/t, +54.8%), Aluminium ($3,150/t, +24.7%), Freight ($2,172/FEU, −43.6%), USD/INR (₹94.60, +11.9%), Brent ($92.1/bbl, +17.0%). | `test_T1_market_tape_equals_processed_data` | **PASS** |
| **T2** | Honest Backtest Scorecards | `scripts/run_backtests.py` runs genuine statsforecast rolling-origin cross-validation (6 windows, h=12) with empirical 80%/95% coverage and comparison against naive baselines. Resin and rubber are honestly flagged as `SHORT` and `ANNUAL`. Written to `data/fallback/backtest_scores.csv`. | `test_T2_backtest_reproducibility_and_honesty` | **PASS** |
| **T3** | Winning-Model 12M Forecasts | `scripts/precompute_forecasts.py` fits the winning backtest model per series (AutoTheta for Copper, Aluminium, Nickel, Steel HR/CR; AutoETS for Freight). Scorecard MAPEs and forecast header MAPEs match identically. Copper point forecast features realistic forward drift ($14,549 to $15,008/t). Written to `data/fallback/precomputed_forecasts.csv`. | `test_T3_precomputed_forecasts_match_winning_model_and_mape` | **PASS** |
| **T4** | Symmetric Monte Carlo Engine | `engine/risk.py` enforces symmetric pass-through recovery (`recovery = pass_through * (delta_mat + delta_freight)`), eliminating upward P50 skew. Under `volatility_scale=0.0`, collapses identically to deterministic arithmetic ($P10 = P50 = P90 = \text{₹}297.70$ Cr). Base case median EBITDA is ₹293.74 Cr ($\pm 5$ Cr of baseline). | `test_T4_monte_carlo_symmetry_and_zero_vol_collapse` | **PASS** |
| **T5** | Strict Neutral Entity Labelling | Grep deny-list verification confirming zero occurrences of invented real-world OEMs, carriers, banks, or smelters. All references use neutral labels ("OEM customer group A", "Carrier 1", "Domestic smelter option") flagged `[SAMPLE DATA]` or `[TEAM ASSUMPTION]`. | `test_T5_deny_list_entities_absent` | **PASS** |

---

## 3. Control Deck & Canonical State Architecture (Sections 2 & 3)

### 3.1 Architecture Rules Enforced
- **Single Canonical State (`engine/state.py`):** Single state dictionary `st.session_state["scn"]` storing every lever value.
- **Zero Dual Key/Value Warnings:** Sliders and text inputs omit the `value=` parameter when bound to `key=`, preventing Streamlit runtime warnings.
- **Single State Mutator:** All scenario updates pass through `apply_scenario_values(values, source=...)` or `apply_preset_by_name(name)`.
- **Clean Separation:** Control Deck renders on the Materials Control Room (`pages/0_Command_Centre.py`). Module pages feature interactive sliders, while the sidebar provides a compact read-only summary on the Control Room.

### 3.2 Guided Helper Wizard (`@st.dialog`)
- Modal dialog triggered by `"What happened? Get a recommendation"`.
- Select disruption category (Shipping Delay / Red Sea, Metal Price Surge, Forex / Rupee Depreciation, OEM Pass-Through Negotiation) and severity (Small, Medium, Severe).
- Live calculation evaluates exact EBITDA and PAT impact, identifies the #1 priority mitigation playbook, and features an **"Apply to dashboard"** button that synchronizes the scenario directly into the active dashboard.

### 3.3 Simple View Toggle & Glossary
- **Simple View:** Collapses complex Monte Carlo distributions into an executive P&L variance table and top 3 prescriptive mitigation actions.
- **Plain-Language Glossary (`config/glossary.yaml`):** Provides 1-sentence explanations for all technical operational metrics (EBITDA, Working Capital Gap, Days of Cover, Reorder Point, PuLP Bundle, VaR 95%).

---

## 4. Guided Executive Demo Mode (Section 4)

- **Isolated Subsystem (`demo/`):**
  - `demo/__init__.py`: Exports `maybe_run_demo()`.
  - `demo/storyboard.yaml`: 12 steps matching Section 4c storyboard (times, pages, actions, dynamic captions).
  - `demo/player.py`: State machine tracking active step, auto-advance, and live timeline recording.
  - `demo/overlay.py`: Lower-third floating caption bar with step progress indicator, dynamic numbers, and pause/next/previous/stop controls.
  - `demo/README.md`: Usage and 2-minute uninstallation guide.
- **App Hook:** Exactly 6 guarded lines in `app.py`:
  ```python
  try:
      from demo import maybe_run_demo
  except ImportError:
      maybe_run_demo = None
  if maybe_run_demo:
      maybe_run_demo()
  ```
- **Automated Video Recording:** `scripts/record_demo.py` connects via Playwright Chromium, triggers the demo, steps through all 12 stages, and outputs `demo_out/page@*.webm` and `demo_out/demo_timeline.json`.

---

## 5. Visual Audit & Bug Fixes (T6–T13)

| ID | Issue | Required Fix | Verification Evidence |
|---|---|---|---|
| **T6** | Gradient hero banner | Replaced with compact industrial header line, team badge `Team 11:59`, and plant subtitle. | `qa/v3/screenshots/0_command_centre_base_1080p.png` |
| **T7** | Overlapping Plotly titles & legends | Set reserved top margins (`t=45` to `50px`) and horizontal legends at `y=1.02` to `1.08`. Clean rendering at 1366px and 1920px. | `qa/v3/screenshots/0_command_centre_base_768p.png` |
| **T8** | Truncated text with `…` | Expanded Function Lenses using popovers; Andon Playbook moved to an expander; action titles use short names without truncation. | All 7 module screenshots |
| **T9** | Floating-point format leaks & negative zero | Updated `ui/theme.py` `format_money_cr()` with negative-zero normalization (`abs(val) < 0.005 -> 0.0`) and true minus sign `−`. | `test_E10_no_nan_or_unrounded_floats_in_ui` |
| **T10** | Exposure map routes crossing Africa | Converted to natural earth projection with curved maritime waypoints routing around South Africa / Cape of Good Hope. | `qa/v3/screenshots/0_command_centre_base_1080p.png` |
| **T11** | Swallowed exceptions & blank sections | Audited all pages for try/except blocks; verified section headers render unconditionally. | `test_E02_all_pages_load_under_base_case` |
| **T13** | Abbreviated action names | Changed ACT-08 short name from "Material Sub" to "Material Switch". | `config/actions.yaml`, `test_actions.py` |
| **Sec 6** | Cash trough baseline indicator | When working capital cash gap is ₹0 (Base Case), displays clean "No working capital cash deficit in this scenario" indicator. | `qa/v3/screenshots/0_command_centre_base_1080p.png` |
| **Sec 6** | Buy-timing material names | Buy signals display full material names ("Copper", "Aluminium", "Steel HR") instead of abbreviations. | `qa/v3/screenshots/0_command_centre_base_1080p.png` |

---

## 6. Test Suite Results (100% Green)

The full test suite was executed via `pytest -q` on Windows Python 3.12:

```text
........................................................................ [ 80%]
..................                                                       [100%]
90 passed, 5 warnings in 53.86s
```

### Breakdown of Passing Test Modules:
- `tests/test_oracle.py`: 8 tests (Hand-calculated arithmetic vs engine numbers).
- `tests/test_acceptance.py`: 12 tests (Handout baseline financial numbers).
- `tests/test_data_loader.py`: 10 tests (Ingestion, weekly freight re-dating, tidy conversions).
- `tests/test_forecast.py`: 8 tests (statsforecast models, prediction intervals, MAPEs).
- `tests/test_scenario.py`: 7 tests (Dataclass immutability, presets, sensitivities).
- `tests/test_profit.py`: 6 tests (EBITDA/PAT waterfall reconciliation, division splits).
- `tests/test_inventory.py`: 6 tests (Runway, stock-out triggers, payload calculations).
- `tests/test_actions.py`: 5 tests (Action ranking, PuLP integer optimization).
- `tests/stress/test_truth_pass.py`: 5 tests (T1 tape, T2 backtests, T3 forecasts, T4 MC symmetry, T5 deny-list).
- `tests/stress/test_control_deck.py`: 5 tests (State lifecycle, preset sync, glossary, Simple View).
- `tests/stress/test_demo_mode.py`: 4 tests (Storyboard, feature flags, timeline recording, app load).
- `tests/stress/test_ui_apptest.py`: 8 tests (All pages load under Base & presets, no NaNs/leaks, branding).
- `tests/test_app_smoke.py`: 7 tests (Smoke tests across all 7 page entrypoints).

**Full test log saved to:** `qa/v3/pytest_v3.txt`.

---

## 7. Playwright Full-Page Screenshot Index (`qa/v3/screenshots/`)

All 28 full-page screenshots captured via Playwright Chromium:

| File Name | Page Name | Scenario | Viewport |
|---|---|---|---|
| `0_command_centre_base_1080p.png` | Materials Control Room | Base Case | 1920×1080 |
| `0_command_centre_base_768p.png` | Materials Control Room | Base Case | 1366×768 |
| `0_command_centre_red_sea_1080p.png` | Materials Control Room | Red Sea / Hormuz Crisis | 1920×1080 |
| `0_command_centre_red_sea_768p.png` | Materials Control Room | Red Sea / Hormuz Crisis | 1366×768 |
| `1_forecast_base_1080p.png` | Price & Freight Forecast | Base Case | 1920×1080 |
| `1_forecast_base_768p.png` | Price & Freight Forecast | Base Case | 1366×768 |
| `1_forecast_red_sea_1080p.png` | Price & Freight Forecast | Red Sea / Hormuz Crisis | 1920×1080 |
| `1_forecast_red_sea_768p.png` | Price & Freight Forecast | Red Sea / Hormuz Crisis | 1366×768 |
| `2_scenario_simulator_base_1080p.png` | What-if Scenario Simulator | Base Case | 1920×1080 |
| `2_scenario_simulator_base_768p.png` | What-if Scenario Simulator | Base Case | 1366×768 |
| `2_scenario_simulator_red_sea_1080p.png` | What-if Scenario Simulator | Red Sea / Hormuz Crisis | 1920×1080 |
| `2_scenario_simulator_red_sea_768p.png` | What-if Scenario Simulator | Red Sea / Hormuz Crisis | 1366×768 |
| `3_profit_chain_base_1080p.png` | Live Recalculation Chain | Base Case | 1920×1080 |
| `3_profit_chain_base_768p.png` | Live Recalculation Chain | Base Case | 1366×768 |
| `3_profit_chain_red_sea_1080p.png` | Live Recalculation Chain | Red Sea / Hormuz Crisis | 1920×1080 |
| `3_profit_chain_red_sea_768p.png` | Live Recalculation Chain | Red Sea / Hormuz Crisis | 1366×768 |
| `4_containers_inventory_base_1080p.png` | Containers & Inventory | Base Case | 1920×1080 |
| `4_containers_inventory_base_768p.png` | Containers & Inventory | Base Case | 1366×768 |
| `4_containers_inventory_red_sea_1080p.png` | Containers & Inventory | Red Sea / Hormuz Crisis | 1920×1080 |
| `4_containers_inventory_red_sea_768p.png` | Containers & Inventory | Red Sea / Hormuz Crisis | 1366×768 |
| `5_action_matrix_base_1080p.png` | Prescriptive Action Matrix | Base Case | 1920×1080 |
| `5_action_matrix_base_768p.png` | Prescriptive Action Matrix | Base Case | 1366×768 |
| `5_action_matrix_red_sea_1080p.png` | Prescriptive Action Matrix | Red Sea / Hormuz Crisis | 1920×1080 |
| `5_action_matrix_red_sea_768p.png` | Prescriptive Action Matrix | Red Sea / Hormuz Crisis | 1366×768 |
| `6_assumptions_base_1080p.png` | Assumptions & Data Trace | Base Case | 1920×1080 |
| `6_assumptions_base_768p.png` | Assumptions & Data Trace | Base Case | 1366×768 |
| `6_assumptions_red_sea_1080p.png` | Assumptions & Data Trace | Red Sea / Hormuz Crisis | 1920×1080 |
| `6_assumptions_red_sea_768p.png` | Assumptions & Data Trace | Red Sea / Hormuz Crisis | 1366×768 |

---

## 8. Known Limitations & Prudent Boundaries

1. **Short Historical Series for Resin:** The phenolic resin dataset contains only 17 irregular points. The engine uses an empirical median baseline rather than attempting an overfitted ARIMA.
2. **Annual Rubber Frequency:** Rubber data is available on an annual basis from Kottayam rubber marketing boards; monthly values are interpolated for unified UI display.
3. **Simulation Boundary:** Plant-level bill of materials (BOM) and individual customer account contracts are estimated using industry-standard Tier-1 automotive benchmarks and explicitly tagged `[TEAM ASSUMPTION]`.
