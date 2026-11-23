# Rane (Madras) MMD Decision Engine · Design Plan & Aesthetic Specification
**Team 11.59 · Xovate'26 Management Hackathon**  
*Lead Designers & Engineers: Vikram T, Sayoni Dan, Trisha Pal (XIME Chennai)*

---

## 1. Executive Summary & Design Vision

The **Rane (Madras) Materials Management Department (MMD) Decision Engine** is an industrial operational command cockpit built for mission-critical automotive supply chain executives. Automotive tier-1 component manufacturing is governed by strict delivery windows, tight gross margins (8.7% EBITDA baseline), and volatile global raw material supply chains. 

Rather than appearing as a generic, airy SaaS web app or a template-driven prototype, the MMD Decision Engine looks and feels like a **high-precision Bloomberg terminal engineered for plant materials directors, chief financial officers, and managing directors**.

---

## 2. Core Design Principles

1. **Dense Industrial Information Hierarchy (Bloomberg for MMD)**
   - Every pixel serves an operational decision. Information density is high, deliberate, and structured into scannable visual layers.
   - Primary operational metrics are instantly legible without endless vertical scrolling. Tabular figures use `font-variant-numeric: tabular-nums` to ensure exact column alignment during live slider updates.

2. **Mill-Scale & Galvanised Steel Palette (Authentic Automotive Manufacturing)**
   - Colors are inspired by hot-rolled steel coils, aluminium ingots, and automotive plant physical control rooms.
   - Deep mill-scale graphite (`#0F172A`, `#1E293B`) forms authoritative headers and navigational anchors.
   - Pale galvanised zinc canvas (`#F8FAFC`, `#F1F5F9`) provides maximum contrast for data visualization.
   - Crisp industrial steel blue (`#0284C7`, `#0369A1`) guides interactive focus and scenario levers.

3. **Toyota-Standard Andon Visual Language (Operational Urgency Without Visual Clutter)**
   - Alerts adhere strictly to Lean manufacturing Andon standards:
     * **Green (`#059669` / `#10B981`)**: Normal operational buffer (>35 days cover, EBITDA positive).
     * **Amber (`#D97706` / `#F59E0B`)**: Reorder trigger breached (Stock $\le$ ROP, 20–35 days cover).
     * **Red (`#DC2626` / `#EF4444`)**: Line stoppage risk / Stock-out alert (< Effective Lead Time, EBITDA erosion > ₹30 Cr).
   - Semantic color is never decorative; it always denotes state and action urgency.

4. **Zero-Fluff Traceability & Deterministic Numbers**
   - No AI filler adjectives ("enterprise-grade", "seamless", "disruptive").
   - Every number displayed in the UI is backed by engine arithmetic (`f-strings`) and data lineage badges (`● LIVE DATA`, `▲ TEAM ASSUMPTION`, `■ SAMPLE DATA`, `! TOO SHORT TO FORECAST`).

---

## 3. Design Critique Against Generic AI Defaults

| Dimension | Generic AI Prototype Default | Team 11.59 Industrial Standard |
|---|---|---|
| **Color Scheme** | Generic AI purple (`#6366F1`) & neon gradients | Precision Mill-scale graphite (`#1E293B`) & Galvanised steel blue (`#0284C7`) |
| **Typography** | Default browser sans, wavy spacing | High-legibility Inter/SF Pro with monospace tabular figures (`font-variant-numeric: tabular-nums`) |
| **Icons & Emojis** | Cartoon emojis everywhere in headers (🚀, 📈, 🔥) | Structured technical SVG symbols and industrial status pills |
| **Component Spacing** | Floating disconnected cards with excessive white space | Dense, structured grid with subtle hairline borders (`1px solid #E2E8F0`) |
| **Text Copy** | Generic hype ("Unlock intelligent cross-functional synergy") | Plain, concrete industrial copy ("See the shock coming, measure what it costs, decide what to do") |
| **Streamlit Chrome** | Deploy button, hamburger menu, running man visible | Clean headless industrial presentation: `[client] toolbarMode = "minimal"`, chrome hidden via CSS |

---

## 4. Design Token System

```css
/* Color Tokens */
--mmd-bg-canvas:        #F8FAFC;  /* Pale galvanised canvas */
--mmd-bg-card:          #FFFFFF;  /* Crisp white card background */
--mmd-bg-dark:          #0F172A;  /* Deep mill-scale graphite */
--mmd-bg-surface:       #1E293B;  /* Slate header surface */

--mmd-border-hairline:  #E2E8F0;  /* Subtle divider border */
--mmd-border-active:    #94A3B8;  /* Focus border */
--mmd-border-focus:     #0284C7;  /* Primary focus outline */

--mmd-text-primary:     #0F172A;  /* High-contrast slate heading */
--mmd-text-secondary:   #475569;  /* Balanced body text */
--mmd-text-muted:       #64748B;  /* Secondary captions & metadata */
--mmd-text-inverse:     #FFFFFF;  /* Contrast text on dark banners */

/* Industrial Accents */
--mmd-accent-steel:     #0284C7;  /* Automotive steel blue */
--mmd-accent-steel-dark:#0369A1;  /* Hover / active steel blue */
--mmd-accent-copper:    #C2410C;  /* LME copper accent */
--mmd-accent-zinc:      #64748B;  /* Zinc / Galv silver */

/* Andon Safety System */
--mmd-andon-green:      #059669;  /* Safe / Buffer intact */
--mmd-andon-green-bg:   #ECFDF5;
--mmd-andon-amber:      #D97706;  /* Reorder trigger / Warning */
--mmd-andon-amber-bg:   #FFFBEB;
--mmd-andon-red:        #DC2626;  /* Critical risk / Line stoppage */
--mmd-andon-red-bg:     #FEF2F2;

/* Typography Tokens */
--mmd-font-family:      -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
--mmd-font-mono:        "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", monospace;
```

