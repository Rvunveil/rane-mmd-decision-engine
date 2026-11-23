import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';
import '../../domain/models/mitigation_action.dart';

class ActionMatrixView extends StatefulWidget {
  final DecisionEngineViewModel viewModel;

  const ActionMatrixView({super.key, required this.viewModel});

  @override
  State<ActionMatrixView> createState() => _ActionMatrixViewState();
}

class _ActionMatrixViewState extends State<ActionMatrixView> {
  bool _showOnlyOptimized = false;

  @override
  Widget build(BuildContext context) {
    final vm = widget.viewModel;
    final res = vm.results;
    final bundle = vm.optimizedBundle;

    final double totalBundleBenefit = bundle.fold(0.0, (sum, a) => sum + a.netBenefitCr);
    final double totalBundleSpend = bundle.fold(0.0, (sum, a) => sum + a.cashBudgetRequiredCr);

    final displayActions = _showOnlyOptimized ? bundle : res.actionRankings;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Prescriptive Action Matrix'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 0-1 Integer Optimizer Controller Card
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surfaceCard,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.primary, width: 1.2),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.auto_awesome, color: AppTheme.primary, size: 18),
                        SizedBox(width: 8),
                        Text(
                          '0-1 INTEGER PORTFOLIO OPTIMIZER',
                          style: TextStyle(
                            color: AppTheme.primary,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.8,
                          ),
                        ),
                      ],
                    ),
                    Text(
                      'Budget: ₹${vm.cashBudgetCr.toStringAsFixed(1)} Cr',
                      style: const TextStyle(
                        color: AppTheme.textPrimary,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                const Text(
                  'Solves mathematical knapsack optimization to select the highest ROI mitigation bundle within available cash budget.',
                  style: TextStyle(color: AppTheme.textMuted, fontSize: 10),
                ),
                SliderTheme(
                  data: SliderThemeData(
                    activeTrackColor: AppTheme.primary,
                    inactiveTrackColor: AppTheme.border,
                    thumbColor: AppTheme.primary,
                    trackHeight: 3,
                    thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
                    overlayShape: const RoundSliderOverlayShape(overlayRadius: 14),
                  ),
                  child: Slider(
                    value: vm.cashBudgetCr,
                    min: 1.0,
                    max: 20.0,
                    divisions: 19,
                    onChanged: vm.updateCashBudget,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppTheme.surface,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildSummaryMetric('Selected Levers', '${bundle.length} Actions'),
                      Container(width: 1, height: 28, color: AppTheme.border),
                      _buildSummaryMetric('Total Spend', '₹${totalBundleSpend.toStringAsFixed(2)} Cr'),
                      Container(width: 1, height: 28, color: AppTheme.border),
                      _buildSummaryMetric('Net Protection', '+₹${totalBundleBenefit.toStringAsFixed(2)} Cr', color: AppTheme.primary),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Segmented Filter Toggle
          Row(
            children: [
              Expanded(
                child: FilterChip(
                  selected: !_showOnlyOptimized,
                  label: Text('All Actions (${res.actionRankings.length})'),
                  selectedColor: AppTheme.primary.withOpacity(0.15),
                  side: BorderSide(color: !_showOnlyOptimized ? AppTheme.primary : AppTheme.border),
                  labelStyle: TextStyle(
                    color: !_showOnlyOptimized ? AppTheme.primary : AppTheme.textSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                  onSelected: (_) => setState(() => _showOnlyOptimized = false),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: FilterChip(
                  selected: _showOnlyOptimized,
                  label: Text('Optimal Bundle (${bundle.length})'),
                  selectedColor: AppTheme.primary.withOpacity(0.15),
                  side: BorderSide(color: _showOnlyOptimized ? AppTheme.primary : AppTheme.border),
                  labelStyle: TextStyle(
                    color: _showOnlyOptimized ? AppTheme.primary : AppTheme.textSecondary,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                  onSelected: (_) => setState(() => _showOnlyOptimized = true),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Action Cards List
          ...displayActions.map((act) => _buildActionCard(act, bundle.any((b) => b.id == act.id))),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildSummaryMetric(String title, String val, {Color? color}) {
    return Column(
      children: [
        Text(title, style: const TextStyle(color: AppTheme.textMuted, fontSize: 9)),
        const SizedBox(height: 2),
        Text(
          val,
          style: TextStyle(
            color: color ?? AppTheme.textPrimary,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildActionCard(MitigationAction act, bool isInBundle) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surfaceCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isInBundle ? AppTheme.primary : AppTheme.border,
          width: isInBundle ? 1.4 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isInBundle ? AppTheme.primary : AppTheme.border,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '#${act.rank}',
                  style: TextStyle(
                    color: isInBundle ? Colors.black : AppTheme.textPrimary,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  act.title,
                  style: const TextStyle(
                    color: AppTheme.textPrimary,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (isInBundle)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppTheme.primary.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'IN BUNDLE',
                    style: TextStyle(color: AppTheme.primary, fontSize: 9, fontWeight: FontWeight.bold),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 2),
          Text(
            '${act.id} · ${act.category}',
            style: const TextStyle(color: AppTheme.textMuted, fontSize: 10),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildMetricColumn('Net Benefit', AppTheme.formatMoneyCr(act.netBenefitCr), color: AppTheme.primary, isBold: true),
              _buildMetricColumn('Gross Benefit', AppTheme.formatMoneyCr(act.benefitCr)),
              _buildMetricColumn('Direct Cost', AppTheme.formatMoneyCr(act.costCr)),
              _buildMetricColumn('Cash Budget', '₹${act.cashBudgetRequiredCr.toStringAsFixed(1)} Cr'),
              _buildMetricColumn('ROI', '${act.roi.toStringAsFixed(1)}x', color: AppTheme.info),
            ],
          ),
          const Divider(color: AppTheme.border, height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.timer_outlined, size: 12, color: AppTheme.textMuted),
                  const SizedBox(width: 4),
                  Text(
                    'Lead Time: ${act.timeToImplement}',
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 10),
                  ),
                ],
              ),
              Expanded(
                child: Text(
                  'Risk: ${act.primaryRisk}',
                  style: const TextStyle(color: AppTheme.textMuted, fontSize: 10),
                  textAlign: TextAlign.right,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricColumn(String label, String value, {Color? color, bool isBold = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 9)),
        const SizedBox(height: 1),
        Text(
          value,
          style: TextStyle(
            color: color ?? AppTheme.textPrimary,
            fontSize: 11,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
