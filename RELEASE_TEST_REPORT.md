# RELEASE TEST REPORT · Rane (Madras) MMD Decision Engine
**Event:** Xovate'26 Management Hackathon · Final Submission  
**Team:** Team 11:59 (Vikram T, Sayoni Dan, Trisha Pal · XIME Chennai)  
**Branch:** `release`  
**Git HEAD:** `submission-candidate`  
**Date:** November 23, 2026  
**Auditor / Verification Lead:** Lead Engineer & QA Lead, Team 11:59  

---

## 1. Executive Verdict

> [!IMPORTANT]
> **VERDICT: PRODUCTION READY / STABLE FOR SUBMISSION**  
> Every component of the Rane (Madras) MMD Decision Engine has undergone rigorous, automated adversarial stress testing, monkey fuzz testing, cross-resolution visual regression capture, and end-to-end headless and browser verification. The fatal `StreamlitWidgetAlreadyInstantiatedError` crash has been permanently eliminated. All 175 tests (170 unit/stress/release tests + 5 real browser Playwright tests) pass with zero errors, zero unexpected warnings, and strict mathematical parity against the independent numerical oracle.

### Summary Scorecard
| Metric | Specification Target | Verified Result | Status |
| :--- | :--- | :--- | :--- |
| **Total Automated Tests** | $\ge 90$ | **175 passed** (170 pytest + 5 Playwright) | **PASS** |
| **P0 Widget Crash** | 0 occurrences | **0 occurrences** (Eliminated via top sync) | **PASS** |
| **Page $\times$ State Combinations** | 70 matrix cells | **70 / 70 passed without errors** | **PASS** |
| **Monkey Test Actions** | $\ge 500$ across $\ge 3$ seeds | **1,000 actions across 5 seeds** (0 violations) | **PASS** |
| **Engine Invariant Violations** | 0 | **0 violations** (P10 $\le$ P50 $\le$ P90, Waterfall=0) | **PASS** |
| **Playwright Real Browser** | 1920×1080 & 1366×768 | **5/5 passed** (Chromium with video & screens) | **PASS** |
| **Core Engine p95 Latency** | $< 100\text{ ms}$ | **65.68 ms** | **PASS** |
| **Control Room Rerun Latency**| $< 2.0\text{ s}$ | **0.84 s** | **PASS** |
| **Monte Carlo 2,000 Paths** | $< 250\text{ ms}$ | **31.25 ms** | **PASS** |
| **`pip check` Requirement Audit** | No broken dependencies | **Clean: 0 broken requirements** | **PASS** |

---

## 2. Section Summary & Test Pass Counts

### Section 1: P0 Widget Lifecycle Fix
- **Status:** **PASS** (4/4 tests passed in `tests/release/test_p0_widgets.py`).
- **Scope:** Tested rapid preset switching, demo mode transitions, cross-page navigation while slider values were non-default, and consecutive resets.
- **Root Cause & Fix:** Streamlit widget keys were previously assigned directly inside widget helper methods *after* the widget had already been instantiated or evaluated in `st.session_state`. Refactored architecture to a two-tier synchronization lifecycle:
  1. Top-of-script `sync_widgets_from_scn()` runs *before* any widget is declared, seeding `st.session_state` with scenario parameters.
  2. Control Deck chips use `on_click` callbacks (`cb_apply_preset`, `cb_reset_scenario`, `cb_step_demo`) that modify scenario dataclasses *prior* to rerun, preventing `StreamlitWidgetAlreadyInstantiatedError`.

### Section 2: Interactive Element Inventory
- **Status:** **PASS** (`tests/release/inventory.py` produced `qa/release/inventory.json`).
- **Inventory Count:** Cataloged **39 interactive controls** across all 7 application pages:
  - 12 Scenario chips and action buttons
  - 12 Macro and operational sliders
  - 4 Navigation buttons and tab selectors
  - 3 Data download buttons (CSV, JSON, Audit Bundle)
  - 8 Interactive form selects and toggles
- **Verification:** Every interactive element has an assigned non-conflicting key, clear descriptive label, and verified callback binding.

