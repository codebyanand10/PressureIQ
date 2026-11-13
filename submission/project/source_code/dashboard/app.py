"""PressureIQ — Interactive Cricket Analytics Dashboard.

Entry point for the Streamlit multi-page application.
Routes seamlessly across all 9 analytical pages.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Define pages for st.navigation
pages = [
    st.Page("pages/1_Overview.py", title="Overview", icon="📊", default=True),
    st.Page("pages/2_Batter_Rankings.py", title="Batter Rankings", icon="🏏"),
    st.Page("pages/3_Bowler_Rankings.py", title="Bowler Rankings", icon="🎯"),
    st.Page("pages/4_Player_Analysis.py", title="Player Analysis", icon="👤"),
    st.Page("pages/5_Player_Comparison.py", title="Player Comparison", icon="⚖️"),
    st.Page("pages/6_Pressure_Analysis.py", title="Pressure Analysis", icon="🔥"),
    st.Page("pages/7_Statistical_Validation.py", title="Statistical Validation", icon="🛡️"),
    st.Page("pages/8_Methodology.py", title="Methodology", icon="📐"),
    st.Page("pages/9_Data_Quality.py", title="Data Quality", icon="🔍"),
]

pg = st.navigation(pages)
pg.run()
