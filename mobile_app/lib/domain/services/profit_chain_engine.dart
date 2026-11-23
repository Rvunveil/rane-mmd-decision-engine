import 'dart:math';
import '../models/scenario.dart';
import '../models/results.dart';
import '../models/mitigation_action.dart';

class ProfitChainEngine {
  static const double baseRevenueCr = 3374.0;
  static const double baseMaterialSpendCr = 1223.0;
  static const double baseOceanFreightCr = 25.0;
  static const double baseEbitdaCr = 297.70;
  static const double basePatCr = 37.60;
  static const double baseFxRate = 84.5648;
  static const double taxRate = 0.25168;

  // Exact commodity baseline spend allocation (Cr)
  static const Map<String, double> materialWeightsCr = {
    'copper': 254.384,
    'aluminium': 211.579,
    'nickel': 78.272,
    'resin': 40.359,
    'rubber': 26.906,
    'steel_hr': 342.440,
    'steel_cr': 269.060,
  };

  static Results runAll(Scenario scenario) {
    final double demandFactor = 1.0 + (scenario.demandVolumePct / 100.0);
    final double scenarioRevenueCr = baseRevenueCr * demandFactor;

    // 1. Material Shock Calculation
    double totalMaterialCostCr = 0.0;
    double deltaMaterialCr = 0.0;
    final Map<String, double> scenarioMaterialSpend = {};

    materialWeightsCr.forEach((matKey, baseSpend) {
      final double shockPct = scenario.priceShockPct[matKey] ?? 0.0;
      final double matSpend = baseSpend * (1.0 + (shockPct / 100.0)) * demandFactor;
      final double deltaSpend = matSpend - (baseSpend * demandFactor);

      scenarioMaterialSpend[matKey] = matSpend;
      totalMaterialCostCr += matSpend;
      deltaMaterialCr += deltaSpend;
    });

    // 2. Inbound Ocean Freight Calculation
    final double fxRatio = scenario.fxInrUsd / baseFxRate;
    final double freightCostCr = baseOceanFreightCr * scenario.freightMultiplier * fxRatio * demandFactor;
    final double deltaFreightCr = freightCostCr - (baseOceanFreightCr * demandFactor);

    // 3. Tariff Calculation (Applied on ~30% imported component spend)
    final double importedBaseCr = baseMaterialSpendCr * 0.30;
    final double tariffCostCr = importedBaseCr * (scenario.tariffPct / 100.0) * demandFactor;

    // 4. Inbound Landed Cost Totals
    final double totalInboundCr = totalMaterialCostCr + freightCostCr + tariffCostCr;
    final double deltaTotalInboundCr = deltaMaterialCr + deltaFreightCr + tariffCostCr;

    // 5. OEM Contractual Pass-Through Recovery
    final double passThroughFactor = scenario.oemPassThroughPct / 100.0;
    final double oemRecoveryCr = passThroughFactor * deltaTotalInboundCr;
    final double netUnrecoveredCostCr = deltaTotalInboundCr - oemRecoveryCr;

    // 6. Working Capital Cash Deficit Drag
    final double workingCapitalDragCr = oemRecoveryCr * (scenario.passThroughLagDays / 365.0);

    // 7. Recalculated Operating Profit (EBITDA & PAT)
    // Revenue volume delta flows through directly to gross contribution
    final double volumeContributionDelta = scenarioRevenueCr - baseRevenueCr;
    final double deltaEbitdaCr = volumeContributionDelta - netUnrecoveredCostCr;
    final double ebitdaCr = baseEbitdaCr + deltaEbitdaCr;
    final double ebitdaMarginPct = scenarioRevenueCr > 0 ? (ebitdaCr / scenarioRevenueCr) * 100.0 : 0.0;

    // Net Profit PAT calculation (after tax & financing drag)
    final double deltaPatCr = deltaEbitdaCr * (1.0 - taxRate);
    final double patCr = basePatCr + deltaPatCr;

    // 8. Division Spend Allocations
    // Steering & Suspension: 62%, Die Casting: 26%, Commercial Vehicles: 12%
    final Map<String, double> divisionSpendCr = {
      'Steering & Suspension Systems': totalInboundCr * 0.62,
      'Die Casting Products (Aluminium)': totalInboundCr * 0.26,
      'Commercial Vehicles & Aftermarket': totalInboundCr * 0.12,
    };

    // 9. Evaluate Prescriptive Action Matrix
    final List<MitigationAction> actionRankings = evaluateActions(
      scenario: scenario,
      deltaMaterialCr: deltaMaterialCr,
      deltaFreightCr: deltaFreightCr,
    );

    return Results(
      revenueCr: scenarioRevenueCr,
      materialCostCr: totalMaterialCostCr,
      deltaMaterialCr: deltaMaterialCr,
      freightCostCr: freightCostCr,
      deltaFreightCr: deltaFreightCr,
      tariffCostCr: tariffCostCr,
      totalInboundCr: totalInboundCr,
      deltaTotalInboundCr: deltaTotalInboundCr,
      netCostImpactCr: deltaTotalInboundCr,
      oemRecoveryCr: oemRecoveryCr,
      netUnrecoveredCostCr: netUnrecoveredCostCr,
      ebitdaCr: ebitdaCr,
      deltaEbitdaCr: deltaEbitdaCr,
      ebitdaMarginPct: ebitdaMarginPct,
      patCr: patCr,
      deltaPatCr: deltaPatCr,
      workingCapitalDragCr: workingCapitalDragCr,
      materialSpendCr: scenarioMaterialSpend,
      divisionSpendCr: divisionSpendCr,
      actionRankings: actionRankings,
    );
  }