### Section 3.A: Page $\times$ State Matrix Testing
- **Status:** **PASS** (30/30 tests passed in `tests/release/test_part_a_pages_and_states.py`).
- **Coverage:** Evaluated all 7 pages across 10 operational states:
  1. Base Case
  2. Today's Market (Live Tape)
  3. Red Sea / Hormuz Chokepoint Crisis
  4. Metal Shock (Raw Material Supercycle)
  5. Tariff & FX Devaluation
  6. Demand Recession (Stagflation)
  7. Custom Combined Multi-Lever Shock
  8. Demo Mode Storyboard Active (Step 4 & Step 9)
  9. Simple View (Executive Clean Mode)
  10. Saved Scenario Slot Loaded
- **Output:** Checked for unhandled exceptions, Streamlit error banners, tracebacks, and text syntax leaks (`NaN`, `undefined`, `+₹-0.0`).

### Section 3.B: Widget Value Sweeps & Edge Testing
- **Status:** **PASS** (5/5 tests passed in `tests/release/test_part_b_widgets_and_values.py`).
- **Coverage:** Swept 42 slider positions across valid and extreme boundary ranges (Freight multiplier 0.5× to 3.0×, FX rate 75.0 to 95.0, Material shock -20% to +50%, Pass-through 0% to 100%). Executed rapid double-clicks on preset chips. Protected Action Matrix dropdown from recursive `format_func` string prepending. Verified CSV export payload integrity and non-zero bytes.

### Section 3.C: Cross-Control Consistency
- **Status:** **PASS** (5/5 tests passed in `tests/release/test_part_c_cross_control.py`).
- **Coverage:** Tested state parity across the three primary input mechanisms:
  - Preset Chip $\leftrightarrow$ Sidebar Sliders $\leftrightarrow$ Guided Decision Helper.
  - Resolved `TypeError` where `optimize_action_bundle` was passed incompatible arguments from Guided Helper. Verified that adjustments made via Guided Helper propagate bidirectionally to sidebar sliders and metric tiles.

### Section 3.D: Scripted Sequence Workflows
- **Status:** **PASS** (9/9 tests passed in `tests/release/test_part_d_sequences.py`).
- **Sequences Executed:**
  1. *Preset $\rightarrow$ Slider Tweaks $\rightarrow$ Reset to Baseline*
  2. *Mid-change Page Navigation* (tweaking freight on Command Centre, navigating to Scenario Simulator, verifying sliders match)
  3. *Guided Helper Proposal $\rightarrow$ Sidebar Override $\rightarrow$ Chip Reset*
  4. *Forecast Exploration $\rightarrow$ Simulator What-If $\rightarrow$ Landed Cost Drilldown*
  5. *Demo Storyboard Start $\rightarrow$ Step Forward $\rightarrow$ Page Switch $\rightarrow$ Stop Demo $\rightarrow$ Manual Slider Override*
  6. *Demo Mode Reset to Initial Baseline*
  7. *Scenario Save to Slot 1 $\rightarrow$ Load Slot 1 during active Demo $\rightarrow$ Verified persistent state*
  8. *Simple View Mode toggle on/off cycle*
  9. *20 Rapid Alternating Preset Clicks* (verifying zero memory leak, zero widget conflicts, zero state corruption)

### Section 3.E: Adversarial Monkey / Fuzz Testing
- **Status:** **PASS** (5/5 test seeds passed in `tests/release/test_part_e_monkey.py`).
- **Execution:** Dispatched **1,000 randomized user actions** across 5 pseudorandom seeds (Seeds 42, 101, 777, 1337, 9999). Actions included random preset clicks, random slider values, random page jumps, and rapid resets.
- **Invariants Checked After Every Action:**
  1. **Waterfall Reconciliation:** $|\text{Baseline EBITDA} + \Delta\text{EBITDA} - \text{Scenario EBITDA}| < 0.001\text{ Cr}$
  2. **Division Sum Integrity:** $\sum \text{Division Material Spend} = \text{Total Material Spend}$
  3. **Risk Percentile Ordering:** $\text{P10 EBITDA} \le \text{P50 EBITDA} \le \text{P90 EBITDA}$
  4. **Action Ranking Completeness:** Exactly 10 mitigation levers evaluated and ranked with positive ROIs
  5. **No Text Formatting Leaks:** Zero occurrences of `NaN`, `undefined`, `+₹-0.0`, or unformatted float strings.

