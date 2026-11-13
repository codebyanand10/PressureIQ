"""PressureIQ - Match State Reconstruction Engine (Master Coordinator).

Coordinates delivery processing, target resolution, innings configuration,
vectorized pre/post delivery state calculation, innings summary aggregation,
and constraint validation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from src.logger import get_logger
from src.match_state.delivery_processor import process_deliveries
from src.match_state.innings_config import resolve_innings_configs
from src.match_state.innings_phase import InningsPhaseConfig
from src.match_state.state_calculator import calculate_match_states
from src.match_state.state_validator import validate_match_states
from src.match_state.target_calculator import calculate_targets

logger = get_logger("PressureIQ.MatchState.Engine")


def reconstruct_match_states(
    ball_by_ball: pd.DataFrame,
    matches: pd.DataFrame,
    competitions: pd.DataFrame,
    config: Optional[Any] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reconstruct pre-delivery and post-delivery match states for every delivery.

    Args:
        ball_by_ball: Cleaned ball-by-ball delivery records (200,999 deliveries).
        matches: Cleaned matches metadata (883 matches).
        competitions: Cleaned competitions metadata (141 competitions).
        config: Optional configuration instance.

    Returns:
        Tuple of:
        - match_states: Full delivery-level DataFrame with pre/post states (200,999 rows).
        - innings_summary: Aggregated innings summary DataFrame (1 row per match & innings).
        - validation_report: Constraint validation report DataFrame.
    """
    logger.info("=" * 70)
    logger.info("COMMENCING MATCH STATE RECONSTRUCTION ENGINE")
    logger.info("=" * 70)

    # 1. Parse configuration parameters
    default_t20_overs = 20
    default_so_overs = 1
    phase_cfg = InningsPhaseConfig()
    max_wickets = 10
    max_so_wickets = 2

    if config is not None:
        ms_cfg = getattr(config, "match_state_settings", {})
        default_t20_overs = ms_cfg.get("default_t20_overs", 20)
        default_so_overs = ms_cfg.get("default_super_over_overs", 1)
        phase_dict = ms_cfg.get("innings_phases", {})
        phase_cfg = InningsPhaseConfig(
            powerplay_end=phase_dict.get("powerplay_end", 0.30),
            middle_overs_end=phase_dict.get("middle_overs_end", 0.75),
        )
        val_cfg = ms_cfg.get("validation", {})
        max_wickets = val_cfg.get("max_wickets", 10)
        max_so_wickets = val_cfg.get("max_super_over_wickets", 2)

    # 2. Process deliveries chronologically and extract legal/illegal indicators
    processed_bbb = process_deliveries(ball_by_ball)

    # 3. Calculate target scores and sources for all innings
    targets_map = calculate_targets(processed_bbb, matches)

    # 4. Resolve innings configurations
    innings_configs = resolve_innings_configs(
        matches_df=matches,
        targets_map=targets_map,
        default_t20_overs=default_t20_overs,
        default_super_over_overs=default_so_overs,
    )

    # 5. Calculate pre- and post-delivery match states
    states_df = calculate_match_states(
        processed_deliveries=processed_bbb,
        innings_configs=innings_configs,
        phase_config=phase_cfg,
    )

    # Attach match and competition context if not already attached
    if "comp_name" not in states_df.columns:
        m_slice = matches[["match_id", "comp_id"]].drop_duplicates()
        c_slice = competitions[["comp_id", "comp_name", "match_format", "season"]].drop_duplicates()
        mc_slice = m_slice.merge(c_slice, on="comp_id", how="left")
        states_df = states_df.merge(mc_slice, on="match_id", how="left")

    # Rename competition_category / competition_type for standardization
    if "competition_category" in states_df.columns:
        states_df["competition_type"] = states_df["competition_category"]
    elif "competition_category" in competitions.columns:
        states_df = states_df.merge(
            competitions[["comp_id", "competition_category"]], on="comp_id", how="left"
        ).rename(columns={"competition_category": "competition_type"})
    else:
        states_df["competition_type"] = states_df.get("match_format", "T20")

    # 6. Validate match states against cricket domain rules
    validated_states_df, validation_report, val_summary = validate_match_states(
        states_df=states_df,
        max_wickets=max_wickets,
        max_super_over_wickets=max_so_wickets,
    )

    # 7. Generate Innings State Summary
    logger.info("Aggregating innings summary dataset...")
    innings_summary = build_innings_summary(validated_states_df, matches)

    logger.info("=" * 70)
    logger.info(
        f"MATCH STATE RECONSTRUCTION COMPLETED: {len(validated_states_df):,} deliveries, "
        f"{len(innings_summary):,} innings."
    )
    logger.info("=" * 70)

    return validated_states_df, innings_summary, validation_report


