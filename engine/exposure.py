"""
Inbound Supply Chain Exposure Map Engine (N2)
Rane (Madras) MMD Decision Engine · Team 11:59 · Xovate'26

Models global inbound trade lanes, maritime chokepoints, container cargo in transit,
and calculates calibrated spend-at-risk (₹ Cr) across supplier origins and plant destinations.
"""

from typing import Any
import plotly.graph_objects as go
from engine.scenario import Scenario
from engine.data_loader import load_assumptions

CHOKEPOINTS = [
    {
        "id": "suez",
        "name": "Bab el-Mandeb & Suez Canal",
        "lat": 12.58,
        "lon": 43.33,
        "description": "Red Sea maritime artery connecting Mediterranean to Indian Ocean."
    },
    {
        "id": "hormuz",
        "name": "Strait of Hormuz",
        "lat": 26.56,
        "lon": 56.25,
        "description": "Persian Gulf exit corridor carrying primary aluminium ingots."
    },
    {
        "id": "cape",
        "name": "Cape of Good Hope",
        "lat": -34.35,
        "lon": 18.47,
        "description": "Southern bypass corridor adding 12-16 days extra sailing time."
    },
    {
        "id": "malacca",
        "name": "Strait of Malacca",
        "lat": 2.50,
        "lon": 101.50,
        "description": "Southeast Asian trade artery for East Asian polymers and nickel."
    }
]

TRADE_LANES = [
    {
        "id": "LANE-CU-CHILE",
        "material": "copper",
        "name": "Chilean Copper Cathode Maritime Lane",
        "origin_name": "San Antonio, Chile",
        "origin_coords": (-33.59, -71.61),
        "dest_name": "Chennai / Ennore Port, India",
        "dest_coords": (13.08, 80.27),
        "primary_carrier": "MSC",
        "normal_transit_days": 38,
        "base_annual_spend_cr": 122.3, # ~10% of material spend
        "chokepoints": ["suez", "cape"]
    },
    {
        "id": "LANE-AL-GULF",
        "material": "aluminium",
        "name": "Gulf Aluminium Ingot Lane",
        "origin_name": "Jebel Ali / Manama (UAE/Bahrain)",
        "origin_coords": (25.01, 55.06),
        "dest_name": "JNPT / Mumbai & Chennai, India",
        "dest_coords": (18.95, 72.95),
        "primary_carrier": "Maersk / CMA CGM",
        "normal_transit_days": 18,
        "base_annual_spend_cr": 269.06, # ~22% of material spend
        "chokepoints": ["hormuz"]
    },
    {
        "id": "LANE-NI-INDO",
        "material": "nickel",
        "name": "Indonesian Precision Nickel Lane",
        "origin_name": "Surabaya, Indonesia",
        "origin_coords": (-7.25, 112.75),
        "dest_name": "Chennai Port, India",
        "dest_coords": (13.08, 80.27),
        "primary_carrier": "ONE",
        "normal_transit_days": 14,
        "base_annual_spend_cr": 73.38, # ~6% of material spend
        "chokepoints": ["malacca"]
    },
    {
        "id": "LANE-RESIN-KOREA",
        "material": "resin",
        "name": "East Asian Specialty Resin Lane",
        "origin_name": "Busan, South Korea",
        "origin_coords": (35.18, 129.07),
        "dest_name": "Chennai Port, India",
        "dest_coords": (13.08, 80.27),
        "primary_carrier": "Hapag-Lloyd",
        "normal_transit_days": 19,
        "base_annual_spend_cr": 73.38, # ~6% of material spend
        "chokepoints": ["malacca"]
    },
    {
        "id": "LANE-STEEL-DOM",
        "material": "steel_hr",
        "name": "Domestic Steel Mill Coastal/Rail Corridor",
        "origin_name": "Angul & Hazira Mills, India",
        "origin_coords": (21.17, 72.74),
        "dest_name": "Rane Sanand & Puducherry Plants",
        "dest_coords": (13.08, 80.27),
        "primary_carrier": "Indian Railways / Coastal Feeder",
        "normal_transit_days": 6,
        "base_annual_spend_cr": 611.5, # ~50% of material spend (Steels)
        "chokepoints": []
    },
    {
        "id": "LANE-RUBBER-KOT",
        "material": "rubber",
        "name": "Kerala Natural Rubber Inland Corridor",
        "origin_name": "Kottayam, Kerala",
        "origin_coords": (9.59, 76.52),
        "dest_name": "Rane Friction Plants (Puducherry/Trichy)",
        "dest_coords": (11.94, 79.80),
        "primary_carrier": "Dedicated Domestic Fleet",
        "normal_transit_days": 3,
        "base_annual_spend_cr": 73.38, # ~6% of material spend
        "chokepoints": []
    }
]