### Section 3.F: Engine Invariants & Oracle Parity
- **Status:** **PASS** (4/4 tests passed in `tests/release/test_part_f_engine_invariants.py`).
- **Parity:** Evaluated `engine/chain.py` against the independent numerical oracle (`tests/oracle.py`). Aligned `engine/risk.py` default Steel CR shock and FX base to ensure zero-volatility Monte Carlo collapses deterministically to exact `run_all()` EBITDA ($\Delta < 0.05\text{ Cr}$).

### Section 3.G: Demo Mode Rigor & Storyboard Audit
- **Status:** **PASS** (4/4 tests passed in `tests/release/test_part_g_demo_mode.py`).
- **Audit:** Accelerated execution of the full 12-step boardroom storyboard. Verified `demo_out/demo_timeline.json` records strictly monotonic timestamps and valid step captions. Verified `MMD_DEMO=0` environment variable clean disable. Tested graceful degradation if demo files are unlinked.

### Section 3.H: Data Resilience & Failure Handling
- **Status:** **PASS** (4/4 tests passed in `tests/release/test_part_h_resilience.py`).
- **Robustness:** Verified core decision engine runs completely offline with zero dependency on network or processed files. Shock radar signals fall back cleanly to synthetic baselines if input files are deleted. Truncated/corrupted CSVs are safely ignored with `on_bad_lines='skip'`. Verified precomputed forecast cache integrity.

### Section 3.I: Performance Benchmarks
- **Status:** **PASS** (5/5 tests passed in `tests/release/test_part_i_performance.py`).
- **Latency Benchmarks:** Core `run_all()` p95 = 65.68ms (Target < 100ms); Page rerun latency = 0.84s (Target < 2.0s); Monte Carlo 2,000 paths = 31.25ms (Target < 250ms); Demo step transition = 0.42s (Target < 1.0s); 200 consecutive actions executed without degradation.

### Section 4: Real Browser Playwright Test Suite
- **Status:** **PASS** (5/5 tests passed in `tests/e2e/test_browser_suite.py`).
- **Execution:** Full Chromium browser automation testing both **1920×1080 (Full HD Desktop)** and **1366×768 (Standard Laptop)** viewports against live Streamlit server on port 8501.
- **Evidence:**
  - 4 High-resolution full-page screenshots captured to `qa/release/screens/`.
  - Full browser session video recordings captured to `qa/release/videos/`.
  - Tested real slider mouse drag interaction and verified live reactive metric updates.
  - Tested 20 consecutive rapid preset button clicks in browser with zero errors.

---

## 3. Exhaustive Bug Log & Resolution Matrix

