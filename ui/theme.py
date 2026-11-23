"""
UI Theme Tokens for Rane (Madras) MMD Decision Engine
Team 11.59 · Xovate'26
"""

# Brand & Core Palette
COLOR_BRAND_PRIMARY = "#1E3A8A"      # Deep Navy Blue
COLOR_BRAND_SECONDARY = "#0284C7"    # Sky Blue Accent
COLOR_BRAND_DARK = "#0F172A"         # Slate 900
COLOR_BG_MAIN = "#FFFFFF"            # Clean White
COLOR_BG_CARD = "#F8FAFC"            # Slate 50
COLOR_BG_HOVER = "#F1F5F9"           # Slate 100
COLOR_BORDER = "#E2E8F0"             # Slate 200

# Status & Alert Palette (STRICT USAGE)
COLOR_STATUS_GREEN = "#16A34A"       # Safe / Covered (> Effective LT + SS)
COLOR_STATUS_AMBER = "#D97706"       # Reorder Trigger / Watch (< ROP)
COLOR_STATUS_RED = "#DC2626"         # Stock-out / Critical Danger (< Effective LT)
COLOR_STATUS_NEUTRAL = "#64748B"     # Slate 500

# Scenario Comparison Palette
COLOR_BASELINE = "#94A3B8"          # Neutral Muted Grey
COLOR_ACTIVE = "#1E3A8A"            # Deep Navy (Brand)
COLOR_SAVED_1 = "#8B5CF6"           # Violet
COLOR_SAVED_2 = "#EC4899"           # Pink

# Fixed Material Colors (Consistent across all charts and pages)
MATERIAL_COLORS = {
    "copper": "#B87333",            # Metallic Copper
    "nickel": "#71717A",            # Nickel Grey
    "aluminium": "#2563EB",         # Aluminium Cobalt
    "resin": "#9333EA",             # Phenolic Purple
    "rubber": "#059669",            # Rubber Green
    "steel_hr": "#D97706",          # Hot-rolled Warm Ochre
    "steel_cr": "#334155",          # Cold-rolled Steel Charcoal
    "freight": "#0D9488",           # Ocean Container Teal
}

# Material Display Names
MATERIAL_LABELS = {
    "copper": "Copper Cathode",
    "nickel": "Nickel Metal",
    "aluminium": "Aluminium (LME)",
    "resin": "Phenolic Resin",
    "rubber": "Natural Rubber (RSS-4)",
    "steel_hr": "Steel HR Coil",
    "steel_cr": "Steel CR Coil",
    "freight": "Global 40ft Freight",
}

# Typography & Spacing
FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
FONT_SIZE_HERO = "1.875rem"
FONT_SIZE_TITLE = "1.5rem"
FONT_SIZE_SUBTITLE = "1.125rem"
FONT_SIZE_BODY = "0.875rem"
FONT_SIZE_KPI_VAL = "1.75rem"
FONT_SIZE_KPI_LABEL = "0.75rem"

RADIUS_CARD = "8px"
RADIUS_BADGE = "4px"
RADIUS_BUTTON = "6px"

# Number Format Helpers
def format_money_cr(val: float, prefix: str = "₹ ", suffix: str = " Cr") -> str:
    """Format in Indian Crores with 1 or 2 decimals"""
    if abs(val) >= 1000:
        return f"{prefix}{val:,.1f}{suffix}"
    return f"{prefix}{val:.2f}{suffix}"

def format_pct(val: float, plus_sign: bool = False) -> str:
    """Format percentage with 1 decimal"""
    if plus_sign and val > 0:
        return f"+{val:.1f}%"
    return f"{val:.1f}%"

def format_inr_t(val: float) -> str:
    """Format INR per tonne"""
    return f"₹ {val:,.0f}/t"

def format_usd(val: float) -> str:
    """Format USD value"""
    return f"${val:,.0f}"

def format_days(val: float) -> str:
    """Format days of cover"""
    return f"{val:.1f} days"
