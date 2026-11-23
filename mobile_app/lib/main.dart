import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'ui/theme/app_theme.dart';
import 'ui/viewmodels/decision_engine_viewmodel.dart';
import 'ui/views/control_room_view.dart';
import 'ui/views/simulator_view.dart';
import 'ui/views/profit_chain_view.dart';
import 'ui/views/inventory_view.dart';
import 'ui/views/action_matrix_view.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: AppTheme.surface,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  runApp(const RaneMmdApp());
}

class RaneMmdApp extends StatelessWidget {
  const RaneMmdApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Rane MMD Decision Engine',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const MainNavigationShell(),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;
  final DecisionEngineViewModel _viewModel = DecisionEngineViewModel();

  @override
  void dispose() {
    _viewModel.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _viewModel,
      builder: (context, _) {
        final List<Widget> pages = [
          ControlRoomView(viewModel: _viewModel),
          SimulatorView(viewModel: _viewModel),
          ProfitChainView(viewModel: _viewModel),
          InventoryView(viewModel: _viewModel),
          ActionMatrixView(viewModel: _viewModel),
        ];

        return Scaffold(
          body: IndexedStack(
            index: _currentIndex,
            children: pages,
          ),
          bottomNavigationBar: Container(
            decoration: const BoxDecoration(
              border: Border(
                top: BorderSide(color: AppTheme.border, width: 1),
              ),
            ),
            child: BottomNavigationBar(
              currentIndex: _currentIndex,
              onTap: (index) => setState(() => _currentIndex = index),
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(Icons.dashboard_outlined),
                  activeIcon: Icon(Icons.dashboard),
                  label: 'Control Room',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.tune_outlined),
                  activeIcon: Icon(Icons.tune),
                  label: 'Simulator',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.waterfall_chart),
                  activeIcon: Icon(Icons.waterfall_chart),
                  label: 'Profit Chain',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.inventory_2_outlined),
                  activeIcon: Icon(Icons.inventory_2),
                  label: 'Inventory',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.checklist_rtl_outlined),
                  activeIcon: Icon(Icons.checklist_rtl),
                  label: 'Actions',
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
