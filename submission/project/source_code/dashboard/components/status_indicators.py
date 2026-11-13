"""PressureIQ Status and Reliability Badges.

Renders HTML and Streamlit status pills for PASS/WARNING/FAIL and reliability tiers.
"""

from __future__ import annotations
import streamlit as st


def render_reliability_badge(level: str) -> str:
    """Return HTML pill for reliability levels."""
    lvl = str(level).strip().capitalize()
    if lvl == "High":
        return '<span class="piq-badge piq-badge-pass">High Reliability</span>'
    elif lvl == "Medium":
        return '<span class="piq-badge piq-badge-warn">Medium Reliability</span>'
    elif lvl == "Low":
        return '<span class="piq-badge piq-badge-warn" style="color:#9CA3AF;border-color:#4B5563;">Low Reliability</span>'
    else:
        return '<span class="piq-badge piq-badge-fail">Provisional</span>'


def render_scorecard_badge(result: str) -> str:
    """Return HTML pill for scorecard results."""
    res = str(result).strip().upper()
    if "PASS" in res:
        return '<span class="piq-badge piq-badge-pass">PASS</span>'
    elif "WARN" in res:
        return '<span class="piq-badge piq-badge-warn">WARNING</span>'
    else:
        return '<span class="piq-badge piq-badge-fail">FAIL</span>'


def render_validation_banner(health_summary: dict) -> None:
    """Render prominent banner if critical validation check failed or all pass."""
    if not health_summary.get("is_fully_validated", False):
        st.error(
            "⚠️ **CRITICAL VALIDATION ALERT:** One or more Phase 9 robustness dimensions failed. "
            "Ratings below are subject to experimental review and must not be treated as fully validated."
        )
        for fail in health_summary.get("critical_failures", []):
            st.caption(f"• Failed check: {fail}")

