"""
OEM Price-Recovery Claim Pack Generator (N5)
Rane (Madras) MMD Decision Engine · Team 11.59 · Xovate'26

Generates auditable price escalation claim dossiers for Tier-1 OEM customer negotiations,
partitioned across operating divisions with index-linked citations and HTML claim memo.
"""

from typing import Any
from engine.scenario import Scenario
from engine.results import Results
from engine.data_loader import load_assumptions


def generate_oem_claims_pack(
    scenario: Scenario,
    results: Results,
    assumptions: dict = None
) -> dict[str, Any]:
    """
    Constructs division-level claim allocations and an exportable executive claim pack.
    """
    if assumptions is None:
        assumptions = load_assumptions()

    total_recovery = results.oem_recovery_cr
    total_unrecovered = (results.delta_material_cr + results.delta_freight_cr) - total_recovery

    # Division weights calibrated to Rane component manufacturing
    # Steering: 40%, Castings: 27%, Friction: 18%, Valves: 15%
    div_specs = [
        {
            "id": "steering",
            "name": "Steering & Mechanical Linkages",
            "oem_customers": "Maruti Suzuki, Tata Motors, M&M",
            "share": 0.40,
            "primary_index": "Ministry of Steel HRC/CRC Index + LME Al Cash",
            "inputs_cited": "Special Quality Steel Bar, Forging Billets, Bushings"
        },
        {
            "id": "castings",
            "name": "Light-Metal Die Castings (India & Mexico)",
            "oem_customers": "Tata Motors, Ashok Leyland, Global Tier-1s",
            "share": 0.27,
            "primary_index": "LME Aluminium Settlement + Cape Freight Surcharge",
            "inputs_cited": "Primary Aluminium A356/ADC12 Ingot, Copper Grain"
        },
        {
            "id": "friction",
            "name": "Friction Materials & Brake Linings",
            "oem_customers": "Brembo, Tata Motors, Aftermarket Export",
            "share": 0.18,
            "primary_index": "Kottayam RSS-4 Spot + ICIS Phenolic Resin Index",
            "inputs_cited": "Phenolic Binder Resin, Kottayam Rubber, Copper Fibers"
        },
        {
            "id": "valves",
            "name": "Engine Valves & Precision Actuation",
            "oem_customers": "Hyundai India, Renault-Nissan, Cummins",
            "share": 0.15,
            "primary_index": "LME Nickel Cash + European Valve Alloy Surcharge",
            "inputs_cited": "21-4N Austenitic Steel, Nimonic Nickel Superalloys"
        }
    ]

    divisions_res = []
    for d in div_specs:
        claim_amt = total_recovery * d["share"]
        unrecovered = total_unrecovered * d["share"]
        divisions_res.append({
            "division_id": d["id"],
            "division_name": d["name"],
            "oem_customers": d["oem_customers"],
            "claim_amount_cr": round(claim_amt, 2),
            "unrecovered_gap_cr": round(unrecovered, 2),
            "primary_index": d["primary_index"],
            "inputs_cited": d["inputs_cited"]
        })

    # Render HTML executive claim memo
    html_memo = f"""
    <div style="font-family: Arial, sans-serif; border: 2px solid #0F172A; padding: 24px; border-radius: 8px; background: #FFFFFF; color: #0F172A;">
        <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #0284C7; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <h2 style="margin: 0; color: #0F172A; letter-spacing: -0.02em;">RANE (MADRAS) LIMITED</h2>
                <div style="font-size: 0.85rem; color: #64748B;">Materials Management Department (MMD) · Corporate Commercial Office</div>
                <div style="font-size: 0.8rem; color: #94A3B8;">Registered Office: 154, Velachery Road, Chennai 600 042, India</div>
            </div>
            <div style="text-align: right;">
                <span style="background: #0284C7; color: #FFF; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">OFFICIAL PRICE ESCALATION CLAIM</span>
                <div style="font-size: 0.85rem; margin-top: 6px; font-weight: bold;">DOSSIER REF: RML/MMD/2026/Q1-REV</div>
                <div style="font-size: 0.8rem; color: #64748B;">Active Scenario: {scenario.name}</div>
            </div>
        </div>

        <p style="font-size: 0.9rem; line-height: 1.5;">
            <b>TO:</b> Heads of Strategic Procurement & Vendor Development (Tier-1 OEM Customers)<br>
            <b>SUBJECT:</b> Contractual Raw Material & Ocean Freight Price Recovery Claim under Long-Term Supply Agreements (Clause 4.2)
        </p>

        <p style="font-size: 0.85rem; line-height: 1.6; color: #334155;">
            In accordance with the index-linked price variation clauses established in our master supply agreements, 
            Rane (Madras) Limited hereby submits this formal reconciliation claim for verified cost increases across 
            global commodity feeds and container ocean lanes. Our pass-through absorption is currently calibrated at 
            <b>{scenario.oem_pass_through_pct:.1f}%</b> under a contract settlement lag of <b>{scenario.pass_through_lag_days} days</b>.
        </p>

        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 16px 0;">
            <thead>
                <tr style="background: #F1F5F9; border-bottom: 2px solid #CBD5E1; text-align: left;">
                    <th style="padding: 8px;">Operating Division</th>
                    <th style="padding: 8px;">Key Benchmark Index</th>
                    <th style="padding: 8px; text-align: right;">Gross Cost Shock</th>
                    <th style="padding: 8px; text-align: right;">Contract Claim (₹ Cr)</th>
                    <th style="padding: 8px; text-align: right;">Rane Absorbed (₹ Cr)</th>
                </tr>
            </thead>
            <tbody>
    """
    for d in divisions_res:
        gross_div = d["claim_amount_cr"] + d["unrecovered_gap_cr"]
        html_memo += f"""
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 8px;"><b>{d['division_name']}</b><br><span style="font-size:0.75rem; color:#64748B;">{d['oem_customers']}</span></td>
                    <td style="padding: 8px; font-size: 0.8rem; color: #475569;">{d['primary_index']}</td>
                    <td style="padding: 8px; text-align: right;">₹ {gross_div:.2f} Cr</td>
                    <td style="padding: 8px; text-align: right; font-weight: bold; color: #0284C7;">₹ {d['claim_amount_cr']:.2f} Cr</td>
                    <td style="padding: 8px; text-align: right; color: #DC2626;">₹ {d['unrecovered_gap_cr']:.2f} Cr</td>
                </tr>
        """
    html_memo += f"""
                <tr style="background: #F8FAFC; font-weight: bold; border-top: 2px solid #0F172A;">
                    <td style="padding: 10px;">TOTAL RECONCILED CLAIM</td>
                    <td style="padding: 10px; font-size: 0.8rem;">Consolidated Auto-Component Operations</td>
                    <td style="padding: 10px; text-align: right;">₹ {results.delta_material_cr + results.delta_freight_cr:.2f} Cr</td>
                    <td style="padding: 10px; text-align: right; color: #0284C7; font-size: 1rem;">₹ {total_recovery:.2f} Cr</td>
                    <td style="padding: 10px; text-align: right; color: #DC2626; font-size: 1rem;">₹ {total_unrecovered:.2f} Cr</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top: 24px; display: flex; justify-content: space-between; font-size: 0.8rem; border-top: 1px solid #E2E8F0; padding-top: 12px; color: #64748B;">
            <div>
                <b>Submitted by:</b><br>
                Materials Management Department (MMD)<br>
                Rane (Madras) Limited
            </div>
            <div style="text-align: right;">
                <b>Verified by:</b><br>
                Chief Financial Officer & Company Secretary<br>
                Rane Group Corporate Office, Chennai
            </div>
        </div>
    </div>
    """

    return {
        "scenario_name": scenario.name,
        "total_recovery_cr": round(total_recovery, 2),
        "total_unrecovered_cr": round(total_unrecovered, 2),
        "divisions": divisions_res,
        "html_memo": html_memo
    }
