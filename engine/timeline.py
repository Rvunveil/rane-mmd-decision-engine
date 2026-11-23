"""
12-Month Cash & OEM Recovery Timeline Engine (N4)
Rane (Madras) MMD Decision Engine · Team 11.59 · Xovate'26

Models month-by-month cash drain and working capital trough caused by the
60-90 day OEM contractual price recovery lag, computing peak deficit and financing interest drag.
"""

import math
from typing import Any
from engine.scenario import Scenario
from engine.results import Results
from engine.data_loader import load_assumptions

MONTH_NAMES = ["M1 (Apr)", "M2 (May)", "M3 (Jun)", "M4 (Jul)", "M5 (Aug)", "M6 (Sep)",
               "M7 (Oct)", "M8 (Nov)", "M9 (Dec)", "M10 (Jan)", "M11 (Feb)", "M12 (Mar)"]


def compute_cash_recovery_timeline(
    scenario: Scenario,
    results: Results,
    assumptions: dict = None
) -> dict[str, Any]:
    """
    Computes 12-month dynamic cash flow profile, working capital trough, and interest drag.
    """
    if assumptions is None:
        assumptions = load_assumptions()

    wc_interest_rate = float(assumptions.get("financial_params", {}).get("working_capital_interest_pct", 9.5)) / 100.0
    lag_days = scenario.pass_through_lag_days

    # Annual figures
    annual_gross_shock = results.delta_material_cr + results.delta_freight_cr
    annual_recovery = results.oem_recovery_cr

    monthly_gross_shock = annual_gross_shock / 12.0
    monthly_recovery_target = annual_recovery / 12.0

    # Lag in fractional months (e.g. 75 days / 30 = 2.5 months)
    lag_months_exact = lag_days / 30.416
    first_full_recovery_month = int(math.ceil(lag_months_exact))

    months_data = []
    cum_cash = 0.0
    max_deficit = 0.0
    trough_month = 1
    total_interest_cost = 0.0

    for m in range(1, 13):
        gross_cost = monthly_gross_shock
        
        # OEM payout ramp based on lag days
        if m < first_full_recovery_month:
            # Complete lag: zero cash received from OEMs
            recovery_cash = 0.0
        elif m == first_full_recovery_month:
            # Partial ramp in the transition month
            fraction = (m - lag_months_exact)
            recovery_cash = monthly_recovery_target * max(min(fraction, 1.0), 0.2)
        else:
            # Steady-state recovery cash flowing in
            recovery_cash = monthly_recovery_target

        net_cash = recovery_cash - gross_cost
        cum_cash += net_cash

        if cum_cash < max_deficit:
            max_deficit = cum_cash
            trough_month = m

        # Monthly interest cost on outstanding negative cash deficit
        monthly_borrowing_cost = (abs(cum_cash) * (wc_interest_rate / 12.0)) if cum_cash < 0 else 0.0
        total_interest_cost += monthly_borrowing_cost

        months_data.append({
            "month_no": m,
            "month_name": MONTH_NAMES[m - 1],
            "gross_shock_cr": round(gross_cost, 2),
            "oem_recovery_cr": round(recovery_cash, 2),
            "net_cash_flow_cr": round(net_cash, 2),
            "cumulative_cash_deficit_cr": round(cum_cash, 2),
            "interest_accrued_cr": round(monthly_borrowing_cost, 3)
        })

    return {
        "months": months_data,
        "max_cumulative_deficit_cr": round(max_deficit, 2),
        "trough_month": trough_month,
        "trough_month_name": MONTH_NAMES[trough_month - 1],
        "financing_interest_cost_cr": round(total_interest_cost, 2),
        "working_capital_interest_rate_pct": wc_interest_rate * 100.0,
        "lag_days": lag_days
    }
