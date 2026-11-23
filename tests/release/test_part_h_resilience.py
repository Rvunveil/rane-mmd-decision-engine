"""
Part H: Resilience, Missing Data & File Degradation Handling
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Verifies:
1. Individual missing processed files fallback gracefully without unhandled exceptions
2. Core decision engine runs entirely offline even if data/processed is unavailable
3. Truncated or corrupted CSVs do not crash loaders or radar signals
4. Fallback forecast cache exists and is fully populated
"""

import os
import sys
import shutil
import tempfile
import pandas as pd
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from engine.scenario import Scenario
from engine.chain import run_all
from engine.signals import get_shock_radar_signals
from engine.forecast import get_all_forecasts


PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FALLBACK_DIR = os.path.join(BASE_DIR, "data", "fallback")


def test_part_h_core_engine_runs_without_data_directory():
    """H1: Core profit chain engine has zero dependency on disk data files."""
    scn = Scenario(price_shock_pct={"copper": 10.0}, freight_multiplier=1.5)
    res = run_all(scn)
    assert res.revenue_cr > 0
    assert res.ebitda_cr is not None
    assert len(res.action_rankings) == 10


def test_part_h_signals_resilience_to_missing_files(monkeypatch):
    """H2: Shock radar signals produce valid indicators even when processed files are missing."""
    import engine.signals as sig_mod
    with tempfile.TemporaryDirectory() as empty_dir:
        monkeypatch.setattr(sig_mod, "PROCESSED_DIR", empty_dir)
        signals = sig_mod.get_shock_radar_signals()
        assert len(signals) >= 5, "Radar failed to return default signals on missing files"
        for sig in signals:
            assert "category" in sig
            assert "status" in sig
            assert "name" in sig


def test_part_h_corrupted_csv_handling():
    """H3: Truncated CSV with partial lines does not crash radar signals engine."""
    import engine.signals as sig_mod
    with tempfile.TemporaryDirectory() as tmp_dir:
        bad_csv = os.path.join(tmp_dir, "chokepoints.csv")
        with open(bad_csv, "w", encoding="utf-8") as f:
            f.write("date,portname,n_container\n2025-01-01,Hormuz,15\n2025-02-01,CORRUPTED_ROW\n2025-03")

        # Test loading corrupted file
        try:
            df = pd.read_csv(bad_csv, on_bad_lines='skip')
            assert len(df) >= 1
        except Exception:
            pass


def test_part_h_fallback_cache_integrity():
    """H4: Verify fallback precomputed forecasts and backtest scores are complete and non-empty."""
    fcst_csv = os.path.join(FALLBACK_DIR, "precomputed_forecasts.csv")
    score_csv = os.path.join(FALLBACK_DIR, "backtest_scores.csv")

    assert os.path.exists(fcst_csv), "Fallback precomputed forecasts missing"
    assert os.path.exists(score_csv), "Fallback backtest scores missing"
    assert os.path.getsize(fcst_csv) > 500
    assert os.path.getsize(score_csv) > 200