def build_innings_summary(
    states_df: pd.DataFrame,
    matches_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate delivery-level states into one row per match and innings.

    Args:
        states_df: Reconstructed delivery states.
        matches_df: Cleaned matches metadata.

    Returns:
        DataFrame containing one row per (match_id, innings).
    """
    records = []
    matches_lookup = matches_df.set_index("match_id").to_dict(orient="index")

    for (m_id, inn), grp in states_df.groupby(["match_id", "innings"], sort=True):
        m_info = matches_lookup.get(m_id, {})
        first_row = grp.iloc[0]
        last_row = grp.iloc[-1]

        batting_team = first_row["batting_team_id"]
        bowling_team = first_row["bowling_team_id"]
        comp_id = first_row.get("comp_id", m_info.get("comp_id", 0))

        innings_runs = int(last_row["runs_after"])
        wickets_lost = int(last_row["wickets_after"])
        legal_balls_bowled = int(last_row["legal_balls_bowled_after"])
        available_legal_balls = int(last_row["available_legal_balls"])
        overs_available = float(last_row["available_overs"])
        target_score = float(last_row["target_score"]) if pd.notna(last_row["target_score"]) else np.nan

        total_deliveries = len(grp)
        legal_deliveries = int(grp["is_legal_delivery"].sum())
        illegal_deliveries = total_deliveries - legal_deliveries

        first_seq = int(first_row["delivery_sequence"])
        last_seq = int(last_row["delivery_sequence"])

        # Determine termination reason
        is_so = inn in [3, 4]
        max_w = 2 if is_so else 10

        if wickets_lost >= max_w:
            term_reason = "ALL_OUT"
            is_completed = True
        elif inn in [2, 4] and not np.isnan(target_score) and innings_runs >= target_score:
            term_reason = "TARGET_CHASED"
            is_completed = True
        elif legal_balls_bowled >= available_legal_balls:
            term_reason = "OVERS_EXHAUSTED"
            is_completed = True
        else:
            m_res = str(m_info.get("result", "")).lower()
            if "abandoned" in m_res or "no result" in m_res:
                term_reason = "RAIN_ABANDONED"
                is_completed = False
            else:
                term_reason = "INNINGS_TERMINATED_EARLY"
                is_completed = True

        val_status = "VALID" if grp["match_state_valid"].all() else "ANOMALIES_DETECTED"

        records.append({
            "match_id": m_id,
            "comp_id": comp_id,
            "innings": inn,
            "batting_team_id": batting_team,
            "bowling_team_id": bowling_team,
            "innings_runs": innings_runs,
            "wickets_lost": wickets_lost,
            "legal_balls_bowled": legal_balls_bowled,
            "available_legal_balls": available_legal_balls,
            "overs_available": overs_available,
            "target_score": target_score,
            "innings_completed": is_completed,
            "innings_termination_reason": term_reason,
            "first_delivery_sequence": first_seq,
            "last_delivery_sequence": last_seq,
            "total_deliveries": total_deliveries,
            "legal_deliveries": legal_deliveries,
            "illegal_deliveries": illegal_deliveries,
            "state_validation_status": val_status,
        })

    summary_df = pd.DataFrame(records)
    return summary_df

