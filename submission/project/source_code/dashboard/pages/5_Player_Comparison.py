"""PressureIQ Page 5: Multi-Player Head-to-Head Comparison.

Side-by-side comparison of 2 to 4 players (Batters vs Batters or Bowlers vs Bowlers),
featuring normalized multi-axis radar charts, grouped bars, and CSV export.
"""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.header import render_header
from dashboard.components.sidebar import render_sidebar
from dashboard.components.charts import render_player_radar_chart
from dashboard.components.download_buttons import render_csv_download
from dashboard.services.comparison_service import compare_batters, compare_bowlers
from dashboard.services.data_loader import load_batter_ratings, load_bowler_ratings
from dashboard.utils.formatting import format_number, format_pct, format_ci, format_overs, format_rank
from dashboard.utils.constants import PLOTLY_LAYOUT_DEFAULTS, COLOR_TEXT_PRIMARY


def main() -> None:
    st.set_page_config(page_title="Player Comparison | PressureIQ", page_icon="⚖️", layout="wide")

    css_path = PROJECT_ROOT / "dashboard" / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()
    render_header(subtitle="Multi-Player Head-to-Head Comparison")

    # Mode Selector: Batting or Bowling
    role_mode = st.radio(
        "Comparison Discipline",
        options=["Batting Comparison", "Bowling Comparison"],
        horizontal=True,
    )
    is_batting = role_mode == "Batting Comparison"

    ratings_df = load_batter_ratings() if is_batting else load_bowler_ratings()
    if ratings_df.empty:
        st.error("No player records available for comparison.")
        return

    # Select 2 to 4 players
    player_options = dict(zip(ratings_df["player_name"], ratings_df["player_id"]))
    top_candidates = list(player_options.keys())[:2]

    selected_names = st.multiselect(
        "Select 2 to 4 Players to Compare",
        options=list(player_options.keys()),
        default=top_candidates,
        max_selections=4,
        help="Choose between 2 and 4 players to contrast their multi-dimensional clutch profiles.",
    )

    if len(selected_names) < 2:
        st.info("💡 Please select at least two players to generate side-by-side comparisons.")
        return

    selected_ids = [player_options[name] for name in selected_names]

    # Run comparison service
    comp_res = compare_batters(selected_ids) if is_batting else compare_bowlers(selected_ids)
    players_df = comp_res.get("players_df", pd.DataFrame())
    radar_data = comp_res.get("radar_data", [])

    st.markdown('<div class="piq-callout piq-callout-info"><b>Methodological Note:</b> Direct player comparisons should account for differences in batting position, bowling phase, and sample opportunity. Radar charts are scaled to normalized [0, 100] percentiles for visual balance without distorting raw unit differences.</div>', unsafe_allow_html=True)

    # 1. Visual Comparison Row: Radar & Grouped Bars
    col_rad, col_bar = st.columns([1, 1])

    with col_rad:
        st.markdown("### 🕸️ Multi-Dimensional Radar Comparison")
        fig_radar = render_player_radar_chart(
            radar_data,
            title=f"{'Batting' if is_batting else 'Bowling'} Multi-Attribute Comparison",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_bar:
        st.markdown("### 📊 Head-to-Head Rating & Baseline Retention")
        fig_grp = go.Figure()
        metric_col = "final_fbpr" if is_batting else "final_fbor"
        bppi_col = "bppi" if is_batting else "bppi_b"

        fig_grp.add_trace(go.Bar(
            name="Pressure Rating (FBPR/FBOR)",
            x=players_df["player_name"],
            y=players_df[metric_col],
            marker_color="#38BDF8",
            text=[f"{v:.1f}" for v in players_df[metric_col]],
            textposition="auto",
        ))
        fig_grp.add_trace(go.Bar(
            name="Baseline Retention (BPPI)",
            x=players_df["player_name"],
            y=players_df[bppi_col],
            marker_color="#8B5CF6",
            text=[f"{v:.1f}" for v in players_df[bppi_col]],
            textposition="auto",
        ))

        layout = dict(PLOTLY_LAYOUT_DEFAULTS)
        layout.update({
            "barmode": "group",
            "title": dict(text="Rating vs Baseline Retention", font=dict(size=14, color=COLOR_TEXT_PRIMARY)),
            "yaxis": dict(title="Score (0–100)", range=[0, 105], gridcolor="#1F2937"),
            "height": 450,
        })
        fig_grp.update_layout(layout)
        st.plotly_chart(fig_grp, use_container_width=True)

    st.markdown("---")

    # 2. Side-by-Side Detailed Matrix Table
    st.markdown("### 📋 Side-by-Side Comparative Matrix")
    matrix_rows = []

    if is_batting:
        metrics_def = [
            ("Official Rank", lambda r: format_rank(r.get("rank"))),
            ("Final Batter Rating (FBPR)", lambda r: format_number(r.get("final_fbpr"), 2)),
            ("95% Confidence Interval", lambda r: format_ci(r.get("ci_lower_fbpr"), r.get("ci_upper_fbpr"))),
            ("BPPI Resilience Score", lambda r: format_number(r.get("bppi"), 1)),
            ("High-Pressure Strike Rate", lambda r: format_number(r.get("strike_rate"), 1)),
            ("Baseline Strike Rate", lambda r: format_number(r.get("overall_strike_rate"), 1)),
            ("Strike Rate Retention", lambda r: format_pct(r.get("strike_rate_retention"), 1)),
            ("High-Pressure Average", lambda r: format_number(r.get("batting_average"), 1)),
            ("Boundary Run %", lambda r: format_pct(r.get("boundary_percentage", r.get("boundary_pct")))),
            ("Dot Ball %", lambda r: format_pct(r.get("dot_ball_percentage", r.get("dot_ball_pct")))),
            ("Balls Faced", lambda r: str(int(r.get("balls_faced", 0)))),
            ("Innings Count", lambda r: str(int(r.get("innings_count", 0)))),
            ("Reliability Level", lambda r: str(r.get("reliability_level", "Medium"))),
        ]
    else:
        metrics_def = [
            ("Official Rank", lambda r: format_rank(r.get("rank"))),
            ("Final Bowler Rating (FBOR)", lambda r: format_number(r.get("final_fbor"), 2)),
            ("95% Confidence Interval", lambda r: format_ci(r.get("ci_lower_fbor"), r.get("ci_upper_fbor"))),
            ("BPPI-B Resilience Score", lambda r: format_number(r.get("bppi_b"), 1)),
            ("High-Pressure Economy", lambda r: format_number(r.get("economy_rate"), 2)),
            ("Baseline Economy", lambda r: format_number(r.get("overall_economy_rate"), 2)),
            ("Economy Improvement (Delta)", lambda r: f"{'+' if r.get('economy_difference', 0) > 0 else ''}{r.get('economy_difference', 0):.2f}"),
            ("High-Pressure Wickets", lambda r: str(int(r.get("wickets_credited", 0)))),
            ("Overs Bowled", lambda r: format_overs(r.get("legal_balls_bowled"))),
            ("Dot Ball %", lambda r: format_pct(r.get("dot_ball_percentage", r.get("dot_ball_pct")))),
            ("Bowling Strike Rate", lambda r: format_number(r.get("bowling_strike_rate"), 1)),
            ("Bowling Role", lambda r: str(r.get("bowling_role", "All-Round"))),
            ("Reliability Level", lambda r: str(r.get("reliability_level", "Medium"))),
        ]

    for label, extractor in metrics_def:
        row_dict = {"Metric": label}
        for _, p_row in players_df.iterrows():
            row_dict[p_row["player_name"]] = extractor(p_row)
        matrix_rows.append(row_dict)

    matrix_df = pd.DataFrame(matrix_rows)
    st.dataframe(matrix_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Export comparison
    st.markdown("### 📥 Export Comparison Report")
    render_csv_download(
        matrix_df,
        filename=f"PressureIQ_Comparison_{'_vs_'.join([n.replace(' ', '_') for n in selected_names])}.csv",
        label="📥 Download Comparison Matrix (CSV)",
    )


if __name__ == "__main__":
    main()

