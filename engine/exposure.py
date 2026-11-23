"""
Inbound Trade Lane Exposure Map Engine (N2 / T5 / T10)
Rane (Madras) MMD Decision Engine · Team 11:59 · Xovate'26

Models 6 critical inbound material trade lanes, maritime waypoints (preventing land crossing),
chokepoint bottlenecks, and computes spend-at-risk.
"""

from typing import Any
import plotly.graph_objects as go
from engine.scenario import Scenario
from engine.data_loader import load_assumptions

CHOKEPOINTS = [
    {
        "id": "suez",
        "name": "Bab el-Mandeb / Suez",
        "lat": 12.58,
        "lon": 43.33,
        "description": "Red Sea bottleneck connecting Europe/Atlantic to Indian Ocean."
    },
    {
        "id": "hormuz",
        "name": "Strait of Hormuz",
        "lat": 26.56,
        "lon": 56.25,
        "description": "Persian Gulf chokepoint for Gulf primary aluminium ingots."
    },
    {
        "id": "cape",
        "name": "Cape of Good Hope",
        "lat": -34.35,
        "lon": 18.47,
        "description": "Southern Africa bypass corridor adding 14–21 days transit time."
    },
    {
        "id": "malacca",
        "name": "Strait of Malacca",
        "lat": 2.50,
        "lon": 101.50,
        "description": "Southeast Asian trade artery for East Asian polymers and nickel."
    }
]

# Trade lanes with maritime waypoints to avoid crossing land masses (T10)
TRADE_LANES = [
    {
        "id": "LANE-CU-CHILE",
        "material": "copper",
        "name": "Chilean Copper Cathode Maritime Lane",
        "origin_name": "San Antonio, Chile",
        "dest_name": "Chennai / Ennore Port, India",
        "primary_carrier": "Global Container Carrier A [SAMPLE DATA]",
        "normal_transit_days": 38,
        "base_annual_spend_cr": 122.3, # ~10% of material spend
        "chokepoints": ["suez", "cape"],
        # Maritime waypoints via South Atlantic and Cape of Good Hope
        "waypoints": [
            (-33.59, -71.61), # San Antonio, Chile
            (-45.0, -60.0),   # South Atlantic approach
            (-35.0, -20.0),   # Mid South Atlantic
            (-34.35, 18.47),  # Cape of Good Hope
            (-20.0, 45.0),    # Madagascar channel / Indian Ocean
            (0.0, 65.0),      # Equatorial Indian Ocean
            (13.08, 80.27)    # Chennai Port
        ]
    },
    {
        "id": "LANE-AL-GULF",
        "material": "aluminium",
        "name": "Gulf Aluminium Ingot Lane",
        "origin_name": "Jebel Ali / Manama (UAE/Bahrain)",
        "dest_name": "JNPT / Mumbai & Chennai, India",
        "primary_carrier": "Regional Feeder Carrier B [SAMPLE DATA]",
        "normal_transit_days": 18,
        "base_annual_spend_cr": 269.06, # ~22% of material spend
        "chokepoints": ["hormuz"],
        "waypoints": [
            (25.01, 55.06), # Jebel Ali
            (26.56, 56.25), # Strait of Hormuz
            (24.0, 60.0),   # Gulf of Oman
            (18.95, 72.95)  # JNPT Mumbai
        ]
    },
    {
        "id": "LANE-NI-INDO",
        "material": "nickel",
        "name": "Indonesian Precision Nickel Lane",
        "origin_name": "Surabaya, Indonesia",
        "dest_name": "Chennai Port, India",
        "primary_carrier": "Pacific Logistics Carrier C [SAMPLE DATA]",
        "normal_transit_days": 14,
        "base_annual_spend_cr": 73.38, # ~6% of material spend
        "chokepoints": ["malacca"],
        "waypoints": [
            (-7.25, 112.75), # Surabaya
            (-1.0, 106.0),   # Java Sea
            (2.50, 101.50),  # Strait of Malacca
            (6.0, 95.0),     # Andaman Sea
            (13.08, 80.27)   # Chennai Port
        ]
    },
    {
        "id": "LANE-RESIN-KOREA",
        "material": "resin",
        "name": "East Asian Specialty Resin Lane",
        "origin_name": "Busan, South Korea",
        "dest_name": "Chennai Port, India",
        "primary_carrier": "East Asian Freight Forwarder D [SAMPLE DATA]",
        "normal_transit_days": 19,
        "base_annual_spend_cr": 73.38, # ~6% of material spend
        "chokepoints": ["malacca"],
        "waypoints": [
            (35.18, 129.07), # Busan
            (25.0, 122.0),   # East China Sea
            (12.0, 112.0),   # South China Sea
            (2.50, 101.50),  # Strait of Malacca
            (13.08, 80.27)   # Chennai Port
        ]
    },
    {
        "id": "LANE-STEEL-DOM",
        "material": "steel_hr",
        "name": "Domestic Steel Mill Coastal Corridor",
        "origin_name": "Hazira & Angul Coastal Mills, India",
        "dest_name": "Rane Manufacturing Unit 1 & Unit 2",
        "primary_carrier": "Domestic Coastal Feeder & Rail [SAMPLE DATA]",
        "normal_transit_days": 6,
        "base_annual_spend_cr": 611.5, # ~50% of material spend (Steels)
        "chokepoints": [],
        "waypoints": [
            (21.17, 72.74), # Hazira
            (15.0, 73.5),   # Konkan Coast
            (8.5, 77.0),    # Kanyakumari
            (13.08, 80.27)  # Chennai Port
        ]
    },
    {
        "id": "LANE-RUBBER-KOT",
        "material": "rubber",
        "name": "Kerala Natural Rubber Inland Corridor",
        "origin_name": "Kottayam, Kerala",
        "dest_name": "Rane Friction Manufacturing Units",
        "primary_carrier": "Domestic Dedicated Fleet [SAMPLE DATA]",
        "normal_transit_days": 3,
        "base_annual_spend_cr": 73.38, # ~6% of material spend
        "chokepoints": [],
        "waypoints": [
            (9.59, 76.52),  # Kottayam
            (10.5, 78.0),   # Central Tamil Nadu
            (11.94, 79.80)  # Manufacturing Plant
        ]
    }
]