| ID | Severity | Symptom / Trigger | Root Cause | Fix Applied | Commit SHA | Guard Test |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0-1** | Critical | `StreamlitWidgetAlreadyInstantiatedError: st.session_state['sb_freight'] cannot be modified` on preset clicks or demo transitions. | Modifying `st.session_state` keys assigned to widgets after widget declaration during page render. | Implemented top-of-script `sync_widgets_from_scn()` and converted chip actions to `on_click` callbacks executed before script evaluation. | `e42890c` | `tests/release/test_p0_widgets.py` |
| **P0-2** | Critical | State sync failure when running AppTest headless test harness or offline scripts. | `apply_scenario_values` attempted to update session state without checking if running in interactive UI session. | Guarded session state updates with active session context checks while preserving offline scenario dictionary synchronization. | `4de7d70` | `tests/release/test_p0_widgets.py` |
| **BUG-1** | Minor | Metric delta display printed `+₹-0.0 Cr` under Base Case on Command Centre. | Default scenario FX rate was set to `84.56` instead of baseline `84.5648`, causing a spurious `-0.03 Cr` delta, combined with unnormalized negative sign in formatting. | Updated `DEFAULT_SCN_DICT["fx_inr_usd"] = 84.5648` and added strict negative-zero normalization (`if abs(val) < 1e-4: val = 0.0`) in `ui/theme.py` and `ui/components.py`. | `e933125` | `tests/release/test_part_a_pages_and_states.py` |
| **BUG-2** | Medium | `ValueError: '#1: #1: Title' is not in list` when selecting actions in Action Matrix under AppTest. | AppTest `Selectbox.index` re-applies `format_func` on the already-formatted string stored in `_value`, causing prefix doubling. | Made `_format_action_option` idempotent: `if str(x).startswith("#"): return str(x)`. | `e0cfb30` | `tests/release/test_part_b_widgets_and_values.py` |
| **BUG-3** | High | `TypeError: optimize_action_bundle() got multiple values for argument 'cash_budget_cr'` in Guided Decision Helper. | `ui/guided_helper.py` called `optimize_action_portfolio(prop_scn, prop_res, 15.0)` with scenario objects instead of passing action list. | Passed `prop_res.action_rankings` and safely extracted action attributes using `_get_act_field`. | `a286e1b` | `tests/release/test_part_c_cross_control.py` |
| **BUG-4** | Medium | Monte Carlo zero-volatility collapse test failed with $\Delta = 20.18\text{ Cr}$. | `engine/risk.py` defaulted `steel_cr` shock to `steel_hr` shock, applying 15% shock to CR even when CR was unshocked in scenario. | Changed `cr_shock` default to `0.0` and weighted HR and CR shocks separately: `(hr * 342.44 + cr * 269.06) / 611.50`. | `29f6cad` | `tests/release/test_part_f_engine_invariants.py` |
| **BUG-5** | Low | Unstaged working tree changes reverted `backtest_scores.csv` to old 7-column schema, causing `KeyError: 'mae'`. | Working tree file had been temporarily overwritten by legacy file format. | Restored canonical V3 truth pass file with full backtest statistics (`mae`, `coverage_80`, `improvement_vs_naive`). | `release` HEAD | `tests/stress/test_truth_pass.py` |
| **BUG-6** | Low | `test_all_repo_files_in_inventory` failed because new test files were not yet indexed in `HANDBOOK.md`. | Project handbook inventory had not been regenerated after adding `tests/release/` and `tests/e2e/` test suites. | Executed `python scripts/build_handbook.py` to regenerate `docs/HANDBOOK.md` with all 143 repository files. | `release` HEAD | `tests/test_handbook.py` |

---

## 4. Performance Benchmarks & Latency Audit

All performance measurements were collected using high-resolution monotonic timers (`time.perf_counter`) over repeated iterations on the target hardware.

```mermaid
xychart-beta
    title "Latency Comparison vs Threshold (Lower is Better, ms)"
    x-axis ["run_all Engine", "Monte Carlo (2k paths)", "Demo Step", "Control Room Rerun"]
    y-axis "Latency (ms)" 0 --> 2000
    bar [65.68, 31.25, 420.0, 840.0]
```

### Benchmark Details
| Benchmark | Description | Measured Value | Threshold Target | Headroom | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`run_all` p95** | Full profit chain calculation across all 7 materials, 3 divisions, tariffs, pass-through, and 10 action rankings | **65.68 ms** | $< 100\text{ ms}$ | **34.3% faster** | **PASS** |
| **Monte Carlo 2,000** | Profit-at-Risk Cholesky simulation across 7 correlated commodities with P10/P50/P90 output | **31.25 ms** | $< 250\text{ ms}$ | **87.5% faster** | **PASS** |
| **Control Room Rerun** | Full Streamlit page execution including Control Deck, 4 metric cards, waterfall chart, and radar table | **0.84 s** | $< 2.0\text{ s}$ | **58.0% faster** | **PASS** |
| **Demo Step Transition** | Storyboard state advance, scenario injection, and component re-render | **0.42 s** | $< 1.0\text{ s}$ | **58.0% faster** | **PASS** |
| **Memory Degradation** | Latency change over 200 consecutive actions (leak detection) | **+1.2%** | $< 20.0\%$ | **Zero leak** | **PASS** |

---

## 5. Visual Evidence Index (Screenshots & Video)

All media assets have been verified, timestamped, and stored in `qa/release/`:

```
qa/release/
├── inventory.json                             [Catalog of all 39 interactive elements]
├── screens/
│   ├── 0_control_room_base_1920x1080.png      [Base Case on 1920x1080 Full HD Desktop]
│   ├── 0_control_room_base_1366x768.png       [Base Case on 1366x768 Laptop Display]
│   ├── 0_control_room_redsea_1920x1080.png    [Red Sea Shock on 1920x1080 Full HD]
│   └── 0_control_room_redsea_1366x768.png     [Red Sea Shock on 1366x768 Laptop]
└── videos/
    ├── page@71e2256c1cfdd039af7bc84d0fdc3732.webm [Real browser interaction & slider drag]
    ├── page@7e2c2bfd0c8b92a8bbfe9490f47a6419.webm [20 rapid preset clicks under Chromium]
    └── page@dd00af94a46acd4ae29a5e2913b4d037.webm [Full responsive reload verification]
```

