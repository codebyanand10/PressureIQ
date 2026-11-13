"""PressureIQ Global Sidebar Navigation & Filter Component.

Provides consistent branding, global filters, and reset capability across pages.
"""

from __future__ import annotations
import streamlit as st
from dashboard.services.filtering import init_filter_state, reset_filters
from dashboard.utils.constants import APP_NAME, APP_TAGLINE


def render_sidebar() -> None:
    """Render global sidebar filters and application branding."""
    init_filter_state()

    with st.sidebar:
        # Branding
        st.markdown(
            f"""
            <div style="padding: 12px 0 8px 0; border-bottom: 1px solid #1F2937; margin-bottom: 16px;">
                <h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; color: #F9FAFB;">
                    🏏 {APP_NAME}
                </h2>
                <div style="font-size: 0.75rem; color: #38BDF8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                    {APP_TAGLINE}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### ⚙️ Global Filters")

        # Competition Filter
        comp = st.selectbox(
            "Competition",
            options=["All Competitions", "IPL", "T20I"],
            key="filter_competition",
            help="Filter candidate views by match tournament environment.",
        )

        # Reliability Level Filter
        rel = st.selectbox(
            "Reliability Threshold",
            options=["All Levels", "High", "Medium"],
            key="filter_reliability",
            help="Filter by minimum Bayesian estimation confidence.",
        )

        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            reset_filters()
            st.rerun()

        st.markdown("---")
        st.caption("SupeRR Selector Season 2 | Round 1")
        st.caption("Phase 10: Interactive Analytics Dashboard")