  static List<MitigationAction> evaluateActions({
    required Scenario scenario,
    required double deltaMaterialCr,
    required double deltaFreightCr,
  }) {
    final double dMat = max(deltaMaterialCr, 0.0);
    final double dFr = max(deltaFreightCr, 0.0);

    final List<Map<String, dynamic>> catalog = [
      {
        'id': 'ACT-01',
        'title': 'Commodity Derivative Hedging',
        'category': 'Procurement & Treasury',
        'budget': 2.5,
        'cost': dMat > 0 ? 0.015 * dMat : 1.2,
        'benefit': dMat > 0 ? 0.45 * dMat : 0.0,
        'time': '1-2 weeks',
        'risk': 'Mark-to-market basis risk',
        'functions': ['Treasury', 'Procurement'],
      },
      {
        'id': 'ACT-02',
        'title': 'Index-Linked OEM Price Re-negotiation',
        'category': 'Commercial & Sales',
        'budget': 1.0,
        'cost': 2.0,
        'benefit': (0.35 * (dMat + dFr)) +
            ((scenario.passThroughLagDays - 30) / 365.0 * (dMat + dFr) * 0.095),
        'time': '3-4 weeks',
        'risk': 'Customer pushback during renewal',
        'functions': ['Sales', 'Finance'],
      },
      {
        'id': 'ACT-03',
        'title': 'Dual-Sourcing / Domestic Near-Shoring',
        'category': 'Vendor Development',
        'budget': 4.5,
        'cost': 4.5,
        'benefit': 0.30 * dFr + (dMat > 0 ? 0.15 * dMat : 2.5),
        'time': '6-8 weeks',
        'risk': 'PPAP quality re-qualification timeline',
        'functions': ['Quality', 'Manufacturing'],
      },
      {
        'id': 'ACT-04',
        'title': '40ft Inbound Container Freight Consolidation',
        'category': 'Logistics & Ocean Freight',
        'budget': 0.8,
        'cost': 0.8,
        'benefit': dFr > 0 ? 0.28 * dFr : 3.2,
        'time': '1 week',
        'risk': 'Carrier equipment shortages at origin',
        'functions': ['Logistics', 'MMD'],
      },
      {
        'id': 'ACT-05',
        'title': 'Cape Route Air-Bridge for Critical Components',
        'category': 'Emergency Expedite',
        'budget': 6.0,
        'cost': 6.0,
        'benefit': scenario.shippingDelayDays > 10 ? 9.5 : 2.0,
        'time': '3 days',
        'risk': 'High unit freight premium burn',
        'functions': ['Operations', 'Executive'],
      },
      {
        'id': 'ACT-06',
        'title': 'Scrap & Slag Remelt Recycling Loop',
        'category': 'Plant Metallurgical Recovery',
        'budget': 3.0,
        'cost': 3.0,
        'benefit': 0.08 * (dMat > 0 ? dMat : 50.0) + 4.2,
        'time': '4 weeks',
        'risk': 'Ingot porosity and inclusion threshold',
        'functions': ['Foundry', 'Sustainability'],
      },
      {
        'id': 'ACT-07',
        'title': 'OEM Working Capital Advance Facility',
        'category': 'Treasury Financing',
        'budget': 0.5,
        'cost': 1.5,
        'benefit': (scenario.passThroughLagDays / 365.0) * (dMat + dFr) * 0.085,
        'time': '2 weeks',
        'risk': 'OEM treasury liquidity agreement',
        'functions': ['Finance', 'Legal'],
      },
      {
        'id': 'ACT-08',
        'title': 'Safety Stock Strategic Inventory Pre-Buy',
        'category': 'Inventory Buffer',
        'budget': 8.0,
        'cost': 8.0,
        'benefit': scenario.shippingDelayDays > 7 ? 11.0 : 3.5,
        'time': '2 weeks',
        'risk': 'Working capital inventory carrying cost',
        'functions': ['Warehouse', 'Procurement'],
      },
      {
        'id': 'ACT-09',
        'title': 'Tier-2 Supplier Raw Material Consignment',
        'category': 'Supply Chain Governance',
        'budget': 2.0,
        'cost': 2.2,
        'benefit': 0.12 * dMat + 2.8,
        'time': '3 weeks',
        'risk': 'Tier-2 balance sheet solvency',
        'functions': ['Supplier Mgmt', 'Audit'],
      },
      {
        'id': 'ACT-10',
        'title': 'Status Quo / Unmitigated Absorption',
        'category': 'Passive Strategy',
        'budget': 0.0,
        'cost': 0.0,
        'benefit': 0.0,
        'time': 'Immediate',
        'risk': 'Complete unrecovered margin loss',
        'functions': ['Board'],
      },
    ];

    final List<MitigationAction> actions = [];
    for (final raw in catalog) {
      final double cost = (raw['cost'] as num).toDouble();
      final double benefit = (raw['benefit'] as num).toDouble();
      final double netBenefit = benefit - cost;
      final double roi = cost > 0 ? benefit / cost : 0.0;

      actions.add(MitigationAction(
        id: raw['id'] as String,
        title: raw['title'] as String,
        category: raw['category'] as String,
        costCr: cost,
        benefitCr: benefit,
        netBenefitCr: netBenefit,
        roi: roi,
        cashBudgetRequiredCr: (raw['budget'] as num).toDouble(),
        timeToImplement: raw['time'] as String,
        primaryRisk: raw['risk'] as String,
        affectedFunctions: List<String>.from(raw['functions'] as List),
      ));
    }

    // Sort descending by Net Benefit
    actions.sort((a, b) => b.netBenefitCr.compareTo(a.netBenefitCr));

    // Assign sequential ranks
    return List.generate(actions.length, (idx) {
      return actions[idx].copyWith(rank: idx + 1);
    });
  }

  // 0-1 Integer Knapsack Portfolio Optimization
  static List<MitigationAction> optimizeActionBundle(
    List<MitigationAction> actions,
    double cashBudgetCr,
  ) {
    final List<MitigationAction> candidates = actions
        .where((a) => a.id != 'ACT-10' && a.netBenefitCr > 0)
        .toList();

    double bestVal = 0.0;
    List<MitigationAction> bestCombo = [];

    final int n = candidates.length;
    final int subsetCount = 1 << n;

    for (int i = 0; i < subsetCount; i++) {
      double totalSpend = 0.0;
      double totalNet = 0.0;
      final List<MitigationAction> currentCombo = [];

      for (int j = 0; j < n; j++) {
        if ((i & (1 << j)) != 0) {
          totalSpend += candidates[j].cashBudgetRequiredCr;
          totalNet += candidates[j].netBenefitCr;
          currentCombo.add(candidates[j]);
        }
      }

      if (totalSpend <= cashBudgetCr && totalNet > bestVal) {
        bestVal = totalNet;
        bestCombo = currentCombo;
      }
    }

    return bestCombo;
  }
}
