import 'package:flutter/material.dart';
import '../../domain/models/scenario.dart';
import '../../domain/models/results.dart';
import '../../domain/models/mitigation_action.dart';
import '../../domain/services/profit_chain_engine.dart';

class DecisionEngineViewModel extends ChangeNotifier {
  Scenario _scenario = const Scenario();
  Results _results = ProfitChainEngine.runAll(const Scenario());
  String _activePresetKey = 'base_case';
  double _cashBudgetCr = 5.0;
  List<MitigationAction> _optimizedBundle = [];

  DecisionEngineViewModel() {
    _recalculate();
  }

  // Getters
  Scenario get scenario => _scenario;
  Results get results => _results;
  String get activePresetKey => _activePresetKey;
  double get cashBudgetCr => _cashBudgetCr;
  List<MitigationAction> get optimizedBundle => _optimizedBundle;

  void _recalculate() {
    _results = ProfitChainEngine.runAll(_scenario);
    _optimizedBundle = ProfitChainEngine.optimizeActionBundle(_results.actionRankings, _cashBudgetCr);
    notifyListeners();
  }

  void applyPreset(String presetKey) {
    final presets = Scenario.getDefaultPresets();
    if (presets.containsKey(presetKey)) {
      _scenario = presets[presetKey]!;
      _activePresetKey = presetKey;
      _recalculate();
    }
  }

  void resetToBase() {
    applyPreset('base_case');
  }

  void updateFreightMultiplier(double val) {
    _scenario = _scenario.copyWith(freightMultiplier: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updateFxRate(double val) {
    _scenario = _scenario.copyWith(fxInrUsd: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updateTariff(double val) {
    _scenario = _scenario.copyWith(tariffPct: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updatePassThrough(double val) {
    _scenario = _scenario.copyWith(oemPassThroughPct: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updatePassThroughLag(int val) {
    _scenario = _scenario.copyWith(passThroughLagDays: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updateShippingDelay(int val) {
    _scenario = _scenario.copyWith(shippingDelayDays: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updateDemandVolume(double val) {
    _scenario = _scenario.copyWith(demandVolumePct: val);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updateMaterialShock(String matKey, double shockPct) {
    final newShocks = Map<String, double>.from(_scenario.priceShockPct);
    newShocks[matKey] = shockPct;
    _scenario = _scenario.copyWith(priceShockPct: newShocks);
    _activePresetKey = 'custom';
    _recalculate();
  }

  void updateCashBudget(double val) {
    _cashBudgetCr = val;
    _optimizedBundle = ProfitChainEngine.optimizeActionBundle(_results.actionRankings, _cashBudgetCr);
    notifyListeners();
  }

  void applyGuidedEvent(String eventType, String severity) {
    // Exact mapping from guided helper
    if (eventType == 'shipping') {
      if (severity == 'Small') {
        _scenario = _scenario.copyWith(name: 'Guided: Shipping Delay', freightMultiplier: 1.5, shippingDelayDays: 7);
      } else if (severity == 'Medium') {
        _scenario = _scenario.copyWith(name: 'Guided: High Freight', freightMultiplier: 2.0, shippingDelayDays: 14);
      } else {
        _scenario = _scenario.copyWith(name: 'Guided: Chokepoint Blockade', freightMultiplier: 2.73, shippingDelayDays: 18);
      }
    } else if (eventType == 'metal') {
      final shocks = Map<String, double>.from(_scenario.priceShockPct);
      final double s = severity == 'Small' ? 10.0 : (severity == 'Medium' ? 20.0 : 35.0);
      shocks['copper'] = s;
      shocks['aluminium'] = s;
      shocks['steel_hr'] = s * 0.8;
      _scenario = _scenario.copyWith(name: 'Guided: Metal Spike ($s%)', priceShockPct: shocks);
    } else if (eventType == 'fx') {
      final double fx = severity == 'Small' ? 88.0 : (severity == 'Medium' ? 92.0 : 96.5);
      _scenario = _scenario.copyWith(name: 'Guided: INR Devaluation', fxInrUsd: fx);
    } else if (eventType == 'demand') {
      final double d = severity == 'Small' ? -5.0 : (severity == 'Medium' ? -8.0 : -12.0);
      _scenario = _scenario.copyWith(name: 'Guided: Demand Slump', demandVolumePct: d);
    } else if (eventType == 'delay') {
      final int del = severity == 'Small' ? 10 : (severity == 'Medium' ? 20 : 30);
      _scenario = _scenario.copyWith(name: 'Guided: Supplier Delay', shippingDelayDays: del);
    } else if (eventType == 'tariff') {
      final double t = severity == 'Small' ? 5.0 : (severity == 'Medium' ? 10.0 : 15.0);
      _scenario = _scenario.copyWith(name: 'Guided: Import Tariff', tariffPct: t);
    }
    _activePresetKey = 'guided';
    _recalculate();
  }
}
