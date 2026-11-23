import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tests.oracle as oracle
from engine.scenario import Scenario
from engine.chain import run_all

test_cases = [
    {
        'desc': 'Judge Case 1: Copper +25%, Aluminium +15%, Freight x1.5, Pass 60%',
        'shocks': {'copper': 25.0, 'aluminium': 15.0},
        'freight': 1.5,
        'fx': 84.5648,
        'tariff': 0.0,
        'demand': 0.0,
        'pass': 60.0
    },
    {
        'desc': 'Judge Case 2: Steel HR +30%, Steel CR +20%, Domestic only, Pass 50%',
        'shocks': {'steel_hr': 30.0, 'steel_cr': 20.0},
        'freight': 1.0,
        'fx': 84.5648,
        'tariff': 0.0,
        'demand': 0.0,
        'pass': 50.0
    },
    {
        'desc': 'Judge Case 3: FX = 92.0, Tariff 5%, Freight x2.0, Pass 50%',
        'shocks': {},
        'freight': 2.0,
        'fx': 92.0,
        'tariff': 5.0,
        'demand': 0.0,
        'pass': 50.0
    },
    {
        'desc': 'Judge Case 4: Demand -15%, Pass 70%, Lag 60d, In-Year',
        'shocks': {'copper': 10.0, 'steel_hr': 10.0},
        'freight': 1.2,
        'fx': 86.0,
        'tariff': 0.0,
        'demand': -15.0,
        'pass': 70.0,
        'lag': 60,
        'in_year': True
    },
    {
        'desc': 'Judge Case 5: Brutal Multivariant: All +15%, Freight x2.5, FX 95, Demand -10%, Pass 40%',
        'shocks': {k: 15.0 for k in oracle.ORACLE_BASELINE_PRICES},
        'freight': 2.5,
        'fx': 95.0,
        'tariff': 5.0,
        'demand': -10.0,
        'pass': 40.0
    }
]

print("=== H24: 5 RANDOM JUDGE SLIDER VERIFICATIONS ===")
for i, tc in enumerate(test_cases, 1):
    scn = Scenario(
        price_shock_pct=tc['shocks'],
        freight_multiplier=tc['freight'],
        fx_inr_usd=tc['fx'],
        tariff_pct=tc['tariff'],
        demand_volume_pct=tc['demand'],
        oem_pass_through_pct=tc['pass'],
        pass_through_lag_days=tc.get('lag', 75),
        in_year_mode=tc.get('in_year', False)
    )
    res = run_all(scn)
    orc = oracle.oracle_calculate(
        shocks=tc['shocks'],
        freight_mult=tc['freight'],
        fx_inr_usd=tc['fx'],
        tariff_pct=tc['tariff'],
        demand_volume_pct=tc['demand'],
        pass_through_pct=tc['pass'],
        lag_days=tc.get('lag', 75),
        in_year_mode=tc.get('in_year', False)
    )
    ebitda_diff = abs(res.ebitda_cr - orc['ebitda_cr'])
    pat_diff = abs(res.pat_cr - orc['pat_cr'])
    status = "PASS" if (ebitda_diff < 0.1 and pat_diff < 0.1) else "FAIL"
    desc = tc['desc']
    print(f"Case {i}: {desc}")
    print(f"  Oracle: EBITDA = ₹{orc['ebitda_cr']:.2f} Cr, PAT = ₹{orc['pat_cr']:.2f} Cr")
    print(f"  Engine: EBITDA = ₹{res.ebitda_cr:.2f} Cr, PAT = ₹{res.pat_cr:.2f} Cr")
    print(f"  Difference: EBITDA Δ = {ebitda_diff:.4f} Cr, PAT Δ = {pat_diff:.4f} Cr -> [{status}]")
