# DATA_TRACE.md · Data Lineage, Quality Audit & Judgement Log
**Event:** Xovate'26 Management Hackathon  
**Team 11:59:** Vikram T · Sayoni Dan · Trisha Pal · XIME Chennai  
**Governing Standard:** Section 4 of the Hackathon Mandate  

---

## 1. Executive Summary of Data Pipeline

Every data file in `data/raw/Dataset xovate (!)/` was ingested, audited for anomalies, and processed through our pure-Python data pipeline (`engine/data_loader.py`). The cleaned datasets are cached in `data/processed/` and precomputed forecast tables are stored in `data/fallback/`.

This document records the exact data lineage, mathematical transformations, deliberate analytical fixes, and reconciliations against the official hackathon baseline.

---

## 2. Key Deliberate Data-Judgement Fixes

### A. Weekly Container Freight Rate Index (Worldwide)
- **Source File:** `Logistics/Weekly Container freight rate index worldwide.xlsx`
- **Observed Anomaly:** The raw sheet listed 165 observations in Columns 2 & 3, but assigned them consecutive daily dates from **12 January 2023 to 25 June 2023**.
- **Internal Documentary Evidence:** In Column 8 of the very same sheet, the author's official description stated:
  > *"Container freight rates oscillated dramatically between January 2023 and March 2026. Freight rates slumped to their lowest level on the 26th of October 2023, when the going rate for a 40-foot container was only 1,342 U.S. dollars. Since then, the global freight rate has significantly increased, hitting over 5,900 U.S. dollars in July 2024... As of March 19, 2026, freight rates stood at 2,172 U.S. dollars per 40ft container."*
- **Engineering Fix Applied:** Re-indexed the 165 points backwards from **19 March 2026** in 7-day weekly intervals:
  $$\text{Date}_i = \text{Timestamp('2026-03-19')} - 7 \times (165 - 1 - i) \text{ days}$$
- **Validation Anchors:**
  1. **October 2023 Low:** Evaluates to **$1,342** (Points in late October 2023).
  2. **July 2024 Peak:** Evaluates to **$5,937** (Point in mid-July 2024, matching the Red Sea crisis peak).
  3. **March 19, 2026 Terminal Value:** Evaluates to **$2,172** (Matches the official handout baseline).
- **Tool Display:** An interactive Before & After comparison chart is rendered on Page 6 (Assumptions & Data Trace).

---

### B. RBI USD/INR Forex Reference Rate
- **Source File:** `Logistics/Forex Exchange Rate (inr - usd).xlsx`
- **Observed Anomaly:** Contains duplicate dates, weekend gaps, and ~49 non-numeric cell entries (`"ND"`, `"-"`, blank strings).
- **Engineering Fix Applied:** Filtered to valid rows where date is chronological and rate is coerced via `pd.to_numeric(errors='coerce')`. Deduplicated on date index. Resampled to monthly calendar mean (`MS`).
- **Baseline Calibration:**
  - **FY25 (Apr 2024 – Mar 2025) Average:** **84.5648 INR/USD** (matches handout reference of ~84.6).
  - **Latest Reference Rate (Jun 2026):** **94.5975 INR/USD** (represents +11.9% depreciation).

---

### C. LME Aluminium Price (2014–2026)
- **Source File:** `Material price/Aluminium Price.xlsx`
- **Observed Anomaly:** High-density wide spreadsheet formatted in three 5-year and 3-year horizontal blocks (rows 3, 20, 37). Within each 5-column block, months are listed in **reverse order** (December down to January).
- **Engineering Fix Applied:** Unwrapped the 2D matrix into a normalized tidy table with columns `['unique_id', 'ds', 'y']`. Extracted `LME Aluminium Cash-Settlement` as the authoritative global benchmark.
- **Validation:** Produces 155 clean monthly points from Jan 2014 to Nov 2026 with zero missing values. FY25 average = **$2,526.0 / t**; Latest = **$3,149.6 / t** (+24.7%).

---

### D. Ministry of Steel Domestic Coils (HRC & CRC)
- **Source File:** `Material price/Steel_Price_Dataset_2021-2026.xlsx`
- **Critical Policy Check:** Values are published by the Ministry of Steel in domestic Indian Rupees per metric tonne (`HR coil 2.5mm (Rs/t)` and `CR coil 0.63mm (Rs/t)`).
- **Engineering Guardrail:** **STRICTLY PROHIBITED FROM APPLYING FX CONVERSION.** Any currency conversion on this series would distort domestic steel prices by an artificial factor of 85x–95x.
- **Baseline Calibration:**
  - Steel HR Coil FY25 Average: **₹ 60,441.8 / t**; Latest: **₹ 76,900.0 / t** (+27.2%).
  - Steel CR Coil FY25 Average: **₹ 69,066.0 / t**; Latest: **₹ 89,670.0 / t** (+29.8%).

---

