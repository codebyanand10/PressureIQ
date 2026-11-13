"""PressureIQ Dashboard Constants and Theme Definitions.

Defines global UI constants, color palettes, typography, and page metadata.
"""

from __future__ import annotations

# Application Metadata
APP_NAME = "PressureIQ"
APP_TAGLINE = "Beyond Performance. Under Pressure."
APP_SUBTITLE = "Cricket Pressure Performance Analytics"
APP_DESCRIPTION = (
    "Discover which players perform best when the match situation demands the most."
)
APP_VERSION = "1.0.0"
DATA_COVERAGE = "IPL & T20 Internationals (2022 – Present)"

# Color Palette (Dark Sports Analytics Aesthetic)
COLOR_BG_DARK = "#0B0F19"
COLOR_CARD_BG = "#111827"
COLOR_CARD_BORDER = "#1F2937"
COLOR_ACCENT_BLUE = "#38BDF8"       # Electric Blue
COLOR_ACCENT_PURPLE = "#8B5CF6"     # Deep Purple
COLOR_ACCENT_INDIGO = "#6366F1"
COLOR_SUCCESS_GREEN = "#10B981"     # PASS / High Performance
COLOR_WARNING_AMBER = "#F59E0B"     # WARNING / Medium Performance
COLOR_DANGER_RED = "#EF4444"        # FAIL / Low Performance
COLOR_TEXT_PRIMARY = "#F9FAFB"
COLOR_TEXT_SECONDARY = "#9CA3AF"
COLOR_TEXT_MUTED = "#6B7280"

# Pressure Tier Colors (Phases 4-6-7)
PRESSURE_TIER_COLORS = {
    "Very Low": "#3B82F6",    # Blue [0 - 20]
    "Low": "#06B6D4",         # Cyan [20 - 40]
    "Moderate": "#F59E0B",    # Amber [40 - 60]
    "High": "#F97316",        # Orange [60 - 80]
    "Extreme": "#EF4444",     # Crimson [80 - 100]
}

# Reliability Badges
RELIABILITY_COLORS = {
    "High": COLOR_SUCCESS_GREEN,
    "Medium": COLOR_WARNING_AMBER,
    "Low": "#9CA3AF",
    "Provisional": COLOR_DANGER_RED,
}

# Plotly Theme Defaults
PLOTLY_LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(17,24,39,0.7)",
    "font": {"color": COLOR_TEXT_PRIMARY, "family": "Inter, system-ui, sans-serif"},
    "margin": {"l": 40, "r": 30, "t": 50, "b": 40},
    "xaxis": {
        "gridcolor": "#1F2937",
        "zerolinecolor": "#374151",
        "tickfont": {"color": COLOR_TEXT_SECONDARY},
    },
    "yaxis": {
        "gridcolor": "#1F2937",
        "zerolinecolor": "#374151",
        "tickfont": {"color": COLOR_TEXT_SECONDARY},
    },
}

# Navigation Pages
PAGES = [
    {"path": "pages/1_Overview.py", "title": "Overview", "icon": "📊"},
    {"path": "pages/2_Batter_Rankings.py", "title": "Batter Rankings", "icon": "🏏"},
    {"path": "pages/3_Bowler_Rankings.py", "title": "Bowler Rankings", "icon": "🎯"},
    {"path": "pages/4_Player_Analysis.py", "title": "Player Analysis", "icon": "👤"},
    {"path": "pages/5_Player_Comparison.py", "title": "Player Comparison", "icon": "⚖️"},
    {"path": "pages/6_Pressure_Analysis.py", "title": "Pressure Analysis", "icon": "🔥"},
    {"path": "pages/7_Statistical_Validation.py", "title": "Statistical Validation", "icon": "🛡️"},
    {"path": "pages/8_Methodology.py", "title": "Methodology", "icon": "📐"},
    {"path": "pages/9_Data_Quality.py", "title": "Data Quality", "icon": "🔍"},
]

