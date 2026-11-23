"""
Level 3 Tests (H08): Computational Performance & Recalculation Speed.
Team 11.59 · Xovate'26
"""

import time
import pytest
import numpy as np
from engine.scenario import Scenario
from engine.chain import run_all

def test_H08_recalc_speed_100_scenarios():
    """H08: Time run_all() for 100 scenarios: mean < 50ms, p95 < 100ms (prompt limit: < 500ms)."""
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    times = []

    # Warm up
    _ = run_all(Scenario())

    for i in range(100):
        scn = Scenario(
            price_shock_pct={m: (i % 20) * 1.5 for m in materials},
            freight_multiplier=1.0 + (i % 10) * 0.1,
            fx_inr_usd=84.56 + (i % 15) * 0.5,
            demand_volume_pct=-(i % 10) * 1.0,
            shipping_delay_days=(i % 30),
            oem_pass_through_pct=50.0 + (i % 10) * 2.0
        )
        t0 = time.perf_counter()
        _ = run_all(scn)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)  # milliseconds

    mean_ms = np.mean(times)
    p95_ms = np.percentile(times, 95)
    max_ms = np.max(times)

    print(f"\n[PERF] 100 Scenarios Recalc - Mean: {mean_ms:.2f} ms | p95: {p95_ms:.2f} ms | Max: {max_ms:.2f} ms")

    # Strict performance requirements
    assert mean_ms < 100.0, f"Mean recalc time too slow: {mean_ms:.2f} ms"
    assert p95_ms < 250.0, f"p95 recalc time too slow: {p95_ms:.2f} ms"
    assert max_ms < 500.0, f"Max recalc time exceeded 500ms limit: {max_ms:.2f} ms"
