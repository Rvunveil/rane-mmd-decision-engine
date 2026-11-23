import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../viewmodels/decision_engine_viewmodel.dart';

class SimulatorView extends StatelessWidget {
  final DecisionEngineViewModel viewModel;

  const SimulatorView({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final scn = viewModel.scenario;
    final res = viewModel.results;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scenario Simulator & Levers'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.restore, color: AppTheme.primary, size: 18),
            label: const Text('Reset', style: TextStyle(color: AppTheme.primary)),
            onPressed: viewModel.resetToBase,
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Live Impact Floating Header
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surfaceCard,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.border),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildImpactPill('EBITDA', AppTheme.formatMoneyCr(res.ebitdaCr), AppTheme.formatDeltaCr(res.deltaEbitdaCr)),
                Container(width: 1, height: 36, color: AppTheme.border),
                _buildImpactPill('Net Cost', AppTheme.formatMoneyCr(res.netUnrecoveredCostCr), 'Unrecovered'),
                Container(width: 1, height: 36, color: AppTheme.border),
                _buildImpactPill('OEM Claim', AppTheme.formatMoneyCr(res.oemRecoveryCr), '${scn.oemPassThroughPct.toInt()}% Pass-Thru'),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // MACRO LEVERS SECTION
          const Text(
            '1. MACRO & SUPPLY CHAIN LEVERS',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 8),

          _buildSliderCard(
            title: 'Container Ocean Freight Multiplier',
            value: '${scn.freightMultiplier.toStringAsFixed(2)}x',
            subtitle: 'Base freight ₹25 Cr/year (Drewry 40ft benchmark)',
            currentValue: scn.freightMultiplier,
            min: 0.5,
            max: 3.5,
            divisions: 30,
            activeColor: scn.freightMultiplier > 2.0 ? AppTheme.danger : AppTheme.primary,
            onChanged: viewModel.updateFreightMultiplier,
          ),

          _buildSliderCard(
            title: 'USD/INR Foreign Exchange Rate',
            value: '₹${scn.fxInrUsd.toStringAsFixed(2)}/\$',
            subtitle: 'Base rate ₹84.56/USD',
            currentValue: scn.fxInrUsd,
            min: 75.0,
            max: 100.0,
            divisions: 50,
            activeColor: scn.fxInrUsd > 90.0 ? AppTheme.warning : AppTheme.primary,
            onChanged: viewModel.updateFxRate,
          ),

          _buildSliderCard(
            title: 'OEM Contractual Pass-Through Recovery',
            value: '${scn.oemPassThroughPct.toStringAsFixed(0)}%',
            subtitle: 'Quarterly indexed raw material recovery clause',
            currentValue: scn.oemPassThroughPct,
            min: 0.0,
            max: 100.0,
            divisions: 20,
            activeColor: AppTheme.info,
            onChanged: viewModel.updatePassThrough,
          ),

          _buildSliderCard(
            title: 'OEM Pass-Through Settlement Lag',
            value: '${scn.passThroughLagDays} Days',
            subtitle: 'Working capital financing gap (Default: 75 days)',
            currentValue: scn.passThroughLagDays.toDouble(),
            min: 15.0,
            max: 180.0,
            divisions: 33,
            activeColor: AppTheme.warning,
            onChanged: (v) => viewModel.updatePassThroughLag(v.toInt()),
          ),

          _buildSliderCard(
            title: 'Shipping Route Delay (Chokepoints)',
            value: '${scn.shippingDelayDays} Days',
            subtitle: 'Cape of Good Hope transit delay (Normal: 0d, Red Sea: 18d)',
            currentValue: scn.shippingDelayDays.toDouble(),
            min: 0.0,
            max: 45.0,
            divisions: 45,
            activeColor: scn.shippingDelayDays > 14 ? AppTheme.danger : AppTheme.primary,
            onChanged: (v) => viewModel.updateShippingDelay(v.toInt()),
          ),

          _buildSliderCard(
            title: 'Import Customs Tariff Surcharge',
            value: '${scn.tariffPct.toStringAsFixed(1)}%',
            subtitle: 'Applied on imported raw materials (~30% of spend)',
            currentValue: scn.tariffPct,
            min: 0.0,
            max: 25.0,
            divisions: 25,
            activeColor: AppTheme.danger,
            onChanged: viewModel.updateTariff,
          ),

          _buildSliderCard(
            title: 'Automotive OEM Volume Contraction / Expansion',
            value: AppTheme.formatPercent(scn.demandVolumePct),
            subtitle: 'Automotive industry cycle volume impact',
            currentValue: scn.demandVolumePct,
            min: -20.0,
            max: 15.0,
            divisions: 35,
            activeColor: scn.demandVolumePct < 0 ? AppTheme.danger : AppTheme.primary,
            onChanged: viewModel.updateDemandVolume,
          ),

          const SizedBox(height: 20),

          // COMMODITY RAW MATERIAL SHOCKS SECTION
          const Text(
            '2. COMMODITY PRICE SHOCKS (%)',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 11,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.8,
            ),
          ),
          const SizedBox(height: 8),

          ...['copper', 'aluminium', 'steel_hr', 'steel_cr', 'nickel', 'resin', 'rubber'].map((mat) {
            final double shock = scn.priceShockPct[mat] ?? 0.0;
            final String title = mat.replaceAll('_', ' ').toUpperCase();

            return _buildSliderCard(
              title: '$title Price Shock',
              value: AppTheme.formatPercent(shock),
              subtitle: 'Landed cost impact on component lines',
              currentValue: shock,
              min: -25.0,
              max: 50.0,
              divisions: 75,
              activeColor: shock > 0 ? AppTheme.danger : (shock < 0 ? AppTheme.primary : AppTheme.textMuted),
              onChanged: (v) => viewModel.updateMaterialShock(mat, v),
            );
          }),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildImpactPill(String title, String val, String sub) {
    return Column(
      children: [
        Text(title, style: const TextStyle(color: AppTheme.textMuted, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: const TextStyle(color: AppTheme.textPrimary, fontSize: 14, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(sub, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 9)),
      ],
    );
  }

  Widget _buildSliderCard({
    required String title,
    required String value,
    required String subtitle,
    required double currentValue,
    required double min,
    required double max,
    required int divisions,
    required Color activeColor,
    required ValueChanged<double> onChanged,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
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
              Text(
                title,
                style: const TextStyle(color: AppTheme.textPrimary, fontSize: 12, fontWeight: FontWeight.w600),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: activeColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  value,
                  style: TextStyle(color: activeColor, fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          Text(subtitle, style: const TextStyle(color: AppTheme.textMuted, fontSize: 10)),
          SliderTheme(
            data: SliderThemeData(
              activeTrackColor: activeColor,
              inactiveTrackColor: AppTheme.border,
              thumbColor: activeColor,
              trackHeight: 3,
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
              overlayShape: const RoundSliderOverlayShape(overlayRadius: 14),
            ),
            child: Slider(
              value: currentValue.clamp(min, max),
              min: min,
              max: max,
              divisions: divisions,
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }
}
