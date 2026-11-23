import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';
import '../widgets/market_tape_widget.dart';
import '../widgets/metric_card_widget.dart';
import '../widgets/preset_selector_widget.dart';
import '../widgets/waterfall_chart_widget.dart';
import 'guided_helper_dialog.dart';

class ControlRoomView extends StatelessWidget {
  final DecisionEngineViewModel viewModel;

  const ControlRoomView({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final res = viewModel.results;
    final scn = viewModel.scenario;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppTheme.primary,
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Text(
                'RANE MMD',
                style: TextStyle(
                  color: Colors.black,
                  fontSize: 11,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 0.5,
                ),
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'Materials Control Room',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline, color: AppTheme.info),
            tooltip: 'What happened?',
            onPressed: () => GuidedHelperDialog.show(context, viewModel),
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: AppTheme.textSecondary),
            tooltip: 'Reset to Base',
            onPressed: viewModel.resetToBase,
          ),
        ],
      ),
      body: Column(
        children: [
          // 1. Live Market Tape Ticker
          const MarketTapeWidget(),

          // 2. Scenario Presets Chips
          PresetSelectorWidget(
            viewModel: viewModel,
            onOpenGuidedHelper: () => GuidedHelperDialog.show(context, viewModel),
          ),

          // 3. Scrollable Dashboard Body
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              children: [
                // Active Scenario Banner
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline, color: AppTheme.info, size: 18),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'ACTIVE SCENARIO: ${scn.name.toUpperCase()}',
                              style: const TextStyle(
                                color: AppTheme.textPrimary,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 0.5,
                              ),
                            ),
                            Text(
                              scn.description,
                              style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                // KPI 2x2 Metric Grid
                GridView.count(
                  crossAxisCount: 2,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                  childAspectRatio: 1.45,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  children: [
                    MetricCardWidget(
                      title: 'Revenue',
                      value: AppTheme.formatMoneyCr(res.revenueCr),
                      delta: AppTheme.formatDeltaCr(res.revenueCr - 3374.0),
                      icon: Icons.account_balance,
                      accentColor: AppTheme.info,
                    ),
                    MetricCardWidget(
                      title: 'EBITDA (Margin)',
                      value: '${AppTheme.formatMoneyCr(res.ebitdaCr)} (${res.ebitdaMarginPct.toStringAsFixed(1)}%)',
                      delta: AppTheme.formatDeltaCr(res.deltaEbitdaCr),
                      icon: Icons.show_chart,
                      accentColor: res.ebitdaCr >= 200 ? AppTheme.primary : AppTheme.danger,
                    ),
                    MetricCardWidget(
                      title: 'Net Profit (PAT)',
                      value: AppTheme.formatMoneyCr(res.patCr),
                      delta: AppTheme.formatDeltaCr(res.deltaPatCr),
                      icon: Icons.savings_outlined,
                      accentColor: res.patCr >= 25 ? AppTheme.primary : AppTheme.danger,
                    ),
                    MetricCardWidget(
                      title: 'Cash Deficit Drag',
                      value: AppTheme.formatMoneyCr(res.workingCapitalDragCr),
                      delta: '${scn.passThroughLagDays}d lag',
                      isPositiveGood: false,
                      icon: Icons.hourglass_top,
                      accentColor: AppTheme.warning,
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Waterfall Chart Bridge
                WaterfallChartWidget(results: res),
                const SizedBox(height: 16),

                // Early Warning Radar / Andon Status
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'EARLY WARNING SHOCK RADAR',
                            style: TextStyle(
                              color: AppTheme.textSecondary,
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.8,
                            ),
                          ),
                          Text(
                            '7 RULES LIVE',
                            style: TextStyle(
                              color: AppTheme.info,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      _buildRadarRow(
                        'Red Sea Chokepoint Transit',
                        scn.shippingDelayDays > 10 ? 'BREACH (18d Cape Diversion)' : 'NORMAL',
                        scn.shippingDelayDays > 10 ? AppTheme.danger : AppTheme.primary,
                        'Triggers emergency air-bridge and safety stock pre-buy',
                      ),
                      const Divider(color: AppTheme.border, height: 16),
                      _buildRadarRow(
                        'Container Freight Escalation',
                        '${scn.freightMultiplier.toStringAsFixed(2)}x Baseline',
                        scn.freightMultiplier > 2.0 ? AppTheme.danger : (scn.freightMultiplier > 1.2 ? AppTheme.warning : AppTheme.primary),
                        'Activates 40ft consolidation and domestic dual-sourcing',
                      ),
                      const Divider(color: AppTheme.border, height: 16),
                      _buildRadarRow(
                        'USD/INR Currency Devaluation',
                        '₹${scn.fxInrUsd.toStringAsFixed(2)}/\$',
                        scn.fxInrUsd > 88.0 ? AppTheme.warning : AppTheme.primary,
                        'Pushes landed imported raw material costs',
                      ),
                      const Divider(color: AppTheme.border, height: 16),
                      _buildRadarRow(
                        'EBITDA Margin Compression',
                        '${res.ebitdaMarginPct.toStringAsFixed(1)}% (Base: 8.8%)',
                        res.ebitdaMarginPct < 6.0 ? AppTheme.danger : (res.ebitdaMarginPct < 8.0 ? AppTheme.warning : AppTheme.primary),
                        'Demands immediate index-linked OEM price claims',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRadarRow(String title, String status, Color color, String subtitle) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          margin: const EdgeInsets.only(top: 3),
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: AppTheme.textPrimary,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    status,
                    style: TextStyle(
                      color: color,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: const TextStyle(
                  color: AppTheme.textMuted,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
