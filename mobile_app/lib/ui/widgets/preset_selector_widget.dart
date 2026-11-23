import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';

class PresetSelectorWidget extends StatelessWidget {
  final DecisionEngineViewModel viewModel;
  final VoidCallback onOpenGuidedHelper;

  const PresetSelectorWidget({
    super.key,
    required this.viewModel,
    required this.onOpenGuidedHelper,
  });

  @override
  Widget build(BuildContext context) {
    final chips = [
      {'key': 'base_case', 'label': 'Base', 'icon': Icons.tune},
      {'key': 'todays_market', 'label': "Today's market", 'icon': Icons.trending_up},
      {'key': 'red_sea_hormuz', 'label': 'Red Sea / Hormuz', 'icon': Icons.warning_amber},
      {'key': 'metal_shock', 'label': 'Metal shock', 'icon': Icons.bolt},
      {'key': 'tariff_fx', 'label': 'Tariff & FX', 'icon': Icons.currency_exchange},
      {'key': 'demand_recession', 'label': 'Demand recession', 'icon': Icons.trending_down},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          // Help Dialog Action Button
          ActionChip(
            avatar: const Icon(Icons.help_outline, color: AppTheme.info, size: 16),
            label: const Text(
              'What happened?',
              style: TextStyle(
                color: AppTheme.info,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            backgroundColor: AppTheme.info.withOpacity(0.12),
            side: const BorderSide(color: AppTheme.info, width: 1),
            onPressed: onOpenGuidedHelper,
          ),
          const SizedBox(width: 8),

          // Preset Chips
          ...chips.map((chip) {
            final isSelected = viewModel.activePresetKey == chip['key'];
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: ChoiceChip(
                selected: isSelected,
                avatar: Icon(
                  chip['icon'] as IconData,
                  size: 15,
                  color: isSelected ? Colors.black : AppTheme.textSecondary,
                ),
                label: Text(
                  chip['label'] as String,
                  style: TextStyle(
                    color: isSelected ? Colors.black : AppTheme.textSecondary,
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                  ),
                ),
                selectedColor: AppTheme.primary,
                backgroundColor: AppTheme.surfaceCard,
                side: BorderSide(
                  color: isSelected ? AppTheme.primary : AppTheme.border,
                  width: 1,
                ),
                onSelected: (_) => viewModel.applyPreset(chip['key'] as String),
              ),
            );
          }),

          // Reset Action Button
          ActionChip(
            avatar: const Icon(Icons.restart_alt, color: AppTheme.textMuted, size: 16),
            label: const Text(
              'Reset',
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 12,
              ),
            ),
            backgroundColor: AppTheme.surface,
            side: const BorderSide(color: AppTheme.border, width: 1),
            onPressed: viewModel.resetToBase,
          ),
        ],
      ),
    );
  }
}
