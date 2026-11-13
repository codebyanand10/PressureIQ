"""PressureIQ Individual Player Profile Component.

Renders player dossier header, statistical KPI grid, narrative explanation callouts,
and multi-scenario baseline comparisons.
"""

from __future__ import annotations
from typing import Any, Dict
import streamlit as st
from dashboard.utils.formatting import format_number, format_pct, format_ci, format_rank, format_overs
from dashboard.components.metric_cards import render_metric_card
from dashboard.components.status_indicators import render_reliability_badge


def render_player_header(dossier: Dict[str, Any]) -> None:
    """Render player banner with name, rank badge, and core rating."""
    pname = dossier.get("player_name", "Unknown Player")
    pid = dossier.get("player_id", "")
    role = dossier.get("role", "Batter")
    comp = dossier.get("competition_coverage", "IPL & T20I")
    r = dossier.get("rating_record", {})

    rank_str = format_rank(r.get("rank"))
    rating_val = format_number(r.get("final_fbpr" if role == "Batter" else "final_fbor"), 2)
    ci_str = format_ci(
        r.get("ci_lower_fbpr" if role == "Batter" else "ci_lower_fbor"),
        r.get("ci_upper_fbpr" if role == "Batter" else "ci_upper_fbor"),
    )
    rel_badge = render_reliability_badge(r.get("reliability_level", "Medium"))

    st.markdown(
        f"""
        <div class="piq-profile-header">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: #F9FAFB;">
                            {pname}
                        </h2>
                        <span class="piq-badge piq-badge-high" style="font-size: 0.85rem; padding: 4px 12px;">
                            {role} {rank_str}
                        </span>
                        {rel_badge}
                    </div>
                    <div style="font-size: 0.85rem; color: #94A3B8;">
                        ID: <code>{pid}</code> | Coverage: <b>{comp}</b>
                    </div>
                </div>
                <div style="text-align: right; margin-top: 8px;">
                    <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8;">
                        {'Final Batter Rating (FBPR)' if role == 'Batter' else 'Final Bowler Rating (FBOR)'}
                    </div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #38BDF8; line-height: 1.1;">
                        {rating_val}
                    </div>
                    <div style="font-size: 0.8rem; color: #94A3B8;">
                        95% CI: {ci_str}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_batter_stats_grid(r: Dict[str, Any]) -> None:
    """Render 10 key batting metrics in clean 5-column layout."""
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("HP Runs", format_number(r.get("total_runs"), 0), "Runs in high pressure")
    with c2:
        render_metric_card("Balls Faced", format_number(r.get("balls_faced"), 0), "Sample volume")
    with c3:
        render_metric_card("Strike Rate", format_number(r.get("strike_rate"), 1), f"Base: {format_number(r.get('overall_strike_rate'), 1)}")
    with c4:
        render_metric_card("Batting Avg", format_number(r.get("batting_average"), 1), f"Base: {format_number(r.get('overall_batting_average'), 1)}")
    with c5:
        render_metric_card("BPPI Score", format_number(r.get("bppi"), 1), "Resilience Index")

    c6, c7, c8, c9, c10 = st.columns(5)
    with c6:
        render_metric_card("Boundary %", format_pct(r.get("boundary_percentage", r.get("boundary_pct"))), "Runs from 4s & 6s")
    with c7:
        render_metric_card("Dot Ball %", format_pct(r.get("dot_ball_percentage", r.get("dot_ball_pct"))), "Non-scoring balls")
    with c8:
        render_metric_card("HP Matches", format_number(r.get("matches_count"), 0), "Pressure appearances")
    with c9:
        render_metric_card("HP Innings", format_number(r.get("innings_count"), 0), "Innings batted")
    with c10:
        render_metric_card("Dismissals", format_number(r.get("dismissals"), 0), f"BPD: {format_number(r.get('balls_per_dismissal'), 1)}")


def render_bowler_stats_grid(r: Dict[str, Any]) -> None:
    """Render 10 key bowling metrics in clean 5-column layout."""
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("HP Wickets", format_number(r.get("wickets_credited"), 0), "Wickets in high pressure")
    with c2:
        render_metric_card("Overs Bowled", format_overs(r.get("legal_balls_bowled")), f"{int(r.get('legal_balls_bowled', 0))} legal balls")
    with c3:
        render_metric_card("HP Economy", format_number(r.get("economy_rate"), 2), f"Base: {format_number(r.get('overall_economy_rate'), 2)}")
    with c4:
        render_metric_card("Bowling Avg", format_number(r.get("bowling_average"), 1), f"Base: {format_number(r.get('overall_bowling_average'), 1)}")
    with c5:
        render_metric_card("BPPI-B Score", format_number(r.get("bppi_b"), 1), "Resilience Index")

    c6, c7, c8, c9, c10 = st.columns(5)
    with c6:
        render_metric_card("Dot Ball %", format_pct(r.get("dot_ball_percentage", r.get("dot_ball_pct"))), "Dots generated")
    with c7:
        render_metric_card("Runs Conceded", format_number(r.get("runs_conceded"), 0), "High pressure runs")
    with c8:
        render_metric_card("Bowling Strike Rate", format_number(r.get("bowling_strike_rate"), 1), "Balls per wicket")
    with c9:
        render_metric_card("HP Matches", format_number(r.get("matches_bowled", r.get("matches_count")), 0), "Pressure appearances")
    with c10:
        render_metric_card("Primary Role", str(r.get("bowling_role", "All-Round")), str(r.get("primary_bowling_style", "Pace")).capitalize())


def render_player_explanation_callout(r: Dict[str, Any]) -> None:
    """Render official narrative explanation box from Phase 8 ranking explanations."""
    expl = r.get("ranking_explanation", "")
    strengths = r.get("key_strengths", "")
    base_comp = r.get("baseline_comparison", "")
    lims = r.get("ranking_limitations", "")

    st.markdown("### 📝 Algorithmic Evaluation & Explanation")

    if expl:
        st.markdown(f'<div class="piq-callout piq-callout-info"><b>Rating Rationale:</b><br>{expl}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if strengths:
            st.markdown(f"**Key Strengths:**\n{strengths}")
        if base_comp:
            st.markdown(f"**Baseline Comparison:**\n{base_comp}")
    with col2:
        if lims:
            st.markdown(f"**Model Limitations:**\n{lims}")
        rel_sum = r.get("reliability_summary", "")
        if rel_sum:
            st.markdown(f"**Reliability Summary:**\n{rel_sum}")

