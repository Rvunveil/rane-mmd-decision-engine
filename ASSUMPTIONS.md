# ASSUMPTIONS.md · Rane (Madras) MMD Decision Engine
**Event:** Xovate'26 Management Hackathon  
**Team 11.59:** Vikram T · Sayoni Dan · Trisha Pal · XIME Chennai  
**Governing Standard:** Section 4 & 7 of the Hackathon Mandate  

---

## 1. Overview & Governance

The official hackathon problem statement provides macroeconomic datasets (LME metals, Ministry of Steel, RBI Forex, NY Fed GSCPI, maritime chokepoints) alongside Rane's official baseline financials (Revenue ₹3,421 Cr, EBITDA ₹297.7 Cr, PAT ₹37.6 Cr, Material Spend ₹1,223 Cr, Freight Spend ₹25 Cr). 

However, plant-level bill of materials (BOM), division allocations, inventory holdings, and corporate tax schedules are not provided in the raw files. In accordance with Section 0 and Section 4 of the prompt, Team 11.59 has established **defensible, transparent assumptions**, labelled them in the UI with `[TEAM ASSUMPTION]` badges, and verified them through automated unit and acceptance tests.

Every assumption is editable in the UI and can be audited live by judges.

---

## 2. Raw Material Spend Breakdown (₹1,223.0 Cr)

The ₹1,223 Cr raw material spend across the 7 inputs is calibrated against the FY25 baseline average prices derived from the cleaned raw datasets:

| Commodity Input | Category | Currency | Spend Share | Annual Spend | FY25 Base Price | Calibrated Tonnes | Engineering Rationale |
|---|---|---|---|---|---|---|---|
| **Steel HR Coil (2.5mm)** | Domestic Coil | INR | 28.0% | **₹ 342.44 Cr** | ₹ 60,442 / t | 56,656 t | Primary feedstock for steering gears, linkages, tie rods, and chassis members. |
| **Steel CR Coil (0.63mm)** | Domestic Coil | INR | 22.0% | **₹ 269.06 Cr** | ₹ 69,066 / t | 38,957 t | Precision cold-formed steering columns and valve stem guides. |
| **Aluminium (LME Cash)** | Imported Ingot | USD | 22.0% | **₹ 269.06 Cr** | $2,526 / t | 12,596 t | Light-metal die casting plants in India and Queretaro, Mexico. |
| **Copper Cathode** | Imported Metal | USD | 10.0% | **₹ 122.30 Cr** | $9,369 / t | 1,544 t | Electric power steering components, sensor wiring, friction heat dispersants. |
| **Nickel Metal** | Imported Metal | USD | 6.0% | **₹ 73.38 Cr** | $16,553 / t | 524 t | Superalloy additions for heat-resistant internal combustion engine valves. |
| **Phenolic Resin** | Imported Organic | USD | 6.0% | **₹ 73.38 Cr** | $1,437 / t | 5,992 t | Thermosetting polymer binder for automotive brake linings and friction pads. |
| **Natural Rubber (RSS-4)** | Domestic Ag | INR | 6.0% | **₹ 73.38 Cr** | ₹ 140,197 / t | 5,234 t | Kottayam RSS-4 for flexible dust boots, bushings, and vibration isolators. |
| **TOTAL** | — | — | **100.0%** | **₹ 1,223.00 Cr** | — | — | *Exact calibration to official handout baseline.* |

---

## 3. Division Allocation & Raw Material Mix

Rane (Madras) operates four core manufacturing divisions. Material spend is allocated using a product-specific weighting matrix:

| Division | Revenue Share | Material Share | Base Material Spend | Dominant Inputs | Operating Plants |
|---|---|---|---|---|---|
| **Steering & Linkages** | 42.0% | 40.0% | ₹ 489.20 Cr | Steel HR (45%), Steel CR (35%), Aluminium (12%), Rubber (5%), Copper (3%) | Puducherry, Pantnagar, Sanand |
| **Light-Metal Castings** | 28.0% | 27.0% | ₹ 330.21 Cr | Aluminium (72%), Copper (10%), Steel HR (10%), Steel CR (8%) | Chennai, Queretaro (Mexico) |
| **Friction Materials & Brake Pads** | 16.0% | 18.0% | ₹ 220.14 Cr | Resin (32%), Rubber (28%), Copper (20%), Steels (20%) | Ambattur, Hyderabad |
| **Engine Valves** | 14.0% | 15.0% | ₹ 183.45 Cr | Steel CR (40%), Nickel (35%), Steel HR (15%), Others (10%) | Viralimalai, Tumkur |

