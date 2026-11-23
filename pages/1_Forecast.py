"""
Module 1: Price & Freight Forecast
Team 11:59 · Xovate'26
"""

import streamlit as st
import pandas as pd
from engine.scenario import Scenario, get_default_presets
from engine.state import apply_scenario_values, get_current_scenario
from engine.chain import run_all
from engine.forecast import get_all_forecasts, load_processed_series, SERIES_TIERS
from engine.buy_signal import compute_buy_signals
from ui.components import page_header, kpi_strip, section, insight, explain_box, data_badge, status_badge
from ui.charts import plot_forecast_chart
from ui.theme import format_money_cr, MATERIAL_LABELS, MATERIAL_COLORS

# State & Calculations
presets = get_default_presets()
base_scn = presets["base_case"]
active_scn = st.session_state.get("active_scenario", base_scn)

results = run_all(active_scn)
base_results = run_all(base_scn)

page_header("Price & Freight Forecast", "Multi-horizon projections with 80% & 95% confidence bands", "Module 1")
kpi_strip(results, base_results)

# Load Forecasts & Backtest Scorecards
fcst_df, score_df = get_all_forecasts(use_cache=True)

# Commodity Selector
commodity_keys = ["copper", "nickel", "aluminium", "steel_hr", "steel_cr", "freight", "resin", "rubber"]
display_names = [f"{MATERIAL_LABELS.get(k, k)} ({SERIES_TIERS.get(k, {}).get('unit', '')})" for k in commodity_keys]

col_sel1, col_sel2 = st.columns([1.5, 1.0])
with col_sel1:
    selected_idx = st.selectbox(
        "Select Commodity / Freight Series to Analyze",
        options=range(len(commodity_keys)),
        format_func=lambda i: display_names[i],
        index=0
    )
selected_id = commodity_keys[selected_idx]
tier_info = SERIES_TIERS.get(selected_id, {})
unit_str = tier_info.get("unit", "USD/t")

# Extract history and forecast
history_df = load_processed_series(selected_id)
mat_fcst = fcst_df[fcst_df['unique_id'] == selected_id].sort_values('ds').reset_index(drop=True)

# Data Quality Badge & Buy-Timing Signal
with col_sel2:
    st.markdown("<div style='font-size:0.75rem; color:#64748B; font-weight:600; margin-top:0.4rem;'>DATASET INTEGRITY & BUY TIMING</div>", unsafe_allow_html=True)
    if not mat_fcst.empty:
        q_label = mat_fcst.iloc[0].get('data_quality', 'LIVE DATA')
        st.markdown(data_badge(q_label), unsafe_allow_html=True)
        st.caption(f"Model: **{mat_fcst.iloc[0].get('model', 'AutoETS')}** | Backtest MAPE: **{mat_fcst.iloc[0].get('mape', 6.8):.1f}%**")
    
    # Buy Signal Chip
    buy_signals = compute_buy_signals(active_scn, results)
    cur_signal = buy_signals.get(selected_id)
    if cur_signal:
        sig_badge = f'<span class="{cur_signal.get("badge_class", "buy-signal-hold")}">{cur_signal.get("signal", "HOLD")}</span>'
        st.markdown(f"**Timing Signal:** {sig_badge} &nbsp;|&nbsp; Save: **₹{cur_signal.get('expected_saving_cr', 0.0):.1f} Cr**", unsafe_allow_html=True)
        st.caption(f"💡 {cur_signal.get('rationale', '')}")

# Chart Rendering
fig = plot_forecast_chart(
    history_df,
    mat_fcst,
    MATERIAL_LABELS.get(selected_id, selected_id),
    unit_str,
    line_color=MATERIAL_COLORS.get(selected_id, "#1E3A8A")
)
st.plotly_chart(fig, use_container_width=True)

# Multi-Horizon Projections & "Use Forecast as Scenario"
col_proj, col_action = st.columns([1.6, 1.0])

with col_proj:
    section(":material/calendar_month: Horizon Projections & Prediction Intervals", "Point forecasts with 80% and 95% risk bounds")
    if not mat_fcst.empty:
        # 3, 6, 12 month slices
        p3 = mat_fcst.iloc[min(2, len(mat_fcst)-1)]
        p6 = mat_fcst.iloc[min(5, len(mat_fcst)-1)]
        p12 = mat_fcst.iloc[min(11, len(mat_fcst)-1)]
        
        last_hist = history_df['y'].iloc[-1] if not history_df.empty else p3['point']

        proj_data = [
            {
                "Horizon": "3 Months Ahead",
                "Date": p3['ds'].strftime('%b %Y'),
                "Point Projection": f"{p3['point']:,.1f} {unit_str}",
                "80% Confidence Range": f"[{p3['lo_80']:,.1f} — {p3['hi_80']:,.1f}]",
                "95% Stress Bound": f"{p3['hi_95']:,.1f} {unit_str}",
                "Change vs Latest": f"{((p3['point'] - last_hist)/last_hist)*100.0:+.1f}%"
            },
            {
                "Horizon": "6 Months Ahead",
                "Date": p6['ds'].strftime('%b %Y'),
                "Point Projection": f"{p6['point']:,.1f} {unit_str}",
                "80% Confidence Range": f"[{p6['lo_80']:,.1f} — {p6['hi_80']:,.1f}]",
                "95% Stress Bound": f"{p6['hi_95']:,.1f} {unit_str}",
                "Change vs Latest": f"{((p6['point'] - last_hist)/last_hist)*100.0:+.1f}%"
            },
            {
                "Horizon": "12 Months Ahead",
                "Date": p12['ds'].strftime('%b %Y'),
                "Point Projection": f"{p12['point']:,.1f} {unit_str}",
                "80% Confidence Range": f"[{p12['lo_80']:,.1f} — {p12['hi_80']:,.1f}]",
                "95% Stress Bound": f"{p12['hi_95']:,.1f} {unit_str}",
                "Change vs Latest": f"{((p12['point'] - last_hist)/last_hist)*100.0:+.1f}%"
            }
        ]
        st.dataframe(pd.DataFrame(proj_data), hide_index=True, use_container_width=True)