def compute_exposure_map(scenario: Scenario, assumptions: dict = None) -> dict[str, Any]:
    """
    Evaluates exposure across all inbound trade lanes and calculates spend-at-risk.
    """
    if assumptions is None:
        assumptions = load_assumptions()

    delay = scenario.shipping_delay_days
    freight_mult = scenario.freight_multiplier

    # Evaluate chokepoints
    chokepoints_res = []
    for cp in CHOKEPOINTS:
        cid = cp["id"]
        if cid == "suez":
            if delay > 12:
                status = "RED"
                delay_days = delay
                reason = f"Severe Red Sea disruption; commercial traffic diverted via Cape (+{delay}d)"
            elif delay > 0:
                status = "AMBER"
                delay_days = delay
                reason = f"Vessels facing convoy delays and war-risk insurance surcharges (+{delay}d)"
            else:
                status = "GREEN"
                delay_days = 0
                reason = "Normal Suez maritime transit on schedule"
        elif cid == "hormuz":
            al_shock = scenario.price_shock_pct.get("aluminium", 0.0)
            if al_shock > 20.0 or delay > 15:
                status = "RED"
                delay_days = 7
                reason = "Acute Persian Gulf tension; vessel escort required"
            elif al_shock > 10.0 or delay > 5:
                status = "AMBER"
                delay_days = 4
                reason = "Port dwell congestion at Jebel Ali / Manama"
            else:
                status = "GREEN"
                delay_days = 0
                reason = "Unimpeded transit through Hormuz straits"
        elif cid == "cape":
            if delay > 0:
                status = "AMBER"
                delay_days = delay
                reason = f"Bypass route active (+{delay}d sailing around African horn)"
            else:
                status = "GREEN"
                delay_days = 0
                reason = "Standard baseline maritime schedule"
        else: # Malacca
            status = "GREEN"
            delay_days = 0
            reason = "Free open ocean transit"

        chokepoints_res.append({
            "id": cid,
            "name": cp["name"],
            "lat": cp["lat"],
            "lon": cp["lon"],
            "status": status,
            "delay_days": delay_days,
            "reason": reason
        })

    # Evaluate trade lanes
    lanes_res = []
    total_spend_at_risk = 0.0
    active_vessels = 6

    for lane in TRADE_LANES:
        mat = lane["material"]
        shock_pct = scenario.price_shock_pct.get(mat, 0.0)
        base_spend = lane["base_annual_spend_cr"]
        
        # Spend at risk represents annual value exposed to disruptions
        is_maritime_disrupted = any(
            cp["status"] in ["RED", "AMBER"]
            for cp in chokepoints_res
            if cp["id"] in lane["chokepoints"]
        )
        
        if is_maritime_disrupted:
            effective_transit = lane["normal_transit_days"] + delay
            status = "RED" if delay > 12 else "AMBER"
            # Pipeline in transit = annual spend * (effective transit days / 365)
            pipeline_cr = (base_spend * (1.0 + shock_pct / 100.0)) * (effective_transit / 365.0)
            # Add freight surcharge exposure
            freight_exposure = 25.0 * (freight_mult - 1.0) * (base_spend / 1223.0)
            lane_spend_at_risk = pipeline_cr + max(freight_exposure, 0.0)
        else:
            effective_transit = lane["normal_transit_days"]
            status = "GREEN"
            pipeline_cr = base_spend * (effective_transit / 365.0)
            lane_spend_at_risk = pipeline_cr * 0.10 # minimal 10% operational pipeline buffer

        total_spend_at_risk += lane_spend_at_risk

        lanes_res.append({
            "id": lane["id"],
            "name": lane["name"],
            "material": mat,
            "origin_name": lane["origin_name"],
            "origin_coords": lane["origin_coords"],
            "dest_name": lane["dest_name"],
            "dest_coords": lane["dest_coords"],
            "primary_carrier": lane["primary_carrier"],
            "normal_transit_days": lane["normal_transit_days"],
            "effective_transit_days": effective_transit,
            "status": status,
            "pipeline_in_transit_cr": round(pipeline_cr, 2),
            "spend_at_risk_cr": round(lane_spend_at_risk, 2)
        })

    return {
        "lanes": lanes_res,
        "chokepoints": chokepoints_res,
        "total_spend_at_risk_cr": round(total_spend_at_risk, 2),
        "active_vessel_count": active_vessels
    }


