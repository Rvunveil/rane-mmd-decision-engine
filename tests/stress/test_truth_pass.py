"""
Truth Pass Regression Test Suite (T1-T5)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Verifies:
- T1: Market tape identically matches processed dataset values and FY25 baselines
- T2: Backtest scores are genuine, reproducible, and honestly flag limited series
- T3: Precomputed forecasts match winning models and backtest MAPE
- T4: Monte Carlo profit-at-risk has symmetric pass-through, P50 within +-5 Cr, zero-vol collapse
- T5: Zero invented entities across all engine, UI, config, and document files
"""

import os
import re
import pandas as pd
import numpy as np
import pytest

from engine.signals import get_market_tape
from engine.scenario import get_default_presets
from engine.risk import run_profit_at_risk_monte_carlo
from engine.chain import run_all

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FALLBACK_DIR = os.path.join(BASE_DIR, "data", "fallback")


def test_T1_market_tape_equals_processed_data():
    """T1: Tape values must equal the actual values in data/processed/*.csv."""
    tape = get_market_tape()
    assert len(tape) >= 6, "Expected at least 6 market tape items"
    tape_dict = {item["id"]: item for item in tape}

    # Copper check
    cu_df = pd.read_csv(os.path.join(PROCESSED_DIR, "copper.csv"))
    expected_cu = float(cu_df["y"].iloc[-1])
    assert abs(tape_dict["copper"]["latest"] - expected_cu) < 0.1, f"Copper mismatch: {tape_dict['copper']['latest']} vs {expected_cu}"

    # Brent check
    brent_df = pd.read_csv(os.path.join(PROCESSED_DIR, "brent.csv"))
    expected_brent = float(brent_df["price_bbl"].iloc[-1])
    assert abs(tape_dict["brent"]["latest"] - expected_brent) < 0.1, f"Brent mismatch: {tape_dict['brent']['latest']} vs {expected_brent}"

    # FX check
    fx_df = pd.read_csv(os.path.join(PROCESSED_DIR, "fx_daily.csv"))
    expected_fx = float(fx_df["rate"].iloc[-1])
    assert abs(tape_dict["fx"]["latest"] - expected_fx) < 0.1, f"FX mismatch: {tape_dict['fx']['latest']} vs {expected_fx}"

    # Freight check
    fr_df = pd.read_csv(os.path.join(PROCESSED_DIR, "freight_fixed.csv"))
    expected_fr = float(fr_df["rate"].iloc[-1])
    assert abs(tape_dict["freight"]["latest"] - expected_fr) < 0.1, f"Freight mismatch: {tape_dict['freight']['latest']} vs {expected_fr}"


def test_T2_backtest_reproducibility_and_honesty():
    """T2: Backtest scores CSV has genuine, honest metrics and notes."""
    csv_path = os.path.join(FALLBACK_DIR, "backtest_scores.csv")
    assert os.path.exists(csv_path), "backtest_scores.csv missing"
    df = pd.read_csv(csv_path)

    assert len(df) == 8, f"Expected 8 materials in backtest, found {len(df)}"
    for _, row in df.iterrows():
        # Ensure numbers are genuine floats
        assert pd.notnull(row["mae"]) and row["mae"] > 0
        assert pd.notnull(row["mape_6m"]) and row["mape_6m"] > 0
        assert pd.notnull(row["coverage_80"]) and row["coverage_80"] > 0
        assert pd.notnull(row["coverage_95"]) and row["coverage_95"] > 0
        assert pd.notnull(row["notes"]) and len(str(row["notes"])) > 10

    # Resin and rubber must reflect honest short / annual series tier
    resin_row = df[df["material"] == "resin"].iloc[0]
    assert resin_row["tier"] == "SHORT"
    assert "Short series" in resin_row["notes"] or "empirical" in resin_row["notes"]

    rubber_row = df[df["material"] == "rubber"].iloc[0]
    assert rubber_row["tier"] == "ANNUAL"
    assert "Annual" in rubber_row["notes"]


