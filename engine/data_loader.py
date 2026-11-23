"""
Data Loader & Cleaning Pipeline for Rane (Madras) MMD Decision Engine
Handles all data sanitization, unit conversions, and deliberate data fixes.
"""

import os
import glob
import pandas as pd
import numpy as np

RAW_BASE = os.path.join("data", "raw", "Dataset xovate (!)")
PROCESSED_BASE = os.path.join("data", "processed")

def get_raw_path(subdir: str, filename_pattern: str) -> str:
    """Finds raw file path matching pattern in subdir"""
    target_dir = os.path.join(RAW_BASE, subdir)
    matches = glob.glob(os.path.join(target_dir, filename_pattern))
    if not matches:
        # Fallback to direct search without spaces/parentheses if needed
        matches = glob.glob(os.path.join("Dataset xovate (!)", subdir, filename_pattern))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Cannot find {filename_pattern} in {target_dir}")


def clean_forex_data() -> pd.DataFrame:
    """
    Cleans Daily RBI reference rate (Forex Exchange Rate (inr - usd).xlsx)
    - Fixes duplicates, non-numeric strings, sorts chronological
    - Computes both daily series and monthly average
    """
    fp = get_raw_path("Logistics", "*Forex*.xlsx")
    df = pd.read_excel(fp)
    df = df.rename(columns={"Date": "date", "RBI Reference Rate": "rate"})
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
    df = df.dropna(subset=['date', 'rate']).sort_values('date').drop_duplicates('date')
    
    # Also monthly resampled
    df_monthly = df.set_index('date').resample('MS')['rate'].mean().reset_index()
    df_monthly.columns = ['ds', 'fx_rate']
    
    return df, df_monthly


