"""
Unified Plotly Charting Library for Rane (Madras) MMD Decision Engine
Registers 'mmd' custom template for Bloomberg/SaaS cockpit visuals.
"""

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
from ui.theme import (
    COLOR_BRAND_PRIMARY, COLOR_BRAND_SECONDARY, COLOR_BRAND_DARK,
    COLOR_BG_MAIN, COLOR_BG_CARD, COLOR_BORDER,
    COLOR_STATUS_GREEN, COLOR_STATUS_AMBER, COLOR_STATUS_RED,
    COLOR_BASELINE, COLOR_ACTIVE, MATERIAL_COLORS
)

# Register custom 'mmd' template
mmd_template = go.layout.Template()
mmd_template.layout = go.Layout(
    font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif", size=12, color="#0F172A"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#0F172A", font=dict(color="#FFFFFF", size=12), bordercolor="#0F172A"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        gridwidth=1,
        zeroline=False,
        linecolor="#CBD5E1",
        tickfont=dict(size=11, color="#64748B")
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#F1F5F9",
        gridwidth=1,
        zeroline=False,
        linecolor="#CBD5E1",
        tickfont=dict(size=11, color="#64748B")
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11, color="#475569")
    )
)

pio.templates["mmd"] = mmd_template
pio.templates.default = "mmd"


def plot_forecast_chart(
    history_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    material_name: str,
    unit: str,
    line_color: str = COLOR_ACTIVE
) -> go.Figure:
    """
    Renders 3/6/12-month projections with 80% and 95% confidence bands.
    """
    fig = go.Figure()

    # 1. Historical Actuals
    if not history_df.empty:
        fig.add_trace(go.Scatter(
            x=history_df['ds'],
            y=history_df['y'],
            name="Historical Actual",
            mode="lines",
            line=dict(color="#64748B", width=2),
            hovertemplate="<b>%{x|%b %Y}</b>: %{y:,.1f} " + unit + "<extra></extra>"
        ))

    if not forecast_df.empty:
        # 2. 95% Confidence Band (Lighter outer band)
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['hi_95'],
            name="95% Upper Band",
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['lo_95'],
            name="95% Confidence Interval",
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(30, 58, 138, 0.08)",
            hovertemplate="95% Low: %{y:,.1f}<extra></extra>"
        ))

        # 3. 80% Confidence Band (Inner band)
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['hi_80'],
            name="80% Upper Band",
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['lo_80'],
            name="80% Confidence Interval",
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(30, 58, 138, 0.16)",
            hovertemplate="80% Low: %{y:,.1f}<extra></extra>"
        ))

        # 4. Point Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['point'],
            name="Model Projection (Point)",
            mode="lines+markers",
            line=dict(color=line_color, width=2.5, dash="dash"),
            marker=dict(size=6, color=line_color),
            hovertemplate="<b>Point Forecast (%{x|%b %Y})</b>: %{y:,.1f} " + unit + "<extra></extra>"
        ))

    fig.update_layout(
        title=f"<b>{material_name}</b> — Price Trajectory & Confidence Envelope",
        yaxis_title=unit,
        xaxis_title="Date",
        height=380,
        hovermode="x unified"
    )
    return fig


def plot_ebitda_waterfall(
    base_ebitda: float,
    delta_material: float,
    delta_freight: float,
    recovery: float,
    lost_contrib: float,
    scenario_ebitda: float,
    scenario_pat: float
) -> go.Figure:
    """
    Renders waterfall bridge from Base EBITDA to Scenario EBITDA and PAT.
    """
    x = [
        "Base EBITDA",
        "Raw Material Δ",
        "Ocean Freight Δ",
        "OEM Pass-Through",
        "Demand Volume Δ",
        "Scenario EBITDA",
        "Fixed D&A & Tax",
        "Scenario PAT"
    ]

    # deltas
    fixed_da_tax = scenario_pat - scenario_ebitda

    y = [
        base_ebitda,
        -delta_material,
        -delta_freight,
        recovery,
        -lost_contrib,
        0, # Total
        fixed_da_tax,
        0  # Total
    ]

    measure = ["absolute", "relative", "relative", "relative", "relative", "total", "relative", "total"]

    text = [
        f"₹{base_ebitda:.1f} Cr",
        f"-₹{delta_material:.1f} Cr" if delta_material > 0 else f"+₹{-delta_material:.1f} Cr",
        f"-₹{delta_freight:.1f} Cr" if delta_freight > 0 else f"+₹{-delta_freight:.1f} Cr",
        f"+₹{recovery:.1f} Cr" if recovery >= 0 else f"-₹{-recovery:.1f} Cr",
        f"-₹{lost_contrib:.1f} Cr" if lost_contrib > 0 else f"+₹{-lost_contrib:.1f} Cr",
        f"₹{scenario_ebitda:.1f} Cr",
        f"₹{fixed_da_tax:.1f} Cr",
        f"₹{scenario_pat:.1f} Cr"
    ]

    fig = go.Figure(go.Waterfall(
        name="P&L Bridge",
        orientation="v",
        measure=measure,
        x=x,
        textposition="outside",
        text=text,
        y=y,
        connector={"line": {"color": "#94A3B8"}},
        decreasing={"marker": {"color": COLOR_STATUS_RED}},
        increasing={"marker": {"color": COLOR_STATUS_GREEN}},
        totals={"marker": {"color": COLOR_ACTIVE}}
    ))

    fig.update_layout(
        title="<b>EBITDA & PAT Waterfall Bridge (₹ Cr)</b>",
        yaxis_title="₹ Crores",
        height=400,
        showlegend=False
    )
    return fig


