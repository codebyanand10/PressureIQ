"""PressureIQ Page 3: Bowler Rankings Leaderboard.

Comprehensive bowling leaderboard featuring role and bowling style filters,
Plotly confidence interval visualizations, and CSV/Excel exports.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.header import render_header
from dashboard.components.sidebar import render_sidebar
from dashboard.components.filters import render_ranking_filters
from dashboard.components.ranking_table import render_bowler_ranking_table
from dashboard.components.charts import render_ranking_bar_chart
from dashboard.components.download_buttons import render_export_suite
from dashboard.services.ranking_service import filter_bowler_rankings
from dashboard.services.filtering import get_filter_notice
from dashboard.services.data_loader import load_bowler_ratings


def main() -> None:
    st.set_page_config(page_title="Bowler Rankings | PressureIQ", page_icon="🎯", layout="wide")

    css_path = PROJECT_ROOT / "dashboard" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header(subtitle="Bowler Rankings Leaderboard")

    notice = get_filter_notice()
    if notice:
        st.info(notice)

    full_bowl_df = load_bowler_ratings()
    total_eligible = len(full_bowl_df) if not full_bowl_df.empty else 232

    # Role and Style filter row
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        bowling_role = st.selectbox(
            "Bowling Role Phase",
            options=["All Roles", "Death", "Powerplay", "Middle", "All-Round"],
            index=0,
            key="bowl_role_filter",
        )
    with r_col2:
        bowling_style = st.selectbox(
            "Bowling Style",
            options=["All Styles", "Pace", "Spin"],
            index=0,
            key="bowl_style_filter",
        )

    # Search and exposure filter row
    search_query, top_n, min_balls = render_ranking_filters(
        role="bowling",
        total_eligible=total_eligible,
        key_prefix="bowl_page",
    )

    filtered_df = filter_bowler_rankings(
        top_n=top_n,
        search_query=search_query,
        bowling_role=bowling_role,
        bowling_style=bowling_style,
        min_balls=min_balls,
    )

    st.markdown(f"### 🎯 Evaluated Bowlers ({len(filtered_df)} shown of {total_eligible} eligible)")

    tab_chart, tab_table = st.tabs(["📊 Interactive Ranking Chart", "📋 Detailed Data Table"])

    with tab_chart:
        fig_bar = render_ranking_bar_chart(filtered_df, role="bowling", top_n=min(20, len(filtered_df)))
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Error whiskers indicate 95% Bayesian confidence intervals ($CI_{95}$ derived from match-level block bootstrap).")

    with tab_table:
        render_bowler_ranking_table(filtered_df)

    st.markdown("---")

    # Export Suite
    st.markdown("### 📥 Export Leaderboard")
    export_df = filtered_df[[
        "rank", "player_name", "final_fbor", "ci_lower_fbor", "ci_upper_fbor",
        "bppi_b", "economy_rate", "wickets_credited", "dot_ball_percentage",
        "legal_balls_bowled", "bowling_role", "primary_bowling_style", "reliability_level"
    ]].copy() if not filtered_df.empty and "rank" in filtered_df.columns else filtered_df

    render_export_suite(
        df=export_df,
        base_filename=f"PressureIQ_Bowler_Rankings_{'Top10' if top_n == 10 else 'Eligible'}",
        sheet_name="Bowler_Rankings",
        key_prefix="bowl_export",
    )


if __name__ == "__main__":
    main()

