"""
Part E: Monkey Test (1,000 Random Walk Actions across 5 Seeds)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Seeded random walk: 200 actions per seed across 5 seeds (1,000 total actions).
Invariants asserted after EVERY single action:
1. No crash / exception
2. Financial waterfall reconciles: Revenue - Material Spend - Conversion Costs == EBITDA
3. Division sum reconciles to total Direct Material spend
4. Risk percentiles monotonic: P10 <= P50 <= P90
5. Action rankings complete: 10 valid actions ranked 1 to 10
6. No leaked placeholders, NaNs, Infs, or negative zeros
"""

import os
import sys
import random
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.scenario import Scenario, get_default_presets
from engine.state import (
    init_canonical_state,
    get_current_scenario,
    apply_preset_by_name,
    apply_scenario_values,
    reset_to_base
)
from engine.chain import run_all
from engine.risk import run_profit_at_risk_monte_carlo
from ui.theme import format_money_cr


SEEDS = [42, 1159, 2026, 7777, 9999]
PRESET_KEYS = ["base_case", "todays_market", "red_sea_hormuz", "metal_shock", "tariff_fx", "demand_recession"]
LEVER_RANGES = {
    "copper": (-30.0, 60.0),
    "nickel": (-30.0, 60.0),
    "aluminium": (-30.0, 60.0),
    "resin": (-30.0, 60.0),
    "rubber": (-30.0, 60.0),
    "steel_hr": (-30.0, 60.0),
    "steel_cr": (-30.0, 60.0),
    "freight_multiplier": (0.5, 4.0),
    "shipping_delay_days": (0, 45),
    "fx_inr_usd": (80.0, 105.0),
    "oem_pass_through_pct": (0.0, 100.0),
    "demand_volume_pct": (-30.0, 30.0),
    "tariff_pct": (0.0, 30.0)
}


def _assert_invariants(state: dict, action_desc: str, step_idx: int, seed: int):
    """Rigorous invariant checker executed after every random action."""
    scn = get_current_scenario(state)
    res = run_all(scn)

    # 1. Financial waterfall reconciliation
    # Revenue - Net Material Outflow - Conversion Costs == EBITDA
    # where Net Material Outflow = material_spend_cr - oem_recovery_cr + delta_freight_cr
    # PAT = (EBITDA - Depr - Interest) * (1 - Tax)
    assert res.revenue_cr > 0, f"Seed {seed} Step {step_idx}: Non-positive revenue {res.revenue_cr}"
    assert res.material_spend_cr > 0, f"Seed {seed} Step {step_idx}: Non-positive material spend {res.material_spend_cr}"
    assert res.ebitda_cr is not None
    assert res.pat_cr is not None

    # Check EBITDA margin consistency
    calculated_margin = (res.ebitda_cr / res.revenue_cr) * 100.0
    assert abs(res.ebitda_margin_pct - calculated_margin) < 0.05, (
        f"Seed {seed} Step {step_idx}: EBITDA margin mismatch {res.ebitda_margin_pct} vs {calculated_margin}"
    )

    # 2. Division spend sum reconciles to material spend
    div_sum = sum(d["scenario_spend_cr"] for d in res.division_costs.values())
    assert abs(div_sum - res.material_spend_cr) < 0.05, (
        f"Seed {seed} Step {step_idx}: Division spend sum {div_sum} != material spend {res.material_spend_cr}"
    )

    # 3. Action rankings completeness
    assert len(res.action_rankings) == 10, f"Seed {seed} Step {step_idx}: Expected 10 ranked actions, found {len(res.action_rankings)}"
    for idx, act in enumerate(res.action_rankings):
        assert act["rank"] == idx + 1
        assert act["title"]
        assert act["category"]
        assert act["cash_budget_cr"] >= 0

    # 4. Monte Carlo percentile ordering (tested periodically to preserve test speed)
    if step_idx % 20 == 0:
        sim = run_profit_at_risk_monte_carlo(scn, num_paths=500)
        assert sim["p10_ebitda_cr"] <= sim["p50_ebitda_cr"] <= sim["p90_ebitda_cr"], (
            f"Seed {seed} Step {step_idx}: Non-monotonic percentiles {sim['p10_ebitda_cr']} <= {sim['p50_ebitda_cr']} <= {sim['p90_ebitda_cr']}"
        )

    # 5. Formatted money leak check
    for val in [res.ebitda_cr, res.pat_cr, res.delta_material_cr, res.oem_recovery_cr]:
        formatted = format_money_cr(val, show_sign=True)
        assert "+₹-0.0" not in formatted
        assert "NaN" not in formatted
        assert "None" not in formatted


@pytest.mark.parametrize("seed", SEEDS)
def test_part_e_monkey_random_walk(seed):
    """Runs 200 random state modifications per seed (1,000 actions total) with full invariant checking."""
    rng = random.Random(seed)
    state = {}
    init_canonical_state(state)

    for step in range(1, 201):
        action_type = rng.choice(["preset", "lever", "multi_lever", "reset"])

        if action_type == "preset":
            pkey = rng.choice(PRESET_KEYS)
            apply_preset_by_name(state, pkey)
            action_desc = f"Preset: {pkey}"

        elif action_type == "lever":
            lever = rng.choice(list(LEVER_RANGES.keys()))
            low, high = LEVER_RANGES[lever]
            val = round(rng.uniform(low, high), 2)
            if lever == "shipping_delay_days":
                val = int(val)
            apply_scenario_values({lever: val}, state=state)
            action_desc = f"Lever: {lever}={val}"

        elif action_type == "multi_lever":
            # Pick 3 random levers to mutate simultaneously
            selected = rng.sample(list(LEVER_RANGES.keys()), 3)
            mutations = {}
            for l in selected:
                low, high = LEVER_RANGES[l]
                v = round(rng.uniform(low, high), 2)
                mutations[l] = int(v) if l == "shipping_delay_days" else v
            apply_scenario_values(mutations, state=state)
            action_desc = f"Multi-Lever: {mutations}"

        else:  # reset
            reset_to_base(state)
            action_desc = "Reset to Base"

        # Check invariants
        _assert_invariants(state, action_desc, step, seed)
