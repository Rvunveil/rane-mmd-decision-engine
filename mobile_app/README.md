# Rane (Madras) MMD Decision Engine — Android & Flutter Mobile Terminal
**Team 11:59 · Xovate'26 Management Hackathon · XIME Chennai**

---

## Overview

The **Rane MMD Decision Engine Mobile App** is a native, offline-first mobile terminal engineered in **Flutter 3.50 & Dart 3.14** for Android. It translates the enterprise decision engine into a responsive, handheld executive cockpit for plant managers, MMD procurement officers, and automotive executives.

### Core Architecture & Capabilities

1. **100% Offline Pure Dart Calculation Engine (`lib/domain/services/profit_chain_engine.dart`)**:
   - Zero dependence on backend servers or internet connectivity.
   - Closed-form mathematical P&L recalculation down to the rupee.
   - Recalculates gross margins, material cost deltas, container freight surges, and OEM pass-through recoveries in sub-milliseconds.
   - Evaluates all **10 Prescriptive Mitigation Levers** and ranks them dynamically by net benefit.
   - Solves the **0-1 Integer Knapsack Portfolio Optimization** locally on the phone's CPU.

2. **Bloomberg Terminal Industrial Dark UI (`lib/ui/theme/app_theme.dart`)**:
   - Palette: Deep Slate (`#0B0F19`), Graphite Card Surface (`#182235`), Emerald (`#10B981`), Rose (`#F43F5E`), Amber (`#F59E0B`), Sky Blue (`#38BDF8`).
   - Tabular figures and high-contrast typography for executive readability.

3. **5 Bottom-Navigation Feature Hubs**:
   - **Tab 1: Control Room** — Live market tape ticker (LME Copper, Aluminium, Nickel, Steel HR/CR, Brent, Freight), 4 key KPI cards, scenario preset chips, EBITDA waterfall bridge, and Early Warning Shock Radar / Andon triggers.
   - **Tab 2: Simulator** — Interactive tactile sliders for Freight Multiplier, USD/INR Forex, Pass-Through %, Lag Days, Tariff %, Demand Volume, and individual metal price shocks.
   - **Tab 3: Profit Chain** — Financial reconciliation table, divisional cost absorption (Steering 62%, Die Casting 26%, CV 12%), and commodity spend breakdown.
   - **Tab 4: Inventory Runway** — 40ft container fleet tracking, daily consumption burn rates, dynamic transit lead-time adjustments, and stock-out alerts.
   - **Tab 5: Action Matrix** — 10 Prescriptive Actions, cash budget slider, and 0-1 Knapsack optimal bundle solver.

4. **"What Happened?" Decision Wizard (`lib/ui/views/guided_helper_dialog.dart`)**:
   - Interactive dialog mapping 6 real-world operational disruption events $\times$ 3 severity levels into immediate bottom-line impact and action recommendations.

---

## How to Load & Run in Android Studio

### Method 1: Open Directly in Android Studio (Recommended)

1. **Launch Android Studio**.
2. Click **File $\rightarrow$ Open...** (or click **Open** on the Welcome screen).
3. Navigate to and select the `mobile_app` folder:
   ```
   C:\Users\ASUS\OneDrive\Desktop\Hackathon PhotoBooth\mobile_app
   ```
4. Click **OK**. Android Studio will automatically recognize the Flutter project and load the Android Gradle project structure.
5. In the top toolbar, select your Android Device or Emulator (e.g. Pixel 8 / API 34).
6. Click the green **Run (Play)** button or press `Shift + F10`.

---

### Method 2: Build APK or Android App Bundle from CLI

Open a terminal in the `mobile_app` folder:

#### 1. Build Debug APK (For quick testing & sideloading):
```powershell
cd mobile_app
flutter build apk --debug
```
*Output location:* `mobile_app/build/app/outputs/flutter-apk/app-debug.apk`

