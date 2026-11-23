"""
Unit tests for Data Loader & Data Quality Pipeline
Verifies acceptance criteria #5 from Section 8.
"""

import pytest
import pandas as pd
import numpy as np
from engine.data_loader import (
    clean_forex_data,
    clean_container_freight_data,
    clean_copper_data,
    clean_nickel_data,
    clean_aluminium_data,
    clean_steel_data,
    clean_resin_data,
    clean_rubber_data
)

def test_container_freight_redating_anchors():
    """
    Verifies that the deliberate weekly re-dating fix:
    - Ends exactly on 2026-03-19 with rate $2,172
    - Has low in Oct/Nov 2023 (~$1,342)
    - Has peak in Jul/Aug 2024 (>$5,900)
    - Has 165 weekly observations
    """
    raw_df, fixed_df = clean_container_freight_data()
    assert len(fixed_df) == 165, f"Expected 165 points, got {len(fixed_df)}"
    
    # End date & rate
    last_row = fixed_df.iloc[-1]
    assert last_row['date'] == pd.Timestamp("2026-03-19")
    assert last_row['rate'] == 2172.0

    # Low in Oct/Nov 2023
    oct_nov_2023 = fixed_df[(fixed_df['date'] >= '2023-10-01') & (fixed_df['date'] <= '2023-11-30')]
    assert not oct_nov_2023.empty
    min_rate = oct_nov_2023['rate'].min()
    assert min_rate == 1342.0, f"Expected low of 1342, got {min_rate}"

    # Peak in Jul/Aug 2024
    jul_aug_2024 = fixed_df[(fixed_df['date'] >= '2024-07-01') & (fixed_df['date'] <= '2024-08-31')]
    assert not jul_aug_2024.empty
    max_rate = jul_aug_2024['rate'].max()
    assert max_rate > 5900.0, f"Expected peak > 5900, got {max_rate}"


def test_forex_dedup_and_numeric():
    """
    Verifies that RBI Forex rates are deduplicated, numeric,
    and have FY25 average ~ 84.6.
    """
    df_daily, df_monthly = clean_forex_data()
    assert df_daily['date'].is_monotonic_increasing
    assert df_daily['date'].duplicated().sum() == 0
    assert not df_daily['rate'].isna().any()

    fy25 = df_daily[(df_daily['date'] >= '2024-04-01') & (df_daily['date'] <= '2025-03-31')]
    fy25_avg = fy25['rate'].mean()
    assert 84.0 <= fy25_avg <= 85.0, f"Expected FY25 avg ~84.6, got {fy25_avg}"


def test_aluminium_reshape():
    """
    Verifies that Aluminium is successfully unwrapped from wide matrix
    into a continuous chronological monthly series from 2014 to 2026.
    """
    df = clean_aluminium_data()
    assert len(df) >= 150
    assert df['ds'].min() <= pd.Timestamp("2014-02-01")
    assert df['ds'].max() >= pd.Timestamp("2026-10-01")
    assert not df['y'].isna().any()
    # Check baseline range
    fy25 = df[(df['ds'] >= '2024-04-01') & (df['ds'] <= '2025-03-31')]
    assert 2400 <= fy25['y'].mean() <= 2650


def test_steel_not_fx_converted():
    """
    Verifies that Steel HR and CR are in domestic INR/t without FX distortion.
    Typical domestic HR coil price is ~ ₹50,000 to ₹80,000 / t.
    """
    df_hr, df_cr, notes = clean_steel_data()
    assert len(df_hr) > 60
    assert len(df_cr) > 60
    assert df_hr['y'].mean() > 40000, "Steel HR appears erroneously in USD!"
    assert df_cr['y'].mean() > 45000, "Steel CR appears erroneously in USD!"


def test_resin_and_rubber_conversions():
    """
    Verifies:
    - Resin: converted USD/kg * 1000 -> USD/t (~ $1,100 - $1,800 / t)
    - Rubber: converted Rs/100kg * 10 -> Rs/t (~ ₹140,000 / t)
    """
    df_res = clean_resin_data()
    assert len(df_res) == 17
    assert 1000 <= df_res['y'].mean() <= 2000, f"Resin price in USD/t unexpected: {df_res['y'].mean()}"

    df_rub = clean_rubber_data()
    assert len(df_rub) >= 18
    assert df_rub['y'].max() > 100000, "Rubber price not converted to Rs/t!"