def clean_container_freight_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cleans Weekly Container freight rate index worldwide.xlsx
    DELIBERATE DATA-JUDGEMENT FIX:
    The raw Excel file erroneously labelled 165 weekly values as consecutive days
    between 12 Jan 2023 and 25 Jun 2023. The sheet description explicitly states
    the timeline spans January 2023 to 19 March 2026, with an Oct 2023 low of $1,342,
    a Jul 2024 peak of >$5,900, and ending at $2,172 on 19 March 2026.
    
    Fix: Re-date the 165 points backwards from 19 March 2026 in 7-day weekly increments.
    Returns: (raw_erroneous_df, fixed_weekly_df)
    """
    fp = get_raw_path("Logistics", "*Weekly Container*.xlsx")
    df_raw = pd.read_excel(fp, header=None)
    
    # Extract Col 2 (raw date) and Col 3 (freight rate)
    sub = df_raw.iloc[2:, [2, 3]].dropna()
    sub.columns = ['raw_date', 'rate']
    sub['raw_date'] = pd.to_datetime(sub['raw_date'], errors='coerce')
    sub['rate'] = pd.to_numeric(sub['rate'], errors='coerce')
    sub = sub.dropna().reset_index(drop=True)
    
    n_points = len(sub) # 165
    # End date is 2026-03-19 per sheet description and official handout
    end_date = pd.Timestamp("2026-03-19")
    fixed_dates = [end_date - pd.to_timedelta(int(7 * (n_points - 1 - i)), unit='D') for i in range(n_points)]
    
    fixed_df = pd.DataFrame({
        "ds": fixed_dates,
        "date": fixed_dates,
        "rate": sub['rate'].values
    })
    
    return sub, fixed_df


def clean_copper_data() -> pd.DataFrame:
    """Monthly Copper Price (USD/tonne) Jan 2014 – Oct 2026"""
    fp = get_raw_path("Material price", "*Copper*.xlsx")
    df = pd.read_excel(fp, header=None).iloc[3:, :2].dropna()
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df['unique_id'] = 'copper'
    return df.dropna().sort_values('ds').reset_index(drop=True)


def clean_nickel_data() -> pd.DataFrame:
    """Monthly Nickel Price (USD/tonne) Jan 2014 – Oct 2026"""
    fp = get_raw_path("Material price", "*Nickel Price*.xlsx")
    df = pd.read_excel(fp, header=None).iloc[2:, :2].dropna()
    df.columns = ['ds', 'y']
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df['unique_id'] = 'nickel'
    return df.dropna().sort_values('ds').reset_index(drop=True)


def clean_aluminium_data() -> pd.DataFrame:
    """
    Tidy Monthly Aluminium Cash-Settlement (USD/tonne) 2014 – Nov 2026.
    Unwraps wide 5-year and 3-year horizontal blocks with reversed months.
    """
    fp = get_raw_path("Material price", "*Aluminium*.xlsx")
    df_al = pd.read_excel(fp, header=None)
    records = []
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    # Blocks start at row 3 (2014-2018), row 20 (2019-2023), row 37 (2024-2026)
    for block_row in [3, 20, 37]:
        for col_idx in range(0, df_al.shape[1], 5):
            year_val = df_al.iloc[block_row, col_idx]
            if pd.notnull(year_val) and str(year_val).replace('.0','').isdigit():
                year = int(float(year_val))
                for r in range(block_row + 2, min(block_row + 14, df_al.shape[0])):
                    m_str = df_al.iloc[r, col_idx]
                    p_val = df_al.iloc[r, col_idx + 1] # Cash settlement
                    if pd.notnull(m_str) and str(m_str).strip() in month_map and pd.notnull(p_val):
                        month = month_map[str(m_str).strip()]
                        records.append({
                            'ds': pd.Timestamp(year, month, 1),
                            'y': float(p_val),
                            'unique_id': 'aluminium'
                        })

    df = pd.DataFrame(records).sort_values('ds').drop_duplicates('ds').reset_index(drop=True)
    return df


def clean_steel_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Cleans Ministry of Steel monthly HR coil and CR coil in INR/t.
    DO NOT CONVERT WITH FX: Values are already domestic INR/t!
    Returns: (df_hr, df_cr, df_quality_notes)
    """
    fp = get_raw_path("Material price", "*Steel_Price*.xlsx")
    df = pd.read_excel(fp, sheet_name='Monthly prices', header=3)
    df_qual = pd.read_excel(fp, sheet_name='Data quality')
    
    df['Month end'] = pd.to_datetime(df['Month end'], errors='coerce')
    df['HR'] = pd.to_numeric(df['HR coil 2.5mm (Rs/t)'], errors='coerce')
    df['CR'] = pd.to_numeric(df['CR coil 0.63mm (Rs/t)'], errors='coerce')
    
    # Month end -> Month start for consistent modelling
    df['ds'] = df['Month end'].dt.to_period('M').dt.to_timestamp()
    
    df_hr = df[['ds', 'HR', 'Flag']].dropna(subset=['HR']).rename(columns={'HR': 'y'}).assign(unique_id='steel_hr')
    df_cr = df[['ds', 'CR', 'Flag']].dropna(subset=['CR']).rename(columns={'CR': 'y'}).assign(unique_id='steel_cr')
    
    return df_hr.sort_values('ds').reset_index(drop=True), df_cr.sort_values('ds').reset_index(drop=True), df_qual


def clean_resin_data() -> pd.DataFrame:
    """
    Phenolic Resin: Short irregular series (June 2024 - Sep 2026).
    Unit: USD/kg * 1000 -> USD/tonne.
    """
    fp = get_raw_path("Material price", "*Resin Price Dataset*.xlsx")
    df = pd.read_excel(fp, header=3)
    df['ds'] = pd.to_datetime(df['Date (YYYY-MM)'], errors='coerce')
    df['price_usd_kg'] = pd.to_numeric(df['Price (USD/KG)'], errors='coerce')
    df = df.dropna(subset=['ds', 'price_usd_kg']).sort_values('ds')
    df['y'] = df['price_usd_kg'] * 1000.0 # Convert USD/kg to USD/t
    df['unique_id'] = 'resin'
    return df[['ds', 'y', 'price_usd_kg', 'unique_id']].reset_index(drop=True)


