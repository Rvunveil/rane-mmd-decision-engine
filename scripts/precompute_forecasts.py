"""
Script to pre-compute forecasts for all 8 series and store in data/fallback/
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.forecast import get_all_forecasts

def main():
    print("Pre-computing forecasts using statsforecast and empirical models...")
    fcst_df, score_df = get_all_forecasts(use_cache=False)
    print(f"Generated {len(fcst_df)} forecast rows across {len(score_df)} commodities.")
    print("\nBacktest Scorecards:")
    print(score_df[['material', 'model', 'mape_3m', 'mape_6m', 'mape_12m']])
    print("\nPre-computation complete! Saved to data/fallback/")

if __name__ == "__main__":
    main()
