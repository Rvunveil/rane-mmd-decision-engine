import 'package:flutter/foundation.dart';

@immutable
class Scenario {
  final String name;
  final String description;
  final Map<String, double> priceShockPct;
  final double freightMultiplier;
  final double fxInrUsd;
  final double oemPassThroughPct;
  final int passThroughLagDays;
  final double tariffPct;
  final double demandVolumePct;
  final int shippingDelayDays;

  const Scenario({
    this.name = 'Base case',
    this.description = 'Baseline FY26 budget parameters',
    this.priceShockPct = const {
      'copper': 0.0,
      'nickel': 0.0,
      'aluminium': 0.0,
      'resin': 0.0,
      'rubber': 0.0,
      'steel_hr': 0.0,
      'steel_cr': 0.0,
    },
    this.freightMultiplier = 1.0,
    this.fxInrUsd = 84.5648,
    this.oemPassThroughPct = 50.0,
    this.passThroughLagDays = 75,
    this.tariffPct = 0.0,
    this.demandVolumePct = 0.0,
    this.shippingDelayDays = 0,
  });

  Scenario copyWith({
    String? name,
    String? description,
    Map<String, double>? priceShockPct,
    double? freightMultiplier,
    double? fxInrUsd,
    double? oemPassThroughPct,
    int? passThroughLagDays,
    double? tariffPct,
    double? demandVolumePct,
    int? shippingDelayDays,
  }) {
    return Scenario(
      name: name ?? this.name,
      description: description ?? this.description,
      priceShockPct: priceShockPct ?? Map<String, double>.from(this.priceShockPct),
      freightMultiplier: freightMultiplier ?? this.freightMultiplier,
      fxInrUsd: fxInrUsd ?? this.fxInrUsd,
      oemPassThroughPct: oemPassThroughPct ?? this.oemPassThroughPct,
      passThroughLagDays: passThroughLagDays ?? this.passThroughLagDays,
      tariffPct: tariffPct ?? this.tariffPct,
      demandVolumePct: demandVolumePct ?? this.demandVolumePct,
      shippingDelayDays: shippingDelayDays ?? this.shippingDelayDays,
    );
  }

  static Map<String, Scenario> getDefaultPresets() {
    return {
      'base_case': const Scenario(
        name: 'Base case',
        description: 'Baseline FY26 budget assumptions',
        priceShockPct: {
          'copper': 0.0,
          'nickel': 0.0,
          'aluminium': 0.0,
          'resin': 0.0,
          'rubber': 0.0,
          'steel_hr': 0.0,
          'steel_cr': 0.0,
        },
        freightMultiplier: 1.0,
        fxInrUsd: 84.5648,
        oemPassThroughPct: 50.0,
        passThroughLagDays: 75,
        tariffPct: 0.0,
        demandVolumePct: 0.0,
        shippingDelayDays: 0,
      ),
      'todays_market': const Scenario(
        name: "Today's market",
        description: 'Latest closing market prices and current FX spot rates',
        priceShockPct: {
          'copper': 4.2,
          'nickel': -1.8,
          'aluminium': 3.1,
          'resin': 1.5,
          'rubber': 2.0,
          'steel_hr': 2.8,
          'steel_cr': 2.5,
        },
        freightMultiplier: 1.15,
        fxInrUsd: 84.5648,
        oemPassThroughPct: 50.0,
        passThroughLagDays: 75,
        tariffPct: 0.0,
        demandVolumePct: 0.0,
        shippingDelayDays: 3,
      ),
      'red_sea_hormuz': const Scenario(
        name: 'Red Sea / Hormuz',
        description: 'Bab el-Mandeb chokepoint shutdown, 2.73x container rate surge & 18-day Cape diversion delay',
        priceShockPct: {
          'copper': 8.0,
          'nickel': 5.0,
          'aluminium': 7.0,
          'resin': 12.0,
          'rubber': 6.0,
          'steel_hr': 4.0,
          'steel_cr': 4.0,
        },
        freightMultiplier: 2.73,
        fxInrUsd: 86.50,
        oemPassThroughPct: 40.0,
        passThroughLagDays: 90,
        tariffPct: 0.0,
        demandVolumePct: -2.0,
        shippingDelayDays: 18,
      ),
      'metal_shock': const Scenario(
        name: 'Metal shock',
        description: 'Coordinated global commodity bull run driven by mine disruptions and smelter curtailments',
        priceShockPct: {
          'copper': 25.0,
          'nickel': 18.0,
          'aluminium': 22.0,
          'resin': 8.0,
          'rubber': 10.0,
          'steel_hr': 15.0,
          'steel_cr': 14.0,
        },
        freightMultiplier: 1.25,
        fxInrUsd: 85.20,
        oemPassThroughPct: 60.0,
        passThroughLagDays: 60,
        tariffPct: 0.0,
        demandVolumePct: 0.0,
        shippingDelayDays: 0,
      ),
      'tariff_fx': const Scenario(
        name: 'Tariff & FX',
        description: '10% protectionist customs duty surcharge coupled with sharp INR depreciation to 90.0/USD',
        priceShockPct: {
          'copper': 5.0,
          'nickel': 4.0,
          'aluminium': 5.0,
          'resin': 6.0,
          'rubber': 4.0,
          'steel_hr': 3.0,
          'steel_cr': 3.0,
        },
        freightMultiplier: 1.30,
        fxInrUsd: 90.00,
        oemPassThroughPct: 45.0,
        passThroughLagDays: 75,
        tariffPct: 10.0,
        demandVolumePct: -3.0,
        shippingDelayDays: 5,
      ),
      'demand_recession': const Scenario(
        name: 'Demand recession',
        description: 'Automotive industry slowdown with 8% order drop, soft metal prices and carrier overcapacity',
        priceShockPct: {
          'copper': -8.0,
          'nickel': -12.0,
          'aluminium': -6.0,
          'resin': -4.0,
          'rubber': -5.0,
          'steel_hr': -7.0,
          'steel_cr': -6.0,
        },
        freightMultiplier: 0.85,
        fxInrUsd: 84.10,
        oemPassThroughPct: 50.0,
        passThroughLagDays: 75,
        tariffPct: 0.0,
        demandVolumePct: -8.0,
        shippingDelayDays: 0,
      ),
    };
  }
}
