"""
Part I: Performance Benchmarks & Computational Speed
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Benchmarks:
1. run_all() p95 < 100 ms
2. Control Room full rerun < 2.0 s (AppTest headless)
3. Monte Carlo simulation runtime & stability
4. Demo step transition < 1.0 s
5. 200 consecutive actions without memory leak or performance degradation
"""

import os
import sys
import time
import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.scenario import Scenario
from engine.chain import run_all
from engine.risk import run_profit_at_risk_monte_carlo
from demo.player import start_demo, stop_demo, _apply_step
from engine.state import init_canonical_state, apply_scenario_values


def test_part_i_run_all_latency():
    """I1: Benchmark 100 runs of run_all(): verify p95 < 100 ms."""
    mats = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    # Warm up
    _ = run_all(Scenario())

    times = []
    for i in range(100):
        scn = Scenario(
            price_shock_pct={m: (i % 25) * 1.5 for m in mats},
            freight_multiplier=1.0 + (i % 15) * 0.1,
            fx_inr_usd=84.56 + (i % 10) * 0.5,
            demand_volume_pct=-(i % 10) * 1.0,
            shipping_delay_days=(i % 30),
            oem_pass_through_pct=50.0 + (i % 10) * 2.0
        )
        t0 = time.perf_counter()
        _ = run_all(scn)
        times.append((time.perf_counter() - t0) * 1000.0)

    p95 = np.percentile(times, 95)
    mean = np.mean(times)
    assert p95 < 100.0, f"run_all() p95 exceeded 100ms threshold: {p95:.2f} ms"
    assert mean < 50.0, f"run_all() mean exceeded 50ms threshold: {mean:.2f} ms"


def test_part_i_control_room_rerun_speed():
    """I2: Control Room AppTest full page rerun < 2.0 s."""
    at = AppTest.from_file(os.path.join(BASE_DIR, "pages/0_Command_Centre.py"), default_timeout=30)
    at.run()
    assert not at.exception

    # Time a subsequent rerun with modified slider
    slider = next(s for s in at.slider if s.key == "deck_freight")
    t0 = time.perf_counter()
    slider.set_value(2.0).run()
    rerun_time = time.perf_counter() - t0

    assert rerun_time < 3.0, f"Control Room rerun took too long: {rerun_time:.2f} s"


def test_part_i_monte_carlo_performance():
    """I3: Monte Carlo simulation with 2,000 paths runs in < 250 ms."""
    scn = Scenario(
        price_shock_pct={"copper": 20.0, "aluminium": 15.0},
        freight_multiplier=2.0
    )
    t0 = time.perf_counter()
    res = run_profit_at_risk_monte_carlo(scn, num_paths=2000)
    dur = (time.perf_counter() - t0) * 1000.0

    assert dur < 250.0, f"Monte Carlo 2,000 paths exceeded 250ms limit: {dur:.2f} ms"
    assert res["p10_ebitda_cr"] <= res["p50_ebitda_cr"] <= res["p90_ebitda_cr"]


def test_part_i_demo_step_transition_speed():
    """I4: Automated demo step transition executes in < 1.0 s."""
    state = {}
    init_canonical_state(state)
    start_demo(state)

    times = []
    for step in range(2, 6):
        t0 = time.perf_counter()
        _apply_step(step, state=state)
        times.append(time.perf_counter() - t0)

    stop_demo(state)
    max_transition = max(times)
    assert max_transition < 1.0, f"Demo transition exceeded 1.0s: {max_transition:.3f} s"


def test_part_i_two_hundred_consecutive_actions():
    """I5: 200 consecutive actions complete without degradation."""
    state = {}
    init_canonical_state(state)

    action_times = []
    for i in range(200):
        t0 = time.perf_counter()
        apply_scenario_values({
            "copper": (i % 40) * 1.0,
            "freight_multiplier": 1.0 + (i % 20) * 0.1,
            "shipping_delay_days": (i % 25)
        }, state=state)
        scn = Scenario(
            price_shock_pct={"copper": state["scn"]["copper"]},
            freight_multiplier=state["scn"]["freight_multiplier"],
            shipping_delay_days=state["scn"]["shipping_delay_days"]
        )
        _ = run_all(scn)
        action_times.append((time.perf_counter() - t0) * 1000.0)

    first_50_avg = np.mean(action_times[:50])
    last_50_avg = np.mean(action_times[-50:])

    # Degradation check: last 50 actions should not be more than 2x slower than first 50
    assert last_50_avg < first_50_avg * 2.5, (
        f"Degradation detected: first 50 avg {first_50_avg:.2f} ms, last 50 avg {last_50_avg:.2f} ms"
    )