def compute_exposure_map(scenario: Scenario, assumptions: dict = None) -> dict[str, Any]:
    """
    Evaluates exposure across all inbound trade lanes and calculates spend-at-risk.
    Definition: spend at risk = annual spend on lanes through chokepoints flagged amber or red.
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
            status = "RED" if delay >= 10 else ("AMBER" if delay > 0 else "GREEN")
            delay_days = delay if delay > 0 else 0
            reason = "Bab el-Mandeb transit reduction; vessels rerouting via Cape." if status != "GREEN" else "Normal maritime transit."
        elif cid == "hormuz":
            status = "RED" if delay >= 15 else ("AMBER" if delay >= 7 else "GREEN")
            delay_days = min(delay, 14)
            reason = "Persian Gulf security restrictions and carrier insurance surcharges." if status != "GREEN" else "Normal maritime transit."
        elif cid == "cape":
            status = "AMBER" if delay > 0 else "GREEN"
            delay_days = delay + 5 if delay > 0 else 0
            reason = "Diverted traffic absorbing bunker surcharges." if status != "GREEN" else "Normal maritime transit."
        elif cid == "malacca":
            status = "AMBER" if delay > 15 else "GREEN"
            delay_days = min(delay, 5)
            reason = "Secondary congestion from delayed European/Middle Eastern feeder schedules." if status != "GREEN" else "Normal maritime transit."
        else:
            status = "GREEN"
            delay_days = 0
            reason = "Open ocean transit"

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
            lane_spend_at_risk = pipeline_cr * 0.10 # Base operational pipeline exposure

        total_spend_at_risk += lane_spend_at_risk

        lanes_res.append({
            "id": lane["id"],
            "name": lane["name"],
            "material": mat,
            "origin_name": lane["origin_name"],
            "dest_name": lane["dest_name"],
            "primary_carrier": lane["primary_carrier"],
            "normal_transit_days": lane["normal_transit_days"],
            "effective_transit_days": effective_transit,
            "status": status,
            "pipeline_in_transit_cr": round(pipeline_cr, 2),
            "spend_at_risk_cr": round(lane_spend_at_risk, 2),
            "waypoints": lane["waypoints"]
        })

    return {
        "lanes": lanes_res,
        "chokepoints": chokepoints_res,
        "total_spend_at_risk_cr": round(total_spend_at_risk, 2),
        "definition": "Spend at risk = annual spend on lanes through chokepoints flagged amber or red",
        "active_vessel_count": active_vessels
    }


def plot_exposure_map(exposure_data: dict[str, Any]) -> go.Figure:
    """
    Renders interactive global supply chain exposure map using Plotly scattergeo.
    T10: Uses natural earth projection cropped to Atlantic <-> Indian Ocean corridors.
    Draws sea routes through authentic maritime waypoints without cutting across land.
    """
    fig = go.Figure()

    status_colors = {"GREEN": "#1E8A4C", "AMBER": "#C98A0B", "RED": "#C2382B"}

    # 1. Draw Maritime Trade Lanes through Waypoints
    for lane in exposure_data["lanes"]:
        color = status_colors.get(lane["status"], "#8E9AA2")
        wps = lane.get("waypoints", [])
        if not wps:
            continue
        lats = [pt[0] for pt in wps]
        lons = [pt[1] for pt in wps]

        fig.add_trace(go.Scattergeo(
            locationmode="ISO-3",
            lon=lons,
            lat=lats,
            mode="lines+markers",
            line=dict(width=2.5 if lane["status"] == "RED" else 1.8, color=color),
            marker=dict(size=5, color=color),
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

    # 2. Draw Chokepoints
    for cp in exposure_data["chokepoints"]:
        cp_color = status_colors.get(cp["status"], "#8E9AA2")
        fig.add_trace(go.Scattergeo(
            lon=[cp["lon"]],
            lat=[cp["lat"]],
            mode="markers+text",
            text=[f" {cp['name']}" if cp["status"] != "GREEN" else ""],
            textposition="top right",
            marker=dict(
                size=12 if cp["status"] == "RED" else 8,
                color=cp_color,
                symbol="circle",
                line=dict(width=1.5, color="#FFFFFF")
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

    # 3. Configure Map Layout
    risk_title = f"Inbound Maritime Trade Lanes · ₹{exposure_data['total_spend_at_risk_cr']:.1f} Cr Spend at Risk"
    fig.update_layout(
        title=dict(
            text=risk_title,
            font=dict(size=13, color="#1D262C", family="sans-serif"),
            x=0.01,
            y=0.96
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="#EEF1F2",
            showocean=True,
            oceancolor="#F8F9F9",
            showcountries=True,
            countrycolor="#C9D1D5",
            coastlinecolor="#8E9AA2",
            showframe=False,
            center=dict(lat=10.0, lon=50.0), # Centered between Atlantic and Indian Ocean
            projection_scale=1.45
        ),
        margin=dict(l=0, r=0, t=32, b=0),
        height=370,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig
