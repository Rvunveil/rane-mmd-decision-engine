# DEMO_SCRIPT.md · 15-Minute Official Presentation Script & Judge Q&A Guide
**Event:** Xovate'26 Management Hackathon  
**Team 11.59:** Vikram T · Sayoni Dan · Trisha Pal · XIME Chennai  
**Tool Name:** Rane (Madras) MMD Decision Engine  
**Tagline:** *"See the shock. Measure it. Decide."*  

---

## 1. 15-Minute Official Presentation Breakdown

| Phase | Duration | Screen / Page | Live Action / Sliders | Key Spoken Points |
|---|---|---|---|---|
| **1. Problem Statement** | **2 min** | Slide Deck & Home Banner | Show hero banner on `0_Command_Centre.py` | *"Rane (Madras) operates 17 plants in India and Mexico making steering systems, brake pads, and valves for OEMs. In this thin-margin business (8.7% EBITDA), raw materials consume ₹1,223 Cr. Today, MMD works in isolated spreadsheets. When the Red Sea closes or copper surges 30%, spot buying, air freight, and line stoppages erase more than ₹60 Cr—wiping out the entire year's profit (PAT ₹37.6 Cr). We built the tool MMD needs to SEE the shock, MEASURE it, and DECIDE."* |
| **2. Approach & Architecture** | **2 min** | `pages/6_Assumptions_Data_Trace_About.py` | Click Tab 1 (Data Trace) & show Freight Re-dating chart | *"Our solution is built on three uncompromising pillars: First, data integrity. When we audited the dataset, we caught a critical error: 165 container freight points labelled as daily dates in 2023. By cross-referencing the sheet's text, we re-dated it weekly to March 2026, perfectly anchoring the Oct 2023 low ($1342) and Jul 2024 peak ($5937). Second, driver-based P&L: every number flows from pure math in pure Python—no hardcoding. Third, cross-functional ripple: a procurement decision isn't isolated; it ripples through Finance, Production, HR, Quality, and Sales."* |
| **3. Master Control Room** | **3 min** | `pages/0_Command_Centre.py` | Show Live Market Tape, Exposure Map, Andon Board & Monte Carlo VaR | *"Welcome to the Materials Control Room—a trading-desk cockpit built for Rane leadership. Across the top, our Live Ticker Tape tracks daily prices from LME and domestic mills. Below, our interactive Inbound Exposure Map models ₹142 Cr of spend at risk across global maritime trade lanes from Chile, Middle East, and East Asia into Chennai and JNPT. On the right, our 7-Trigger Andon Board monitors Red Sea delays, cash drag, and plant stock-outs. Below, our 2,000-path Monte Carlo engine computes Value-at-Risk and loss probability P(PAT < 0). Watch: our Decisions Now panel gives MMD instant Buy-Timing signals—Buy Now, Stagger, or Hold."* |
| **4. Forecasting & Recalculation** | **3 min** | `pages/1_Forecast.py` & `pages/3_Profit_Chain.py` | Show Forecast & Buy signals; switch to Module 3; show 12M Timeline & Claim Dossier | *"On Module 1 (Forecast), statsforecast fits AutoETS, AutoARIMA, and AutoTheta with 80% and 95% confidence bands. For short series like Phenolic Resin, we honestly flag it 'Too Short to Forecast' and deploy robust median envelopes. On Module 3 (Profit Chain), watch the live recalculation: Landed cost of imported metals escalates; division line costs jump across Castings (+18%) and Steering (+9%). Look at our 12-Month Cash Deficit Timeline: because OEMs take 75 days to settle price adjustments, Rane faces a ₹22 Cr working capital cash trough at Month 3! But with one click, our engine generates an official OEM Price-Recovery Claim Pack partitioned across all 4 divisions ready for Maruti Suzuki and Tata Motors."* |
| **5. Containers, Inventory & Prescriptive Action Matrix** | **3 min** | `pages/4_Containers_Inventory.py` & `pages/5_Action_Matrix.py` | Show Runway Chart (Copper turns RED); switch to Module 5; adjust Budget slider to ₹15 Cr | *"Here is Module 4 (Containers & Inventory). Notice the red alert: Copper and Resin have fallen below effective lead time because Cape rerouting added 18 days. Stock-out is 9 days away! How do we respond? On Module 5 (Action Matrix), our 10 actions are dynamically re-ranked by Net ₹ Benefit. In baseline, container packing was #1. But in this Red Sea crisis, ACT-02 (Index-linked contract) and ACT-06 (Cape slot booking) surge to the top with +₹38 Cr net benefit. Below, our PuLP Linear Optimizer takes a ₹15 Cr cash budget and instantly computes the optimal portfolio bundle: combining hedging, domestic near-shoring, and air-freight bridge."* |
| **6. Business Value & Close** | **2 min** | `pages/5_Action_Matrix.py` (Ripple Matrix) | Inspect Cross-Functional Ripple tabs; return to Command Centre; download Decision Brief | *"Finally, our Cross-Functional Ripple Matrix proves why MMD cannot decide in a silo: Flying emergency valves (ACT-05) saves ₹14 Cr in OEM line stoppage penalties, but Finance incurs ₹4.8 Cr unbudgeted cash drain and Quality faces rushed receiving inspections. The MMD Decision Engine bridges procurement, finance, and plant operations into one cockpit. It turns supply chain chaos into clear ₹ decisions. We are Team 11.59—Vikram, Sayoni, and Trisha from XIME Chennai. We welcome your questions."* |

---

## 2. Slide Deck Number Mapping Table

Judges will cross-verify numbers shown in your presentation slides against the live app. Here is how to reproduce each deck figure:

| Slide # | Deck Figure / Claim | How to Reproduce in Live App | Engine Formula / Verification |
|---|---|---|---|
| **Slide 2** | Baseline Revenue: ₹3,421 Cr, EBITDA: ₹297.7 Cr (8.7%), PAT: ₹37.6 Cr | Open `0_Command_Centre.py`, ensure preset is set to **Base case** | Handout Baseline figures; PBT = 37.6 / (1 - 0.2517) = ₹50.25 Cr; Fixed D&A/Interest = ₹247.46 Cr |
| **Slide 3** | 10% Raw Material Shock erases >₹60 Cr, PAT turns to -₹10.9 Cr | In sidebar, set all 7 material price sliders to **+10.0%**, pass-through **50%** | $\Delta\text{Mat} = \text{₹122.3 Cr}$; Recovery = ₹61.15 Cr; EBITDA drop = ₹61.15 Cr; $\text{PBT} = 236.55 - 247.46 = -\text{₹10.91 Cr}$ |
| **Slide 5** | Container Freight baseline $2,172 vs peak $5,937 (2.73x multiplier) | Go to `pages/6_Assumptions_Data_Trace_About.py`, Tab 1 | 165 weekly values; Oct 2023 low ($1342), Jul 2024 peak ($5937), Mar 19, 2026 terminal ($2172) |
| **Slide 7** | Live Copper surge: +54.8% ($14,508 vs FY25 $9,369) | Select preset **Today's market (Live Data)**; check KPI card | Computed directly from `data/raw/Copper Price.xlsx` (Latest Oct 2026 vs FY25 average) |
| **Slide 8** | Red Sea Crisis: Bab el-Mandeb down 72%, Cape rerouting up +220% | View Shock Radar cards on `pages/0_Command_Centre.py` | Computed from `Daily_Chokepoints_Data.xlsx` (2023 avg vs latest 30-day transits) |
| **Slide 10** | Red Sea unmitigated EBITDA falls to ₹168.2 Cr; Cash Gap = ₹22.8 Cr | Select preset **Red Sea / Hormuz crisis**; view `3_Profit_Chain.py` | Freight mult 2.73x, FX 86.5, delay 18d; Cash gap = $\text{Recovery} \times (90/365)$ |
| **Slide 12** | PuLP Optimal Bundle recovers +₹42 Cr under ₹15 Cr Cash Budget | On `pages/5_Action_Matrix.py`, set Budget slider to **₹15.0 Cr** | 0-1 Integer solver maximizes $\sum x_i \cdot \text{Net}_i$ subject to $\sum x_i \cdot \text{Cost}_i \le 15.0$ |

---

## 3. Ten Toughest Judge Questions & Defensive Answers

### Q1: "Why did you override the Statista Rane financials in the dataset?"
**Answer:**  
*"In Section 2 of the hackathon mandate, the organizers explicitly stated: 'Official baseline: Revenue ₹3,421 Cr, EBITDA ₹297.7 Cr (8.7%), PAT ₹37.6 Cr, RM spend ₹1,223 Cr — USE THESE, they override every other file.' When we audited the Statista files, FY2025 revenue was listed as ₹3,863 Cr and net income as ₹107.5 Cr, and FY2021 operating profit contained an obvious unit typo ('3.0'). Rather than blending incompatible numbers, we maintained 100% adherence to the official baseline and documented the reconciliation on our Data Trace page."*

### Q2: "How did you discover that the container freight dates were wrong, and how do you defend re-dating them?"
**Answer:**  
*"The raw file labelled 165 rows as consecutive calendar days between January and June 2023. But in cell I2 of that exact sheet, the author's narrative explicitly said the series runs from January 2023 to March 19, 2026, hitting a low of $1,342 in late October 2023 and a peak of $5,900 in July 2024. Consecutive days in 2023 could not possibly include October 2023 or July 2024! Re-dating the 165 points backwards from 19 March 2026 at weekly 7-day intervals aligns the data with the author's own narrative. On Page 6 of our tool, judges can toggle our interactive Before & After chart."*

