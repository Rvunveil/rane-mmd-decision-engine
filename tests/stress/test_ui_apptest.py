"""
Level 1 (E02-E11), Level 2 (M30) & Level 3 (H09) Streamlit AppTest Suite.
Team 11.59 · Xovate'26
"""

import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from engine.scenario import Scenario, get_default_presets
from engine.chain import run_all

ROOT = Path(__file__).parent.parent.parent

PAGE_FILES = [
    "0_Command_Centre.py",
    "1_Forecast.py",
    "2_Scenario_Simulator.py",
    "3_Profit_Chain.py",
    "4_Containers_Inventory.py",
    "5_Action_Matrix.py",
    "6_Assumptions_Data_Trace_About.py"
]

def test_E02_all_pages_load_under_base_case():
    """E02: Every single page loads under Base case with zero exceptions."""
    for p in PAGE_FILES:
        at = AppTest.from_file(str(ROOT / "pages" / p), default_timeout=30)
        at.run()
        assert not at.exception, f"Page {p} raised exception: {at.exception}"


def test_E03_pages_load_under_presets():
    """E03: Every page loads under major presets (Red Sea, Metal Shock, Tariff FX)."""
    presets = get_default_presets()
    test_presets = ["red_sea_hormuz", "metal_shock", "tariff_fx"]
    
    # Test on key decision engine pages
    target_pages = ["0_Command_Centre.py", "2_Scenario_Simulator.py", "3_Profit_Chain.py", "5_Action_Matrix.py"]
    for p in target_pages:
        for pkey in test_presets:
            at = AppTest.from_file(str(ROOT / "pages" / p), default_timeout=30)
            at.session_state["active_scenario"] = presets[pkey]
            at.session_state["active_preset_name"] = presets[pkey].name
            at.run()
            assert not at.exception, f"Page {p} failed under preset {pkey}: {at.exception}"


def test_E05_branding_text_present():
    """E05: Mandatory branding tokens present across page outputs."""
    at = AppTest.from_file(str(ROOT / "pages" / "6_Assumptions_Data_Trace_About.py"), default_timeout=30)
    at.run()
    assert not at.exception

    all_text = " ".join([str(m.value) for m in at.markdown])
    assert "Rane (Madras)" in all_text
    assert "Team 11.59" in all_text
    assert "Vikram T" in all_text
    assert "Sayoni Dan" in all_text
    assert "Trisha Pal" in all_text
    assert "XIME Chennai" in all_text


def test_E07_preset_slider_values_documented():
    """E07: Preset dataclass holds calibrated values."""
    presets = get_default_presets()
    rs = presets["red_sea_hormuz"]
    # 2.73x = Jul 2024 peak ($5,937 / $2,172)
    assert abs(rs.freight_multiplier - 2.73) < 0.01
    assert rs.shipping_delay_days == 18
    assert rs.price_shock_pct.get("aluminium", 0.0) == 18.0

    ms = presets["metal_shock"]
    assert ms.price_shock_pct.get("copper", 0.0) == 35.0
    assert ms.price_shock_pct.get("steel_hr", 0.0) == 28.0


def test_E10_no_nan_or_unrounded_floats_in_ui():
    """E10: No raw floats like 297.700000001 or 'NaN' in formatted UI text."""
    for p in ["0_Command_Centre.py", "3_Profit_Chain.py", "5_Action_Matrix.py"]:
        at = AppTest.from_file(str(ROOT / "pages" / p), default_timeout=30)
        at.run()
        for md in at.markdown:
            val = str(md.value)
            words = val.replace(",", " ").replace(".", " ").split()
            assert "NaN" not in words, f"NaN in {p}: {val}"
            assert "nan" not in words, f"nan in {p}: {val}"
            assert "297.70000" not in val, f"Unrounded float in {p}: {val}"


def test_E11_expander_formula_boxes_present():
    """E11: Mathematical formula explain boxes exist on technical pages."""
    at = AppTest.from_file(str(ROOT / "pages" / "3_Profit_Chain.py"), default_timeout=30)
    at.run()
    assert not at.exception
    # Should have expander explanation boxes
    assert len(at.expander) >= 1


def test_M30_kpi_strip_consistency():
    """M30: Results dataclass properties yield identical KPI metrics across screens."""
    base_res = run_all(Scenario())
    assert abs(base_res.ebitda_cr - 297.7) < 0.01
    assert abs(base_res.revenue_cr - 3421.0) < 0.01
    assert abs(base_res.pat_cr - 37.6) < 0.01
    assert abs(base_res.delta_material_cr - 0.0) < 0.01


def test_H09_saved_scenarios_management():
    """H09: Scenario saving state management."""
    at = AppTest.from_file(str(ROOT / "pages" / "2_Scenario_Simulator.py"), default_timeout=30)
    at.session_state["saved_scenarios"] = [
        Scenario(name="Custom A", freight_multiplier=1.5),
        Scenario(name="Custom B", freight_multiplier=2.0)
    ]
    at.run()
    assert not at.exception
    assert len(at.session_state["saved_scenarios"]) == 2


def test_B01_regression_text_leak_scanner():
    """B1 Regression: Scans all rendered pages for broken f-strings, NaN, None, or raw format specifiers."""
    for p in PAGE_FILES:
        at = AppTest.from_file(str(ROOT / "pages" / p), default_timeout=30)
        at.run()
        assert not at.exception, f"Page {p} crashed on load: {at.exception}"

        for md in at.markdown:
            val = str(md.value)
            # Check for unformatted Python format specifiers
            assert ":.1f}" not in val, f"Broken format specifier ':.1f}}' in {p}: {val}"
            assert ":.2f}" not in val, f"Broken format specifier ':.2f}}' in {p}: {val}"
            assert "{results." not in val, f"Broken template '{{results.' in {p}: {val}"
            assert "{active_scn." not in val, f"Broken template '{{active_scn.' in {p}: {val}"

            # Check for standalone None or nan tokens in UI text (ignoring LaTeX)
            if "\\begin" not in val and "$$" not in val:
                clean_text = val.replace("(", " ").replace(")", " ").replace(",", " ").replace(".", " ")
                words = clean_text.split()
                assert "NaN" not in words, f"NaN token in {p}: {val}"
                assert "nan" not in words, f"nan token in {p}: {val}"
                assert "None" not in words, f"None token in {p}: {val}"
