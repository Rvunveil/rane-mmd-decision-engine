"""
Rane (Madras) MMD Decision Engine · Main Application Entry Point
Team 11:59 · Xovate'26 Management Hackathon
Tagline: "See the shock. Measure it. Decide."
"""

import streamlit as st
from ui.layout import page_setup, render_sidebar

# Initialize layout and session state
page_setup(title="MMD Decision Engine · Team 11:59")

# Define pages for st.navigation
pages = [
    st.Page("pages/0_Command_Centre.py", title="Materials Control Room", icon="🎛️", default=True),
    st.Page("pages/1_Forecast.py", title="1 Price & Freight Forecast", icon="📈"),
    st.Page("pages/2_Scenario_Simulator.py", title="2 What-if Scenario Simulator", icon="⚡"),
    st.Page("pages/3_Profit_Chain.py", title="3 Live Recalculation Chain", icon="⛓️"),
    st.Page("pages/4_Containers_Inventory.py", title="4 Containers & Inventory", icon="🚢"),
    st.Page("pages/5_Action_Matrix.py", title="5 Prescriptive Action Matrix", icon="📋"),
    st.Page("pages/6_Assumptions_Data_Trace_About.py", title="Assumptions & Data Trace", icon="ℹ️")
]

nav = st.navigation(pages)

# Render global shared sidebar
render_sidebar()

# Run the selected page
nav.run()
