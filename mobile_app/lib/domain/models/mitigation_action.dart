import 'package:flutter/foundation.dart';

@immutable
class MitigationAction {
  final String id;
  final String title;
  final String category;
  final double costCr;
  final double benefitCr;
  final double netBenefitCr;
  final double roi;
  final double cashBudgetRequiredCr;
  final String timeToImplement;
  final String primaryRisk;
  final List<String> affectedFunctions;
  final int rank;

  const MitigationAction({
    required this.id,
    required this.title,
    required this.category,
    required this.costCr,
    required this.benefitCr,
    required this.netBenefitCr,
    required this.roi,
    required this.cashBudgetRequiredCr,
    required this.timeToImplement,
    required this.primaryRisk,
    this.affectedFunctions = const [],
    this.rank = 1,
  });

  MitigationAction copyWith({
    String? id,
    String? title,
    String? category,
    double? costCr,
    double? benefitCr,
    double? netBenefitCr,
    double? roi,
    double? cashBudgetRequiredCr,
    String? timeToImplement,
    String? primaryRisk,
    List<String>? affectedFunctions,
    int? rank,
  }) {
    return MitigationAction(
      id: id ?? this.id,
      title: title ?? this.title,
      category: category ?? this.category,
      costCr: costCr ?? this.costCr,
      benefitCr: benefitCr ?? this.benefitCr,
      netBenefitCr: netBenefitCr ?? this.netBenefitCr,
      roi: roi ?? this.roi,
      cashBudgetRequiredCr: cashBudgetRequiredCr ?? this.cashBudgetRequiredCr,
      timeToImplement: timeToImplement ?? this.timeToImplement,
      primaryRisk: primaryRisk ?? this.primaryRisk,
      affectedFunctions: affectedFunctions ?? this.affectedFunctions,
      rank: rank ?? this.rank,
    );
  }
}
