import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../../domain/models/results.dart';

class WaterfallChartWidget extends StatelessWidget {
  final Results results;

  const WaterfallChartWidget({super.key, required this.results});

  @override
  Widget build(BuildContext context) {
    final bars = [
      {'label': 'Base EBITDA', 'value': 297.70, 'color': AppTheme.info},
      {'label': 'Material Shock', 'value': -results.deltaMaterialCr, 'color': AppTheme.danger},
      {'label': 'Freight Surge', 'value': -results.deltaFreightCr, 'color': AppTheme.warning},
      {'label': 'Tariff Duty', 'value': -results.tariffCostCr, 'color': AppTheme.danger},
      {'label': 'OEM Recovery', 'value': results.oemRecoveryCr, 'color': AppTheme.primary},
      {'label': 'New EBITDA', 'value': results.ebitdaCr, 'color': results.ebitdaCr >= 200 ? AppTheme.primary : AppTheme.danger},
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'EBITDA WATERFALL BRIDGE',
                style: TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              Text(
                'Net Delta: ${AppTheme.formatDeltaCr(results.deltaEbitdaCr)}',
                style: TextStyle(
                  color: results.deltaEbitdaCr >= 0 ? AppTheme.primary : AppTheme.danger,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 160,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: bars.map((b) {
                final double val = b['value'] as double;
                final Color color = b['color'] as Color;
                final double absHeight = (val.abs() / 350.0 * 120).clamp(8.0, 120.0);

                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          '${val >= 0 ? '' : '-'}${val.abs().toStringAsFixed(1)}',
                          style: TextStyle(
                            color: color,
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          height: absHeight,
                          decoration: BoxDecoration(
                            color: color.withOpacity(0.85),
                            borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          b['label'] as String,
                          style: const TextStyle(
                            color: AppTheme.textMuted,
                            fontSize: 8,
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
