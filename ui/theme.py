"""
UI Theme Tokens & Formatters (Section 5b / T9)
Team 11:59 · Xovate'26 · Rane (Madras) MMD Decision Engine

Industrial Palette:
- Ink: #1D262C (mill-scale graphite text)
- Canvas: #EEF1F2 (galvanised grey)
- Panel: #F8F9F9 (soft panel background)
- Rule: #C9D1D5 (boundary rules & borders)
- Steel blue: #2F5D7C (primary active brand)
- Base comparison: #8E9AA2 (comparison grey)
- Andon green: #1E8A4C | amber: #C98A0B | red: #C2382B
- Fixed material palette: Copper #B4602E, Nickel #6E7F73, Aluminium #8FA3B5,
  Resin #7A5C99, Rubber #3D6B4F, Steel HR #44515C, Steel CR #6C8CA6, Freight #A3472A.
"""

# Core Industrial Palette
COLOR_INK = "#1D262C"
COLOR_CANVAS = "#EEF1F2"
COLOR_PANEL = "#F8F9F9"
COLOR_RULE = "#C9D1D5"

COLOR_BRAND_PRIMARY = "#2F5D7C"      # Steel Blue (Active)
COLOR_BRAND_SECONDARY = "#4A7C9D"    # Slate Blue
COLOR_BRAND_DARK = "#1D262C"         # Ink Graphite
COLOR_BG_MAIN = "#EEF1F2"            # Canvas
COLOR_BG_CARD = "#F8F9F9"            # Panel
COLOR_BG_HOVER = "#E5E9EB"           # Muted Hover
COLOR_BORDER = "#C9D1D5"             # Cold Rule

# Status & Andon Palette (WCAG AA Checked)
COLOR_STATUS_GREEN = "#1E8A4C"       # Verified Safe / On Schedule
COLOR_STATUS_AMBER = "#C98A0B"       # Warning / Reorder Watch
COLOR_STATUS_RED = "#C2382B"         # Critical Danger / Stock-out
COLOR_STATUS_NEUTRAL = "#8E9AA2"     # Base Comparison

# Scenario Comparison Palette
COLOR_BASELINE = "#8E9AA2"          # Base Comparison Grey
COLOR_ACTIVE = "#2F5D7C"            # Active Scenario Steel Blue
COLOR_SAVED_1 = "#6E7F73"           # Sage
COLOR_SAVED_2 = "#7A5C99"           # Heather Purple

# Fixed Material Colors (Section 5b)
MATERIAL_COLORS = {
    "copper": "#B4602E",            # Copper Cathode
    "nickel": "#6E7F73",            # Precision Nickel
    "aluminium": "#8FA3B5",         # Aluminium Cobalt
    "resin": "#7A5C99",             # Phenolic Binder
    "rubber": "#3D6B4F",            # Kottayam Natural Rubber
    "steel_hr": "#44515C",          # Hot-rolled Coil
    "steel_cr": "#6C8CA6",          # Cold-rolled Coil
    "freight": "#A3472A",           # Container Freight
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
FONT_FAMILY = "Archivo, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_SIZE_HERO = "1.5rem"
FONT_SIZE_TITLE = "1.25rem"
FONT_SIZE_SUBTITLE = "0.95rem"
FONT_SIZE_BODY = "0.85rem"
FONT_SIZE_KPI_VAL = "1.5rem"
FONT_SIZE_KPI_LABEL = "0.72rem"

RADIUS_CARD = "6px"
RADIUS_BADGE = "4px"
RADIUS_BUTTON = "4px"


# Number Format Helpers (T9: True Minus and Negative-Zero Normalization)
def format_money_cr(val: float, prefix: str = "₹ ", suffix: str = " Cr", show_sign: bool = False) -> str:
    """
    Format in Indian Crores with 1 or 2 decimals.
    T9: Normalizes negative zero and guarantees single true minus sign '−'.
    """
    if abs(val) < 0.005:
        val = 0.0

    num_str = f"{abs(val):,.2f}" if abs(val) < 1000 else f"{abs(val):,.1f}"
    if num_str in ["0.00", "0.0", "-0.00", "-0.0"]:
        num_str = "0.00"
        val = 0.0
    
    if show_sign:
        if val > 0.005:
            return f"+{prefix}{num_str}{suffix}"
        elif val < -0.005:
            return f"−{prefix}{num_str}{suffix}"
        else:
            return f"{prefix}0.0{suffix}"
    else:
        if val < -0.005:
            return f"−{prefix}{num_str}{suffix}"
        return f"{prefix}{num_str}{suffix}"


def format_pct(val: float, plus_sign: bool = False) -> str:
    """Format percentage with 1 decimal and true minus sign."""
    if abs(val) < 0.05:
        val = 0.0
    if plus_sign and val > 0:
        return f"+{val:.1f}%"
    elif val < 0:
        return f"−{abs(val):.1f}%"
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
