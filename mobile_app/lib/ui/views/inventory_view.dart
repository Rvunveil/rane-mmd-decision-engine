import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';
import '../../domain/models/market_data.dart';

class InventoryView extends StatelessWidget {
  final DecisionEngineViewModel viewModel;

  const InventoryView({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final scn = viewModel.scenario;
    final runways = ContainerRunwayItem.getSampleRunways(scn.shippingDelayDays);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory Runway & Containers'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Transit Status Summary Banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surfaceCard,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: scn.shippingDelayDays > 10 ? AppTheme.danger : AppTheme.border,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  scn.shippingDelayDays > 10 ? Icons.warning_amber : Icons.local_shipping_outlined,
                  color: scn.shippingDelayDays > 10 ? AppTheme.danger : AppTheme.info,
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        scn.shippingDelayDays > 10
                            ? 'CRITICAL TRANSIT DELAY: +${scn.shippingDelayDays} DAYS'
                            : 'INBOUND CONTAINER LANES ON SCHEDULE',
                        style: TextStyle(
                          color: scn.shippingDelayDays > 10 ? AppTheme.danger : AppTheme.textPrimary,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        scn.shippingDelayDays > 10
                            ? 'Cape of Good Hope diversion adds 18 days to transit times, threatening plant stock-out thresholds.'
                            : 'Normal 21-day average shipping lead time from overseas smelters to Chennai/Tuticorin ports.',
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          const Text(
            'ACTIVE COMPONENT INVENTORY COVERAGE',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 8),

          ...runways.map((item) {
            Color statusColor;
            IconData statusIcon;
            if (item.status == 'CRITICAL') {
              statusColor = AppTheme.danger;
              statusIcon = Icons.error_outline;
            } else if (item.status == 'WARNING') {
              statusColor = AppTheme.warning;
              statusIcon = Icons.warning_amber;
            } else {
              statusColor = AppTheme.primary;
              statusIcon = Icons.check_circle_outline;
            }

            final double coverageRatio = (item.daysOfCover / item.safeRunwayDays).clamp(0.0, 1.0);

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: AppTheme.surfaceCard,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppTheme.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          item.material,
                          style: const TextStyle(
                            color: AppTheme.textPrimary,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: statusColor, width: 0.5),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(statusIcon, color: statusColor, size: 12),
                            const SizedBox(width: 4),
                            Text(
                              item.status,
                              style: TextStyle(
                                color: statusColor,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  Text(
                    item.category,
                    style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildMiniCol('On-Hand Stock', '${item.currentStockTonnes.toInt()} t'),
                      _buildMiniCol('Daily Burn', '${item.dailyBurnTonnes} t/d'),
                      _buildMiniCol('Containers', '${item.containersInTransit} FEU'),
                      _buildMiniCol('Runway Cover', '${item.daysOfCover} Days', color: statusColor, isBold: true),
                    ],
                  ),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: coverageRatio,
                    backgroundColor: AppTheme.surface,
                    valueColor: AlwaysStoppedAnimation<Color>(statusColor),
                    minHeight: 4,
                    borderRadius: BorderRadius.circular(2),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Buffer Target: ${item.safeRunwayDays} days',
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 9),
                      ),
                      Text(
                        '${(coverageRatio * 100).toInt()}% of safe stock',
                        style: TextStyle(color: statusColor, fontSize: 9, fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ],
              ),
            );
          }),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildMiniCol(String label, String val, {Color? color, bool isBold = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: AppTheme.textMuted, fontSize: 9)),
        const SizedBox(height: 1),
        Text(
          val,
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
