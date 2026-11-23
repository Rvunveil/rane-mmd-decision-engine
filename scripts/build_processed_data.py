"""
Script to execute the full data cleaning pipeline and cache processed data
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from engine.data_loader import load_all_cleaned_datasets, PROCESSED_BASE

def main():
    os.makedirs(PROCESSED_BASE, exist_ok=True)
    print("Executing Rane MMD Data Cleaning Pipeline...")
    data = load_all_cleaned_datasets()

    for key, df in data.items():
        if isinstance(df, pd.DataFrame):
            csv_path = os.path.join(PROCESSED_BASE, f"{key}.csv")
            df.to_csv(csv_path, index=False)
            print(f"  [SAVED] {key}: {len(df)} rows -> {csv_path}")

    print("\nData pipeline completed successfully!")

if __name__ == "__main__":
    main()