---

## 5. ASCII Wireframe: Materials Control Room (Master Home)

```
+---------------------------------------------------------------------------------------------------------------+
| LIVE COMMODITY TAPE:  Cu: $9,650/t (+3.2%) | Al: $2,420/t (+1.5%) | Fe: ₹58,400/t (-0.4%) | Freight: $4,850/40ft (+123%) | FX: ₹86.40 |
+---------------------------------------------------------------------------------------------------------------+
| RANE (MADRAS) MATERIALS CONTROL ROOM · TEAM 11.59 (XIME CHENNAI)                                               |
| "See the shock. Measure it. Decide." · Calibrated Baseline: FY25 Handout (₹3,421 Cr Rev / ₹297.7 Cr EBITDA)   |
+---------------------------------------------------------------------------------------------------------------+
| REVENUE: ₹3,421 Cr | EBITDA: ₹297.7 Cr (8.7%) | PAT: ₹37.6 Cr | MAT Δ: +₹0.0 Cr | MIN COVER: 24d (Al) | TOP ACT: ACT-07 (+₹2.1 Cr) |
+---------------------------------------------------------------------------------------------------------------+
| [HERO: GLOBAL INBOUND EXPOSURE MAP - Plotly Scattergeo]  | [ANDON RISK BOARD: 7 CRITICAL TRIGGERS]             |
|                                                          |   [!] Red Sea Vessel Diversion       -> RED (18d)  |
|   (Interactive trade lanes from Chile, Middle East,      |   [!] Copper LME Above Resistance    -> AMBER      |
|    East Asia into Chennai / Ennore & JNPT)               |   [!] Working Capital Cash Drag      -> AMBER      |
|                                                          |   [ok] Domestic Steel Scrap Spreads  -> GREEN      |
|   Spend at Risk: ₹142.5 Cr | 6 Active Vessels Tracked    |   [ok] Plant Buffer Inventory        -> GREEN      |
+----------------------------------------------------------+----------------------------------------------------+
| [MONTE CARLO PROFIT-AT-RISK (N3)]                        | [DECISIONS NOW: PRESCRIPTIVE TOP 3 ACTIONS (N6)]   |
|   P10 EBITDA:  ₹184.2 Cr  (Severe Stress)                |   #1 ACT-02: Index-Linked Contracts   (+₹14.8 Cr Net)|
|   P50 EBITDA:  ₹268.5 Cr  (Expected Case)                |   #2 ACT-06: Cape Slot Guarantees     (+₹8.2 Cr Net) |
|   P90 EBITDA:  ₹305.1 Cr  (Mild Case)                    |   #3 ACT-07: Container Consolidation  (+₹2.1 Cr Net) |
|   P(PAT < 0):  18.4% Probability of Net Loss             |   >> BUY TIMING SIGNALS: Cu: BUY NOW | Al: STAGGER   |
+----------------------------------------------------------+----------------------------------------------------+
| [CROSS-FUNCTIONAL IMPACT LENSES (N8)]                                                                         |
|   MMD: -₹18.4 Cr | Finance: ₹24.2 Cr Gap | Production: 2 Lines at Risk | HR: 0 OT | Quality: PPAP Pending      |
+---------------------------------------------------------------------------------------------------------------+
| [12-MONTH CASH TROUGH & OEM RECOVERY TIMELINE (N4)]      | [DYNAMIC INVENTORY RUNWAY STRIP (N1)]              |
|   Cumulative Cash Deficit: -₹16.8 Cr at Month 4          |   Steels: 45d [SAFE] | Copper: 24d [WATCH]            |
|   OEM Price Pass-Through Recovery Trajectory (Lag 75d)   |   Aluminium: 18d [CRITICAL] | Resin: 32d [SAFE]       |
+---------------------------------------------------------------------------------------------------------------+
```

---

## 6. ASCII Wireframe: Standard Module Page

```
+---------------------------------------------------------------------------------------------------------------+
| [MODULE BADGE]  MODULE TITLE                                                                                  |
| Concise executive subtitle explaining analytical objective                                                     |
+---------------------------------------------------------------------------------------------------------------+
| [GLOBAL STANDARDIZED KPI STRIP: 6 CARDS]                                                                      |
| Revenue (₹ Cr) | EBITDA (₹ Cr / %) | PAT (₹ Cr) | Material Spend Δ | Min Days of Cover | Top Action           |
+---------------------------------------------------------------------------------------------------------------+
| [EXECUTIVE INSIGHT BANNER: Green / Amber / Red depending on operating conditions]                             |
+---------------------------------------------------------------------------------------------------------------+
| [PRIMARY SECTION 1: INTERACTIVE CHART WITH TOOLTIPS AND EXPOSURE HIGHLIGHTS]                                  |
|                                                                                                               |
|                                                                                                               |
+---------------------------------------------------------------------------------------------------------------+
| [PRIMARY SECTION 2: STRUCTURED DATAFRAME WITH EXPLICIT COLUMN CONFIG, TEXT WRAP, AND NO TRUNCATION]          |
|                                                                                                               |
+---------------------------------------------------------------------------------------------------------------+
| [📐 EXPANDABLE HOW IS THIS CALCULATED? BOX: Full mathematical formula + Raw data lineage source]              |
+---------------------------------------------------------------------------------------------------------------+
```
