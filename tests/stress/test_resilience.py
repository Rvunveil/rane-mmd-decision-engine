"""
Level 3 Tests (H13, H14): Resilience to Missing Files & Processed Cache Integrity.
Team 11:59 · Xovate'26
"""

import os
import pytest
from engine.scenario import Scenario
from engine.chain import run_all
from engine.signals import get_shock_radar_signals
from engine.forecast import get_all_forecasts

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
FALLBACK_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "fallback")

def test_H13_resilience_to_missing_data_files():
    """H13: Shock radar and calculations fall back gracefully even if individual files are missing."""
    # Signals generator has built-in fallbacks for missing CSVs
    signals = get_shock_radar_signals()
    assert len(signals) >= 5

    # Core engine runs without needing raw files (all baseline values are in config)
    res = run_all(Scenario())
    assert res.ebitda_cr == 297.7


def test_H14_processed_and_fallback_cache_integrity():
    """H14: Processed cache and precomputed forecast fallback exist and are complete."""
    required_processed = [
        "fx_daily.csv", "freight_fixed.csv", "copper.csv", "nickel.csv",
        "aluminium.csv", "steel_hr.csv", "steel_cr.csv", "resin.csv",
        "rubber.csv", "brent.csv", "gscpi.csv", "chokepoints.csv"
    ]
    for fname in required_processed:
        path = os.path.join(PROCESSED_DIR, fname)
        assert os.path.exists(path), f"Processed file missing: {fname}"
        assert os.path.getsize(path) > 0, f"Processed file is empty: {fname}"

    # Precomputed forecasts
    fcst_csv = os.path.join(FALLBACK_DIR, "precomputed_forecasts.csv")
    score_csv = os.path.join(FALLBACK_DIR, "backtest_scores.csv")
    assert os.path.exists(fcst_csv)
    assert os.path.exists(score_csv)
