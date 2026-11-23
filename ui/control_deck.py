"""
Materials Control Deck Component (Section 2a / Section 3 / P0 Fix)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Renders the top control deck:
- Scenario chips with active highlighting and on_click callbacks (P0)
- 6 big levers inline with delta vs base
- Popover for individual metals with on_change callbacks
- Reset, Save, Compare, and Guided Helper actions
- Simple View toggle
"""

import streamlit as st
from engine.state import (
    init_canonical_state,
    apply_scenario_values,
    apply_preset_by_name,
    reset_to_base,
    get_current_scenario,
    load_glossary
)
from engine.chain import run_all
from engine.scenario import get_default_presets
from ui.guided_helper import render_guided_helper_dialog
from ui.theme import format_money_cr


def render_control_deck():
    """
    Renders the unified interactive control deck directly on the dashboard.
    Enforces Rule 3b: no duplicate value= and key= arguments.
    Enforces P0: All scenario mutations happen via on_click/on_change callbacks.
    """
    init_canonical_state()
    scn = st.session_state["scn"]
    presets = get_default_presets()
    glossary = load_glossary()

    # 1. SCENARIO CHIPS ROW (P0: on_click callbacks)
    chip_cols = st.columns([1, 1.1, 1.3, 1, 1.1, 1.2, 0.8, 1.5])
    active_name = scn.get("name", "Custom")

    preset_chips = [
        ("Base", "base_case"),
        ("Today's market", "todays_market"),
        ("Red Sea / Hormuz", "red_sea_hormuz"),
        ("Metal shock", "metal_shock"),
        ("Tariff & FX", "tariff_fx"),
        ("Demand recession", "demand_recession")
    ]

    for idx, (label, pkey) in enumerate(preset_chips):
        with chip_cols[idx]:
            is_active = (active_name == label) or (label == "Base" and active_name == "Base case")
            btn_type = "primary" if is_active else "secondary"
            st.button(
                label,
                key=f"chip_{pkey}",
                type=btn_type,
                use_container_width=True,
                on_click=apply_preset_by_name,
                args=(pkey,)
            )

    with chip_cols[6]:
        is_custom = active_name not in ["Base case", "Base", "Today's market", "Red Sea / Hormuz crisis", "Metal shock", "Tariff & FX escalation", "Demand recession"]
        st.button("Custom", key="chip_custom", type="primary" if is_custom else "secondary", disabled=True, use_container_width=True)

    with chip_cols[7]:
        if st.button(":material/help: What happened?", type="secondary", use_container_width=True):
            render_guided_helper_dialog()

    # 2. SIX BIG LEVERS INLINE (P0: on_change callbacks, no value= with key=)
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    l_cols = st.columns(6)

    def _on_metal_change():
        apply_scenario_values({"metal_master": st.session_state["deck_metal"], "name": "Custom"})

    def _on_freight_change():
        apply_scenario_values({"freight_multiplier": st.session_state["deck_freight"], "name": "Custom"})

    def _on_delay_change():
        apply_scenario_values({"shipping_delay_days": st.session_state["deck_delay"], "name": "Custom"})

    def _on_fx_change():
        apply_scenario_values({"fx_inr_usd": st.session_state["deck_fx"], "name": "Custom"})

    def _on_pass_through_change():
        apply_scenario_values({"oem_pass_through_pct": st.session_state["deck_pass_through"], "name": "Custom"})

    def _on_demand_change():
        apply_scenario_values({"demand_volume_pct": st.session_state["deck_demand"], "name": "Custom"})

    # Levers with live delta tags vs Base Case
    with l_cols[0]:
        val_metal = scn.get("metal_master", 0.0)
        delta_m = f"+{val_metal:.0f}%" if val_metal > 0 else (f"−{abs(val_metal):.0f}%" if val_metal < 0 else "0%")
        st.markdown(f"<div class='mmd-lever-header'><b>Metal Prices</b> <span class='mmd-lever-delta'>{delta_m}</span></div>", unsafe_allow_html=True)
        st.slider("Metal Prices", min_value=-30.0, max_value=60.0, step=1.0, key="deck_metal", on_change=_on_metal_change, label_visibility="collapsed")

    with l_cols[1]:
        val_fr = scn.get("freight_multiplier", 1.0)
        delta_fr = f"+{val_fr - 1.0:+.2f}x" if val_fr != 1.0 else "1.0x"
        st.markdown(f"<div class='mmd-lever-header'><b>Freight Mult</b> <span class='mmd-lever-delta'>{delta_fr}</span></div>", unsafe_allow_html=True)
        st.slider("Freight Mult", min_value=0.5, max_value=4.0, step=0.05, key="deck_freight", on_change=_on_freight_change, label_visibility="collapsed")

    with l_cols[2]:
        val_d = scn.get("shipping_delay_days", 0)
        delta_d = f"+{val_d}d" if val_d > 0 else "0d"
        st.markdown(f"<div class='mmd-lever-header'><b>Shipping Delay</b> <span class='mmd-lever-delta'>{delta_d}</span></div>", unsafe_allow_html=True)
        st.slider("Shipping Delay", min_value=0, max_value=45, step=1, key="deck_delay", on_change=_on_delay_change, label_visibility="collapsed")

    with l_cols[3]:
        val_fx = scn.get("fx_inr_usd", 84.56)
        delta_fx = f"+₹{val_fx - 84.56:.2f}" if val_fx > 84.56 else (f"−₹{84.56 - val_fx:.2f}" if val_fx < 84.56 else "Base")
        st.markdown(f"<div class='mmd-lever-header'><b>USD / INR</b> <span class='mmd-lever-delta'>{delta_fx}</span></div>", unsafe_allow_html=True)
        st.slider("USD / INR", min_value=80.0, max_value=105.0, step=0.25, key="deck_fx", on_change=_on_fx_change, label_visibility="collapsed")

    with l_cols[4]:
        val_pt = scn.get("oem_pass_through_pct", 50.0)
        delta_pt = f"{val_pt:.0f}%"
        st.markdown(f"<div class='mmd-lever-header'><b>OEM Pass-Thru</b> <span class='mmd-lever-delta'>{delta_pt}</span></div>", unsafe_allow_html=True)
        st.slider("OEM Pass-Through", min_value=0.0, max_value=100.0, step=5.0, key="deck_pass_through", on_change=_on_pass_through_change, label_visibility="collapsed")

    with l_cols[5]:
        val_dem = scn.get("demand_volume_pct", 0.0)
        delta_dem = f"{val_dem:+.0f}%" if val_dem != 0 else "0%"
        st.markdown(f"<div class='mmd-lever-header'><b>Demand Volume</b> <span class='mmd-lever-delta'>{delta_dem}</span></div>", unsafe_allow_html=True)
        st.slider("Demand Volume", min_value=-30.0, max_value=30.0, step=1.0, key="deck_demand", on_change=_on_demand_change, label_visibility="collapsed")

    # 3. CONTROLS FOOTER STRIP (Reset, Save, Compare, Simple View toggle, Metal Drawer)
    f_cols = st.columns([1, 1, 1.2, 1.8, 1.5])
    
    with f_cols[0]:
        st.button(":material/restart_alt: Reset", use_container_width=True, on_click=reset_to_base)

    with f_cols[1]:
        with st.popover(":material/bookmark: Save"):
            s_name = st.text_input("Scenario Name", value=f"Scenario-{len(st.session_state.get('saved_scenarios', {})) + 1}")
            def _on_save():
                st.session_state.setdefault("saved_scenarios", {})[s_name] = get_current_scenario()
            st.button("Save Current", on_click=_on_save)

    with f_cols[2]:
        with st.popover(":material/compare_arrows: Compare"):
            st.markdown("#### Scenario Comparison")
            base_s = presets["base_case"]
            active_s = get_current_scenario()
            b_res = run_all(base_s)
            a_res = run_all(active_s)
            
            comp_data = {
                "Metric": ["Revenue", "EBITDA", "EBITDA Margin", "PAT", "Material Spend", "Freight Spend"],
                "Base Case": [
                    format_money_cr(b_res.revenue_cr),
                    format_money_cr(b_res.ebitda_cr),
                    f"{b_res.ebitda_margin_pct:.1f}%",
                    format_money_cr(b_res.pat_cr),
                    format_money_cr(b_res.material_spend_cr),
                    format_money_cr(b_res.ocean_freight_spend_cr)
                ],
                f"Active ({active_s.name})": [
                    format_money_cr(a_res.revenue_cr),
                    format_money_cr(a_res.ebitda_cr),
                    f"{a_res.ebitda_margin_pct:.1f}%",
                    format_money_cr(a_res.pat_cr),
                    format_money_cr(a_res.material_spend_cr),
                    format_money_cr(a_res.ocean_freight_spend_cr)
                ]
            }
            st.dataframe(comp_data, use_container_width=True, hide_index=True)

    with f_cols[3]:
        with st.popover(":material/tune: Individual Metals"):
            st.markdown("<b>Fine-Tune Individual Material Price Shocks (%):</b>", unsafe_allow_html=True)
            
            def _make_fine_cb(metal_key):
                def _cb():
                    val = st.session_state.get(f"fine_{metal_key}", 0.0)
                    apply_scenario_values({metal_key: val, "name": "Custom"})
                return _cb

            for m_key, m_label in [
                ("copper", "Copper Cathode"),
                ("aluminium", "Aluminium Ingot"),
                ("nickel", "Nickel Superalloy"),
                ("steel_hr", "Steel HR Coil"),
                ("steel_cr", "Steel CR Coil"),
                ("resin", "Phenolic Resin"),
                ("rubber", "Natural Rubber")
            ]:
                st.slider(
                    m_label,
                    min_value=-30.0,
                    max_value=60.0,
                    step=1.0,
                    key=f"fine_{m_key}",
                    on_change=_make_fine_cb(m_key)
                )

    with f_cols[4]:
        def _on_simple_toggle():
            st.session_state["simple_view"] = st.session_state.get("simple_view_toggle", False)

        st.toggle("Simple view", key="simple_view_toggle", on_change=_on_simple_toggle)

    st.markdown("<hr style='margin: 8px 0 16px 0; border: none; border-top: 1px solid #C9D1D5;'>", unsafe_allow_html=True)
