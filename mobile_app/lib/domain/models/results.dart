import 'package:flutter/foundation.dart';
import 'mitigation_action.dart';

@immutable
class Results {
  final double revenueCr;
  final double materialCostCr;
  final double deltaMaterialCr;
  final double freightCostCr;
  final double deltaFreightCr;
  final double tariffCostCr;
  final double totalInboundCr;
  final double deltaTotalInboundCr;
  final double netCostImpactCr;
  final double oemRecoveryCr;
  final double netUnrecoveredCostCr;
  final double ebitdaCr;
  final double deltaEbitdaCr;
  final double ebitdaMarginPct;
  final double patCr;
  final double deltaPatCr;
  final double workingCapitalDragCr;
  final Map<String, double> materialSpendCr;
  final Map<String, double> divisionSpendCr;
  final List<MitigationAction> actionRankings;

  const Results({
    required this.revenueCr,
    required this.materialCostCr,
    required this.deltaMaterialCr,
    required this.freightCostCr,
    required this.deltaFreightCr,
    required this.tariffCostCr,
    required this.totalInboundCr,
    required this.deltaTotalInboundCr,
    required this.netCostImpactCr,
    required this.oemRecoveryCr,
    required this.netUnrecoveredCostCr,
    required this.ebitdaCr,
    required this.deltaEbitdaCr,
    required this.ebitdaMarginPct,
    required this.patCr,
    required this.deltaPatCr,
    required this.workingCapitalDragCr,
    required this.materialSpendCr,
    required this.divisionSpendCr,
    required this.actionRankings,
  });
}
