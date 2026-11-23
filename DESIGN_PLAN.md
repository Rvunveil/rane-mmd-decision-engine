# Rane (Madras) MMD Decision Engine · Design Plan & Aesthetic Specification (V3)
**Team 11:59 · Xovate'26 Management Hackathon**  
*Lead Systems Architect & Product Engineering: Vikram T, Sayoni Dan, Trisha Pal (XIME Chennai)*

---

## 1. Executive Summary & Design Vision

The **Rane (Madras) Materials Management Department (MMD) Decision Engine** is an industrial operational cockpit engineered for tier-1 automotive manufacturing executives. Automotive component manufacturing operates under severe delivery windows, wafer-thin EBITDA margins (8.7% baseline on ₹3,421 Cr turnover), and acute exposure to global commodities and maritime corridors.

Rather than resembling a generic, airy SaaS web prototype or template-driven dashboard, the Decision Engine looks and behaves like an **industrial decision terminal** tailored for plant procurement heads, chief financial officers, and managing directors.

**Core Tagline:** *"See the shock coming, measure what it costs, decide what to do."*

---

## 2. Industrial Design Foundations & Color Tokens (Section 5)

### 2.1 Concrete Color Tokens
All styling is grounded in a mill-scale graphite and galvanised steel palette:

| Token Name | Hex Code | Visual Semantic & Usage |
|---|---|---|
| **Ink** | `#1D262C` | Primary text, high-contrast headings, ticker background |
| **Slate** | `#536471` | Secondary labels, metric descriptors, sub-captions |
| **Muted Slate** | `#8E9AA2` | Tertiary labels, hairline dividers, footer meta |
| **Canvas** | `#EEF1F2` | Global application background (light industrial paper) |
| **Panel** | `#F8F9F9` | Card and table row background |
| **Border** | `#C9D1D5` | Hairline dividers, table borders, card frames |
| **Steel Blue** | `#2F5D7C` | Active accent, primary branding pill, button highlight |
| **Deep Navy** | `#142938` | Dark surfaces, modal dialog header accents |
| **Industrial Amber** | `#D97706` | Warning status, reorder triggers (Stock $\le$ ROP) |
| **Signal Red** | `#C2382B` | Danger status, stock-out line starvation, freight chokepoints |
| **Signal Green** | `#1E7E34` | Safe operational status, cost savings, pass-through recoveries |

### 2.2 Typography & Tabular Numerals
- **Primary Sans:** `Archivo` (loaded via Google Fonts) for clean geometric legibility across factory floor monitors and laptops.
- **Monospace & Numerics:** `JetBrains Mono` and `font-variant-numeric: tabular-nums` applied unconditionally across all metric cards, financial tables, ticker tapes, and waterfall annotations to guarantee strict vertical column alignment during live slider updates.
- **Iconography Standard:** Zero emoji in navigation, section titles, expanders, or buttons. Every icon uses Google Material Symbols via `:material/...:`.

---

## 3. Control Deck & Guided Helper Architecture (Sections 2 & 3)

### 3.1 Single Canonical State Architecture
- Single state dictionary `st.session_state["scn"]` managed through `engine/state.py`.
- Widgets omit the `value=` parameter when assigned a persistent session key, completely eliminating dual key/value Streamlit warnings.
- All scenario changes (presets, manual slider edits, guided dialog recommendations, reset actions, demo player) route exclusively through `apply_scenario_values(dict, source=...)`.

### 3.2 Command Centre Control Deck
- **Scenario Preset Chips:** One-click activation for *Base Case*, *Today's Market (Live Feeds)*, *Red Sea / Hormuz Crisis*, *Global Metal Shock*, *Tariff & FX Surge*, and *Vehicle Demand Recession*.
- **Inline Levers & Live Deltas:** Six inline levers for Metal Master (+% vs FY25), Ocean Freight Multiplier, Shipping Delay (days), USD/INR Forex, OEM Pass-Through Recovery (%), and Vehicle Demand (%).
- **Individual Metals Popover:** Allows fine-grained override of Copper, Aluminium, Nickel, Steel HR, Steel CR, Resin, and Rubber shocks.
- **Guided Helper Modal (`@st.dialog`):** "What happened? Get a recommendation" wizard diagnosing disruption category (Shipping Delay / Red Sea, Metal Price Surge, Forex / Rupee Depreciation, OEM Pass-Through Negotiation) and severity (Small, Medium, Severe). Displays estimated P&L exposure and applies the optimal action bundle directly into active state.
- **Simple View Toggle:** Instantly collapses complex Monte Carlo distributions into an executive summary table and top 3 prescriptive actions for non-technical leadership.

---

## 4. Visualization & Plotly Layout Standards

- **Chart Background:** Fully transparent (`paper_bgcolor="rgba(0,0,0,0)"`, `plot_bgcolor="rgba(0,0,0,0)"`).
- **Gridlines:** Faint horizontal lines (`#E2E8F0`), zero vertical gridlines.
- **Legend & Margins:** Legends placed horizontally above plots (`y=1.02` to `1.08`) with reserved top margins (`t=45` to `50px`) to prevent legend/title overlap at 1366px laptop resolution.
- **Exposure Map (N2):** Natural earth projection with curved maritime waypoints avoiding African land mass crossings.
- **Cash Deficit Profile:** Displays a clean "No working capital cash deficit in this scenario" indicator under Base Case rather than an empty broken chart.

---

## 5. Guided Executive Demo Mode (Section 4)

- **Strict Isolation:** Entire subsystem contained within `demo/` (`player.py`, `overlay.py`, `storyboard.yaml`, `README.md`).
- **Integration Hook:** Exactly 6 guarded lines in `app.py`.
- **Feature Flagging:** Governed by `config/demo.yaml` and overridden instantly via `MMD_DEMO=0`.
- **Timeline Logging:** Writes live computed P&L values to `demo_out/demo_timeline.json`.
- **Video Recording:** Playwright headless recording script `scripts/record_demo.py` outputs `demo_out/*.webm`.

---

## 6. Audit & Acceptance Testing

- **100% Test Coverage:** 90 automated pytest unit, integration, AppTest UI, and Stress tests passing cleanly.
- **Oracle Verification:** Independent mathematical oracle (`tests/oracle.py`) validating P&L arithmetic without calling engine code.
- **Playwright Full-Page Screenshots:** 28 full-page PNG screenshots captured across all 7 modules at 1920×1080 and 1366×768 saved in `qa/v3/screenshots/`.
