"""PressureIQ Leaderboard Table Component.

Renders sortable, interactive ranking tables with reliability badges and confidence intervals.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
import streamlit as st
from dashboard.utils.formatting import format_number, format_pct, format_ci, format_rank, format_overs
from dashboard.components.status_indicators import render_reliability_badge


def render_batter_ranking_table(df: pd.DataFrame, show_top_n: Optional[int] = None) -> None:
    """Render the official batter leaderboard dataframe."""
    if df.empty:
        st.info("No batters matched the active search and filter criteria.")
        return

    table_data = []
    subset = df.head(show_top_n) if show_top_n else df

    for _, r in subset.iterrows():
        sr_diff = r.get("strike_rate_difference", 0.0)
        table_data.append({
            "Rank": format_rank(r.get("rank")),
            "Player": r.get("player_name", "Unknown"),
            "FBPR (Rating)": format_number(r.get("final_fbpr"), 2),
            "95% CI": format_ci(r.get("ci_lower_fbpr"), r.get("ci_upper_fbpr")),
            "BPPI": format_number(r.get("bppi"), 1),
            "Strike Rate": format_number(r.get("strike_rate"), 1),
            "SR Delta": f"{'+' if sr_diff > 0 else ''}{sr_diff:.1f}",
            "Boundary %": format_pct(r.get("boundary_percentage", r.get("boundary_pct"))),
            "Dot %": format_pct(r.get("dot_ball_percentage", r.get("dot_ball_pct"))),
            "Balls": int(r.get("balls_faced", 0)),
            "Innings": int(r.get("innings_count", 0)),
            "Reliability": r.get("reliability_level", "Medium"),
        })

    display_df = pd.DataFrame(table_data)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Player": st.column_config.TextColumn("Player", width="medium"),
            "FBPR (Rating)": st.column_config.TextColumn("FBPR", width="small"),
            "95% CI": st.column_config.TextColumn("95% CI", width="medium"),
            "Strike Rate": st.column_config.TextColumn("HP Strike Rate", width="small"),
            "SR Delta": st.column_config.TextColumn("SR vs Base", width="small"),
            "Reliability": st.column_config.TextColumn("Reliability", width="small"),
        },
    )


def render_bowler_ranking_table(df: pd.DataFrame, show_top_n: Optional[int] = None) -> None:
    """Render the official bowler leaderboard dataframe."""
    if df.empty:
        st.info("No bowlers matched the active search and filter criteria.")
        return

    table_data = []
    subset = df.head(show_top_n) if show_top_n else df

    for _, r in subset.iterrows():
        econ_diff = r.get("economy_difference", 0.0)
        table_data.append({
            "Rank": format_rank(r.get("rank")),
            "Player": r.get("player_name", "Unknown"),
            "FBOR (Rating)": format_number(r.get("final_fbor"), 2),
            "95% CI": format_ci(r.get("ci_lower_fbor"), r.get("ci_upper_fbor")),
            "BPPI-B": format_number(r.get("bppi_b"), 1),
            "Economy": format_number(r.get("economy_rate"), 2),
            "Econ Delta": f"{'+' if econ_diff > 0 else ''}{econ_diff:.2f}",
            "Wickets": int(r.get("wickets_credited", 0)),
            "Dot %": format_pct(r.get("dot_ball_percentage", r.get("dot_ball_pct"))),
            "Overs": format_overs(r.get("legal_balls_bowled")),
            "Role": r.get("bowling_role", "All-Round"),
            "Reliability": r.get("reliability_level", "Medium"),
        })

    display_df = pd.DataFrame(table_data)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Player": st.column_config.TextColumn("Player", width="medium"),
            "FBOR (Rating)": st.column_config.TextColumn("FBOR", width="small"),
            "95% CI": st.column_config.TextColumn("95% CI", width="medium"),
            "Economy": st.column_config.TextColumn("HP Economy", width="small"),
            "Econ Delta": st.column_config.TextColumn("Econ vs Base", width="small"),
            "Role": st.column_config.TextColumn("Role", width="small"),
            "Reliability": st.column_config.TextColumn("Reliability", width="small"),
        },
    )