def clean_rubber_data() -> pd.DataFrame:
    """
    Natural Rubber: Annual RSS-4 Kottayam series (2005-06 to 2024-25).
    Unit: INR/100kg * 10 -> INR/tonne.
    """
    fp = get_raw_path("Material price", "*Rubber*.xlsx")
    df = pd.read_excel(fp, header=6)
    df = df.dropna(subset=['Year (April to March)'])
    
    # Parse years e.g. 2005-06 -> timestamp 2005-04-01
    records = []
    for _, row in df.iterrows():
        y_val = row['Average price of RSS-4 Kottayam (Rs/100kg)']
        yr_val = row['Year (April to March)']
        if pd.notnull(y_val) and pd.notnull(yr_val):
            # year can be datetime or string
            if isinstance(yr_val, pd.Timestamp):
                year = yr_val.year
                records.append({
                    'ds': pd.Timestamp(year, 4, 1),
                    'y': float(y_val) * 10.0, # Rs/100kg * 10 = Rs/t
                    'price_rs_100kg': float(y_val),
                    'unique_id': 'rubber'
                })
            elif str(yr_val)[:4].isdigit():
                year = int(str(yr_val)[:4])
                records.append({
                    'ds': pd.Timestamp(year, 4, 1),
                    'y': float(y_val) * 10.0, # Rs/100kg * 10 = Rs/t
                    'price_rs_100kg': float(y_val),
                    'unique_id': 'rubber'
                })
    return pd.DataFrame(records).sort_values('ds').reset_index(drop=True)


def clean_brent_data() -> pd.DataFrame:
    """Daily Brent Crude Oil (USD/barrel)"""
    fp = get_raw_path("Material price", "*brent*.csv")
    df = pd.read_csv(fp)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    return df.dropna().rename(columns={'Date': 'ds', 'Price': 'price_bbl'}).sort_values('ds').reset_index(drop=True)


def clean_gscpi_data() -> pd.DataFrame:
    """Monthly Global Supply Chain Pressure Index (GSCPI)"""
    fp = get_raw_path("Logistics", "*GSCPI*.xls")
    df = pd.read_excel(fp)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['GSCPI'] = pd.to_numeric(df['GSCPI'], errors='coerce')
    return df.dropna().rename(columns={'Date': 'ds', 'GSCPI': 'gscpi'}).sort_values('ds').reset_index(drop=True)


def clean_chokepoints_data() -> pd.DataFrame:
    """Daily Chokepoints transit and capacity metrics"""
    fp = get_raw_path("Logistics", "*Chokepoints*.xlsx")
    df = pd.read_excel(fp)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


def load_all_cleaned_datasets() -> dict[str, pd.DataFrame]:
    """Loads and standardizes all clean datasets into a single dictionary."""
    df_fx_daily, df_fx_monthly = clean_forex_data()
    raw_freight, fixed_freight = clean_container_freight_data()
    df_cu = clean_copper_data()
    df_ni = clean_nickel_data()
    df_al = clean_aluminium_data()
    df_hr, df_cr, df_steel_notes = clean_steel_data()
    df_res = clean_resin_data()
    df_rub = clean_rubber_data()
    df_brent = clean_brent_data()
    df_gscpi = clean_gscpi_data()
    df_chokepoints = clean_chokepoints_data()

    return {
        "fx_daily": df_fx_daily,
        "fx_monthly": df_fx_monthly,
        "freight_raw": raw_freight,
        "freight_fixed": fixed_freight,
        "copper": df_cu,
        "nickel": df_ni,
        "aluminium": df_al,
        "steel_hr": df_hr,
        "steel_cr": df_cr,
        "steel_notes": df_steel_notes,
        "resin": df_res,
        "rubber": df_rub,
        "brent": df_brent,
        "gscpi": df_gscpi,
        "chokepoints": df_chokepoints
    }


def load_assumptions() -> dict:
    """Loads config/assumptions.yaml safely."""
    path = os.path.join(os.path.dirname(__file__), "..", "config", "assumptions.yaml")
    if os.path.exists(path):
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