### Q3: "Did you convert domestic Indian Steel prices using USD/INR exchange rates?"
**Answer:**  
*"No, absolutely not. The Ministry of Steel dataset specifically states prices in domestic ₹ per metric tonne for HR Coil 2.5mm and CR Coil 0.63mm. Converting them by USD/INR would be a severe error, deflating domestic steel by 85x–95x. In our engine (`engine/chain.py`), Steel HR, Steel CR, and Kottayam Rubber are treated as domestic inputs—they react to commodity shocks and logistics friction, but are never subjected to currency conversion."*

### Q4: "Why did you avoid AutoARIMA for Phenolic Resin?"
**Answer:**  
*"Phenolic Resin contains only 17 irregular data points between June 2024 and September 2026 with huge quarterly gaps and ±40% price swings. Fitting an ARIMA(p,d,q) model with seasonal parameters to 17 points violates statistical degrees of freedom and results in severe overfitting. In Section 4, the mandate advised: 'SHORT series: robust fallback (recent median/naive) with wide empirical bands; Too short to forecast reliably badge.' We implemented a rolling median naive model with 80% and 95% empirical volatility bounds, and badged it clearly for executive transparency."*

### Q5: "How does the ₹60 Cr unhedged shock test work in your engine?"
**Answer:**  
*"At baseline, material spend is ₹1,223 Cr. A 10% unhedged price shock across all 7 inputs increases material spend by exactly ₹122.3 Cr. With the official 50% default OEM pass-through, Rane recovers ₹61.15 Cr, leaving an unrecovered EBITDA reduction of ₹61.15 Cr. Baseline EBITDA falls from ₹297.7 Cr to ₹236.55 Cr. After deducting fixed interest and D&A of ₹247.46 Cr, PBT drops to -₹10.91 Cr. Since taxes cannot be negative without immediate relief, PAT is -₹10.91 Cr. The entire ₹37.6 Cr net profit is wiped out. This is verified automatically in our acceptance test `test_acceptance_2_ten_percent_shock_wipes_out_profit`."*

### Q6: "How did you calibrate the ₹1,223 Cr spend split across the 7 inputs?"
**Answer:**  
*"Because plant-level bills of materials were not in the dataset, we used industry manufacturing logic: Steel HR and CR represent 50% (₹611.5 Cr) because Rane is a premier manufacturer of heavy steering linkages, tie rods, and valve stems. Aluminium accounts for 22% (₹269 Cr) reflecting light-metal casting operations in India and Mexico. Copper, Nickel, Resin, and Rubber make up the remaining 28% for friction materials, brake pads, and valve superalloys. Baseline tonnes were calibrated so that `sum(tonnes_i * base_landed_i)` equals ₹1,223.00 Cr to the exact rupee."*

### Q7: "What is the working capital recovery cash gap, and why is it important?"
**Answer:**  
*"While Rane has contract clauses allowing 50% of cost increases to be passed to OEMs, automotive contracts operate on 60 to 90-day review cycles. Under a ₹180 Cr shock, Rane must pay spot suppliers immediately in cash, but will not receive reimbursement from Maruti or Tata for 2.5 months. At 75 days lag, Rane faces a ₹28 Cr working capital cash gap. At a 9.5% bank borrowing rate, servicing this deficit costs over ₹2.6 Cr annually. Our Action Matrix specifically prioritizes ACT-02 to compress recovery lag from 75 to 30 days."*

### Q8: "How does your Action Matrix ranking change between scenarios?"
**Answer:**  
*"In the Base Case, there are no commodity surges or vessel delays, so operational cost-downs rank highest: ACT-07 (Container Consolidation) is Rank #1 (+₹3.3 Cr net benefit). But when the Red Sea crisis strikes, container freight spikes to $5,937 and maritime delays reach 18 days. The cost of stock-outs skyrockets. In response, our engine re-ranks ACT-02 (Index-linked pricing) and ACT-06 (Cape slot booking) to Rank #1 and #2, delivering over +₹38 Cr in net benefit. This dynamic re-ranking is verified by acceptance test #6."*

### Q9: "What algorithm did you use for the Action Bundle Optimizer?"
**Answer:**  
*"We implemented a 0-1 Integer Linear Program that solves the knapsack optimization problem: maximizing total Net Benefit subject to the user's cash budget constraint. For 9 actionable candidate mitigations, there are $2^9 = 512$ decision states. Our pure-Python branch-and-bound solver evaluates the optimal portfolio in less than 1 millisecond with zero external solver dependencies, ensuring 100% offline stability without binary solver installation errors."*

### Q10: "Can this engine scale to all 17 Rane plants in production?"
**Answer:**  
*"Yes. The architecture is cleanly decoupled into pure-Python engines (`engine/`) and presentation layers (`ui/`). To deploy across all 17 plants, we only need to map each plant's ERP bill of materials (SAP / Oracle) into the `tonnes_map` parameter of `run_all()`. The recalculation engine runs in sub-second time without database bottlenecks and can be deployed in a lightweight Docker container or enterprise Streamlit cloud."*
