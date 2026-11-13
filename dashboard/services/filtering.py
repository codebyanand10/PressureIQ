"""PressureIQ Global Filter & Session State Management Service.

Maintains filter states across pages, enforces filter validity rules,
and ensures proper labelling when viewing filtered subsets of global ratings.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import streamlit as st


def init_filter_state() -> None:
    """Initialize default filter state variables in st.session_state."""
    defaults = {
        "filter_competition": "All Competitions",
        "filter_season": "All Seasons",
        "filter_pressure_tier": "All Pressure Tiers",
        "filter_reliability": "All Levels",
        "filter_min_exposure": 0,
        "filter_search_query": "",
        "filter_top_n": 10,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_filters() -> None:
    """Reset all global filters to default states."""
    st.session_state["filter_competition"] = "All Competitions"
    st.session_state["filter_season"] = "All Seasons"
    st.session_state["filter_pressure_tier"] = "All Pressure Tiers"
    st.session_state["filter_reliability"] = "All Levels"
    st.session_state["filter_min_exposure"] = 0
    st.session_state["filter_search_query"] = ""
    st.session_state["filter_top_n"] = 10


def is_filtered_view() -> bool:
    """Check if active filters represent a subset view of global rankings."""
    init_filter_state()
    return (
        st.session_state.get("filter_competition", "All Competitions") != "All Competitions"
        or st.session_state.get("filter_season", "All Seasons") != "All Seasons"
        or st.session_state.get("filter_reliability", "All Levels") != "All Levels"
        or int(st.session_state.get("filter_min_exposure", 0)) > 0
    )


def get_filter_notice() -> Optional[str]:
    """Return compliant warning notice when a filtered view is displayed."""
    if is_filtered_view():
        return (
            "📌 **Global Player Rating — Filtered View:** "
            "Displayed rankings represent candidates matching your filter criteria ordered by their "
            "validated global PressureIQ rating. They do not constitute newly recalculated competition-specific baselines."
        )
    return None