### E. Phenolic Resin (Short Volatile Series)
- **Source File:** `Material price/Resin Price Dataset (June 2024 - Sep 2026).xlsx`
- **Observed Anomaly:** Only 17 irregular points with quarterly gaps and swings exceeding ±40%. Quoted in USD/kg.
- **Engineering Fix Applied:** Multiplied by 1,000 to convert from USD/kg to USD/tonne ($1,437 / t at FY25 baseline).
- **Analytical Prudence:** Marked with `[TOO SHORT TO FORECAST]` badge. Complex ARIMA models were deliberately avoided to prevent severe statistical overfitting. Projections utilize a robust rolling median with empirical quantile bands (80% and 95%).

---

### F. Natural Rubber Kottayam RSS-4
- **Source File:** `Material price/Natural Rubber Yearly Trends India (2005-06 to 2024-25) (1).xlsx`
- **Observed Anomaly:** Annual agricultural marketing years (April to March) quoted in ₹/100kg. Sheet contains footer totals and averages (`20-Year Average`, `20-Year Total`).
- **Engineering Fix Applied:** Screened out non-numeric footer rows. Converted ₹/100kg × 10 to standard ₹/tonne (₹14,019.7 / 100kg = ₹140,197 / t). Labelled as `[ANNUAL SERIES]` in the UI.

---

### G. Statista Rane Financials Mismatch
- **Source Files:** `Rane financials/` (`revenue_of_rane_madras_limited...xlsx`, `operating_profit...xlsx`, `net_income...xlsx`)
- **Observed Discrepancy:**
  - Statista FY2025 Revenue = ₹3,863 Cr (vs Handout ₹3,421 Cr)
  - Statista FY2025 Net Income = ₹107.5 Cr (vs Handout ₹37.6 Cr)
  - Statista FY2021 Operating Profit = "3.0" (obvious data entry unit error)
- **Governance Decision:** The **Official Handout Baseline overrides all Statista files**. Statista figures are archived as labelled historical context ("different corporate reporting perimeter") and do not enter the mathematical P&L calculation chain.

---

## 3. Dataset Inventory Summary

| Dataset Identifier | Raw Filename | Clean Rows | Frequency | Start Date | End Date | Primary Use in Cockpit |
|---|---|---|---|---|---|---|
| `fx_daily` | Forex Exchange Rate...xlsx | 6,259 | Daily | 2000-08-21 | 2026-06-30 | Live FX conversion & currency stress |
| `freight_fixed` | Weekly Container...xlsx | 165 | Weekly | 2023-01-19 | 2026-03-19 | Ocean logistics multiplier & container model |
| `copper` | Copper Price.xlsx | 154 | Monthly | 2014-01-01 | 2026-10-01 | Full AutoETS / AutoARIMA forecast |
| `nickel` | Nickel Price List.xlsx | 154 | Monthly | 2014-01-01 | 2026-10-01 | Full AutoARIMA forecast |
| `aluminium` | Aluminium Price.xlsx | 155 | Monthly | 2014-01-01 | 2026-11-01 | Full AutoARIMA forecast |
| `steel_hr` | Steel_Price_Dataset...xlsx | 69 | Monthly | 2021-01-01 | 2026-09-01 | Full AutoTheta forecast (₹/t) |
| `steel_cr` | Steel_Price_Dataset...xlsx | 69 | Monthly | 2021-01-01 | 2026-09-01 | Full AutoTheta forecast (₹/t) |
| `resin` | Resin Price Dataset...xlsx | 17 | Irregular | 2024-06-01 | 2026-09-01 | Short series empirical median fallback |
| `rubber` | Rubber Yearly Trends...xlsx | 20 | Annual | 2005-04-01 | 2024-04-01 | Annual trend projection |
| `chokepoints` | Daily_Chokepoints_Data.xlsx | 80,528 | Daily | 2019-01-01 | 2026-11-15 | Shock Radar: Hormuz, Bab el-Mandeb, Cape |
| `gscpi` | The Global Supply Chain...xls | 346 | Monthly | 1998-01-31 | 2026-10-31 | Shock Radar: NY Fed supply pressure index |
| `brent` | brent-daily oil.csv | 9,128 | Daily | 1987-05-20 | 2026-11-11 | Shock Radar: Crude benchmark |

---

## 4. Shock Radar Indicators Lineage & Formulas (QA Verified)

All metrics displayed on the Shock Radar (Page 0) are computed strictly from underlying data files without hardcoded percentages or unsupported causal claims:
1. **Bab el-Mandeb (Red Sea):** Recent 30-day average container transits vs FY23 baseline average (`chokepoints.csv`). Red Sea transit drop computed as `((b_recent - b_2023) / b_2023) * 100% = -69.7%` (verified vs raw data).
2. **Cape of Good Hope Diverted Traffic:** Traffic volume surge computed as `((c_recent - c_2023) / c_2023) * 100% = +115.4%` (verified vs raw data).
3. **Brent Crude Benchmark:** FY25 baseline computed as average of daily prices between 2024-04-01 and 2025-03-31 ($78.5/bbl) from `brent.csv`.
4. **RBI Forex Reference:** FY25 average computed as average daily RBI reference rate (₹84.56/$) from `fx_daily.csv`.
5. **LME Copper Benchmark:** FY25 average computed from `copper.csv` ($9,369/t). Current spot ~$14,508/t (+54.8%).
6. **No Invented Claims:** All radar texts cite data observations only (e.g. transit vessel count drops, lead time extensions) with zero speculative non-data claims.
