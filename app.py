"""
Rane (Madras) MMD Decision Engine · Main Application Entry Point
Team 11:59 · Xovate'26 Management Hackathon
Tagline: "See the shock. Measure it. Decide."
"""

import streamlit as st
from engine.state import sync_widgets_from_scn
from ui.layout import page_setup, render_sidebar

# Initialize layout and session state
page_setup(title="MMD Decision Engine · Team 11:59")

# P0: Sync all widget keys from canonical scn BEFORE any widget is created
sync_widgets_from_scn()

# Define pages for st.navigation
pages = [
    st.Page("pages/0_Command_Centre.py", title="Materials Control Room", icon=":material/dashboard:", default=True),
    st.Page("pages/1_Forecast.py", title="1 Price & Freight Forecast", icon=":material/trending_up:"),
    st.Page("pages/2_Scenario_Simulator.py", title="2 What-if Scenario Simulator", icon=":material/tune:"),
    st.Page("pages/3_Profit_Chain.py", title="3 Live Recalculation Chain", icon=":material/account_tree:"),
    st.Page("pages/4_Containers_Inventory.py", title="4 Containers & Inventory", icon=":material/inventory_2:"),
    st.Page("pages/5_Action_Matrix.py", title="5 Prescriptive Action Matrix", icon=":material/checklist:"),
    st.Page("pages/6_Assumptions_Data_Trace_About.py", title="Assumptions & Data Trace", icon=":material/info:")
]

nav = st.navigation(pages)

# Demo mode hook (runs before sidebar and page widgets, using rerun-safe state)
try:
    from demo import maybe_run_demo
except ImportError:
    maybe_run_demo = None
if maybe_run_demo:
    maybe_run_demo()

# Render global shared sidebar
render_sidebar()

# Run the selected page
nav.run()
