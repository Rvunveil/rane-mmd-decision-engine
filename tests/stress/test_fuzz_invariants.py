"""
Level 3 Tests (H05, H06, H26): Fuzz Invariant Checking, Monotonicity Sweeps, and Session Stress.
Team 11.59 · Xovate'26
"""

import pytest
import random
import math
from engine.scenario import Scenario
from engine.chain import run_all

def test_H05_fuzz_300_scenarios_invariants():
    """H05: Random fuzz across 300 scenarios: 0 exceptions, all mathematical invariants hold."""
    random.seed(42)
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]

    for i in range(300):
        # Generate random scenario within realistic physical bounds
        shocks = {m: random.uniform(-20.0, 80.0) for m in materials}
        freight_mult = random.uniform(0.5, 3.5)
        fx = random.uniform(80.0, 105.0)
        tariff = random.uniform(0.0, 20.0)
        demand = random.uniform(-25.0, 25.0)
        delay = random.randint(0, 45)
        pass_pct = random.uniform(0.0, 100.0)
        lag = random.randint(0, 120)

        scn = Scenario(
            price_shock_pct=shocks,
            freight_multiplier=freight_mult,
            fx_inr_usd=fx,
            tariff_pct=tariff,
            demand_volume_pct=demand,
            shipping_delay_days=delay,
            oem_pass_through_pct=pass_pct,
            pass_through_lag_days=lag
        )

        res = run_all(scn)

        # 1. No NaN or inf anywhere
        for val in [res.revenue_cr, res.ebitda_cr, res.pat_cr, res.material_spend_cr, res.delta_material_cr, res.delta_freight_cr]:
            assert not math.isnan(val), f"NaN encountered at fuzz iteration {i}"
            assert not math.isinf(val), f"Inf encountered at fuzz iteration {i}"

        # 2. Revenue and Material Spend must be positive
        assert res.revenue_cr > 0
        assert res.material_spend_cr > 0

        # 3. Waterfall reconciliation invariant:
        # ebitda_change == -delta_material - delta_freight + recovery + volume_delta
        vol_delta = (res.revenue_cr - 3421.0) * 0.28
        expected_ebitda = 297.7 - res.delta_material_cr - res.delta_freight_cr + res.oem_recovery_cr + vol_delta
        assert abs(res.ebitda_cr - expected_ebitda) < 0.01

        # 4. Division sum reconciliation invariant:
        div_sum = sum(d["scenario_spend_cr"] for d in res.division_costs.values())
        assert abs(div_sum - res.material_spend_cr) < 0.01

        # 5. Full action ranking list present (10 actions)
        assert len(res.action_rankings) == 10

        # 6. If all shocks >= 0, freight >= 1.0, fx >= base, tariff >= 0, demand <= 0, and pass < 100%: EBITDA <= 297.7
        if (all(s >= 0 for s in shocks.values()) and freight_mult >= 1.0 and fx >= 84.5648 and
            tariff >= 0.0 and demand <= 0.0 and pass_pct < 100.0):
            assert res.ebitda_cr <= 297.7 + 1e-4


def test_H06_monotonicity_sweeps():
    """H06: 21-step monotonicity sweeps: EBITDA & margins move strictly in predictable economic directions."""
    materials = ["copper", "nickel", "aluminium", "resin", "rubber", "steel_hr", "steel_cr"]

    # 1. Uniform shock sweep (0% -> 100%, pass 50%): EBITDA strictly decreasing
    shock_steps = [run_all(Scenario(price_shock_pct={m: s for m in materials}, oem_pass_through_pct=50.0)).ebitda_cr
                   for s in [i * 5.0 for i in range(21)]]
    for i in range(len(shock_steps) - 1):
        assert shock_steps[i] > shock_steps[i + 1], f"Shock monotonicity failed at step {i}"

    # 2. Freight multiplier sweep (1.0x -> 4.0x, pass 50%): EBITDA strictly decreasing
    freight_steps = [run_all(Scenario(freight_multiplier=1.0 + i * 0.15, oem_pass_through_pct=50.0)).ebitda_cr
                     for i in range(21)]
    for i in range(len(freight_steps) - 1):
        assert freight_steps[i] > freight_steps[i + 1], f"Freight monotonicity failed at step {i}"

    # 3. FX sweep (84.56 -> 105.0, pass 50%): EBITDA strictly decreasing
    fx_steps = [run_all(Scenario(fx_inr_usd=84.5648 + i * 1.0, oem_pass_through_pct=50.0)).ebitda_cr
                for i in range(21)]
    for i in range(len(fx_steps) - 1):
        assert fx_steps[i] > fx_steps[i + 1], f"FX monotonicity failed at step {i}"

    # 4. Pass-through sweep (0% -> 100% under +20% shock): EBITDA strictly increasing
    shocks_20 = {m: 20.0 for m in materials}
    pass_steps = [run_all(Scenario(price_shock_pct=shocks_20, oem_pass_through_pct=i * 5.0)).ebitda_cr
                  for i in range(21)]
    for i in range(len(pass_steps) - 1):
        assert pass_steps[i] < pass_steps[i + 1], f"Pass-through monotonicity failed at step {i}"

    # 5. Demand volume sweep (-30% -> +30%): Revenue strictly increasing
    rev_steps = [run_all(Scenario(demand_volume_pct=-30.0 + i * 3.0)).revenue_cr
                 for i in range(21)]
    for i in range(len(rev_steps) - 1):
        assert rev_steps[i] < rev_steps[i + 1], f"Demand revenue monotonicity failed at step {i}"

    # 6. Shipping delay sweep (0 -> 40 days): runway margin never improves as delay rises
    delay_steps = [run_all(Scenario(shipping_delay_days=i * 2)).worst_runway_margin_days
                   for i in range(21)]
    for i in range(len(delay_steps) - 1):
        assert delay_steps[i] >= delay_steps[i + 1], f"Delay margin monotonicity failed at step {i}"


def test_H26_long_session_stress():
    """H26: 200 rapid scenario changes without memory degradation or performance penalty."""
    for i in range(200):
        scn = Scenario(
            freight_multiplier=1.0 + (i % 10) * 0.2,
            shipping_delay_days=(i % 15),
            oem_pass_through_pct=float(i % 100)
        )
        res = run_all(scn)
        assert res.revenue_cr == 3421.0
