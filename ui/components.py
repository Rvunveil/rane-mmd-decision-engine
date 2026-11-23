"""
Shared UI Components for Rane (Madras) MMD Decision Engine
Team 11:59 · Xovate'26
"""

import streamlit as st
from ui.theme import format_money_cr, format_pct

def page_header(title: str, subtitle: str, module_no: str = None):
    """Render standardized page header with module badge."""
    badge_html = f'<span class="mmd-module-badge">{module_no}</span> ' if module_no else ''
    st.markdown(
        f"""
        <div class="mmd-header-container">
            <h1 class="mmd-header-title">{badge_html}{title}</h1>
            <p class="mmd-header-sub">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def kpi_card(label: str, value: str, delta_str: str = "", delta_type: str = "neutral", tooltip: str = ""):
    """Render a single KPI card."""
    delta_class = "mmd-delta-neutral"
    if delta_type == "good":
        delta_class = "mmd-delta-down-good"
    elif delta_type == "bad":
        delta_class = "mmd-delta-up-bad"

    delta_html = f'<div class="mmd-kpi-delta {delta_class}">{delta_str}</div>' if delta_str else ''
    title_attr = f'title="{tooltip}"' if tooltip else ''

    st.markdown(
        f"""
        <div class="mmd-kpi-card" {title_attr}>
            <div class="mmd-kpi-label">{label}</div>
            <div class="mmd-kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def kpi_strip(results, base_results):
    """
    Standard top KPI strip across all pages:
    Revenue, EBITDA ₹ Cr + margin, PAT, Material Δ, Worst days of cover, Top action
    """
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # 1. Revenue
    rev_delta = results.revenue_cr - base_results.revenue_cr
    rev_delta_str = f"{rev_delta:+.1f} Cr vs base" if abs(rev_delta) > 0.05 else "Baseline"
    with col1:
        kpi_card("Revenue", format_money_cr(results.revenue_cr), rev_delta_str, "good" if rev_delta >= 0 else "bad")

    # 2. EBITDA + Margin
    ebitda_delta = results.ebitda_cr - base_results.ebitda_cr
    ebitda_delta_str = f"{ebitda_delta:+.1f} Cr ({results.ebitda_margin_pct:.1f}%)"
    with col2:
        kpi_card("EBITDA", format_money_cr(results.ebitda_cr), ebitda_delta_str, "good" if ebitda_delta >= 0 else "bad")

    # 3. PAT
    pat_delta = results.pat_cr - base_results.pat_cr
    pat_delta_str = f"{pat_delta:+.1f} Cr vs base" if abs(pat_delta) > 0.05 else "Baseline"
    with col3:
        kpi_card("Net Profit (PAT)", format_money_cr(results.pat_cr), pat_delta_str, "good" if pat_delta >= 0 else "bad")

    # 4. Material Δ
    mat_delta = results.delta_material_cr
    if abs(results.oem_recovery_cr) < 0.05:
        mat_delta_str = "Net pass-thru: ₹0.0 Cr"
    elif results.oem_recovery_cr > 0:
        mat_delta_str = f"Net pass-thru: +₹{results.oem_recovery_cr:.1f} Cr"
    else:
        mat_delta_str = f"Net pass-thru: −₹{abs(results.oem_recovery_cr):.1f} Cr"
    with col4:
        kpi_card("Material Shock Δ", format_money_cr(mat_delta), mat_delta_str, "bad" if mat_delta > 0 else "good")

    # 5. Worst Runway
    worst_runway = results.worst_days_of_cover
    runway_status = "good" if worst_runway > 35 else ("bad" if worst_runway < 20 else "neutral")
    with col5:
        kpi_card("Min Days of Cover", f"{worst_runway:.0f} days", f"Material: {results.worst_material_name}", runway_status)

    # 6. Top Action
    top_act = results.top_action_title
    short_act = getattr(results, "top_action_short_name", "") or (top_act if len(top_act) <= 20 else top_act[:18])
    net_val = results.top_action_net_benefit_cr
    if abs(net_val) < 0.05:
        net_str = "Net: ₹0.0 Cr"
    elif net_val > 0:
        net_str = f"Net: +₹{net_val:.1f} Cr"
    else:
        net_str = f"Net: −₹{abs(net_val):.1f} Cr"
    with col6:
        kpi_card("Top Ranked Action", short_act, net_str, "good", tooltip=top_act)


def status_badge(text: str, status: str = "green") -> str:
    """Return inline HTML for status pill."""
    color_map = {
        "green": ("#ECFDF5", "#065F46", "#A7F3D0"),
        "amber": ("#FFFBEB", "#B45309", "#FDE68A"),
        "red": ("#FEF2F2", "#B91C1C", "#FECACA"),
        "neutral": ("#F8FAFC", "#475569", "#E2E8F0")
    }
    bg, fg, border = color_map.get(status, color_map["neutral"])
    return f'<span style="background-color:{bg}; color:{fg}; border:1px solid {border}; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700;">{text}</span>'


def data_badge(badge_type: str) -> str:
    """
    Renders standardized transparency badge:
    'LIVE DATA' | 'TEAM ASSUMPTION' | 'SAMPLE DATA' | 'TOO SHORT TO FORECAST'
    """
    if badge_type == "LIVE DATA":
        return '<span class="badge-live">● LIVE DATA</span>'
    elif badge_type == "TEAM ASSUMPTION":
        return '<span class="badge-assumption">▲ TEAM ASSUMPTION</span>'
    elif badge_type == "SAMPLE DATA":
        return '<span class="badge-sample">■ SAMPLE DATA</span>'
    elif badge_type == "TOO SHORT TO FORECAST":
        return '<span class="badge-short">! TOO SHORT TO FORECAST</span>'
    return f'<span>{badge_type}</span>'


def insight(text: str, is_warning: bool = False):
    """Renders prominent key analytical takeaway box."""
    css_class = "mmd-warning-box" if is_warning else "mmd-insight-box"
    prefix = "🚨 <b>CRITICAL DECISION ALERT:</b> " if is_warning else "💡 <b>EXECUTIVE INSIGHT:</b> "
    st.markdown(
        f"""
        <div class="{css_class}">
            {prefix}{text}
        </div>
        """,
        unsafe_allow_html=True
    )


def section(title: str, help_tooltip: str = ""):
    """Renders section title with optional tooltip."""
    help_html = f'<span title="{help_tooltip}" style="cursor:help; font-size:0.85rem; color:#94A3B8;">ⓘ</span>' if help_tooltip else ""
    st.markdown(
        f"""
        <div class="mmd-section-title">
            <span>{title}</span> {help_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def explain_box(title: str, formula: str, data_source: str):
    """Renders traceable formula explain box."""
    with st.expander(f"📐 How is this calculated? ({title})", expanded=False):
        st.markdown(f"**Mathematical Formula:** `{formula}`")
        st.markdown(f"**Data Lineage & Source:** {data_source}")
