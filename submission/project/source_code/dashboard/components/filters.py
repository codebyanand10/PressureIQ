"""PressureIQ Page-Level Interactive Filter Controls.

Provides search input, top-N selectors, and exposure threshold sliders.
"""

from __future__ import annotations
from typing import Tuple
import streamlit as st


def render_ranking_filters(
    role: str = "batting",
    total_eligible: int = 170,
    key_prefix: str = "rank",
) -> Tuple[str, int, int]:
    """Render search query input, top-N limit, and minimum ball exposure sliders.
    
    Returns:
        (search_query, top_n_limit, min_balls)
    """
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_query = st.text_input(
            "🔍 Search Player Name",
            value="",
            placeholder="Type player name...",
            key=f"{key_prefix}_search",
        )

    with col2:
        top_n_choice = st.selectbox(
            "Leaderboard Scope",
            options=["Top 10", "Top 25", "Top 50", f"All Eligible ({total_eligible})"],
            index=0,
            key=f"{key_prefix}_top_n",
        )
        if "10" in top_n_choice:
            top_n = 10
        elif "25" in top_n_choice:
            top_n = 25
        elif "50" in top_n_choice:
            top_n = 50
        else:
            top_n = total_eligible

    with col3:
        exposure_label = "Min Pressure Balls" if role == "batting" else "Min Legal Balls"
        min_balls = st.number_input(
            exposure_label,
            min_value=0,
            max_value=300,
            value=0,
            step=10,
            key=f"{key_prefix}_min_balls",
        )

    return search_query, top_n, int(min_balls)

