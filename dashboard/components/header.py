"""PressureIQ Global Header Component.

Displays unified application title, tagline, coverage period, and validation badge.
"""

from __future__ import annotations
import streamlit as st
from dashboard.utils.constants import APP_NAME, APP_SUBTITLE, APP_DESCRIPTION, DATA_COVERAGE
from dashboard.services.data_validation import get_validation_health_summary
from dashboard.components.status_indicators import render_validation_banner


def render_header(subtitle: str = "") -> None:
    """Render the standard top header banner across dashboard pages."""
    health = get_validation_health_summary()

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 2px;">
                <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em;">
                    🏏 <span class="piq-title-gradient">{APP_NAME}</span>
                </h1>
                <span style="font-size: 0.95rem; color: #9CA3AF; font-weight: 500;">
                    {subtitle or APP_SUBTITLE}
                </span>
            </div>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">
                {APP_DESCRIPTION}
            </p>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        val_badge = (
            '<span class="piq-badge piq-badge-pass" style="font-size: 0.8rem; padding: 4px 10px;">'
            '✓ Phase 9 Validated (10/10)</span>'
            if health.get("is_fully_validated", False)
            else '<span class="piq-badge piq-badge-fail">⚠️ Validation Warning</span>'
        )
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 6px;">
                <div style="margin-bottom: 4px;">{val_badge}</div>
                <div style="font-size: 0.75rem; color: #64748B;">Coverage: {DATA_COVERAGE}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border-color: #1F2937; margin: 12px 0 16px 0;" />', unsafe_allow_html=True)
    render_validation_banner(health)

