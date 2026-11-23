"""
Monte Carlo Profit-at-Risk Engine (N3)
Rane (Madras) MMD Decision Engine · Team 11.59 · Xovate'26

Vectorised multivariate Monte Carlo simulation (2,000 paths) estimating the empirical
probability distribution of EBITDA, PAT, Value-at-Risk (VaR), and loss probability P(PAT < 0).
"""

from typing import Any
import numpy as np
from engine.scenario import Scenario
from engine.data_loader import load_assumptions

# Calibrated historical volatilities (annualized 1-sigma %)
ANNUAL_VOLATILITIES = {
    "copper": 14.5,
    "aluminium": 12.8,
    "nickel": 16.2,
    "steel_hr": 9.5,
    "steel_cr": 9.0,
    "resin": 18.0,
    "rubber": 11.0,
    "freight": 28.0,
    "fx": 4.5,
    "demand": 6.0
}

# Empirical correlation matrix among primary inputs
# Order: [copper, aluminium, nickel, steel_hr, resin, freight, fx]
CORRELATION_MATRIX = np.array([
    # Cu    Al    Ni    Fe    Res   Frgt  FX
    [1.00, 0.68, 0.58, 0.42, 0.35, 0.40, 0.32], # Copper
    [0.68, 1.00, 0.52, 0.45, 0.38, 0.42, 0.30], # Aluminium
    [0.58, 0.52, 1.00, 0.38, 0.30, 0.35, 0.28], # Nickel
    [0.42, 0.45, 0.38, 1.00, 0.25, 0.30, 0.22], # Steel HR
    [0.35, 0.38, 0.30, 0.25, 1.00, 0.32, 0.20], # Resin
    [0.40, 0.42, 0.35, 0.30, 0.32, 1.00, 0.38], # Freight
    [0.32, 0.30, 0.28, 0.22, 0.20, 0.38, 1.00], # FX
])


def run_profit_at_risk_monte_carlo(
    scenario: Scenario,
    num_paths: int = 2000,
    seed: int = 42,
    assumptions: dict = None
) -> dict[str, Any]:
    """
    Executes fast vectorised Monte Carlo simulation across 2,000 joint disruption paths.
    """
    if assumptions is None:
        assumptions = load_assumptions()

    np.random.seed(seed)

    base_rev = 3421.0
    base_ebitda = 297.70
    base_mat = 1223.0
    base_freight = 25.0
    fixed_da = 247.458
    tax_rate = 0.2517
    contrib_margin = 0.28

    # Input baseline spend weights (Cr)
    # copper: 122.3, al: 269.06, ni: 73.38, steel: 611.5, resin: 73.38, rubber: 73.38
    weights = np.array([122.3, 269.06, 73.38, 611.5, 73.38]) # Cu, Al, Ni, Fe, Resin

    # Extract scenario expected shock centers (%)
    mean_shocks = np.array([
        scenario.price_shock_pct.get("copper", 0.0),
        scenario.price_shock_pct.get("aluminium", 0.0),
        scenario.price_shock_pct.get("nickel", 0.0),
        scenario.price_shock_pct.get("steel_hr", 0.0),
        scenario.price_shock_pct.get("resin", 0.0),
        (scenario.freight_multiplier - 1.0) * 100.0,
        ((scenario.fx_inr_usd / 84.56) - 1.0) * 100.0
    ])

    vols = np.array([
        ANNUAL_VOLATILITIES["copper"],
        ANNUAL_VOLATILITIES["aluminium"],
        ANNUAL_VOLATILITIES["nickel"],
        ANNUAL_VOLATILITIES["steel_hr"],
        ANNUAL_VOLATILITIES["resin"],
        ANNUAL_VOLATILITIES["freight"],
        ANNUAL_VOLATILITIES["fx"]
    ])

    # Construct covariance matrix: D * R * D
    D = np.diag(vols)
    cov_matrix = D @ CORRELATION_MATRIX @ D

    # Generate correlated random shock variations
    shock_variations = np.random.multivariate_normal(mean=np.zeros(7), cov=cov_matrix, size=num_paths)
    paths_shocks = mean_shocks + shock_variations

    # Decompose into components
    mat_shocks = paths_shocks[:, :5] # shape: (num_paths, 5)
    frt_shocks_pct = paths_shocks[:, 5] # shape: (num_paths,)
    fx_shocks_pct = paths_shocks[:, 6]

    # Demand volume random path
    demand_shocks_pct = np.random.normal(scenario.demand_volume_pct, ANNUAL_VOLATILITIES["demand"], size=num_paths)
    demand_mult = 1.0 + (demand_shocks_pct / 100.0)

    # 1. Material spend delta across paths (Cr)
    # delta_mat = sum_i(weight_i * shock_i / 100 * demand_mult)
    delta_mat_paths = np.sum((weights * (mat_shocks / 100.0)), axis=1) * demand_mult

    # 2. Freight spend delta across paths (Cr)
    # freight_mult = (1 + frt_shocks_pct/100) * (1 + fx_shocks_pct/100)
    frt_mult_paths = (1.0 + frt_shocks_pct / 100.0) * (1.0 + fx_shocks_pct / 100.0)
    delta_freight_paths = base_freight * (frt_mult_paths - 1.0) * demand_mult

    # 3. OEM pass-through recovery (Cr)
    pass_through_frac = scenario.oem_pass_through_pct / 100.0
    recovery_paths = pass_through_frac * np.maximum(delta_mat_paths + delta_freight_paths, 0.0)

    # 4. Volume contribution delta (Cr)
    vol_revenue_delta = base_rev * (demand_shocks_pct / 100.0)
    lost_contrib_paths = vol_revenue_delta * contrib_margin

    # 5. Simulated EBITDA and PAT paths
    ebitda_paths = base_ebitda - delta_mat_paths - delta_freight_paths + recovery_paths + lost_contrib_paths
    pbt_paths = ebitda_paths - fixed_da
    pat_paths = np.where(pbt_paths > 0.0, pbt_paths * (1.0 - tax_rate), pbt_paths)

    # Summary statistics
    p10_ebitda = float(np.percentile(ebitda_paths, 10))
    p50_ebitda = float(np.percentile(ebitda_paths, 50))
    p90_ebitda = float(np.percentile(ebitda_paths, 90))

    p10_pat = float(np.percentile(pat_paths, 10))
    p50_pat = float(np.percentile(pat_paths, 50))
    p90_pat = float(np.percentile(pat_paths, 90))

    prob_loss = float(np.mean(pat_paths < 0.0) * 100.0)
    var_95_ebitda = float(base_ebitda - np.percentile(ebitda_paths, 5))
    var_99_ebitda = float(base_ebitda - np.percentile(ebitda_paths, 1))

    return {
        "num_paths": num_paths,
        "base_ebitda_cr": base_ebitda,
        "p10_ebitda_cr": round(p10_ebitda, 2),
        "p50_ebitda_cr": round(p50_ebitda, 2),
        "p90_ebitda_cr": round(p90_ebitda, 2),
        "p10_pat_cr": round(p10_pat, 2),
        "p50_pat_cr": round(p50_pat, 2),
        "p90_pat_cr": round(p90_pat, 2),
        "prob_loss_pat_pct": round(prob_loss, 1),
        "var_95_ebitda_cr": round(max(var_95_ebitda, 0.0), 2),
        "var_99_ebitda_cr": round(max(var_99_ebitda, 0.0), 2),
        "ebitda_samples": ebitda_paths.tolist(),
        "pat_samples": pat_paths.tolist()
    }
