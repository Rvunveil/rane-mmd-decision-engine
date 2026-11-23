import 'package:flutter/material.dart';
import '../../domain/models/market_data.dart';
import '../theme/app_theme.dart';

class MarketTapeWidget extends StatelessWidget {
  const MarketTapeWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final items = MarketTickerItem.getLatestTape();

    return Container(
      height: 44,
      color: const Color(0xFF070A10),
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: items.length,
        separatorBuilder: (_, _) => const VerticalDivider(
          color: AppTheme.border,
          indent: 10,
          endIndent: 10,
          width: 24,
        ),
        itemBuilder: (context, index) {
          final item = items[index];
          final color = item.isUp ? AppTheme.primary : AppTheme.danger;
          final icon = item.isUp ? Icons.arrow_drop_up : Icons.arrow_drop_down;

          return Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                item.symbol,
                style: const TextStyle(
                  color: AppTheme.textMuted,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                '${item.name}: ',
                style: const TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                ),
              ),
              Text(
                '${item.price.toStringAsFixed(item.price > 100 ? 0 : 2)} ${item.unit}',
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: 4),
              Icon(icon, color: color, size: 16),
              Text(
                '${item.changePct.toStringAsFixed(2)}%',
                style: TextStyle(
                  color: color,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
