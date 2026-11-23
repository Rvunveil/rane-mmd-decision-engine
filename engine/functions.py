"""
Cross-Functional Impact Lenses Engine (N8)
Rane (Madras) MMD Decision Engine · Team 11:59 · Xovate'26

Translates active scenario disruptions into 7 department-specific operational perspectives:
MMD, Finance, Production, HR/IR, Quality, Logistics, and Commercial Sales.
"""

from typing import Any
from engine.scenario import Scenario
from engine.results import Results
from engine.data_loader import load_assumptions


def compute_cross_functional_lenses(
    scenario: Scenario,
    results: Results,
    assumptions: dict = None
) -> dict[str, dict[str, Any]]:
    """
    Computes department-specific KPIs, impact summaries, and prescriptive actions.
    """
    if assumptions is None:
        assumptions = load_assumptions()

    total_cost_delta = results.delta_material_cr + results.delta_freight_cr
    ebitda_diff = results.ebitda_cr - 297.70
    min_cover = results.worst_days_of_cover
    delay = scenario.shipping_delay_days
    freight_mult = scenario.freight_multiplier

    lenses = {}

    # 1. MMD (Materials Management)
    mmd_status = "RED" if total_cost_delta > 40.0 else ("AMBER" if total_cost_delta > 15.0 else "GREEN")
    lenses["MMD"] = {
        "title": "Materials Management (MMD)",
        "status": mmd_status,
        "primary_kpi": f"Δ ₹{total_cost_delta:+.1f} Cr Spend",
        "impact_summary": f"Gross purchase order cost expansion of ₹{total_cost_delta:.1f} Cr across imported copper, aluminium ingots, and steels. High spot exposure on unhedged volumes.",
        "prescriptive_action": "ACT-01: Execute 60-day forward hedge on LME copper/aluminium to lock in price ceilings."
    }

    # 2. Finance & Treasury
    fin_status = "RED" if ebitda_diff < -30.0 or results.working_capital_gap_cr > 15.0 else ("AMBER" if ebitda_diff < -10.0 else "GREEN")
    lenses["Finance"] = {
        "title": "Finance & Treasury",
        "status": fin_status,
        "primary_kpi": f"₹{results.working_capital_gap_cr:.1f} Cr Cash Gap",
        "impact_summary": f"EBITDA margin compresses to {results.ebitda_margin_pct:.1f}% (vs 8.7% base). Operating cash flow impaired by ₹{results.working_capital_gap_cr:.1f} Cr due to 75-day OEM recovery lag.",
        "prescriptive_action": "ACT-02: Enforce 30-day indexation clause to eliminate working capital cash trough."
    }

    # 3. Production & Shop Floor
    prod_status = "RED" if min_cover <= 20.0 else ("AMBER" if min_cover <= 35.0 else "GREEN")
    lenses["Production"] = {
        "title": "Production Operations",
        "status": prod_status,
        "primary_kpi": f"{min_cover:.0f}d Min Cover ({results.worst_material_name})",
        "impact_summary": f"Assembly lines vulnerable to stock-out in {results.worst_material_name}. Takt times at risk across steering and casting machining cells.",
        "prescriptive_action": "ACT-09: Re-sequence plant shift schedules to prioritize models with ample domestic steel inventory."
    }

    # 4. Human Resources & Industrial Relations
    hr_status = "RED" if delay > 15 else ("AMBER" if delay > 5 else "GREEN")
    lenses["HR"] = {
        "title": "HR & Industrial Relations",
        "status": hr_status,
        "primary_kpi": f"{'+2 Weekend Shifts' if delay > 12 else 'Standard Shifts'}",
        "impact_summary": "Erratic batch arrivals from shipping delays trigger unscheduled overtime shifts, increasing operator fatigue and wage premiums by ₹1.8–3.2 Cr.",
        "prescriptive_action": "ACT-09: Implement overtime smoothing protocol and balanced takt time rosters."
    }

    # 5. Quality Assurance & Metallurgical Engineering
    qual_status = "AMBER" if delay > 10 or total_cost_delta > 30.0 else "GREEN"
    lenses["Quality"] = {
        "title": "Quality & PPAP Engineering",
        "status": qual_status,
        "primary_kpi": "Standard Spec Integrity" if qual_status == "GREEN" else "Fast-Track PPAP Watch",
        "impact_summary": "Emergency sourcing of domestic secondary smelter ingots requires accelerated PPAP Level-3 approvals to ensure zero porosity defects in steering housings.",
        "prescriptive_action": "ACT-08: Pre-qualify alternative low-nickel alloys with Tier-1 OEM technical sign-off."
    }

    # 6. Logistics & Inbound Transportation
    log_status = "RED" if freight_mult > 2.0 or delay > 12 else ("AMBER" if freight_mult > 1.3 or delay > 4 else "GREEN")
    lenses["Logistics"] = {
        "title": "Ocean & Inland Logistics",
        "status": log_status,
        "primary_kpi": f"{freight_mult:.2f}x Freight Rate (+{delay}d)",
        "impact_summary": f"Container freight landed cost elevated. Average container payload at {results.avg_container_payload_pct:.1f}%; port dwell time threatens demurrage charges.",
        "prescriptive_action": "ACT-07: Consolidate inbound containers into 25.5t dense high-cube FCLs to save 8.47% freight spend."
    }

    # 7. Sales & OEM Key Account Management
    sales_status = "RED" if results.oem_recovery_cr < (total_cost_delta * 0.4) and total_cost_delta > 20.0 else ("AMBER" if total_cost_delta > 15.0 else "GREEN")
    lenses["Sales"] = {
        "title": "Sales & Commercial OEM",
        "status": sales_status,
        "primary_kpi": f"₹{results.oem_recovery_cr:.1f} Cr Reimbursed",
        "impact_summary": f"Customer negotiations required with Maruti, Tata, and M&M. Delivery schedules must be re-baselined to preserve 100% OTIF and avoid demerit penalties.",
        "prescriptive_action": "ACT-02: Issue OEM Claim Pack detailing verified LME/ICEMA price movements for quarterly reimbursement."
    }

    return lenses
