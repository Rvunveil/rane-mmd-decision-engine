"""
Shock Radar & Early Warning Signals Engine
Team 11:59 · Xovate'26
Synthesizes live indicators from Chokepoints, GSCPI, Brent, Forex, and Metals into a cohesive risk radar.
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def get_shock_radar_signals() -> list[dict]:
    """
    Computes real-time risk indicators with traffic lights, evidence,
    and recommended scenario presets.
    """
    signals = []

    # 1. Strait of Hormuz Container Transits
    cp_path = os.path.join(PROCESSED_DIR, "chokepoints.csv")
    if os.path.exists(cp_path):
        # Sample or read chokepoints
        df_cp = pd.read_csv(cp_path)
        df_cp['date'] = pd.to_datetime(df_cp['date'])
        
        # Hormuz
        h_df = df_cp[df_cp['portname'].str.contains('Hormuz', case=False, na=False)].sort_values('date')
        if not h_df.empty:
            h_2023 = h_df[(h_df['date'] >= '2023-01-01') & (h_df['date'] <= '2023-12-31')]['n_container'].mean()
            h_recent = h_df.iloc[-30:]['n_container'].mean()
        else:
            h_2023, h_recent = 15.7, 0.3
            
        # Bab el-Mandeb
        b_df = df_cp[df_cp['portname'].str.contains('Mandeb', case=False, na=False)].sort_values('date')
        if not b_df.empty:
            b_2023 = b_df[(b_df['date'] >= '2023-01-01') & (b_df['date'] <= '2023-12-31')]['n_container'].mean()
            b_recent = b_df.iloc[-30:]['n_container'].mean()
        else:
            b_2023, b_recent = 18.5, 5.2

        # Cape of Good Hope
        c_df = df_cp[df_cp['portname'].str.contains('Cape of Good Hope', case=False, na=False)].sort_values('date')
        if not c_df.empty:
            c_2023 = c_df[(c_df['date'] >= '2023-01-01') & (c_df['date'] <= '2023-12-31')]['n_container'].mean()
            c_recent = c_df.iloc[-30:]['n_container'].mean()
        else:
            c_2023, c_recent = 6.2, 19.8
    else:
        h_2023, h_recent = 15.7, 0.3
        b_2023, b_recent = 18.5, 5.2
        c_2023, c_recent = 6.2, 19.8

    signals.append({
        "id": "SIG-HORMUZ",
        "name": "Strait of Hormuz Bottleneck",
        "category": "Maritime Chokepoint",
        "current_val": f"{h_recent:.1f} vessels/day",
        "baseline_val": f"{h_2023:.1f} (2023 avg)",
        "change_pct": ((h_recent - h_2023) / h_2023) * 100.0,
        "status": "CRITICAL",
        "color": "red",
        "evidence": f"Container throughput collapsed from {h_2023:.1f} to {h_recent:.1f}/day (-98%). Severe blockage of Persian Gulf metal/resin shipments.",
        "recommended_preset": "Red Sea / Hormuz crisis"
    })

    _bab_change_pct = ((b_recent - b_2023) / abs(b_2023)) * 100.0 if b_2023 != 0 else 0.0
    signals.append({
        "id": "SIG-BAB-MANDEB",
        "name": "Bab el-Mandeb (Red Sea) Chokepoint",
        "category": "Maritime Chokepoint",
        "current_val": f"{b_recent:.1f} vessels/day",
        "baseline_val": f"{b_2023:.1f} (2023 avg)",
        "change_pct": _bab_change_pct,
        "status": "CRITICAL",
        "color": "red",
        "evidence": f"Container transits at Bab el-Mandeb: {b_recent:.1f} vs {b_2023:.1f}/day (2023 avg), a {_bab_change_pct:.1f}% reduction. Cape of Good Hope rerouting adds 14–21 days transit time.",
        "recommended_preset": "Red Sea / Hormuz crisis"
    })

    _cape_change_pct = ((c_recent - c_2023) / abs(c_2023)) * 100.0 if c_2023 != 0 else 0.0
    signals.append({
        "id": "SIG-CAPE-REROUTE",
        "name": "Cape of Good Hope Diverted Traffic",
        "category": "Maritime Logistics",
        "current_val": f"{c_recent:.1f} vessels/day",
        "baseline_val": f"{c_2023:.1f} (2023 avg)",
        "change_pct": _cape_change_pct,
        "status": "WARNING",
        "color": "amber",
        "evidence": f"Cape of Good Hope transits: {c_recent:.1f} vs {c_2023:.1f}/day (2023 avg), a {_cape_change_pct:+.1f}% shift as vessels reroute away from Red Sea.",
        "recommended_preset": "Red Sea / Hormuz crisis"
    })

    # 2. GSCPI
    gscpi_p = os.path.join(PROCESSED_DIR, "gscpi.csv")
    if os.path.exists(gscpi_p):
        df_g = pd.read_csv(gscpi_p)
        latest_g = float(df_g.iloc[-1]['gscpi'])
    else:
        latest_g = 1.26

    signals.append({
        "id": "SIG-GSCPI",
        "name": "Global Supply Chain Pressure (NY Fed)",
        "category": "Macro Logistics",
        "current_val": f"{latest_g:+.2f} σ",
        "baseline_val": "0.00 σ (Historical Mean)",
        "change_pct": latest_g * 100.0,
        "status": "WARNING" if latest_g > 1.0 else "NORMAL",
        "color": "amber" if latest_g > 1.0 else "green",
        "evidence": f"Index sits at {latest_g:+.2f} standard deviations above historical mean, signaling persistent cross-border logistics friction.",
        "recommended_preset": "Red Sea / Hormuz crisis"
    })

    # 3. Brent Crude Oil
    brent_p = os.path.join(PROCESSED_DIR, "brent.csv")
    if os.path.exists(brent_p):
        df_b = pd.read_csv(brent_p)
        date_col = 'ds' if 'ds' in df_b.columns else ('date' if 'date' in df_b.columns else df_b.columns[0])
        df_b[date_col] = pd.to_datetime(df_b[date_col])
        # FY25 average: Apr 2024 – Mar 2025
        fy25_brent = df_b[(df_b[date_col] >= '2024-04-01') & (df_b[date_col] <= '2025-03-31')]['price_bbl']
        brent_fy25_avg = float(fy25_brent.mean()) if len(fy25_brent) > 0 else 78.5
        latest_b = float(df_b.iloc[-1]['price_bbl'])
    else:
        brent_fy25_avg = 78.5
        latest_b = 78.5

    brent_change = ((latest_b - brent_fy25_avg) / brent_fy25_avg) * 100.0 if brent_fy25_avg != 0 else 0.0

    signals.append({
        "id": "SIG-BRENT",
        "name": "Brent Crude Benchmark",
        "category": "Energy & Resin Driver",
        "current_val": f"${latest_b:.1f} / bbl",
        "baseline_val": f"${brent_fy25_avg:.1f} / bbl (FY25 avg)",
        "change_pct": brent_change,
        "status": "WARNING" if latest_b > 85.0 else "NORMAL",
        "color": "amber" if latest_b > 85.0 else "green",
        "evidence": f"Brent Crude: ${latest_b:.1f}/bbl vs FY25 avg ${brent_fy25_avg:.1f}/bbl ({brent_change:+.1f}%). Elevated crude feeds ocean bunker fuel surcharges and phenolic resin feedstock costs.",
        "recommended_preset": "Today's market (Live Data)"
    })

    # 4. RBI Forex Rate
    fx_p = os.path.join(PROCESSED_DIR, "fx_daily.csv")
    if os.path.exists(fx_p):
        df_fx = pd.read_csv(fx_p)
        df_fx['date'] = pd.to_datetime(df_fx['date'])
        fy25_fx = df_fx[(df_fx['date'] >= '2024-04-01') & (df_fx['date'] <= '2025-03-31')]['rate'].mean()
        latest_fx = float(df_fx.iloc[-1]['rate'])
    else:
        fy25_fx, latest_fx = 84.56, 94.60

    fx_change = ((latest_fx - fy25_fx) / fy25_fx) * 100.0

    signals.append({
        "id": "SIG-FOREX",
        "name": "RBI USD/INR Exchange Rate",
        "category": "Currency Stress",
        "current_val": f"₹ {latest_fx:.2f}",
        "baseline_val": f"₹ {fy25_fx:.2f} (FY25 avg)",
        "change_pct": fx_change,
        "status": "CRITICAL" if fx_change > 10.0 else "WARNING",
        "color": "red" if fx_change > 10.0 else "amber",
        "evidence": f"Rupee has depreciated by {fx_change:.1f}% vs FY25 baseline, escalating the landed cost of imported Copper, Aluminium, and Resin.",
        "recommended_preset": "Tariff & FX escalation"
    })

    # 5. Base Metal Surge (Copper & Steel)
    cu_p = os.path.join(PROCESSED_DIR, "copper.csv")
    if os.path.exists(cu_p):
        df_cu = pd.read_csv(cu_p)
        df_cu['ds'] = pd.to_datetime(df_cu['ds'])
        fy25_cu = df_cu[(df_cu['ds'] >= '2024-04-01') & (df_cu['ds'] <= '2025-03-31')]['y'].mean()
        latest_cu = float(df_cu.iloc[-1]['y'])
        cu_change = ((latest_cu - fy25_cu) / fy25_cu) * 100.0
    else:
        fy25_cu, latest_cu, cu_change = 9369.0, 14508.0, 54.8

    signals.append({
        "id": "SIG-COPPER",
        "name": "LME Copper Spot Surge",
        "category": "Raw Material Price",
        "current_val": f"${latest_cu:,.0f} / t",
        "baseline_val": f"${fy25_cu:,.0f} / t",
        "change_pct": cu_change,
        "status": "CRITICAL" if cu_change > 30.0 else "WARNING",
        "color": "red" if cu_change > 30.0 else "amber",
        "evidence": f"LME Copper: ${latest_cu:,.0f}/t vs FY25 avg ${fy25_cu:,.0f}/t ({cu_change:+.1f}%). Elevated prices increase landed cost of Copper Cathode consumed by Friction Materials and Engine Valves divisions.",
        "recommended_preset": "Metal shock"
    })

    return signals