---

## 4. Financial & Tax Parameters

- **Corporate Income Tax Rate:** **25.17%**  
  *Rationale:* Prescribed effective corporate tax rate in India under Section 115BAA of the Income Tax Act (22% base + 10% surcharge + 4% health & education cess).
- **Fixed Below-EBITDA Expenses (D&A + Net Interest):** **₹ 247.46 Cr**  
  *Mathematical Derivation:*  
  $$\text{Base PBT} = \frac{\text{Base PAT (₹37.6 Cr)}}{1 - 0.2517} = \text{₹ 50.247 Cr}$$  
  $$\text{Fixed Charges} = \text{Base EBITDA (₹297.7 Cr)} - \text{Base PBT (₹50.247 Cr)} = \text{₹ 247.453 Cr}$$
- **Contribution Margin on Volume Variance:** **28.0%**  
  *Rationale:* Standard variable margin contribution in Tier-1 auto components. If vehicle production volume drops by -10%, lost contribution equals $3,421 \times 10\% \times 28\% = \text{₹ 95.8 Cr}$.
- **Short-Term Borrowing Interest Rate:** **9.5% p.a.**  
  *Rationale:* Working capital cash-credit borrowing rate in Indian commercial banks.

---

## 5. Inventory & Supply Chain Parameters

- **Target Safety Stock Service Level:** **95.0%** ($z = 1.65$).
- **Maximum 40ft Container Payload:** **26.0 tonnes**.
- **Domestic Transport Freight & Handling:**
  - Steel HR: ₹2,500 / t freight + ₹1,500 / t handling
  - Steel CR: ₹2,800 / t freight + ₹1,600 / t handling
  - Rubber: ₹3,500 / t freight + ₹1,200 / t handling
- **Import Surcharges & Customs Duties:**
  - Copper: 5.0% base customs duty
  - Nickel: 2.5% base customs duty
  - Aluminium: 7.5% base customs duty
  - Phenolic Resin: 7.5% base customs duty
  - Additional Tariff Surcharge: 0.0% at baseline, adjustable via slider up to 25.0%.
- **Supplier Lead Times (Baseline):**
  - Copper: 42 days (Chile/Peru via Cape/Suez)
  - Nickel: 45 days (Indonesia/Europe)
  - Aluminium: 35 days (Middle East smelters)
  - Resin: 40 days (East Asian petrochemical plants)
  - Rubber: 21 days (Kerala domestic market)
  - Steel HR/CR: 25–28 days (Domestic integrated mills)

---

## 6. V2 Upgrade Parameters & Calibrations

- **Container Consolidation Benefit (ACT-07):**  
  Calibrated benefit moving from current average payload ($89.7\%$ in raw sample data) to target payload ($98.0\%$):  
  $$\text{Freight Reduction Fraction} = 1.0 - \frac{89.7}{98.0} = 8.469\%$$  
  $$\text{Net Benefit} = \text{Freight Spend} \times 8.469\% - \text{₹1.2 Cr packaging redesign}$$
- **Monte Carlo Profit-at-Risk Engine (N3):**  
  2,000 multivariate joint disruption paths with fixed seed ($42$). Covariance matrix $D \times R \times D$ calibrated against historical annual price volatilities (Cu 14.5%, Al 12.8%, Ni 16.2%, Steels 9.5%, Resin 18.0%, Freight 28.0%, FX 4.5%, Demand 6.0%) and empirical metal/energy/freight correlations.
- **OEM Price Recovery Partitioning (N5):**  
  Partitioned across Rane's 4 core operating divisions: Steering (40%), Castings (27%), Friction (18%), Engine Valves (15%). Matches total contractual reimbursement to $0.001$ Cr.
- **Dynamic Andon Triggers (N7):**  
  7 operational triggers governing Red Sea maritime diversions (>12d RED), LME Copper (>25% RED), LME Aluminium (>20% RED), Freight multiplier (>2.2x RED), Cash gap (>₹16 Cr RED), Days of cover (<=20d RED), and FX depreciation (>₹92 RED).
- **Cross-Functional Ripple Lenses (N8):**  
  Simultaneous tracking of 7 departments: MMD (Procurement), Finance (Working Capital), Production (Line Starvation), HR/IR (Overtime), Quality (PPAP), Logistics (Demurrage), and Sales (OEM OTIF).
