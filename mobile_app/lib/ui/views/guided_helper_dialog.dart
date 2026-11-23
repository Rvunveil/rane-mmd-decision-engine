import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';

class GuidedHelperDialog extends StatefulWidget {
  final DecisionEngineViewModel viewModel;

  const GuidedHelperDialog({super.key, required this.viewModel});

  static Future<void> show(BuildContext context, DecisionEngineViewModel viewModel) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => GuidedHelperDialog(viewModel: viewModel),
    );
  }

  @override
  State<GuidedHelperDialog> createState() => _GuidedHelperDialogState();
}

class _GuidedHelperDialogState extends State<GuidedHelperDialog> {
  String _selectedEvent = 'shipping';
  String _selectedSeverity = 'Medium';

  final List<Map<String, String>> _events = [
    {
      'key': 'shipping',
      'title': 'Shipping Route Blocked / Slow',
      'desc': 'Red Sea / Cape diversion, container rate escalation',
      'icon': 'directions_boat',
    },
    {
      'key': 'metal',
      'title': 'Commodity Metal Price Spike',
      'desc': 'Copper, Aluminium, or Steel jump on global exchanges',
      'icon': 'bolt',
    },
    {
      'key': 'fx',
      'title': 'Rupee Depreciation vs USD',
      'desc': 'Forex escalation pushing landed raw material costs',
      'icon': 'currency_exchange',
    },
    {
      'key': 'demand',
      'title': 'OEM Automotive Demand Slump',
      'desc': 'Automakers cut production schedules and order volumes',
      'icon': 'trending_down',
    },
    {
      'key': 'delay',
      'title': 'Supplier Lead Time Delay',
      'desc': 'Critical component shipments stuck at ports or customs',
      'icon': 'schedule',
    },
    {
      'key': 'tariff',
      'title': 'Customs Duty / Tariff Increase',
      'desc': 'Import surcharge or carbon border duty adjustment',
      'icon': 'gavel',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        top: 20,
        left: 20,
        right: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.85,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.help_outline, color: AppTheme.info, size: 22),
                  SizedBox(width: 8),
                  Text(
                    'What Happened? Decision Wizard',
                    style: TextStyle(
                      color: AppTheme.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.close, color: AppTheme.textMuted),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            'Select the real-world operational event. The engine will instantly calculate the financial impact and load the optimal mitigation moves.',
            style: TextStyle(color: AppTheme.textSecondary, fontSize: 12),
          ),
          const SizedBox(height: 16),
          const Text(
            '1. SELECT EVENT TYPE',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: _events.length,
              separatorBuilder: (_, _) => const SizedBox(height: 6),
              itemBuilder: (context, index) {
                final ev = _events[index];
                final isSelected = _selectedEvent == ev['key'];

                return InkWell(
                  onTap: () => setState(() => _selectedEvent = ev['key']!),
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: isSelected ? AppTheme.surfaceCard : Colors.transparent,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: isSelected ? AppTheme.primary : AppTheme.border,
                        width: isSelected ? 1.5 : 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          _getIcon(ev['icon']!),
                          color: isSelected ? AppTheme.primary : AppTheme.textMuted,
                          size: 20,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                ev['title']!,
                                style: TextStyle(
                                  color: isSelected ? AppTheme.textPrimary : AppTheme.textSecondary,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              Text(
                                ev['desc']!,
                                style: const TextStyle(
                                  color: AppTheme.textMuted,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                        if (isSelected)
                          const Icon(Icons.check_circle, color: AppTheme.primary, size: 18),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 14),
          const Text(
            '2. SELECT SEVERITY',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: ['Small', 'Medium', 'Large'].map((sev) {
              final isSel = _selectedSeverity == sev;
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      backgroundColor: isSel ? AppTheme.primary : AppTheme.surfaceCard,
                      side: BorderSide(
                        color: isSel ? AppTheme.primary : AppTheme.border,
                      ),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                    ),
                    onPressed: () => setState(() => _selectedSeverity = sev),
                    child: Text(
                      sev,
                      style: TextStyle(
                        color: isSel ? Colors.black : AppTheme.textSecondary,
                        fontWeight: isSel ? FontWeight.bold : FontWeight.w500,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton.icon(
              icon: const Icon(Icons.bolt, color: Colors.black),
              label: const Text(
                'Apply Disruption & Get Action Plan',
                style: TextStyle(
                  color: Colors.black,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primary,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: () {
                widget.viewModel.applyGuidedEvent(_selectedEvent, _selectedSeverity);
                Navigator.of(context).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    backgroundColor: AppTheme.surfaceCard,
                    content: Text(
                      'Applied: ${_selectedEvent.toUpperCase()} ($_selectedSeverity) Disruption',
                      style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  IconData _getIcon(String iconName) {
    switch (iconName) {
      case 'directions_boat':
        return Icons.directions_boat;
      case 'bolt':
        return Icons.bolt;
      case 'currency_exchange':
        return Icons.currency_exchange;
      case 'trending_down':
        return Icons.trending_down;
      case 'schedule':
        return Icons.schedule;
      case 'gavel':
        return Icons.gavel;
      default:
        return Icons.info_outline;
    }
  }
}
