"""
OEM Price-Recovery Claim Pack Generator (N5 / T5)
Rane (Madras) MMD Decision Engine · Team 11:59 · Xovate'26

Generates internal commercial price escalation reconciliations for OEM customer negotiations,
partitioned across operating divisions using authentic dataset benchmark citations.

T5 Compliance:
- Fully neutral OEM and supplier labels tagged [SAMPLE DATA]
- Cites only authentic series present in data/processed: LME Copper/Aluminium/Nickel,
  Ministry of Steel HR/CR, Kottayam RSS-4, IMARC Resin, and Container Freight Index.
- Neutral non-legal wording: "Indicative price-variation claim basis (for internal review)"
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
            "name": "Steering & Mechanical Linkages Division",
            "oem_customers": "Passenger Vehicle OEM Group A & Commercial Vehicle OEM B [SAMPLE DATA]",
            "share": 0.40,
            "primary_index": "Ministry of Steel Domestic HRC Benchmark + LME Aluminium Cash Settlement",
            "inputs_cited": "Special Quality Steel Bar, Forging Billets, Bushings"
        },
        {
            "id": "castings",
            "name": "Light-Metal Die Castings Division",
            "oem_customers": "Domestic Tier-1 Assembly Group C & Export Tier-1 Group D [SAMPLE DATA]",
            "share": 0.27,
            "primary_index": "LME Aluminium Cash Settlement + Inbound Container Freight Index",
            "inputs_cited": "Primary Aluminium Ingot (A356/ADC12), Copper Grain"
        },
        {
            "id": "friction",
            "name": "Friction Materials Division",
            "oem_customers": "Braking System OEM Group E & Commercial Vehicle OEM F [SAMPLE DATA]",
            "share": 0.18,
            "primary_index": "Kottayam RSS-4 Natural Rubber Benchmark + IMARC Phenolic Resin Index",
            "inputs_cited": "Phenolic Binder Resin, Kottayam Natural Rubber, Copper Powders"
        },
        {
            "id": "valves",
            "name": "Engine Valves & Precision Actuation Division",
            "oem_customers": "Powertrain Engine OEM Group G & Off-Highway Customer H [SAMPLE DATA]",
            "share": 0.15,
            "primary_index": "LME Nickel Cash Settlement + Ministry of Steel Domestic Benchmark",
            "inputs_cited": "Austenitic Valve Steel (21-4N), High-Nickel Superalloys"
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

    # Render HTML executive claim memo with neutral internal wording
    html_memo = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border: 1px solid #C9D1D5; padding: 24px; border-radius: 6px; background: #FFFFFF; color: #1D262C;">
        <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #2F5D7C; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <h2 style="margin: 0; color: #1D262C; font-size: 1.25rem; font-weight: 600;">RANE (MADRAS) LIMITED</h2>
                <div style="font-size: 0.85rem; color: #536471;">Materials Management Department (MMD) · Commercial Operations</div>
                <div style="font-size: 0.8rem; color: #8E9AA2;">Head Office: Chennai, Tamil Nadu, India</div>
            </div>
            <div style="text-align: right;">
                <span style="background: #2F5D7C; color: #FFF; padding: 4px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">INDICATIVE PRICE-VARIATION CLAIM BASIS (FOR INTERNAL REVIEW)</span>
                <div style="font-size: 0.82rem; margin-top: 6px; font-weight: 600;">DOSSIER REF: RML/MMD/2026/INTERNAL-RECON</div>
                <div style="font-size: 0.78rem; color: #536471;">Active Scenario: {scenario.name}</div>
            </div>
        </div>

        <p style="font-size: 0.88rem; line-height: 1.5; color: #1D262C;">
            <b>DOCUMENT TYPE:</b> Indicative Price-Variation Claim Basis (For Internal Review)<br>
            <b>SUBJECT:</b> Internal Commercial Reconciliation: Raw Material & Inbound Freight Cost Variation Analysis [TEAM ASSUMPTION]
        </p>

        <p style="font-size: 0.84rem; line-height: 1.6; color: #536471;">
            Prepared for internal executive review by the Materials Management Department (MMD). Evaluates contract indexation 
            mechanics across global commodity benchmarks and inbound container lanes. Pass-through recovery is currently 
            calibrated at <b>{scenario.oem_pass_through_pct:.1f}%</b> under an indicative settlement lag of <b>{scenario.pass_through_lag_days} days</b>.
        </p>

        <table style="width: 100%; border-collapse: collapse; font-size: 0.84rem; margin: 16px 0;">
            <thead>
                <tr style="background: #EEF1F2; border-bottom: 2px solid #C9D1D5; text-align: left;">
                    <th style="padding: 8px;">Operating Division</th>
                    <th style="padding: 8px;">Benchmark Index Basis</th>
                    <th style="padding: 8px; text-align: right;">Gross Cost Shock</th>
                    <th style="padding: 8px; text-align: right;">Indicative Claim (₹ Cr)</th>
                    <th style="padding: 8px; text-align: right;">Unrecovered (₹ Cr)</th>
                </tr>
            </thead>
            <tbody>
    """
    for d in divisions_res:
        gross_div = d["claim_amount_cr"] + d["unrecovered_gap_cr"]
        html_memo += f"""
                <tr style="border-bottom: 1px solid #EEF1F2;">
                    <td style="padding: 8px;"><b>{d['division_name']}</b><br><span style="font-size:0.75rem; color:#8E9AA2;">{d['oem_customers']}</span></td>
                    <td style="padding: 8px; font-size: 0.8rem; color: #536471;">{d['primary_index']}</td>
                    <td style="padding: 8px; text-align: right; font-variant-numeric: tabular-nums;">₹ {gross_div:.2f} Cr</td>
                    <td style="padding: 8px; text-align: right; font-weight: 600; color: #2F5D7C; font-variant-numeric: tabular-nums;">₹ {d['claim_amount_cr']:.2f} Cr</td>
                    <td style="padding: 8px; text-align: right; color: #C2382B; font-variant-numeric: tabular-nums;">₹ {d['unrecovered_gap_cr']:.2f} Cr</td>
                </tr>
        """
    html_memo += f"""
                <tr style="background: #F8F9F9; font-weight: 600; border-top: 2px solid #1D262C;">
                    <td style="padding: 10px;">TOTAL RECONCILED BASIS</td>
                    <td style="padding: 10px; font-size: 0.8rem; color: #536471;">Consolidated Component Operations</td>
                    <td style="padding: 10px; text-align: right; font-variant-numeric: tabular-nums;">₹ {results.delta_material_cr + results.delta_freight_cr:.2f} Cr</td>
                    <td style="padding: 10px; text-align: right; color: #2F5D7C; font-size: 0.95rem; font-variant-numeric: tabular-nums;">₹ {total_recovery:.2f} Cr</td>
                    <td style="padding: 10px; text-align: right; color: #C2382B; font-size: 0.95rem; font-variant-numeric: tabular-nums;">₹ {total_unrecovered:.2f} Cr</td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top: 24px; display: flex; justify-content: space-between; font-size: 0.8rem; border-top: 1px solid #C9D1D5; padding-top: 12px; color: #8E9AA2;">
            <div>
                <b>Prepared by:</b><br>
                Materials Management Department (MMD)<br>
                Rane (Madras) Limited
            </div>
            <div style="text-align: right;">
                <b>Review Status:</b><br>
                Internal Decision Brief [TEAM ASSUMPTION]<br>
                Commercial Review Committee
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
