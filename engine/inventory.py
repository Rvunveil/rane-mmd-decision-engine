"""
Inventory Runway & Inbound Container Simulation Models
Team 11:59 · Xovate'26
"""

import math
from typing import Any
from engine.scenario import Scenario

def evaluate_inventory(scenario: Scenario, assumptions: dict, annual_tonnes_map: dict[str, float]) -> tuple[list[dict[str, Any]], float, str, float, str]:
    """
    Evaluates inventory coverage vs supplier lead times + shipping delays.
    Returns: (inventory_summary_list, worst_days_of_cover, worst_days_material_name, worst_runway_margin_days, worst_margin_material_name)
    """
    materials_cfg = assumptions.get("materials", {})
    summary = []
    
    worst_days = 999.0
    worst_days_mat = ""
    worst_margin = 999.0
    worst_margin_mat = ""

    for mat_id, cfg in materials_cfg.items():
        tonnes_yr = annual_tonnes_map.get(mat_id, 1000.0)
        daily_usage = tonnes_yr / 365.0
        
        stock_tonnes = float(cfg.get("stock_on_hand_tonnes", 500.0))
        days_of_cover = stock_tonnes / daily_usage if daily_usage > 0 else 999.0
        
        supplier_lt = int(cfg.get("supplier_lead_time_days", 30))
        # Shipping delay only affects imported materials
        is_import = cfg.get("import_dependent", True)
        added_delay = scenario.shipping_delay_days if is_import else 0
        effective_lt = supplier_lt + added_delay
        
        # Safety Stock = z * sigma_daily * sqrt(effective_lt)
        sigma_pct = float(cfg.get("daily_usage_sigma_pct", 15.0)) / 100.0
        sigma_daily = daily_usage * sigma_pct
        z = float(cfg.get("service_level_z", 1.65))
        safety_stock = z * sigma_daily * math.sqrt(max(effective_lt, 1))
        
        # Reorder Point = (daily_usage * effective_lt) + safety_stock
        rop_tonnes = (daily_usage * effective_lt) + safety_stock
        
        # Status calculation
        margin_days = days_of_cover - effective_lt
        if days_of_cover < effective_lt:
            status = "Stock-out Risk"
            status_color = "red"
        elif stock_tonnes <= rop_tonnes:
            status = "Watch / Reorder"
            status_color = "amber"
        else:
            status = "Covered / Safe"
            status_color = "green"
            
        if days_of_cover < worst_days:
            worst_days = days_of_cover
            worst_days_mat = cfg.get("name", mat_id)
            
        if margin_days < worst_margin:
            worst_margin = margin_days
            worst_margin_mat = cfg.get("name", mat_id)

        summary.append({
            "material_id": mat_id,
            "material_name": cfg.get("name", mat_id),
            "stock_on_hand_tonnes": stock_tonnes,
            "daily_usage_tonnes": daily_usage,
            "days_of_cover": days_of_cover,
            "supplier_lead_time": supplier_lt,
            "effective_lead_time": effective_lt,
            "safety_stock_tonnes": safety_stock,
            "reorder_point_tonnes": rop_tonnes,
            "runway_margin_days": margin_days,
            "status": status,
            "status_color": status_color,
            "primary_origin": cfg.get("primary_origin", "Global"),
            "import_dependent": is_import
        })

    return summary, worst_days, worst_days_mat, worst_margin, worst_margin_mat


def evaluate_containers(scenario: Scenario, assumptions: dict) -> tuple[list[dict[str, Any]], float, float]:
    """
    Evaluates inbound container shipments, payload %, and freight ₹/t.
    B6 fix: In Base case (delay 0), routes and ETAs show normal on-schedule transit.
    Under disruption (delay > 0), routes reflect rerouting via Cape and Hormuz convoy delays.
    """
    container_cfg = assumptions.get("container_logistics", {})
    max_payload = float(container_cfg.get("max_payload_tonnes", 26.0))
    shipments = container_cfg.get("sample_inbound_shipments", [])
    
    current_freight_usd = 2172.0 * scenario.freight_multiplier
    current_freight_inr = current_freight_usd * scenario.fx_inr_usd
    
    processed_shipments = []
    total_payload_pct = 0.0
    total_freight_per_t = 0.0

    delay = scenario.shipping_delay_days

    for s in shipments:
        cargo_t = float(s.get("cargo_tonnes", 20.0))
        payload_pct = min((cargo_t / max_payload) * 100.0, 100.0)
        freight_per_t = current_freight_inr / cargo_t if cargo_t > 0 else 0.0
        
        base_eta = int(s.get("eta_days", 20))
        mat = s.get("material", "")

        # Dynamic routing and transit status based on active scenario delay
        is_delayed = "Bottleneck" in s.get("status", "") or "Disrupted" in s.get("route", "")
        if delay == 0:
            if mat == "copper":
                route = "Suez Canal / Direct Maritime"
                status = "In Transit / On Schedule"
            elif mat == "aluminium":
                route = "Strait of Hormuz (Normal Transit)"
                status = "In Transit / On Schedule"
            elif mat == "nickel":
                route = "Strait of Malacca (Normal Transit)"
                status = "In Transit / On Schedule"
            elif mat == "resin":
                route = "East China Sea -> Malacca"
                status = "In Transit / On Schedule"
            else:
                route = "Standard Ocean Lane"
                status = "In Transit / On Schedule"
            effective_eta = base_eta
        else:
            if mat == "copper":
                route = "Cape of Good Hope (Rerouted from Suez)"
                status = f"Diverted (+{delay}d transit)" if is_delayed else "In Transit"
            elif mat == "aluminium":
                route = "Strait of Hormuz (Disrupted / Convoy)"
                status = f"Delayed / Bottleneck (+{delay}d)"
            elif mat == "nickel":
                route = "Strait of Malacca (Normal Transit)"
                status = "On Schedule"
            elif mat == "resin":
                route = "East China Sea -> Malacca"
                status = "On Schedule"
            else:
                route = s.get("route", "Disrupted Ocean Lane")
                status = f"Delayed (+{delay}d)"
            effective_eta = base_eta + (delay if is_delayed else 0)

        processed_shipments.append({
            "id": s.get("id"),
            "material": mat,
            "origin": s.get("origin"),
            "route": route,
            "cargo_tonnes": cargo_t,
            "payload_pct": payload_pct,
            "base_eta_days": base_eta,
            "effective_eta_days": effective_eta,
            "status": status,
            "carrier": s.get("carrier"),
            "freight_cost_per_tonne_inr": freight_per_t
        })
        
        total_payload_pct += payload_pct
        total_freight_per_t += freight_per_t

    n = max(len(shipments), 1)
    avg_payload = total_payload_pct / n
    avg_freight_t = total_freight_per_t / n

    return processed_shipments, avg_payload, avg_freight_t
