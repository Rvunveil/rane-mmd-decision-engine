"""
Results Dataclass for Rane (Madras) MMD Decision Engine
Holds all financial, operational, inventory, container, and prescriptive action metrics.
"""

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Results:
    scenario_name: str
    
    # Financial Statement Metrics (₹ Crores)
    revenue_cr: float
    ebitda_cr: float
    ebitda_margin_pct: float
    pbt_cr: float
    tax_cr: float
    pat_cr: float
    
    # Cost Drivers & Shock Deltas (₹ Crores)
    material_spend_cr: float
    ocean_freight_spend_cr: float
    delta_material_cr: float
    delta_freight_cr: float
    oem_recovery_cr: float
    lost_contribution_cr: float
    working_capital_gap_cr: float
    
    # Granular Landed Cost per Tonne Breakdown
    landed_costs: dict[str, dict[str, Any]] = field(default_factory=dict)
    
    # Division Allocation Breakdown
    division_costs: dict[str, dict[str, Any]] = field(default_factory=dict)
    
    # Inventory Runway & Alert Metrics
    inventory_summary: list[dict[str, Any]] = field(default_factory=list)
    worst_days_of_cover: float = 0.0
    worst_material_name: str = ""
    worst_runway_margin_days: float = 0.0
    
    # Container Logistics Breakdown
    containers: list[dict[str, Any]] = field(default_factory=list)
    avg_container_payload_pct: float = 0.0
    avg_freight_per_tonne_inr: float = 0.0
    
    # Prescriptive Action Matrix
    action_rankings: list[dict[str, Any]] = field(default_factory=list)
    top_action_id: str = ""
    top_action_title: str = ""
    top_action_net_benefit_cr: float = 0.0
