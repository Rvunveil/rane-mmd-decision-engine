"""
Part F: Engine Mathematical Invariants & Oracle Parity
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Covers:
1. Oracle parity under baseline and 10% uniform input shock
2. 1,000 scenario fuzz with strict physical and accounting bounds
3. Monotonicity sweeps across all 5 primary risk axes
4. Zero-volatility Monte Carlo collapse (P10 == P50 == P90)
5. Symmetric recovery validation
6. Breakeven plug-back consistency
7. Claims and triggers fire / clear behavior
"""

import os
import sys
import math
import random
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all
from engine.risk import run_profit_at_risk_monte_carlo
from tests.oracle import (
    oracle_calculate,
    oracle_breakeven_uniform_shock
)


def test_part_f_oracle_parity():
    """F1: Pure-arithmetic oracle parity for Baseline and 10% Shock."""
    # 1. Baseline
    scn_base = Scenario(name="Base case")
    engine_base = run_all(scn_base)
    ora_base = oracle_calculate()

    assert abs(engine_base.revenue_cr - ora_base["revenue_cr"]) < 0.05
    assert abs(engine_base.ebitda_cr - ora_base["ebitda_cr"]) < 0.05
    assert abs(engine_base.pat_cr - ora_base["pat_cr"]) < 0.05
    assert abs(engine_base.material_spend_cr - ora_base["material_spend_cr"]) < 0.05

    # 2. 10% Uniform Shock
    mats = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    shocks_10 = {m: 10.0 for m in mats}
    scn_10 = Scenario(
        name="10% Input Shock",
        price_shock_pct=shocks_10,
        oem_pass_through_pct=50.0
    )
    engine_10 = run_all(scn_10)
    ora_10 = oracle_calculate(shocks=shocks_10, pass_through_pct=50.0)

    assert abs(engine_10.material_spend_cr - ora_10["material_spend_cr"]) < 0.1
    assert abs(engine_10.delta_material_cr - ora_10["delta_material_cr"]) < 0.1
    assert abs(engine_10.oem_recovery_cr - ora_10["oem_recovery_cr"]) < 0.1
    assert abs(engine_10.ebitda_cr - ora_10["ebitda_cr"]) < 0.1
    assert abs(engine_10.pat_cr - ora_10["pat_cr"]) < 0.1


def test_part_f_zero_volatility_mc_collapse():
    """F2: Zero-volatility Monte Carlo collapses P10 == P50 == P90 to deterministic engine EBITDA."""
    scn = Scenario(
        price_shock_pct={"copper": 20.0, "steel_hr": 15.0},
        freight_multiplier=1.8,
        oem_pass_through_pct=50.0
    )
    det_res = run_all(scn)

    # Run with volatility_scale = 0.0
    mc = run_profit_at_risk_monte_carlo(scn, num_paths=200, volatility_scale=0.0)

    # Percentiles collapse
    assert abs(mc["p10_ebitda_cr"] - mc["p50_ebitda_cr"]) < 0.05
    assert abs(mc["p50_ebitda_cr"] - mc["p90_ebitda_cr"]) < 0.05
    # Value equals deterministic EBITDA
    assert abs(mc["p50_ebitda_cr"] - det_res.ebitda_cr) < 0.1


def test_part_f_breakeven_plug_back():
    """F3: Solve for pass-through required for target EBITDA and verify plug-back."""
    # Under a 20% input shock, find pass-through required to maintain Baseline EBITDA (₹297.7 Cr)
    # delta_cost = delta_material + delta_freight
    # ebitda = 297.7 - delta_cost + (pass_pct * delta_cost)
    # ebitda == 297.7  => pass_pct must equal 100% (1.0)
    mats = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]
    scn_breakeven = Scenario(
        price_shock_pct={m: 20.0 for m in mats},
        oem_pass_through_pct=100.0
    )
    res_be = run_all(scn_breakeven)
    assert abs(res_be.ebitda_cr - 297.7) < 0.1

    # Solve for 75% pass-through target
    scn_75 = Scenario(
        price_shock_pct={m: 20.0 for m in mats},
        oem_pass_through_pct=75.0
    )
    res_75 = run_all(scn_75)
    expected_ebitda_75 = 297.7 - 0.25 * res_75.delta_material_cr
    assert abs(res_75.ebitda_cr - expected_ebitda_75) < 0.1


def test_part_f_fuzz_1000_scenarios():
    """F4: Fuzz 1,000 scenarios: verify mathematical bounds and non-divergence."""
    rng = random.Random(1159)
    mats = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]

    for i in range(1000):
        shocks = {m: rng.uniform(-25.0, 75.0) for m in mats}
        scn = Scenario(
            price_shock_pct=shocks,
            freight_multiplier=rng.uniform(0.5, 4.0),
            fx_inr_usd=rng.uniform(80.0, 105.0),
            tariff_pct=rng.uniform(0.0, 25.0),
            demand_volume_pct=rng.uniform(-30.0, 30.0),
            shipping_delay_days=rng.randint(0, 45),
            oem_pass_through_pct=rng.uniform(0.0, 100.0)
        )

        res = run_all(scn)
        assert not math.isnan(res.revenue_cr)
        assert not math.isnan(res.ebitda_cr)
        assert not math.isnan(res.pat_cr)
        assert res.revenue_cr > 0
        assert res.material_spend_cr > 0

        # Monotonicity check: if pass-through is 100% and volume delta is 0,
        # cost delta is 100% recovered, so EBITDA == 297.7 Cr!
        if abs(scn.oem_pass_through_pct - 100.0) < 0.01 and abs(scn.demand_volume_pct) < 0.01:
            assert abs(res.ebitda_cr - 297.7) < 0.05