def plot_exposure_map(exposure_data: dict[str, Any]) -> go.Figure:
    """
    Renders interactive global supply chain exposure map using Plotly scattergeo.
    """
    fig = go.Figure()

    # 1. Draw Trade Lanes (Lines)
    status_colors = {"GREEN": "#10B981", "AMBER": "#F59E0B", "RED": "#EF4444"}

    for lane in exposure_data["lanes"]:
        color = status_colors.get(lane["status"], "#64748B")
        orig_lat, orig_lon = lane["origin_coords"]
        dest_lat, dest_lon = lane["dest_coords"]

        fig.add_trace(go.Scattergeo(
            locationmode="ISO-3",
            lon=[orig_lon, dest_lon],
            lat=[orig_lat, dest_lat],
            mode="lines+markers",
            line=dict(width=2.5 if lane["status"] == "RED" else 1.8, color=color),
            marker=dict(size=6, color=color),
            name=lane["name"],
            hoverinfo="text",
            hovertext=(
                f"<b>{lane['name']}</b><br>"
                f"Origin: {lane['origin_name']}<br>"
                f"Destination: {lane['dest_name']}<br>"
                f"Carrier: {lane['primary_carrier']}<br>"
                f"Transit: {lane['effective_transit_days']} days (Base: {lane['normal_transit_days']}d)<br>"
                f"Spend at Risk: ₹{lane['spend_at_risk_cr']:.1f} Cr<br>"
                f"Status: {lane['status']}"
            )
        ))

    # 2. Draw Chokepoints (Pulsing Markers)
    for cp in exposure_data["chokepoints"]:
        cp_color = status_colors.get(cp["status"], "#64748B")
        fig.add_trace(go.Scattergeo(
            lon=[cp["lon"]],
            lat=[cp["lat"]],
            mode="markers+text",
            text=[f" ⚠ {cp['name']}" if cp["status"] != "GREEN" else ""],
            textposition="top right",
            marker=dict(
                size=12 if cp["status"] == "RED" else 9,
                color=cp_color,
                symbol="circle",
                line=dict(width=2, color="#FFFFFF")
            ),
            showlegend=False,
            hoverinfo="text",
            hovertext=(
                f"<b>CHOKEPOINT: {cp['name']}</b><br>"
                f"Status: {cp['status']}<br>"
                f"Transit Impact: +{cp['delay_days']} days<br>"
                f"Assessment: {cp['reason']}"
            )
        ))

    # 3. Configure Map Projection and Styling
    fig.update_layout(
        title=dict(
            text=f"Global Inbound Trade Lanes & Chokepoint Exposure · ₹{exposure_data['total_spend_at_risk_cr']:.1f} Cr at Risk",
            font=dict(size=14, color="#0F172A", family="sans-serif")
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="#F1F5F9",
            showocean=True,
            oceancolor="#E2E8F0",
            showcountries=True,
            countrycolor="#CBD5E1",
            coastlinecolor="#94A3B8",
            showframe=False,
            center=dict(lat=15.0, lon=65.0), # Centered on Indian Ocean & Arabian Sea
            projection_scale=1.45
        ),
        margin=dict(l=0, r=0, t=35, b=0),
        height=380,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig
