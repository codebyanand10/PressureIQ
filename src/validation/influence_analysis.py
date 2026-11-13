"""Outlier and single-match influence analysis module for Phase 9.

Identifies whether specific high-leverage matches or innings disproportionately
influence the ratings and rankings of top performers, distinguishing genuine
cricketing masterclasses from statistical anomalies.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple
import duckdb
import numpy as np
import pandas as pd

from src.config import config
from src.validation.validation_config import ValidationConfig

logger = logging.getLogger(__name__)


def evaluate_influential_matches(
    ranked_batters: pd.DataFrame,
    ranked_bowlers: pd.DataFrame,
    bat_match_agg: pd.DataFrame,
    bowl_match_agg: pd.DataFrame,
    match_meta: pd.DataFrame,
    config_val: ValidationConfig,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Identify and analyze most influential matches for Top 10 players.

    Returns:
        Tuple of (influence_analysis_df, influence_metrics).
    """
    logger.info("Executing outlier and single-match influence analysis for Top 10 players...")

    # Map match_id to match context (teams, date, stage)
    match_lookup = match_meta.set_index("match_id").to_dict("index") if not match_meta.empty else {}

    top_batters = ranked_batters.head(config_val.top_n)
    top_bowlers = ranked_bowlers.head(config_val.top_n)

    influence_records: List[Dict[str, Any]] = []

    # 1. Batters Influence Analysis
    for _, b_row in top_batters.iterrows():
        pid = b_row["player_id"]
        p_matches = bat_match_agg[bat_match_agg["player_id"] == pid].copy()
        if p_matches.empty:
            continue

        # Sort matches by high pressure runs scored
        p_matches = p_matches.sort_values("hp_runs", ascending=False).reset_index(drop=True)
        top_match = p_matches.iloc[0]
        mid = top_match["match_id"]

        tot_runs = p_matches["hp_runs"].sum()
        tot_balls = p_matches["hp_balls"].sum()

        match_runs = top_match["hp_runs"]
        match_balls = top_match["hp_balls"]
        run_share = match_runs / tot_runs if tot_runs > 0 else 0.0

        # Performance without this single top match
        rem_runs = tot_runs - match_runs
        rem_balls = tot_balls - match_balls
        rem_sr = (rem_runs / rem_balls * 100.0) if rem_balls > 0 else 120.0

        # Estimated rating delta
        sr_diff = b_row["strike_rate"] - rem_sr
        rating_drop = max(0.0, round(float(sr_diff * 0.15), 2))
        sim_rating = round(b_row["final_fbpr"] - rating_drop, 2)

        meta = match_lookup.get(mid, {})
        m_desc = f"{meta.get('home_team', 'Team A')} vs {meta.get('away_team', 'Team B')} ({meta.get('match_date', '2022+')})"

        # Statistical justification assessment
        if len(p_matches) >= 5 and run_share < 0.40:
            justification = "Statistically Robust: Proven multi-match portfolio; no single match dominates rating."
            flag_high_influence = False
        elif run_share >= 0.40:
            justification = "High Single-Match Leverage: One exceptional match accounts for >40% of high-pressure runs."
            flag_high_influence = True
        else:
            justification = "Moderate Leverage: Moderate sample size with clutch ceiling."
            flag_high_influence = False

        influence_records.append({
            "player_id": pid,
            "player_name": b_row["player_name"],
            "role": "batter",
            "official_rank": int(b_row["rank"]),
            "official_rating": float(b_row["final_fbpr"]),
            "most_influential_match_id": mid,
            "match_description": m_desc,
            "match_performance": f"{int(match_runs)} runs off {int(match_balls)} balls (SR: {(match_runs/max(match_balls,1)*100):.1f})",
            "volume_share_in_match": round(run_share * 100.0, 1),
            "rating_without_match": sim_rating,
            "rating_drop": rating_drop,
            "flag_high_influence": flag_high_influence,
            "statistical_interpretation": justification,
        })

    # 2. Bowlers Influence Analysis
    for _, bw_row in top_bowlers.iterrows():
        pid = bw_row["player_id"]
        p_matches = bowl_match_agg[bowl_match_agg["player_id"] == pid].copy()
        if p_matches.empty:
            continue

        p_matches = p_matches.sort_values("hp_wickets", ascending=False).reset_index(drop=True)
        top_match = p_matches.iloc[0]
        mid = top_match["match_id"]

        tot_wkts = p_matches["hp_wickets"].sum()
        tot_lb = p_matches["hp_legal_balls"].sum()
        tot_runs = p_matches["hp_runs_conceded"].sum()

        m_wkts = top_match["hp_wickets"]
        m_lb = top_match["hp_legal_balls"]
        m_runs = top_match["hp_runs_conceded"]
        wkt_share = m_wkts / tot_wkts if tot_wkts > 0 else 0.0

        rating_drop = min(5.0, round(float(m_wkts * 0.4 + (m_lb / 6.0) * 0.3), 2))
        sim_rating = round(bw_row["final_fbor"] - rating_drop, 2)

        meta = match_lookup.get(mid, {})
        m_desc = f"{meta.get('home_team', 'Team A')} vs {meta.get('away_team', 'Team B')} ({meta.get('match_date', '2022+')})"

        if len(p_matches) >= 5 and wkt_share < 0.45:
            justification = "Statistically Robust: Multi-spell economy and wicket delivery across tournaments."
            flag_high_influence = False
        elif wkt_share >= 0.45:
            justification = "High Single-Match Leverage: Wickets concentrated in a single match."
            flag_high_influence = True
        else:
            justification = "Moderate Leverage: Consistent containment with one marquee spell."
            flag_high_influence = False

        influence_records.append({
            "player_id": pid,
            "player_name": bw_row["player_name"],
            "role": "bowler",
            "official_rank": int(bw_row["rank"]),
            "official_rating": float(bw_row["final_fbor"]),
            "most_influential_match_id": mid,
            "match_description": m_desc,
            "match_performance": f"{int(m_wkts)} wkts, {int(m_runs)} runs off {int(m_lb)} legal balls",
            "volume_share_in_match": round(wkt_share * 100.0, 1),
            "rating_without_match": sim_rating,
            "rating_drop": rating_drop,
            "flag_high_influence": flag_high_influence,
            "statistical_interpretation": justification,
        })

    df_influence = pd.DataFrame(influence_records)
    metrics = {
        "batters_with_high_influence_match": int(df_influence[(df_influence["role"] == "batter") & (df_influence["flag_high_influence"])].shape[0]),
        "bowlers_with_high_influence_match": int(df_influence[(df_influence["role"] == "bowler") & (df_influence["flag_high_influence"])].shape[0]),
    }

    logger.info("Influence analysis complete.")
    return df_influence, metrics

