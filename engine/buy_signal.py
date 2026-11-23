"""
Buy-Timing Signal Engine (N6)
Rane (Madras) MMD Decision Engine · Team 11:59 · Xovate'26

Generates algorithmic buy-timing recommendations for MMD procurement buyers:
'BUY NOW' (Front-Load), 'STAGGER' (Tranche / Dollar-Cost Average), or 'HOLD' (Buffer Draw-Down).
"""

from typing import Any
from engine.scenario import Scenario
from engine.results import Results
from engine.data_loader import load_assumptions


def compute_buy_signals(
    scenario: Scenario,
    results: Results,
    assumptions: dict = None
) -> dict[str, dict[str, Any]]:
    """
    Evaluates optimal purchase timing per material based on inventory runway,
    effective lead times, and forward price volatility.
    """
    if assumptions is None:
        assumptions = load_assumptions()

    inv_map = {item.get("material_id", item.get("material", "")): item for item in results.inventory_summary}
    signals = {}

    materials = ["copper", "aluminium", "nickel", "steel_hr", "steel_cr", "resin", "rubber"]

    for mat in materials:
        inv = inv_map.get(mat, {})
        cover_days = inv.get("days_of_cover", 30.0)
        eff_lt = inv.get("effective_lead_time", 25)
        stock_status = inv.get("status", "Covered / Safe")
        shock_pct = scenario.price_shock_pct.get(mat, 0.0)

        # Base annual spend in Cr
        cfg = assumptions.get("materials", {}).get(mat, {})
        spend_share = float(cfg.get("spend_share_pct", 10.0))
        base_annual_spend = 1223.0 * (spend_share / 100.0)

        # Decision rules
        if cover_days <= eff_lt or shock_pct >= 20.0:
            # Urgent stock-out risk or steep price appreciation
            sig = "BUY NOW"
            badge_class = "buy-signal-buy-now"
            saving = base_annual_spend * (shock_pct / 100.0) * (30.0 / 365.0) if shock_pct > 0 else 0.85
            if cover_days <= eff_lt:
                rationale = f"Stock runway ({cover_days:.0f}d) breached effective lead time ({eff_lt}d). Front-load purchase order immediately to prevent line halt."
            else:
                rationale = f"Price shock (+{shock_pct:.1f}%) signals steep upward momentum. Front-load 45-day requirements to lock spot prices."

        elif cover_days <= 35.0 or (10.0 <= shock_pct < 20.0):
            # Moderate runway / moderate shock
            sig = "STAGGER"
            badge_class = "buy-signal-stagger"
            saving = base_annual_spend * 0.03 # 3% volatility variance reduction
            rationale = f"Runway is adequate ({cover_days:.0f}d) but volatility is elevated (+{shock_pct:.1f}%). Split monthly PO into 3 tranches to dollar-cost average."

        else:
            # High cover, stable or negative price movement
            sig = "HOLD"
            badge_class = "buy-signal-hold"
            # Carrying cost saved on 15 days of inventory at 9.5%
            saving = base_annual_spend * (15.0 / 365.0) * 0.095
            rationale = f"Comfortable buffer ({cover_days:.0f}d cover vs {eff_lt}d LT). Hold spot purchases and draw down existing inventory to conserve ₹{saving:.2f} Cr working capital."

        signals[mat] = {
            "signal": sig,
            "badge_class": badge_class,
            "rationale": rationale,
            "expected_saving_cr": round(max(saving, 0.1), 2),
            "days_of_cover": round(cover_days, 1),
            "effective_lead_time": eff_lt,
            "status": stock_status
        }

    return signals
