"""PressureIQ - Streamlit Dashboard Entry Point.

Phase 0: Minimal application startup verification.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config
from src.logger import get_logger

logger = get_logger("PressureIQ.Dashboard")


def main() -> None:
    """Render minimal Phase 0 application dashboard."""
    st.set_page_config(
        page_title="PressureIQ - Cricket Pressure Analytics",
        page_icon="🏏",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    logger.info("Rendering dashboard Phase 0 startup view")

    st.title("🏏 PressureIQ")
    st.subheader("AI-Powered Cricket Pressure Performance Analytics and Player Ranking System")
    st.caption("SupeRR Selector Season 2 — Round 1 | Phase 0")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
            ### System Overview
            **PressureIQ** is an advanced cricket analytical framework designed to quantitatively measure,
            evaluate, and rank batting and bowling performances under high-pressure match situations.
            
            Using granular ball-by-ball data and match-context modeling, PressureIQ distinguishes players
            who consistently rise to the occasion from those whose performance dips when the game is on the line.
            """
        )

        st.info("ℹ️ **Current Status:** Development Environment Initialized (Phase 0 Complete)")
        st.success("🎯 **Next Milestone:** Phase 1 — Dataset Exploration & Schema Inspection")

    with col2:
        st.markdown("### Environment Info")
        st.write(f"**Version:** `{config.version}`")
        st.write(f"**Environment:** `{config.environment}`")
        st.write(f"**Data Directory:** `{config.data_raw_dir.name}/`")
        st.write(f"**Logging Level:** `{config.log_level}`")

    st.divider()
    st.markdown(
        """
        > *Note: Analytics engines, dynamic pressure indices, and ranking models will be activated in upcoming phases.*
        """
    )


if __name__ == "__main__":
    main()

