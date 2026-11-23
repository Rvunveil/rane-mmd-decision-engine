import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class MetricCardWidget extends StatelessWidget {
  final String title;
  final String value;
  final String delta;
  final bool isPositiveGood;
  final IconData icon;
  final Color? accentColor;

  const MetricCardWidget({
    super.key,
    required this.title,
    required this.value,
    required this.delta,
    this.isPositiveGood = true,
    required this.icon,
    this.accentColor,
  });

  @override
  Widget build(BuildContext context) {
    final bool isZero = delta.contains('0.00') || delta.contains('0.0%');
    final bool isPositive = delta.startsWith('+');

    Color badgeColor;
    if (isZero) {
      badgeColor = AppTheme.textMuted;
    } else if (isPositive) {
      badgeColor = isPositiveGood ? AppTheme.primary : AppTheme.danger;
    } else {
      badgeColor = isPositiveGood ? AppTheme.danger : AppTheme.primary;
    }

    final accent = accentColor ?? AppTheme.primary;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.surfaceCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  title.toUpperCase(),
                  style: const TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.8,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: accent.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Icon(icon, color: accent, size: 14),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: AppTheme.textPrimary,
              fontSize: 19,
              fontWeight: FontWeight.bold,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: badgeColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  delta,
                  style: TextStyle(
                    color: badgeColor,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(width: 6),
              const Text(
                'vs Base',
                style: TextStyle(
                  color: AppTheme.textMuted,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
