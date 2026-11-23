import 'package:flutter/material.dart';

class AppTheme {
  // Brand Palette
  static const Color background = Color(0xFF0B0F19);
  static const Color surface = Color(0xFF131D2E);
  static const Color surfaceCard = Color(0xFF182235);
  static const Color border = Color(0xFF26334D);

  static const Color primary = Color(0xFF10B981); // Emerald
  static const Color danger = Color(0xFFF43F5E); // Crimson Rose
  static const Color warning = Color(0xFFF59E0B); // Amber
  static const Color info = Color(0xFF38BDF8); // Sky Blue
  static const Color accent = Color(0xFF6366F1); // Indigo

  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: const ColorScheme.dark(
        primary: primary,
        secondary: accent,
        surface: surface,
        error: danger,
        onPrimary: Colors.black,
        onSurface: textPrimary,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.bold,
          letterSpacing: -0.3,
        ),
        iconTheme: IconThemeData(color: textPrimary),
      ),
      cardTheme: CardThemeData(
        color: surfaceCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: border, width: 1),
        ),
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 0),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: primary,
        unselectedItemColor: textMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontSize: 11),
      ),
    );
  }

  // Formatters
  static String formatMoneyCr(double val) {
    if (val.abs() < 1e-4) return '₹0.00 Cr';
    final sign = val < 0 ? '-' : '';
    final absVal = val.abs();
    return '$sign₹${absVal.toStringAsFixed(2)} Cr';
  }

  static String formatDeltaCr(double val) {
    if (val.abs() < 1e-4) return '₹0.00 Cr';
    final sign = val > 0 ? '+' : '-';
    return '$sign₹${val.abs().toStringAsFixed(2)} Cr';
  }

  static String formatPercent(double val) {
    final sign = val > 0 ? '+' : '';
    return '$sign${val.toStringAsFixed(1)}%';
  }
}
