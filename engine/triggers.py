"""
Dynamic Andon Trigger Playbook Engine (N7)
Rane (Madras) MMD Decision Engine · Team 11.59 · Xovate'26

Evaluates 7 mission-critical operational triggers across ocean logistics, commodity surges,
working capital drag, and plant buffer inventories to drive prescriptive Andon playbooks.
"""

import os
from typing import Any
import yaml
from engine.scenario import Scenario
from engine.results import Results

TRIGGERS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "triggers.yaml")


def load_triggers_config() -> list[dict]:
    if os.path.exists(TRIGGERS_PATH):
        with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get("triggers", [])
    return []


def evaluate_andon_triggers(
    scenario: Scenario,
    results: Results,
    triggers_cfg: list = None
) -> list[dict[str, Any]]:
    """
    Evaluates trigger state (GREEN, AMBER, RED) for all 7 playbook triggers under active scenario.
    """
    if triggers_cfg is None:
        triggers_cfg = load_triggers_config()

    evaluated = []

    for t in triggers_cfg:
        tid = t.get("id")
        metric_name = t.get("metric", "")
        
        # Extract live metric value
        if metric_name == "shipping_delay_days":
            val = scenario.shipping_delay_days
            unit = " days"
            status = "RED" if val > 12 else ("AMBER" if val > 5 else "GREEN")
            threshold = "Safe: <=5d | Warning: >5d | Danger: >12d"

        elif metric_name == "copper_shock_pct":
            val = scenario.price_shock_pct.get("copper", 0.0)
            unit = "%"
            status = "RED" if val > 25.0 else ("AMBER" if val > 10.0 else "GREEN")
            threshold = "Safe: <=10% | Warning: >10% | Danger: >25%"

        elif metric_name == "aluminium_shock_pct":
            val = scenario.price_shock_pct.get("aluminium", 0.0)
            unit = "%"
            status = "RED" if val > 20.0 else ("AMBER" if val > 10.0 else "GREEN")
            threshold = "Safe: <=10% | Warning: >10% | Danger: >20%"

        elif metric_name == "freight_multiplier":
            val = scenario.freight_multiplier
            unit = "x"
            status = "RED" if val > 2.2 else ("AMBER" if val > 1.4 else "GREEN")
            threshold = "Safe: <=1.4x | Warning: >1.4x | Danger: >2.2x"

        elif metric_name == "working_capital_gap_cr":
            val = results.working_capital_gap_cr
            unit = " Cr"
            status = "RED" if val > 16.0 else ("AMBER" if val > 8.0 else "GREEN")
            threshold = "Safe: <=₹8 Cr | Warning: >₹8 Cr | Danger: >₹16 Cr"

        elif metric_name == "worst_days_of_cover":
            val = results.worst_days_of_cover
            unit = " days"
            status = "RED" if val <= 20.0 else ("AMBER" if val <= 35.0 else "GREEN")
            threshold = "Safe: >35d | Warning: <=35d | Danger: <=20d"

        elif metric_name == "fx_inr_usd":
            val = scenario.fx_inr_usd
            unit = " ₹/$"
            status = "RED" if val > 92.0 else ("AMBER" if val > 87.0 else "GREEN")
            threshold = "Safe: <=₹87 | Warning: >₹87 | Danger: >₹92"

        else:
            val = 0.0
            unit = ""
            status = "GREEN"
            threshold = "N/A"

        evaluated.append({
            "id": tid,
            "name": t.get("name", tid),
            "category": t.get("category", "General"),
            "status": status,
            "metric_name": metric_name,
            "current_value": val,
            "current_value_formatted": f"{val:.1f}{unit}" if isinstance(val, float) else f"{val}{unit}",
            "threshold_rule": threshold,
            "owner": t.get("owner", "MMD"),
            "playbook_action": t.get("playbook_action", "ACT-01"),
            "mitigation_sop": t.get("mitigation_sop", "")
        })

    return evaluated
