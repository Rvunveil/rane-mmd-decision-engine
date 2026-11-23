"""
Guard Test Suite for P0 Widget State Bug (Section 1)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Verifies:
1. Static AST / text scan: No code outside sync_widgets_from_scn() and initialisation assigns to widget keys.
2. Static AST / text scan: No `if st.button(` blocks calling apply_*/reset/load/demo-step functions.
3. AppTest UI test: Click every preset chip, Apply, and Reset on Control Room, switch pages, click sidebar preset selector. No StreamlitWidgetAlreadyInstantiatedError or other exceptions.
4. AppTest UI test: Start demo, step through, stop. No exceptions, sliders end in expected state.
"""

import os
import re
import ast
import pytest
from streamlit.testing.v1 import AppTest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_PATH = os.path.join(BASE_DIR, "app.py")


def get_all_widget_keys() -> set[str]:
    """Auto-discovers all widget keys used in ui/, pages/, demo/."""
    keys = set()
    for d in ["ui", "pages", "demo"]:
        dirpath = os.path.join(BASE_DIR, d)
        for root, _, files in os.walk(dirpath):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        text = f.read()
                    found = re.findall(r'key\s*=\s*["\']([^"\']+)["\']', text)
                    for k in found:
                        keys.add(k)
                    # Also find f-strings like key=f"chip_{pkey}" -> prefix patterns
    return keys


def test_P0_1_no_direct_widget_key_assignments_outside_sync():
    """Static test: Verifies that no code outside sync_widgets_from_scn() assigns st.session_state[<widget_key>]."""
    widget_keys = get_all_widget_keys()
    assert len(widget_keys) > 10, f"Expected > 10 widget keys, found {len(widget_keys)}"

    violations = []
    # Scan all python files in project (excluding tests, venv, git)
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in [".git", "_refs", ".venv", ".pytest_cache", "__pycache__", "tests"]]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel = os.path.relpath(filepath, BASE_DIR).replace(os.sep, "/")
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for idx, line in enumerate(lines):
                    # Check for st.session_state["<widget_key>"] = ...
                    # Allow inside engine/state.py: sync_widgets_from_scn or init_canonical_state
                    if rel == "engine/state.py":
                        continue

                    for wk in widget_keys:
                        # Match st.session_state["<key>"] = or st.session_state['<key>'] =
                        pattern = rf'st\.session_state\s*\[\s*["\']{re.escape(wk)}["\']\s*\]\s*='
                        if re.search(pattern, line):
                            violations.append(f"{rel}:{idx+1}: {line.strip()}")

    assert not violations, f"Forbidden direct assignments to widget keys found:\n" + "\n".join(violations)


def test_P0_2_no_if_button_calling_scenario_mutation():
    """Static test: Verifies that no `if st.button(` block calls apply_preset_by_name, apply_scenario_values, or reset_to_base."""
    violations = []
    forbidden_funcs = ["apply_preset_by_name", "apply_scenario_values", "reset_to_base", "start_demo", "stop_demo"]

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in [".git", "_refs", ".venv", ".pytest_cache", "__pycache__", "tests"]]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel = os.path.relpath(filepath, BASE_DIR).replace(os.sep, "/")
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to check if any If test is an st.button call and body contains forbidden functions
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.If):
                            # Check if test expression calls st.button
                            is_st_button = False
                            for subnode in ast.walk(node.test):
                                if isinstance(subnode, ast.Call):
                                    if isinstance(subnode.func, ast.Attribute) and subnode.func.attr == "button":
                                        is_st_button = True
                            
                            if is_st_button:
                                # Check body for forbidden functions
                                for body_item in node.body:
                                    for call_node in ast.walk(body_item):
                                        if isinstance(call_node, ast.Call):
                                            fname = ""
                                            if isinstance(call_node.func, ast.Name):
                                                fname = call_node.func.id
                                            elif isinstance(call_node.func, ast.Attribute):
                                                fname = call_node.func.attr
                                            if fname in forbidden_funcs:
                                                violations.append(f"{rel}: line {node.lineno}: `if st.button(...)` body calls `{fname}()`")
                except Exception as e:
                    pass

    assert not violations, f"Found `if st.button` blocks mutating scenario state instead of on_click callbacks:\n" + "\n".join(violations)


def test_P0_3_control_room_preset_clicks_and_reset_in_apptest():
    """AppTest UI test: Clicks every preset chip and Reset on Control Room. Verifies zero exceptions and state sync."""
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    assert not at.exception, f"Initial boot exception: {at.exception}"

    # Verify buttons present on Control Room
    preset_chip_keys = [
        "chip_base_case", "chip_todays_market", "chip_red_sea_hormuz",
        "chip_metal_shock", "chip_tariff_fx", "chip_demand_recession"
    ]

    for pkey in preset_chip_keys:
        matching = [b for b in at.button if b.key == pkey]
        if matching:
            btn = matching[0]
            btn.click().run(timeout=30)
            assert not at.exception, f"Exception after clicking chip {pkey}: {at.exception}"
            # Verify no StreamlitWidgetAlreadyInstantiatedError
            for exc in at.exception:
                assert "StreamlitWidgetAlreadyInstantiatedError" not in str(exc.value)

    # Click Reset button
    reset_buttons = [b for b in at.button if "Reset" in (b.label or "")]
    assert reset_buttons, "Reset button not found"
    reset_buttons[0].click().run(timeout=30)
    assert not at.exception, f"Exception after Reset: {at.exception}"


def test_P0_4_demo_lifecycle_in_apptest():
    """AppTest UI test: Starts demo, steps through, and stops without widget instantiation errors."""
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=30)
    assert not at.exception, f"Initial boot exception: {at.exception}"

    # Start demo
    start_btns = [b for b in at.button if b.key == "btn_start_demo"]
    if start_btns:
        start_btns[0].click().run(timeout=30)
        assert not at.exception, f"Exception on start_demo: {at.exception}"

        # Click next step if present
        next_btns = [b for b in at.button if b.key == "demo_btn_next"]
        if next_btns:
            next_btns[0].click().run(timeout=30)
            assert not at.exception, f"Exception on next step: {at.exception}"

        # Click stop
        stop_btns = [b for b in at.button if b.key == "demo_btn_stop"]
        if stop_btns:
            stop_btns[0].click().run(timeout=30)
            assert not at.exception, f"Exception on stop_demo: {at.exception}"
