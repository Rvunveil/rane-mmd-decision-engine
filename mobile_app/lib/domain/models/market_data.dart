import 'package:flutter/foundation.dart';

@immutable
class MarketTickerItem {
  final String symbol;
  final String name;
  final double price;
  final String unit;
  final double changePct;
  final bool isUp;

  const MarketTickerItem({
    required this.symbol,
    required this.name,
    required this.price,
    required this.unit,
    required this.changePct,
    required this.isUp,
  });

  static List<MarketTickerItem> getLatestTape() {
    return const [
      MarketTickerItem(
        symbol: 'LME:CU',
        name: 'Copper',
        price: 9140.0,
        unit: r'$/t',
        changePct: 0.82,
        isUp: true,
      ),
      MarketTickerItem(
        symbol: 'LME:AL',
        name: 'Aluminium',
        price: 2610.0,
        unit: r'$/t',
        changePct: -0.45,
        isUp: false,
      ),
      MarketTickerItem(
        symbol: 'LME:NI',
        name: 'Nickel',
        price: 16250.0,
        unit: r'$/t',
        changePct: 1.15,
        isUp: true,
      ),
      MarketTickerItem(
        symbol: 'MUM:FE-HR',
        name: 'Steel HR',
        price: 58400.0,
        unit: '₹/t',
        changePct: 0.20,
        isUp: true,
      ),
      MarketTickerItem(
        symbol: 'MUM:FE-CR',
        name: 'Steel CR',
        price: 64200.0,
        unit: '₹/t',
        changePct: -0.10,
        isUp: false,
      ),
      MarketTickerItem(
        symbol: 'FBX:40FT',
        name: 'Ocean Freight',
        price: 3210.0,
        unit: r'$/FEU',
        changePct: 3.40,
        isUp: true,
      ),
      MarketTickerItem(
        symbol: 'ICE:BRENT',
        name: 'Brent Crude',
        price: 74.20,
        unit: r'$/bbl',
        changePct: -0.65,
        isUp: false,
      ),
      MarketTickerItem(
        symbol: 'FX:USDINR',
        name: 'USD/INR',
        price: 84.56,
        unit: '₹',
        changePct: 0.05,
        isUp: true,
      ),
    ];
  }
}

@immutable
class AndonAlert {
  final String triggerId;
  final String name;
  final String severity; // RED, AMBER, GREEN
  final String condition;
  final String activeStatus;
  final String actionRecommendation;

  const AndonAlert({
    required this.triggerId,
    required this.name,
    required this.severity,
    required this.condition,
    required this.activeStatus,
    required this.actionRecommendation,
  });
}

@immutable
class ContainerRunwayItem {
  final String material;
  final String category;
  final int containersInTransit;
  final double currentStockTonnes;
  final double dailyBurnTonnes;
  final int daysOfCover;
  final int safeRunwayDays;
  final String status; // CRITICAL, WARNING, SECURE

  const ContainerRunwayItem({
    required this.material,
    required this.category,
    required this.containersInTransit,
    required this.currentStockTonnes,
    required this.dailyBurnTonnes,
    required this.daysOfCover,
    required this.safeRunwayDays,
    required this.status,
  });

  static List<ContainerRunwayItem> getSampleRunways(int shippingDelayDays) {
    return [
      ContainerRunwayItem(
        material: 'High-Purity Aluminium Ingots',
        category: 'Die Casting Division',
        containersInTransit: 14,
        currentStockTonnes: 450.0,
        dailyBurnTonnes: 18.5,
        daysOfCover: (450.0 / 18.5 - shippingDelayDays).clamp(1, 99).toInt(),
        safeRunwayDays: 21,
        status: (450.0 / 18.5 - shippingDelayDays) < 14
            ? 'CRITICAL'
            : (450.0 / 18.5 - shippingDelayDays) < 21
                ? 'WARNING'
                : 'SECURE',
      ),
      ContainerRunwayItem(
        material: 'Refined Copper Rods (8mm)',
        category: 'Steering & Electrical',
        containersInTransit: 8,
        currentStockTonnes: 210.0,
        dailyBurnTonnes: 9.2,
        daysOfCover: (210.0 / 9.2 - shippingDelayDays).clamp(1, 99).toInt(),
        safeRunwayDays: 25,
        status: (210.0 / 9.2 - shippingDelayDays) < 14
            ? 'CRITICAL'
            : (210.0 / 9.2 - shippingDelayDays) < 25
                ? 'WARNING'
                : 'SECURE',
      ),
      ContainerRunwayItem(
        material: 'Automotive Grade Special Steel CR',
        category: 'Steering Column Shafts',
        containersInTransit: 22,
        currentStockTonnes: 820.0,
        dailyBurnTonnes: 24.0,
        daysOfCover: (820.0 / 24.0 - shippingDelayDays).clamp(1, 99).toInt(),
        safeRunwayDays: 30,
        status: (820.0 / 24.0 - shippingDelayDays) < 20
            ? 'CRITICAL'
            : (820.0 / 24.0 - shippingDelayDays) < 30
                ? 'WARNING'
                : 'SECURE',
      ),
      ContainerRunwayItem(
        material: 'Engineered Polymer Resins (PA66)',
        category: 'Bushings & Seals',
        containersInTransit: 5,
        currentStockTonnes: 95.0,
        dailyBurnTonnes: 3.5,
        daysOfCover: (95.0 / 3.5 - shippingDelayDays).clamp(1, 99).toInt(),
        safeRunwayDays: 20,
        status: (95.0 / 3.5 - shippingDelayDays) < 14
            ? 'CRITICAL'
            : (95.0 / 3.5 - shippingDelayDays) < 20
                ? 'WARNING'
                : 'SECURE',
      ),
    ];
  }
}
