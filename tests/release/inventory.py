"""
Full Interaction Inventory Generator (Section 2)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Auto-discovers every page and every interactive element:
buttons, sliders, selectboxes, radios, toggles, checkboxes, number inputs,
download buttons, popovers, and dialogs.
Saves the structured manifest to qa/release/inventory.json.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import re
import ast
from typing import Dict, Any, List
from streamlit.testing.v1 import AppTest
OUT_DIR = os.path.join(BASE_DIR, "qa", "release")
INVENTORY_FILE = os.path.join(OUT_DIR, "inventory.json")

PAGES = [
    ("pages/0_Command_Centre.py", "Control Room"),
    ("pages/1_Forecast.py", "Price & Freight Forecast"),
    ("pages/2_Scenario_Simulator.py", "What-if Scenario Simulator"),
    ("pages/3_Profit_Chain.py", "Live Recalculation Chain"),
    ("pages/4_Containers_Inventory.py", "Containers & Inventory"),
    ("pages/5_Action_Matrix.py", "Prescriptive Action Matrix"),
    ("pages/6_Assumptions_Data_Trace_About.py", "Assumptions & Data Trace")
]


def extract_ast_elements(filepath: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extracts popovers and dialogs from Python source AST."""
    popovers = []
    dialogs = []
    
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Search for st.popover(...)
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "popover":
                        label = ""
                        if node.args and isinstance(node.args[0], ast.Constant):
                            label = str(node.args[0].value)
                        popovers.append({"label": label, "lineno": node.lineno})
                # Search for @st.dialog(...)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "dialog":
                            d_label = ""
                            if dec.args and isinstance(dec.args[0], ast.Constant):
                                d_label = str(dec.args[0].value)
                            dialogs.append({"label": d_label, "function": node.name, "lineno": node.lineno})
        except Exception:
            pass

    return {"popovers": popovers, "dialogs": dialogs}


def discover_inventory() -> Dict[str, Any]:
    """Renders each page with AppTest and inspects interactive elements."""
    inventory = {
        "pages": {},
        "total_elements": 0,
        "summary": {}
    }

    total_count = 0
    type_counts = {}

    for page_rel, page_title in PAGES:
        page_path = os.path.join(BASE_DIR, page_rel)
        page_dict = {
            "title": page_title,
            "path": page_rel,
            "buttons": [],
            "sliders": [],
            "selectboxes": [],
            "radios": [],
            "toggles": [],
            "checkboxes": [],
            "number_inputs": [],
            "download_buttons": [],
            "popovers": [],
            "dialogs": []
        }

        # 1. AST static scan for popovers and dialogs
        ast_data = extract_ast_elements(page_path)
        page_dict["popovers"].extend(ast_data["popovers"])
        page_dict["dialogs"].extend(ast_data["dialogs"])

        # Also inspect ui/ components referenced by page
        if "0_Command_Centre" in page_rel:
            deck_ast = extract_ast_elements(os.path.join(BASE_DIR, "ui", "control_deck.py"))
            page_dict["popovers"].extend(deck_ast["popovers"])
            helper_ast = extract_ast_elements(os.path.join(BASE_DIR, "ui", "guided_helper.py"))
            page_dict["dialogs"].extend(helper_ast["dialogs"])

        # 2. Dynamic AppTest render
        try:
            at = AppTest.from_file(page_path)
            at.run(timeout=30)

            # Buttons
            for b in at.button:
                item = {"label": b.label or "", "key": b.key, "disabled": b.disabled}
                page_dict["buttons"].append(item)
                total_count += 1
                type_counts["button"] = type_counts.get("button", 0) + 1

            # Sliders
            for s in at.slider:
                item = {
                    "label": s.label or "",
                    "key": s.key,
                    "min": s.min,
                    "max": s.max,
                    "value": s.value
                }
                page_dict["sliders"].append(item)
                total_count += 1
                type_counts["slider"] = type_counts.get("slider", 0) + 1

            # Selectboxes
            for sb in at.selectbox:
                item = {
                    "label": sb.label or "",
                    "key": sb.key,
                    "options": [str(o) for o in (sb.options or [])],
                    "value": str(sb.value)
                }
                page_dict["selectboxes"].append(item)
                total_count += 1
                type_counts["selectbox"] = type_counts.get("selectbox", 0) + 1

            # Radios
            for r in at.radio:
                item = {
                    "label": r.label or "",
                    "key": r.key,
                    "options": [str(o) for o in (r.options or [])],
                    "value": str(r.value)
                }
                page_dict["radios"].append(item)
                total_count += 1
                type_counts["radio"] = type_counts.get("radio", 0) + 1

            # Toggles
            for tg in at.toggle:
                item = {"label": tg.label or "", "key": tg.key, "value": tg.value}
                page_dict["toggles"].append(item)
                total_count += 1
                type_counts["toggle"] = type_counts.get("toggle", 0) + 1

            # Checkboxes
            for cb in at.checkbox:
                item = {"label": cb.label or "", "key": cb.key, "value": cb.value}
                page_dict["checkboxes"].append(item)
                total_count += 1
                type_counts["checkbox"] = type_counts.get("checkbox", 0) + 1

            # Number inputs
            for ni in at.number_input:
                item = {
                    "label": ni.label or "",
                    "key": ni.key,
                    "min": ni.min,
                    "max": ni.max,
                    "value": ni.value
                }
                page_dict["number_inputs"].append(item)
                total_count += 1
                type_counts["number_input"] = type_counts.get("number_input", 0) + 1

            # Download buttons
            for db in at.download_button:
                item = {"label": db.label or "", "key": db.key}
                page_dict["download_buttons"].append(item)
                total_count += 1
                type_counts["download_button"] = type_counts.get("download_button", 0) + 1

        except Exception as e:
            page_dict["error"] = str(e)

        inventory["pages"][page_rel] = page_dict

    inventory["total_elements"] = total_count
    inventory["summary"] = type_counts
    return inventory


def save_inventory(filepath: str = INVENTORY_FILE) -> Dict[str, Any]:
    """Generates and writes qa/release/inventory.json."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    inv = discover_inventory()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2)
    return inv


def get_inventory() -> Dict[str, Any]:
    """Loads inventory manifest, regenerating if missing."""
    if not os.path.exists(INVENTORY_FILE):
        return save_inventory(INVENTORY_FILE)
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return save_inventory(INVENTORY_FILE)


if __name__ == "__main__":
    print("Generating full interaction inventory...")
    data = save_inventory()
    print(f"Inventory saved: {INVENTORY_FILE}")
    print(f"Total interactive elements: {data['total_elements']}")
    for k, v in data["summary"].items():
        print(f"  - {k}: {v}")
