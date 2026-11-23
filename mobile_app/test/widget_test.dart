import 'package:flutter_test/flutter_test.dart';
import 'package:rane_mmd_app/domain/models/scenario.dart';
import 'package:rane_mmd_app/domain/services/profit_chain_engine.dart';
import 'package:rane_mmd_app/main.dart';

void main() {
  group('MMD Decision Engine Dart Port Parity Tests', () {
    test('Base Case Parity Test', () {
      const scn = Scenario();
      final res = ProfitChainEngine.runAll(scn);

      expect(res.revenueCr, closeTo(3374.0, 0.01));
      expect(res.materialCostCr, closeTo(1223.0, 0.01));
      expect(res.freightCostCr, closeTo(25.0, 0.01));
      expect(res.ebitdaCr, closeTo(297.70, 0.01));
      expect(res.patCr, closeTo(37.60, 0.01));
      expect(res.deltaMaterialCr, closeTo(0.0, 0.01));
      expect(res.deltaFreightCr, closeTo(0.0, 0.01));
      expect(res.actionRankings.length, 10);
    });

    test('10% Commodity Price Shock Parity Test', () {
      final scn = const Scenario().copyWith(
        priceShockPct: {
          'copper': 10.0,
          'nickel': 10.0,
          'aluminium': 10.0,
          'resin': 10.0,
          'rubber': 10.0,
          'steel_hr': 10.0,
          'steel_cr': 10.0,
        },
      );
      final res = ProfitChainEngine.runAll(scn);

      // Delta material should be exactly 10% of 1,223 = 122.30 Cr
      expect(res.deltaMaterialCr, closeTo(122.30, 0.05));
      // With default 50% pass through, recovery is 61.15 Cr
      expect(res.oemRecoveryCr, closeTo(61.15, 0.05));
      // Unrecovered cost is 61.15 Cr
      expect(res.netUnrecoveredCostCr, closeTo(61.15, 0.05));
      // EBITDA drops from 297.70 to 236.55 Cr
      expect(res.ebitdaCr, closeTo(236.55, 0.05));
    });

    test('Red Sea / Hormuz Chokepoint Preset Parity Test', () {
      final presets = Scenario.getDefaultPresets();
      final redSea = presets['red_sea_hormuz']!;
      final res = ProfitChainEngine.runAll(redSea);

      expect(res.deltaFreightCr, greaterThan(35.0));
      expect(res.ebitdaCr, lessThan(270.0));
      expect(res.actionRankings.first.netBenefitCr, greaterThan(0.0));
    });

    test('0-1 Integer Knapsack Optimizer Test', () {
      const scn = Scenario();
      final res = ProfitChainEngine.runAll(scn);
      final bundle = ProfitChainEngine.optimizeActionBundle(res.actionRankings, 5.0);

      expect(bundle, isNotEmpty);
      final totalSpend = bundle.fold(0.0, (sum, a) => sum + a.cashBudgetRequiredCr);
      expect(totalSpend, lessThanOrEqualTo(5.0));
    });
  });

  group('Flutter Mobile App Widget Smoke Test', () {
    testWidgets('App loads cleanly with Control Room view', (WidgetTester tester) async {
      await tester.pumpWidget(const RaneMmdApp());
      await tester.pumpAndSettle();

      expect(find.text('Materials Control Room'), findsOneWidget);
      expect(find.text('REVENUE'), findsOneWidget);
      expect(find.text('EBITDA (MARGIN)'), findsOneWidget);
    });
  });
}