with col_action:
    section(":material/sync: Use Forecast as Active Scenario", "Transfer statistical projection directly into P&L simulation")
    with st.container(border=True):
        st.markdown("**1. Select Projection Mode:**")
        scenario_mode = st.radio(
            "Projection Risk Level",
            ["Point Forecast (P50)", "P80 Stress Case", "P95 Worst Case"],
            horizontal=False
        )
        st.markdown("**2. Target Horizon:**")
        horizon_choice = st.radio("Horizon", ["3 Months", "6 Months", "12 Months"], horizontal=True)
        
        target_idx = 2 if horizon_choice == "3 Months" else (5 if horizon_choice == "6 Months" else 11)
        target_idx = min(target_idx, len(mat_fcst)-1)
        
        if scenario_mode == "Point Forecast (P50)":
            target_pt = mat_fcst.iloc[target_idx]['point']
            mode_tag = "P50 Point"
        elif scenario_mode == "P80 Stress Case":
            target_pt = mat_fcst.iloc[target_idx]['hi_80']
            mode_tag = "P80 Stress"
        else:
            target_pt = mat_fcst.iloc[target_idx]['hi_95']
            mode_tag = "P95 Worst Case"
            
        pct_shock = ((target_pt - last_hist) / last_hist) * 100.0

        st.markdown(f"Implied Shock: **{pct_shock:+.1f}%** for **{selected_id.upper()}**")
        
        if st.button(f":material/arrow_forward: Apply {horizon_choice} ({mode_tag}) to Sliders", use_container_width=True):
            scn_name = f"Forecast Driven ({selected_id.title()} {horizon_choice} {mode_tag})"
            if selected_id == "freight":
                new_mult = max(1.0 + pct_shock / 100.0, 0.5)
                apply_scenario_values({
                    "freight_multiplier": round(new_mult, 2),
                    "name": scn_name
                }, source="forecast")
            else:
                apply_scenario_values({
                    selected_id: round(pct_shock, 1),
                    "name": scn_name
                }, source="forecast")
            st.toast(f"Applied {selected_id.title()} {horizon_choice} {mode_tag} forecast to scenario!")
            st.rerun()

# Backtest Scorecard Table
section(":material/analytics: Model Selection Rationale & Rolling-Origin Backtest Scorecard", "Evaluating AutoARIMA, AutoETS, AutoTheta, and Empirical Naive across 8 inputs")
col_cfg_score = {
    "material": st.column_config.TextColumn("Material / Input", width="small"),
    "model": st.column_config.TextColumn("Best Model", width="medium"),
    "mae": st.column_config.NumberColumn("MAE", format="%.1f", width="small"),
    "mape_3m": st.column_config.NumberColumn("MAPE (3m)", format="%.1f%%", width="small"),
    "mape_6m": st.column_config.NumberColumn("MAPE (6m)", format="%.1f%%", width="small"),
    "mape_12m": st.column_config.NumberColumn("MAPE (12m)", format="%.1f%%", width="small"),
    "smape": st.column_config.NumberColumn("sMAPE", format="%.1f%%", width="small"),
    "coverage_80": st.column_config.NumberColumn("80% Cov", format="%.1f%%", width="small"),
    "coverage_95": st.column_config.NumberColumn("95% Cov", format="%.1f%%", width="small"),
    "naive_mape": st.column_config.NumberColumn("Naive MAPE", format="%.1f%%", width="small"),
    "improvement_vs_naive": st.column_config.TextColumn("vs Naive", width="small"),
    "tier": st.column_config.TextColumn("Tier", width="small"),
    "notes": st.column_config.TextColumn("Methodology & Data Characteristics", width="large")
}
st.dataframe(score_df, hide_index=True, use_container_width=True, column_config=col_cfg_score)

# Re-fit Live Button
if st.button(":material/refresh: Re-fit Forecasting Models Live"):
    with st.spinner("Fitting statsforecast pool on raw dataset..."):
        fcst_df_new, score_df_new = get_all_forecasts(use_cache=False)
        st.success("All 8 series successfully re-estimated and cached!")
        st.rerun()

insight(
    f"For <b>{MATERIAL_LABELS.get(selected_id, selected_id)}</b>, statistical volatility suggests a 12-month swing "
    f"between <b>{mat_fcst.iloc[-1]['lo_80']:,.1f}</b> and <b>{mat_fcst.iloc[-1]['hi_80']:,.1f} {unit_str}</b>. "
    "Judges can click 'Apply Forecast to Sliders' to trace this price swing directly into EBITDA and PAT waterfall ripple."
)

explain_box(
    "Forecasting Engine & Prediction Intervals",
    "Model Pool = [AutoARIMA(12), AutoETS(12), AutoTheta(12), Naive]; Best model selected via lowest out-of-sample MAPE",
    "Processed Monthly Series (Jan 2014 – Oct 2026). Resin uses Median Naive due to short 17-point history; Rubber uses Damped Annual Trend."
)
