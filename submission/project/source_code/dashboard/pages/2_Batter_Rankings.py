"""PressureIQ Page 2: Batter Rankings Leaderboard.

Comprehensive batting leaderboard featuring interactive sorting, filtering,
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
from dashboard.components.ranking_table import render_batter_ranking_table
from dashboard.components.charts import render_ranking_bar_chart
from dashboard.components.download_buttons import render_export_suite
from dashboard.services.ranking_service import filter_batter_rankings
from dashboard.services.filtering import get_filter_notice
from dashboard.services.data_loader import load_batter_ratings


def main() -> None:
    st.set_page_config(page_title="Batter Rankings | PressureIQ", page_icon="🏏", layout="wide")

    css_path = PROJECT_ROOT / "dashboard" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header(subtitle="Batter Rankings Leaderboard")

    # Filter notice if global filter active
    notice = get_filter_notice()
    if notice:
        st.info(notice)

    full_bat_df = load_batter_ratings()
    total_eligible = len(full_bat_df) if not full_bat_df.empty else 170

    # Interactive Filter Controls
    search_query, top_n, min_balls = render_ranking_filters(
        role="batting",
        total_eligible=total_eligible,
        key_prefix="bat_page",
    )

    # Filtered dataframe
    filtered_df = filter_batter_rankings(
        top_n=top_n,
        search_query=search_query,
        min_balls=min_balls,
    )

    st.markdown(f"### 🏆 Evaluated Batters ({len(filtered_df)} shown of {total_eligible} eligible)")

    # Chart & Table Layout
    tab_chart, tab_table = st.tabs(["📊 Interactive Ranking Chart", "📋 Detailed Data Table"])

    with tab_chart:
        fig_bar = render_ranking_bar_chart(filtered_df, role="batting", top_n=min(20, len(filtered_df)))
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Error whiskers indicate 95% Bayesian confidence intervals ($CI_{95}$ derived from match-level block bootstrap).")

    with tab_table:
        render_batter_ranking_table(filtered_df)

    st.markdown("---")

    # Export Suite
    st.markdown("### 📥 Export Leaderboard")
    export_df = filtered_df[[
        "rank", "player_name", "final_fbpr", "ci_lower_fbpr", "ci_upper_fbpr",
        "bppi", "strike_rate", "batting_average", "boundary_percentage", "dot_ball_percentage",
        "balls_faced", "innings_count", "reliability_level"
    ]].copy() if not filtered_df.empty and "rank" in filtered_df.columns else filtered_df

    render_export_suite(
        df=export_df,
        base_filename=f"PressureIQ_Batter_Rankings_{'Top10' if top_n == 10 else 'Eligible'}",
        sheet_name="Batter_Rankings",
        key_prefix="bat_export",
    )


if __name__ == "__main__":
    main()

