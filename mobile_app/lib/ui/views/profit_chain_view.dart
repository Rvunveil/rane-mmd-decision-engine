import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';
import '../widgets/waterfall_chart_widget.dart';

class ProfitChainView extends StatelessWidget {
  final DecisionEngineViewModel viewModel;

  const ProfitChainView({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final res = viewModel.results;
    final scn = viewModel.scenario;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profit Chain & Landed Cost'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Waterfall Bridge
          WaterfallChartWidget(results: res),
          const SizedBox(height: 16),

          // P&L SUMMARY TABLE CARD
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
                const Text(
                  'FINANCIAL RECONCILIATION (₹ CR)',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 12),
                _buildRow('Operating Revenue', '₹3,374.00 Cr', AppTheme.formatMoneyCr(res.revenueCr), AppTheme.formatDeltaCr(res.revenueCr - 3374.0)),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Raw Material Spend', '₹1,223.00 Cr', AppTheme.formatMoneyCr(res.materialCostCr), AppTheme.formatDeltaCr(res.deltaMaterialCr)),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Ocean Container Freight', '₹25.00 Cr', AppTheme.formatMoneyCr(res.freightCostCr), AppTheme.formatDeltaCr(res.deltaFreightCr)),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Customs Tariff Surcharge', '₹0.00 Cr', AppTheme.formatMoneyCr(res.tariffCostCr), AppTheme.formatDeltaCr(res.tariffCostCr)),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Total Inbound Landed Cost', '₹1,248.00 Cr', AppTheme.formatMoneyCr(res.totalInboundCr), AppTheme.formatDeltaCr(res.deltaTotalInboundCr)),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('OEM Pass-Through Recovery', '₹0.00 Cr', AppTheme.formatMoneyCr(res.oemRecoveryCr), '+${scn.oemPassThroughPct.toInt()}%'),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Net Unrecovered Cost', '₹0.00 Cr', AppTheme.formatMoneyCr(res.netUnrecoveredCostCr), AppTheme.formatDeltaCr(res.netUnrecoveredCostCr)),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Operating Profit (EBITDA)', '₹297.70 Cr', AppTheme.formatMoneyCr(res.ebitdaCr), AppTheme.formatDeltaCr(res.deltaEbitdaCr), isBold: true),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Net Profit After Tax (PAT)', '₹37.60 Cr', AppTheme.formatMoneyCr(res.patCr), AppTheme.formatDeltaCr(res.deltaPatCr), isBold: true),
                const Divider(color: AppTheme.border, height: 16),
                _buildRow('Working Capital Cash Drag', '₹0.00 Cr', AppTheme.formatMoneyCr(res.workingCapitalDragCr), '${scn.passThroughLagDays}d lag', isWarn: true),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // DIVISION COST ALLOCATION
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
                const Text(
                  'DIVISIONAL INBOUND COST ABSORPTION',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 12),
                ...res.divisionSpendCr.entries.map((entry) {
                  final double pct = (entry.value / res.totalInboundCr) * 100.0;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              entry.key,
                              style: const TextStyle(color: AppTheme.textPrimary, fontSize: 12, fontWeight: FontWeight.w600),
                            ),
                            Text(
                              '${AppTheme.formatMoneyCr(entry.value)} (${pct.toStringAsFixed(0)}%)',
                              style: const TextStyle(color: AppTheme.info, fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value: pct / 100.0,
                          backgroundColor: AppTheme.surface,
                          valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.info),
                          minHeight: 4,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ],
                    ),
                  );
                }),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // COMMODITY RAW MATERIAL BREAKDOWN
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
                const Text(
                  'COMMODITY SPEND BREAKDOWN',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 12),
                ...res.materialSpendCr.entries.map((entry) {
                  final String mat = entry.key.replaceAll('_', ' ').toUpperCase();
                  final double shock = scn.priceShockPct[entry.key] ?? 0.0;
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(mat, style: const TextStyle(color: AppTheme.textPrimary, fontSize: 12)),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                              decoration: BoxDecoration(
                                color: shock == 0 ? Colors.transparent : (shock > 0 ? AppTheme.danger.withOpacity(0.15) : AppTheme.primary.withOpacity(0.15)),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                AppTheme.formatPercent(shock),
                                style: TextStyle(
                                  color: shock == 0 ? AppTheme.textMuted : (shock > 0 ? AppTheme.danger : AppTheme.primary),
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              AppTheme.formatMoneyCr(entry.value),
                              style: const TextStyle(color: AppTheme.textPrimary, fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                }),
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildRow(String title, String base, String current, String delta, {bool isBold = false, bool isWarn = false}) {
    return Row(
      children: [
        Expanded(
          flex: 4,
          child: Text(
            title,
            style: TextStyle(
              color: isBold ? AppTheme.textPrimary : AppTheme.textSecondary,
              fontSize: 12,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
        Expanded(
          flex: 3,
          child: Text(
            current,
            style: TextStyle(
              color: isWarn ? AppTheme.warning : (isBold ? AppTheme.primary : AppTheme.textPrimary),
              fontSize: 12,
              fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
            ),
            textAlign: TextAlign.right,
          ),
        ),
        Expanded(
          flex: 2,
          child: Text(
            delta,
            style: TextStyle(
              color: delta.startsWith('+') ? AppTheme.danger : (delta.startsWith('-') ? AppTheme.primary : AppTheme.textMuted),
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }
}
