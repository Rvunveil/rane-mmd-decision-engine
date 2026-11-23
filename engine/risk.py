"""
Monte Carlo Profit-at-Risk Engine (N3 / T4)
Rane (Madras) MMD Decision Engine · Team 11:59 · Xovate'26

Vectorised multivariate Monte Carlo simulation (2,000 paths) estimating the empirical
probability distribution of EBITDA, PAT, Value-at-Risk (VaR), and loss probability P(PAT < 0).

T4 updates:
- Weights dynamically derived from config/assumptions.yaml
- Symmetric pass-through recovery by default (index pricing contracts move both ways)
- Optional asymmetric recovery toggle (OEM keeps savings on raw material drops)
- Volatilities computed from historical monthly returns (labelled TEAM ASSUMPTION)
- Collapses to deterministic engine result under zero volatility
"""

import os
from typing import Any
import numpy as np
import pandas as pd
from engine.scenario import Scenario
from engine.data_loader import load_assumptions

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# Baseline historical volatilities (% p.a. 1-sigma) derived from processed dataset series
DEFAULT_HISTORICAL_VOLATILITIES = {
    "copper": 15.9,
    "aluminium": 15.8,
    "nickel": 25.6,
    "steel_hr": 15.8,
    "steel_cr": 15.8,
    "resin": 22.0,
    "rubber": 12.0,
    "freight": 27.5,
    "fx": 6.2,
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


def compute_historical_volatilities(processed_dir: str = None) -> dict[str, float]:
    """
    Computes annualized 1-sigma volatilities (% p.a.) directly from
    historical monthly/daily returns of processed dataset series.
    Labelled: TEAM ASSUMPTION from historical returns.
    """
    pdir = processed_dir or PROCESSED_DIR
    vols = dict(DEFAULT_HISTORICAL_VOLATILITIES)
    
    files = {
        'copper': ('copper.csv', 'y'),
        'aluminium': ('aluminium.csv', 'y'),
        'nickel': ('nickel.csv', 'y'),
        'steel_hr': ('steel_hr.csv', 'y'),
        'freight': ('freight_fixed.csv', 'rate'),
        'fx': ('fx_daily.csv', 'rate')
    }

    for k, (fname, col) in files.items():
        p = os.path.join(pdir, fname)
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                s = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(s) > 10:
                    rets = s.pct_change().dropna()
                    if 'daily' in fname:
                        ann_vol = float(rets.std() * np.sqrt(252) * 100.0)
                    else:
                        ann_vol = float(rets.std() * np.sqrt(12) * 100.0)
                    vols[k] = round(ann_vol, 1)
            except Exception:
                pass

    return vols


def run_profit_at_risk_monte_carlo(
    scenario: Scenario,
    num_paths: int = 2000,
    seed: int = 42,
    assumptions: dict = None,
    symmetric_recovery: bool = True,
    volatility_scale: float = 1.0
) -> dict[str, Any]:
    """
    Executes fast vectorised Monte Carlo simulation across 2,000 joint disruption paths.
    
    Parameters:
    - scenario: active Scenario dataclass
    - num_paths: number of simulation trajectories (default 2000)
    - seed: random seed for reproducibility
    - assumptions: configuration dictionary from config/assumptions.yaml
    - symmetric_recovery: whether OEM pass-through applies symmetrically to both cost increases and decreases
    - volatility_scale: multiplier on volatilities (set to 0.0 for deterministic zero-volatility collapse)
    """
    if assumptions is None:
        assumptions = load_assumptions()

    np.random.seed(seed)

    fin_params = assumptions.get("financial_params", {}) if assumptions else {}
    base_rev = 3421.0
    base_ebitda = 297.70
    base_freight = 25.0
    fixed_da = fin_params.get("fixed_da_interest_cr", 247.458)
    tax_rate = fin_params.get("tax_rate_pct", 25.17) / 100.0
    contrib_margin = fin_params.get("contribution_margin_pct", 28.0) / 100.0

    # Input baseline spend weights dynamically read from assumptions.yaml (Cr)
    mat_cfg = assumptions.get("materials", {}) if assumptions else {}
    cu_w = mat_cfg.get("copper", {}).get("spend_cr", 122.3)
    al_w = mat_cfg.get("aluminium", {}).get("spend_cr", 269.06)
    ni_w = mat_cfg.get("nickel", {}).get("spend_cr", 73.38)
    fe_w = mat_cfg.get("steel_hr", {}).get("spend_cr", 342.44) + mat_cfg.get("steel_cr", {}).get("spend_cr", 269.06)
    res_w = mat_cfg.get("resin", {}).get("spend_cr", 73.38)
    weights = np.array([cu_w, al_w, ni_w, fe_w, res_w])

    # Extract scenario expected shock centers (%)
    fx_baseline = 84.5648
    hr_shock = float(scenario.price_shock_pct.get("steel_hr", 0.0))
    cr_shock = float(scenario.price_shock_pct.get("steel_cr", 0.0))
    fe_combined_shock = (hr_shock * 342.44 + cr_shock * 269.06) / 611.50

    mean_shocks = np.array([
        float(scenario.price_shock_pct.get("copper", 0.0)),
        float(scenario.price_shock_pct.get("aluminium", 0.0)),
        float(scenario.price_shock_pct.get("nickel", 0.0)),
        fe_combined_shock,
        float(scenario.price_shock_pct.get("resin", 0.0)),
        (float(scenario.freight_multiplier) - 1.0) * 100.0,
        ((float(scenario.fx_inr_usd) / fx_baseline) - 1.0) * 100.0
    ])

    vols_dict = compute_historical_volatilities()
    vols = np.array([
        vols_dict.get("copper", 15.9),
        vols_dict.get("aluminium", 15.8),
        vols_dict.get("nickel", 25.6),
        vols_dict.get("steel_hr", 15.8),
        vols_dict.get("resin", 22.0),
        vols_dict.get("freight", 27.5),
        vols_dict.get("fx", 6.2)
    ]) * max(volatility_scale, 0.0)

    # Correlated random shocks
    if volatility_scale > 0.0:
        D = np.diag(vols)
        cov_matrix = D @ CORRELATION_MATRIX @ D
        shock_variations = np.random.multivariate_normal(mean=np.zeros(7), cov=cov_matrix, size=num_paths)
        demand_vol = vols_dict.get("demand", 6.0) * volatility_scale
        demand_shocks_pct = np.random.normal(scenario.demand_volume_pct, demand_vol, size=num_paths)
    else:
        shock_variations = np.zeros((num_paths, 7))
        demand_shocks_pct = np.full(num_paths, scenario.demand_volume_pct)

    paths_shocks = mean_shocks + shock_variations

    # Decompose into components
    mat_shocks = paths_shocks[:, :5] # (num_paths, 5)
    frt_shocks_pct = paths_shocks[:, 5]
    fx_shocks_pct = paths_shocks[:, 6]
    demand_mult = 1.0 + (demand_shocks_pct / 100.0)

    # 1. Material spend delta across paths (Cr)
    delta_mat_paths = np.sum((weights * (mat_shocks / 100.0)), axis=1) * demand_mult

    # 2. Freight spend delta across paths (Cr)
    frt_mult_paths = (1.0 + frt_shocks_pct / 100.0) * (1.0 + fx_shocks_pct / 100.0)
    delta_freight_paths = base_freight * (frt_mult_paths - 1.0) * demand_mult

    # 3. OEM pass-through recovery (Cr)
    pass_through_frac = scenario.oem_pass_through_pct / 100.0
    cost_variation = delta_mat_paths + delta_freight_paths
    
    if symmetric_recovery:
        # Standard index-linked formula: pricing moves symmetrically with raw material delta
        recovery_paths = pass_through_frac * cost_variation
    else:
        # Asymmetric recovery: OEM only absorbs cost spikes; retains savings on drops
        recovery_paths = pass_through_frac * np.maximum(cost_variation, 0.0)

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
        "symmetric_recovery": symmetric_recovery,
        "volatilities": vols_dict,
        "volatility_note": "TEAM ASSUMPTION from historical monthly returns",
        "ebitda_samples": ebitda_paths.tolist(),
        "pat_samples": pat_paths.tolist()
    }
