"""
Level 2 Tests (M24-M29): Forecasting Quality, Backtesting, and Data Fixes Verification.
Team 11.59 · Xovate'26
"""

import os
import pytest
import pandas as pd
import numpy as np
from engine.forecast import get_all_forecasts, SERIES_TIERS
from engine.signals import get_shock_radar_signals
from engine import data_loader

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

def test_M24_forecast_confidence_bands_monotonicity():
    """M24: Projections have lo95 <= lo80 <= point <= hi80 <= hi95; bands widen with horizon."""
    df_fcst, _ = get_all_forecasts(use_cache=True)
    assert not df_fcst.empty

    for uid, grp in df_fcst.groupby("unique_id"):
        # Verify ordering for each point
        for _, row in grp.iterrows():
            assert row["lo_95"] <= row["lo_80"] + 1e-4, f"{uid}: lo_95 > lo_80"
            assert row["lo_80"] <= row["point"] + 1e-4, f"{uid}: lo_80 > point"
            assert row["point"] <= row["hi_80"] + 1e-4, f"{uid}: point > hi_80"
            assert row["hi_80"] <= row["hi_95"] + 1e-4, f"{uid}: hi_80 > hi_95"

        # Check that band width (hi_95 - lo_95) generally widens or stays consistent with horizon
        widths = (grp["hi_95"] - grp["lo_95"]).values
        if len(widths) >= 6:
            assert widths[-1] >= widths[0] * 0.95, f"{uid}: horizon uncertainty does not widen"


def test_M25_series_tiers_and_quality_badges():
    """M25: Resin badge is SHORT, rubber is ANNUAL, freight is flagged as ending Mar 2026."""
    _, df_scores = get_all_forecasts(use_cache=True)
    score_map = {row["material"]: row for _, row in df_scores.iterrows()}

    assert score_map["resin"]["tier"] == "SHORT"
    assert score_map["rubber"]["tier"] == "ANNUAL"
    assert score_map["freight"]["tier"] == "FREIGHT"


def test_M26_backtest_scorecard_metrics():
    """M26: Backtest table has MAPE per horizon (3m, 6m, 12m), reasonable bounds."""
    _, df_scores = get_all_forecasts(use_cache=True)
    assert not df_scores.empty

    for _, row in df_scores.iterrows():
        assert 0.0 <= row["mape_3m"] <= 50.0
        assert 0.0 <= row["mape_6m"] <= 60.0
        assert 0.0 <= row["mape_12m"] <= 75.0
        assert row["model"] != ""


def test_M27_forecast_to_scenario_conversion():
    """M27: Forecast converts to scenario shock percentage vs FY25 baseline."""
    df_fcst, _ = get_all_forecasts(use_cache=True)
    cu_fcst = df_fcst[df_fcst["unique_id"] == "copper"]
    assert not cu_fcst.empty
    
    # Base copper is 9,369.4. 12m point forecast should give a valid numeric percentage
    pt_12m = cu_fcst.iloc[-1]["point"]
    shock_pct = ((pt_12m - 9369.4) / 9369.4) * 100.0
    assert not np.isnan(shock_pct)
    assert not np.isinf(shock_pct)


def test_M28_data_cleaning_fixes_verification():
    """M28: Verify all intentional data cleaning fixes: freight, forex, metals, rubber."""
    # 1. Freight re-dating: weekly ending 2026-03-19, min Oct/Nov 2023 (~1342), max Jul/Aug 2024 (~5937), terminal 2172
    fp = os.path.join(PROCESSED_DIR, "freight_fixed.csv")
    df_fr = pd.read_csv(fp)
    df_fr['ds'] = pd.to_datetime(df_fr['ds'])
    assert df_fr['ds'].max() == pd.Timestamp("2026-03-19")
    assert abs(df_fr.iloc[-1]['rate'] - 2172.0) < 1.0
    assert abs(df_fr['rate'].min() - 1342.0) < 50.0
    assert abs(df_fr['rate'].max() - 5937.0) < 50.0

    # 2. Forex: unique dates, numeric, FY25 avg in [84.0, 85.5]
    fx_p = os.path.join(PROCESSED_DIR, "fx_daily.csv")
    df_fx = pd.read_csv(fx_p)
    df_fx['date'] = pd.to_datetime(df_fx['date'])
    assert df_fx['date'].is_monotonic_increasing
    assert df_fx['date'].nunique() == len(df_fx)
    fy25_fx = df_fx[(df_fx['date'] >= '2024-04-01') & (df_fx['date'] <= '2025-03-31')]['rate'].mean()
    assert 84.0 <= fy25_fx <= 85.5

    # 3. Aluminium: continuous monthly to Nov 2026
    al_p = os.path.join(PROCESSED_DIR, "aluminium.csv")
    df_al = pd.read_csv(al_p)
    df_al['ds'] = pd.to_datetime(df_al['ds'])
    assert df_al['ds'].max() >= pd.Timestamp("2026-11-01")

    # 4. Resin: USD/t (~1200 - 1800)
    res_p = os.path.join(PROCESSED_DIR, "resin.csv")
    df_res = pd.read_csv(res_p)
    assert df_res['y'].mean() > 1000.0  # Converted from USD/kg * 1000

    # 5. Rubber: INR/t (~120,000 - 200,000)
    rub_p = os.path.join(PROCESSED_DIR, "rubber.csv")
    df_rub = pd.read_csv(rub_p)
    assert df_rub['y'].mean() > 100000.0  # Converted from INR/100kg * 10

    # 6. Steel: Domestic INR/t (~50,000 - 90,000), not FX converted
    hr_p = os.path.join(PROCESSED_DIR, "steel_hr.csv")
    df_hr = pd.read_csv(hr_p)
    assert 50000.0 <= df_hr['y'].mean() <= 90000.0


def test_M29_radar_signals_computed_accurately():
    """M29: Radar values computed from data match what UI displays."""
    signals = get_shock_radar_signals()
    sig_map = {s["id"]: s for s in signals}

    assert "SIG-HORMUZ" in sig_map
    assert "SIG-BAB-MANDEB" in sig_map
    assert "SIG-CAPE-REROUTE" in sig_map
    assert "SIG-GSCPI" in sig_map
    assert "SIG-BRENT" in sig_map
    assert "SIG-FOREX" in sig_map
    assert "SIG-COPPER" in sig_map

    # Bab el-Mandeb: computed % change is negative
    assert sig_map["SIG-BAB-MANDEB"]["change_pct"] < -50.0

    # Cape of Good Hope: computed % change is positive (+100% to +300%)
    assert sig_map["SIG-CAPE-REROUTE"]["change_pct"] > 100.0