def plot_tornado_sensitivity(sensitivity_data: list[dict]) -> go.Figure:
    """
    Renders Tornado sensitivity chart showing impact of individual shock factors on EBITDA.
    sensitivity_data: list of dicts with keys: 'factor', 'low_ebitda', 'high_ebitda', 'base_ebitda'
    """
    df = pd.DataFrame(sensitivity_data)
    df['swing'] = (df['high_ebitda'] - df['low_ebitda']).abs()
    df = df.sort_values('swing', ascending=True)

    base_val = df['base_ebitda'].iloc[0] if not df.empty else 297.7

    fig = go.Figure()

    # Low swing (downside impact)
    fig.add_trace(go.Bar(
        y=df['factor'],
        x=df['low_ebitda'] - base_val,
        base=base_val,
        orientation='h',
        name='Adverse Stress (-20% / Shock)',
        marker=dict(color=COLOR_STATUS_RED, opacity=0.85)
    ))

    # High swing (upside or mitigated)
    fig.add_trace(go.Bar(
        y=df['factor'],
        x=df['high_ebitda'] - base_val,
        base=base_val,
        orientation='h',
        name='Favourable / Mild (+10% pass-through / Softening)',
        marker=dict(color=COLOR_STATUS_GREEN, opacity=0.85)
    ))

    fig.add_vline(x=base_val, line_dash="dash", line_color="#0F172A", annotation_text=f"Base: ₹{base_val:.1f} Cr")

    fig.update_layout(
        title="<b>Tornado Sensitivity: EBITDA Impact by Shock Factor (₹ Cr)</b>",
        xaxis_title="Scenario EBITDA (₹ Cr)",
        barmode='overlay',
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_inventory_runway(inventory_rows: list[dict]) -> go.Figure:
    """
    Plots days of cover vs effective lead time with alert boundaries.
    """
    df = pd.DataFrame(inventory_rows)
    
    # Sort by criticality: lowest runway margin first
    df['margin_days'] = df['days_of_cover'] - df['effective_lead_time']
    df = df.sort_values('margin_days', ascending=True)

    colors = []
    for _, row in df.iterrows():
        if row['status'] == 'Stock-out Risk':
            colors.append(COLOR_STATUS_RED)
        elif row['status'] == 'Watch / Reorder':
            colors.append(COLOR_STATUS_AMBER)
        else:
            colors.append(COLOR_STATUS_GREEN)

    fig = go.Figure()

    # Current Stock Days of Cover
    fig.add_trace(go.Bar(
        name="Current Days of Cover",
        y=df['material_name'],
        x=df['days_of_cover'],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{v:.0f}d" for v in df['days_of_cover']],
        textposition="auto"
    ))

    # Effective Lead Time Marker
    fig.add_trace(go.Scatter(
        name="Effective Lead Time (Supplier LT + Delay)",
        y=df['material_name'],
        x=df['effective_lead_time'],
        mode="markers",
        marker=dict(symbol="line-ns-open", size=24, line=dict(color="#0F172A", width=3)),
        hovertemplate="Effective LT: %{x:.0f} days<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Inventory Runway vs Effective Lead Time (Days)</b>",
        xaxis_title="Days",
        height=380,
        barmode='group'
    )
    return fig


def plot_freight_redating_trace(raw_df: pd.DataFrame, fixed_df: pd.DataFrame) -> go.Figure:
    """
    Before/After demonstration of the deliberate weekly re-dating data-judgement fix.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=raw_df['raw_date'],
        y=raw_df['rate'],
        name="Raw File Error (Consecutive Days in 2023)",
        mode="lines",
        line=dict(color=COLOR_STATUS_RED, width=1.5, dash="dot"),
        hovertemplate="Raw Label: %{x|%Y-%m-%d}: $%{y:,.0f}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=fixed_df['date'],
        y=fixed_df['rate'],
        name="Team 11.59 Deliberate Fix (Weekly ending 19 Mar 2026)",
        mode="lines",
        line=dict(color=COLOR_BRAND_PRIMARY, width=2.5),
        hovertemplate="Fixed Date: %{x|%Y-%m-%d}: $%{y:,.0f}<extra></extra>"
    ))

    # Add annotations for key anchors
    fig.add_annotation(
        x=pd.Timestamp("2023-10-26"), y=1342,
        text="Oct 2023 Low ($1,342)", showarrow=True, arrowhead=1
    )
    fig.add_annotation(
        x=pd.Timestamp("2024-07-15"), y=5937,
        text="Jul 2024 Red Sea Peak ($5,937)", showarrow=True, arrowhead=1
    )
    fig.add_annotation(
        x=pd.Timestamp("2026-03-19"), y=2172,
        text="Handout Baseline 19 Mar 2026 ($2,172)", showarrow=True, arrowhead=1
    )

    fig.update_layout(
        title="<b>Deliberate Data-Judgement Fix: Weekly Container Freight Re-dating</b>",
        yaxis_title="USD per 40ft Container",
        xaxis_title="Timeline",
        height=400
    )
    return fig
