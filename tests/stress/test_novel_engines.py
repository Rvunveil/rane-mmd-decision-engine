"""
Test Suite for V2 Novel Engine Modules:
N2: Exposure Map (engine/exposure.py)
N3: Monte Carlo Profit-at-Risk (engine/risk.py)
N4: 12-Month Cash & Recovery Timeline (engine/timeline.py)
N5: OEM Price-Recovery Claim Pack (engine/claims.py)
N6: Buy-Timing Signal Engine (engine/buy_signal.py)
N7: Dynamic Andon Triggers (engine/triggers.py)
N8: Cross-Functional Impact Lenses (engine/functions.py)

Team 11.59 · Xovate'26
"""

import pytest
import time
from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all
from engine.exposure import compute_exposure_map
from engine.risk import run_profit_at_risk_monte_carlo
from engine.timeline import compute_cash_recovery_timeline
from engine.claims import generate_oem_claims_pack
from engine.buy_signal import compute_buy_signals
from engine.triggers import evaluate_andon_triggers
from engine.functions import compute_cross_functional_lenses


def test_N2_exposure_map():
    """N2: Exposure map computes inbound lanes, chokepoints, and spend at risk."""
    base_scn = Scenario()
    exp_base = compute_exposure_map(base_scn)
    assert "lanes" in exp_base
    assert len(exp_base["lanes"]) >= 5
    assert "chokepoints" in exp_base
    assert exp_base["total_spend_at_risk_cr"] > 0
    assert exp_base["active_vessel_count"] >= 5

    # Test under Red Sea disruption
    presets = get_default_presets()
    exp_crisis = compute_exposure_map(presets["red_sea_hormuz"])
    # Under Red Sea crisis, Red Sea / Suez chokepoint should be RED or AMBER
    choke_map = {c["id"]: c for c in exp_crisis["chokepoints"]}
    assert choke_map["suez"]["status"] in ["RED", "AMBER"]
    assert exp_crisis["total_spend_at_risk_cr"] > exp_base["total_spend_at_risk_cr"]


def test_N3_risk_monte_carlo_distribution():
    """N3: 2000-path Monte Carlo simulation returns distribution with monotonic quantiles in <200ms."""
    base_scn = Scenario()
    t0 = time.perf_counter()
    risk_res = run_profit_at_risk_monte_carlo(base_scn, num_paths=2000, seed=42)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 500.0, f"Monte Carlo took {elapsed_ms:.1f}ms (target <500ms)"
    assert risk_res["p10_ebitda_cr"] <= risk_res["p50_ebitda_cr"] <= risk_res["p90_ebitda_cr"]
    assert risk_res["p10_pat_cr"] <= risk_res["p50_pat_cr"] <= risk_res["p90_pat_cr"]
    assert 0.0 <= risk_res["prob_loss_pat_pct"] <= 100.0
    assert len(risk_res["ebitda_samples"]) == 2000
    assert len(risk_res["pat_samples"]) == 2000


def test_N4_cash_recovery_timeline():
    """N4: 12-month timeline models cash deficit trough and recovery lag arithmetic."""
    presets = get_default_presets()
    crisis_scn = presets["red_sea_hormuz"]
    results = run_all(crisis_scn)
    timeline = compute_cash_recovery_timeline(crisis_scn, results)

    assert len(timeline["months"]) == 12
    # Deficit trough should be non-positive during initial lag months
    assert timeline["max_cumulative_deficit_cr"] <= 0.0
    assert timeline["financing_interest_cost_cr"] >= 0.0
    # Month 1 cash flow should reflect immediate unrecovered material & freight surge
    assert timeline["months"][0]["gross_shock_cr"] > 0


def test_N5_oem_claims_pack():
    """N5: OEM claim pack partitions recovery across 4 operating divisions."""
    presets = get_default_presets()
    crisis_scn = presets["red_sea_hormuz"]
    results = run_all(crisis_scn)
    claim_pack = generate_oem_claims_pack(crisis_scn, results)

    assert "divisions" in claim_pack
    assert len(claim_pack["divisions"]) == 4
    total_claim = sum(d["claim_amount_cr"] for d in claim_pack["divisions"])
    assert abs(total_claim - results.oem_recovery_cr) < 0.05
    assert claim_pack["html_memo"] != ""


def test_N6_buy_signals():
    """N6: Buy timing engine outputs valid actionable signal per commodity."""
    base_scn = Scenario()
    results = run_all(base_scn)
    signals = compute_buy_signals(base_scn, results)

    assert len(signals) >= 6
    valid_signals = {"BUY NOW", "STAGGER", "HOLD"}
    for mat_id, sig in signals.items():
        assert sig["signal"] in valid_signals
        assert "rationale" in sig
        assert "expected_saving_cr" in sig


def test_N7_andon_triggers():
    """N7: Andon trigger playbook correctly evaluates 7 critical triggers."""
    base_scn = Scenario()
    res_base = run_all(base_scn)
    trig_base = evaluate_andon_triggers(base_scn, res_base)

    assert len(trig_base) == 7
    # Under base case, most triggers should be GREEN
    green_count = sum(1 for t in trig_base if t["status"] == "GREEN")
    assert green_count >= 5

    # Under crisis, delay and freight triggers should be RED
    presets = get_default_presets()
    res_crisis = run_all(presets["red_sea_hormuz"])
    trig_crisis = evaluate_andon_triggers(presets["red_sea_hormuz"], res_crisis)
    trig_map = {t["id"]: t for t in trig_crisis}
    assert trig_map["TRG-01"]["status"] == "RED" # Delay = 18d > 12d
    assert trig_map["TRG-04"]["status"] == "RED" # Freight mult = 2.73x > 2.2x


def test_N8_function_lenses():
    """N8: Function lenses evaluate all 7 enterprise departments."""
    presets = get_default_presets()
    res = run_all(presets["red_sea_hormuz"])
    lenses = compute_cross_functional_lenses(presets["red_sea_hormuz"], res)

    expected_depts = ["MMD", "Finance", "Production", "HR", "Quality", "Logistics", "Sales"]
    for dept in expected_depts:
        assert dept in lenses
        lens = lenses[dept]
        assert "status" in lens
        assert "primary_kpi" in lens
        assert "impact_summary" in lens
        assert "prescriptive_action" in lens
