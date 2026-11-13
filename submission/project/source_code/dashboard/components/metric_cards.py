"""PressureIQ Reusable Metric Cards Component.

Renders dark-aesthetic KPI tiles with clear typographic hierarchy and responsive styling.
"""

from __future__ import annotations
from typing import Any, List, Optional
import streamlit as st


def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    delta: Optional[str] = None,
    delta_color: str = "normal",  # normal, inverse, off
) -> None:
    """Render a single styled metric tile."""
    delta_html = ""
    if delta:
        color = "#10B981" if "+" in delta else "#EF4444"
        delta_html = f'<span style="font-size: 0.85rem; font-weight: 600; color: {color}; margin-left: 8px;">{delta}</span>'

    st.markdown(
        f"""
        <div class="piq-metric-card">
            <div class="piq-metric-title">{title}</div>
            <div class="piq-metric-value">{value}{delta_html}</div>
            <div class="piq-metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(cards: List[dict]) -> None:
    """Render a row of metric cards evenly spaced across columns."""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            render_metric_card(
                title=card.get("title", ""),
                value=str(card.get("value", "")),
                subtitle=card.get("subtitle", ""),
                delta=card.get("delta"),
            )

