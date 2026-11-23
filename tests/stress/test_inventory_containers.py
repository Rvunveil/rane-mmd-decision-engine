"""
Level 2 Tests (M18-M20): Inventory Runways & Container Logistics.
Team 11:59 · Xovate'26
"""

import pytest
from engine.scenario import Scenario
from engine.chain import run_all
from engine.inventory import evaluate_inventory, evaluate_containers
import tests.oracle as oracle

def test_M18_inventory_hand_calc_oracle_match():
    """M18: Days of cover, safety stock, ROP and status match oracle for imported & domestic."""
    res = run_all(Scenario())
    
    # Check imported (Copper)
    cu_actual = next(r for r in res.inventory_summary if r["material_id"] == "copper")
    cu_oracle = oracle.oracle_inventory_item("copper", added_delay_days=0)
    assert abs(cu_actual["days_of_cover"] - cu_oracle["days_of_cover"]) < 0.1
    assert abs(cu_actual["safety_stock_tonnes"] - cu_oracle["safety_stock"]) < 0.1
    assert abs(cu_actual["reorder_point_tonnes"] - cu_oracle["rop"]) < 0.1
    assert cu_actual["status"] == cu_oracle["status"]

    # Check domestic (Steel HR)
    hr_actual = next(r for r in res.inventory_summary if r["material_id"] == "steel_hr")
    hr_oracle = oracle.oracle_inventory_item("steel_hr", added_delay_days=0)
    assert abs(hr_actual["days_of_cover"] - hr_oracle["days_of_cover"]) < 0.1
    assert abs(hr_actual["safety_stock_tonnes"] - hr_oracle["safety_stock"]) < 0.1
    assert abs(hr_actual["reorder_point_tonnes"] - hr_oracle["rop"]) < 0.1
    assert hr_actual["status"] == hr_oracle["status"]


def test_M19_delay_monotonic_degradation():
    """M19: Delay 0 -> 15 -> 30 -> 45 days: imported runway margin decreases monotonically."""
    delays = [0, 15, 30, 45]
    res_list = [run_all(Scenario(shipping_delay_days=d)) for d in delays]

    # For imported material (Aluminium), runway margin must decrease monotonically
    al_margins = [
        next(r for r in res.inventory_summary if r["material_id"] == "aluminium")["runway_margin_days"]
        for res in res_list
    ]
    for i in range(len(al_margins) - 1):
        assert al_margins[i] > al_margins[i + 1]

    # Domestic material (Steel HR) shipping delay is 0, so margin remains unaffected
    hr_margins = [
        next(r for r in res.inventory_summary if r["material_id"] == "steel_hr")["runway_margin_days"]
        for res in res_list
    ]
    for i in range(len(hr_margins) - 1):
        assert hr_margins[i] == hr_margins[i + 1]


def test_M20_container_metrics_formula_match():
    """M20: Container payload %, freight ₹/t, and ETA match oracle."""
    freight_mult = 2.5
    fx = 90.0
    delay = 15
    scn = Scenario(freight_multiplier=freight_mult, fx_inr_usd=fx, shipping_delay_days=delay)
    res = run_all(scn)
    orc_containers = oracle.oracle_containers(freight_mult=freight_mult, fx=fx, delay_days=delay)

    assert len(res.containers) == len(orc_containers)
    for act, exp in zip(res.containers, orc_containers):
        assert abs(act["payload_pct"] - exp["payload_pct"]) < 0.01
        assert abs(act["freight_cost_per_tonne_inr"] - exp["freight_per_t_inr"]) < 0.01
        assert act["effective_eta_days"] == exp["effective_eta"]