#### 2. Build Release APK (Optimized standalone binary):
```powershell
cd mobile_app
flutter build apk --release
```
*Output location:* `mobile_app/build/app/outputs/flutter-apk/app-release.apk`

#### 3. Build Android App Bundle (AAB for Google Play Store):
```powershell
cd mobile_app
flutter build appbundle
```
*Output location:* `mobile_app/build/app/outputs/bundle/release/app-release.aab`

---

## Directory Structure

```
mobile_app/
├── android/                         # Android Studio native Gradle project
│   ├── app/
│   │   ├── build.gradle.kts         # SDK configs (minSdk 21, compileSdk 34+, Java 17)
│   │   └── src/main/
│   │       └── AndroidManifest.xml  # App label "Rane MMD Engine", permissions, launcher
│   └── build.gradle.kts             # Gradle root configuration
├── lib/
│   ├── main.dart                    # Application entry point & 5-tab navigation shell
│   ├── domain/
│   │   ├── models/
│   │   │   ├── scenario.dart        # Scenario dataclass & 6 presets
│   │   │   ├── results.dart         # Financial results & metrics
│   │   │   ├── mitigation_action.dart # Action matrix model & attributes
│   │   │   └── market_data.dart     # Ticker tape & container runway models
│   │   └── services/
│   │       └── profit_chain_engine.dart # Offline mathematical profit engine & 0-1 optimizer
│   └── ui/
│       ├── theme/
│       │   └── app_theme.dart       # Bloomberg dark industrial palette & formatters
│       ├── viewmodels/
│       │   └── decision_engine_viewmodel.dart # ChangeNotifier state container
│       ├── views/
│       │   ├── control_room_view.dart    # Tab 1: Control Room Dashboard
│       │   ├── simulator_view.dart       # Tab 2: Levers & Sliders
│       │   ├── profit_chain_view.dart    # Tab 3: Landed Cost & P&L
│       │   ├── inventory_view.dart       # Tab 4: Containers & Runway
│       │   ├── action_matrix_view.dart   # Tab 5: 0-1 Optimization Bundle
│       │   └── guided_helper_dialog.dart # "What happened?" Decision Wizard
│       └── widgets/
│           ├── market_tape_widget.dart   # Live commodity ticker
│           ├── metric_card_widget.dart   # KPI card with delta badge
│           ├── preset_selector_widget.dart # Scenario chip bar
│           └── waterfall_chart_widget.dart # Custom EBITDA waterfall chart
├── test/
│   └── widget_test.dart             # Parity unit tests & widget smoke tests
└── pubspec.yaml                     # Dependencies (intl, cupertino_icons)
```

---

## Verification & Parity

All numerical derivations in the Flutter mobile app match the Python decision engine and the independent mathematical oracle (`tests/oracle.py`):

| Test Case | Python Engine | Flutter Dart Engine | Parity Verdict |
| :--- | :--- | :--- | :--- |
| **Base Revenue** | ₹3,374.00 Cr | ₹3,374.00 Cr | **Exact match** |
| **Base Material Spend** | ₹1,223.00 Cr | ₹1,223.00 Cr | **Exact match** |
| **Base Ocean Freight** | ₹25.00 Cr | ₹25.00 Cr | **Exact match** |
| **Baseline EBITDA** | ₹297.70 Cr | ₹297.70 Cr | **Exact match** |
| **Baseline PAT** | ₹37.60 Cr | ₹37.60 Cr | **Exact match** |
| **10% Material Shock** | ₹122.30 Cr delta | ₹122.30 Cr delta | **Exact match** |
| **50% OEM Recovery** | ₹61.15 Cr recovery | ₹61.15 Cr recovery | **Exact match** |
| **Post-Shock EBITDA** | ₹236.55 Cr | ₹236.55 Cr | **Exact match** |
| **Action Rankings** | 10 Actions Ranked | 10 Actions Ranked | **Exact match** |
| **0-1 Knapsack Solver** | Optimal Bundle $\le$ Budget | Optimal Bundle $\le$ Budget | **Exact match** |
