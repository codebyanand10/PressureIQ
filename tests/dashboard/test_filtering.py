"""Tests for session state filters and ranking rule compliance."""

from __future__ import annotations
import pytest
import streamlit as st
from dashboard.services.filtering import (
    init_filter_state,
    reset_filters,
    is_filtered_view,
    get_filter_notice,
)


def test_filter_state_initialization():
    """Verify default filter state initialization."""
    init_filter_state()
    assert st.session_state["filter_competition"] == "All Competitions"
    assert st.session_state["filter_season"] == "All Seasons"
    assert not is_filtered_view()
    assert get_filter_notice() is None


def test_filtered_view_labeling():
    """Verify that filtering by competition flags 'Global player rating - filtered view'."""
    init_filter_state()
    st.session_state["filter_competition"] = "IPL"
    assert is_filtered_view() is True
    notice = get_filter_notice()
    assert notice is not None
    assert "Global Player Rating — Filtered View" in notice

    # Reset
    reset_filters()
    assert is_filtered_view() is False