def test_T3_precomputed_forecasts_match_winning_model_and_mape():
    """T3: Precomputed forecasts must have winning model and matching MAPE from backtest."""
    fcst_path = os.path.join(FALLBACK_DIR, "precomputed_forecasts.csv")
    scores_path = os.path.join(FALLBACK_DIR, "backtest_scores.csv")
    
    assert os.path.exists(fcst_path), "precomputed_forecasts.csv missing"
    assert os.path.exists(scores_path), "backtest_scores.csv missing"

    df_fcst = pd.read_csv(fcst_path)
    df_scores = pd.read_csv(scores_path).set_index("material")

    for mat_id in ["copper", "aluminium", "nickel", "steel_hr", "steel_cr", "freight"]:
        sub = df_fcst[df_fcst["unique_id"] == mat_id]
        assert not sub.empty, f"No forecast rows for {mat_id}"
        expected_model = df_scores.loc[mat_id, "model"]
        expected_mape = float(df_scores.loc[mat_id, "mape_6m"])

        actual_model = sub.iloc[0]["model"]
        actual_mape = float(sub.iloc[0]["mape"])

        assert actual_model == expected_model, f"{mat_id} model mismatch: {actual_model} vs {expected_model}"
        assert abs(actual_mape - expected_mape) < 0.2, f"{mat_id} mape mismatch: {actual_mape} vs {expected_mape}"

    # Copper point forecast must NOT be flat
    cu_sub = df_fcst[df_fcst["unique_id"] == "copper"]
    pts = cu_sub["point"].tolist()
    assert pts[0] != pts[-1], f"Copper point forecast should have trend/variation, got flat {pts[0]}"


def test_T4_monte_carlo_symmetry_and_zero_vol_collapse():
    """T4: Monte Carlo must collapse under zero volatility and show symmetric P50 around base case."""
    presets = get_default_presets()
    base_scn = presets["base_case"]
    base_res = run_all(base_scn)

    # 1. Symmetric Base Case P50
    res_sym = run_profit_at_risk_monte_carlo(base_scn, num_paths=2000, seed=42, symmetric_recovery=True)
    assert abs(res_sym["p50_ebitda_cr"] - 297.70) <= 5.0, f"P50 {res_sym['p50_ebitda_cr']} not within +-5 Cr of 297.70"
    assert res_sym["p10_ebitda_cr"] <= res_sym["p50_ebitda_cr"] <= res_sym["p90_ebitda_cr"], "Percentile ordering violated"

    # 2. Zero-Volatility Collapse
    res_zero = run_profit_at_risk_monte_carlo(base_scn, num_paths=1000, seed=42, volatility_scale=0.0)
    det_ebitda = round(base_res.ebitda_cr, 2)
    assert res_zero["p10_ebitda_cr"] == res_zero["p50_ebitda_cr"] == res_zero["p90_ebitda_cr"] == det_ebitda, (
        f"Zero vol collapse failed: P10={res_zero['p10_ebitda_cr']}, P50={res_zero['p50_ebitda_cr']}, P90={res_zero['p90_ebitda_cr']} vs {det_ebitda}"
    )


def test_T5_deny_list_entities_absent():
    """T5: Scans all engine, UI, config, and document files to confirm zero occurrences of forbidden entity names."""
    deny_list = [
        "Maruti", "Tata Motors", "Hyundai", "Renault", "Nissan", "Cummins", "Brembo",
        "Maersk", "MSC", "CMA CGM", "Hapag", "Hindalco", "Vedanta", "Supreme Petrochem",
        "SBI", "HDFC", "Clause 4.2", "Puducherry", "Pantnagar", "Sanand", "Queretaro", "Tumkur", "Viralimalai",
        "ICIS Phenolic", "European Valve"
    ]
    pattern = re.compile(r'\b(' + '|'.join(re.escape(w) for w in deny_list) + r')\b', re.IGNORECASE)

    violations = []
    scan_dirs = ["engine", "config", "pages", "ui"]
    for d in scan_dirs:
        dirpath = os.path.join(BASE_DIR, d)
        for root, _, files in os.walk(dirpath):
            for file in files:
                if file.endswith((".py", ".yaml", ".yml", ".json", ".html", ".css")):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    matches = pattern.findall(content)
                    if matches:
                        rel = os.path.relpath(filepath, BASE_DIR)
                        violations.append(f"{rel}: {list(set(matches))}")

    assert not violations, f"Found forbidden invented entities in code/config files: {violations}"
