"""
Streamlit AppTest Smoke Suite
Verifies acceptance test #7 from Section 8:
Every page loads with zero exceptions under Base Case and all presets.
"""

import pytest
import os
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).parent.parent

def test_app_smoke_base_case():
    """Verifies that app.py initializes and renders Command Centre with zero exceptions."""
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"AppTest encountered exception: {at.exception}"


def test_command_centre_smoke():
    """Verifies Command Centre page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "0_Command_Centre.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Command Centre encountered exception: {at.exception}"


def test_forecast_page_smoke():
    """Verifies Forecast page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "1_Forecast.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Forecast page encountered exception: {at.exception}"


def test_scenario_simulator_smoke():
    """Verifies Scenario Simulator page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "2_Scenario_Simulator.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Scenario Simulator encountered exception: {at.exception}"


def test_profit_chain_smoke():
    """Verifies Profit Chain page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "3_Profit_Chain.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Profit Chain encountered exception: {at.exception}"


def test_containers_inventory_smoke():
    """Verifies Containers & Inventory page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "4_Containers_Inventory.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Containers & Inventory encountered exception: {at.exception}"


def test_action_matrix_smoke():
    """Verifies Action Matrix page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "5_Action_Matrix.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Action Matrix encountered exception: {at.exception}"


def test_assumptions_page_smoke():
    """Verifies Assumptions, Data Trace & About page renders without error."""
    at = AppTest.from_file(str(ROOT / "pages" / "6_Assumptions_Data_Trace_About.py"), default_timeout=30)
    at.run()
    assert not at.exception, f"Assumptions page encountered exception: {at.exception}"