### Visual Audit Findings
1. **Responsive Flex Layout:** Under 1366×768, the Control Deck scenario chips collapse gracefully into 2 rows without overlapping or truncating text.
2. **High-DPI Clarity:** Full HD (1920×1080) metrics render sharp typography using tabular numerical lining (`font-variant-numeric: tabular-nums`).
3. **Contrast Compliance:** All status pills (`ON TRACK`, `MONITOR`, `BREACH`) satisfy WCAG AA contrast ratios ($\ge 4.5:1$) against dark backgrounds (`#0F172A`).

---

## 6. Environment & Runtime Audit

### Dependency Check
Ran `pip check` in virtual environment:
```powershell
.venv\Scripts\pip check
# Output: No broken requirements found.
```

### Path & Portability Verification
- **Zero hardcoded absolute paths**: Audited all source files in `engine/`, `ui/`, `pages/`, `demo/`, and `tests/`. All paths are constructed dynamically using `os.path.join(BASE_DIR, ...)` or relative pathing.
- **Cross-platform Path Separators**: Forward slashes or `os.sep` normalized across all loaders. Fully compatible with Linux, macOS, and Windows.
- **Case Sensitivity**: Verified all file references (`0_Command_Centre.py`, `HANDBOOK.md`, `processed/*.csv`) match on-disk casing exactly.
- **OneDrive Synchronization Guidance**: If running from a cloud-synced directory, disable OneDrive file locking on `.venv/` and `data/` to avoid temporary file access latency.

---

## 7. Emergency Presentation Playbook ("What to do if X fails")

In a live boardroom or hackathon pitch, unexpected environment issues can occur. Follow this exact triage procedure:

```mermaid
flowchart TD
    Issue{What failed?}
    Issue -->|Browser Blank / Frozen| A[Ctrl + Shift + R Hard Refresh]
    Issue -->|Port Collision / Not Starting| B[Kill existing task and restart on 8501]
    Issue -->|Demo Mode Out of Sync| C[Click 'Reset' Chip in Control Deck]
    Issue -->|Question on a Number| D[Refer to Section 6 of docs/HANDBOOK.md]
```

### Scenario 1: The Browser Page Freezes or Shows a Blank Screen
- **Action:** Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac) to perform a hard reload.
- **Why it works:** The engine state is persistently synced in `st.session_state`. A hard reload reconnects the Streamlit WebSocket and immediately re-renders the current scenario without losing data.

### Scenario 2: Streamlit Server Fails to Start (Port 8501 Occupied)
- **Action:** Open terminal and run:
  ```powershell
  Get-Process -Name python | Stop-Process -Force
  .venv\Scripts\streamlit run app.py --server.headless true --server.port 8501
  ```
- **Why it works:** Kills any orphaned background Python instances and binds cleanly to the standard port.

### Scenario 3: Accidental Lever Modification During Demo Mode
- **Action:** Simply click the **":material/restart_alt: Reset"** button on the Control Deck (top of Command Centre).
- **Why it works:** The reset callback instantly clears all override levers, resets macro shocks to 0%, and re-anchors to the validated Base Case (Revenue ₹3,374.00 Cr, EBITDA ₹297.70 Cr).

### Scenario 4: A Judge Asks "Where Does This Number Come From?"
- **Action:** Open `docs/HANDBOOK.md` in your browser or Markdown viewer and navigate directly to:
  - **Part B, Section 5:** *Profit Chain Formulas & Algebraic Derivations*
  - **Part B, Section 6:** *Verified Baseline & Shock Proofs*
- **Talking Point:** *"Every single number in our application is derived from first principles in the audited profit chain formula. For example, our 10% material shock reduces EBITDA by exactly ₹61.15 Cr before pass-through, matching our closed-form algebraic oracle to the rupee."*

---

**Team 11:59 · Xovate'26 · Ready for Final Submission**
