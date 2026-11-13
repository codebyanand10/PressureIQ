"""PressureIQ - Pre- and Post-Delivery Match State Calculator.

Reconstructs cumulative runs, wickets, legal balls, required run rates,
and situation categories immediately before and after each delivery event.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from src.logger import get_logger
from src.match_state.innings_config import InningsConfig
from src.match_state.innings_phase import InningsPhaseConfig, classify_innings_phase

logger = get_logger("PressureIQ.MatchState.StateCalculator")


def calculate_match_states(
    processed_deliveries: pd.DataFrame,
    innings_configs: Dict[Tuple[int, int], InningsConfig],
    phase_config: Optional[InningsPhaseConfig] = None,
) -> pd.DataFrame:
    """Calculate pre- and post-delivery match states for all deliveries.

    Args:
        processed_deliveries: Deliveries pre-processed with legal flags and runs.
        innings_configs: Innings configuration parameters.
        phase_config: Optional phase thresholds.

    Returns:
        DataFrame containing all reconstructed pre- and post-delivery state metrics.
    """
    logger.info("Calculating pre- and post-delivery match states...")
    df = processed_deliveries.copy()

    # 1. Attach innings configuration parameters
    avail_balls_list = []
    avail_overs_list = []
    target_score_list = []
    target_source_list = []
    is_chasing_list = []
    is_super_over_list = []

    for row in df.itertuples():
        key = (row.match_id, row.innings)
        cfg = innings_configs.get(key)
        if cfg is not None:
            avail_balls_list.append(cfg.available_legal_balls)
            avail_overs_list.append(cfg.available_overs)
            target_score_list.append(cfg.target_score if cfg.has_target else np.nan)
            target_source_list.append(cfg.target_source)
            is_chasing_list.append(cfg.is_chasing_innings)
            is_super_over_list.append(cfg.is_super_over)
        else:
            avail_balls_list.append(120)
            avail_overs_list.append(20.0)
            target_score_list.append(np.nan)
            target_source_list.append("UNAVAILABLE")
            is_chasing_list.append(row.innings in [2, 4])
            is_super_over_list.append(row.innings in [3, 4])

    df["available_legal_balls"] = np.array(avail_balls_list, dtype=np.int64)
    df["available_overs"] = np.array(avail_overs_list, dtype=np.float64)
    df["target_score"] = np.array(target_score_list, dtype=np.float64)
    df["target_source"] = target_source_list
    df["is_chasing_innings"] = np.array(is_chasing_list, dtype=bool)
    df["is_super_over"] = np.array(is_super_over_list, dtype=bool)

    # 2. Vectorized cumulative sums within (match_id, innings)
    grp = df.groupby(["match_id", "innings"])

    # Cumulative runs
    df["runs_after"] = grp["delivery_runs"].cumsum()
    df["runs_before"] = df["runs_after"] - df["delivery_runs"]

    # Cumulative wickets
    df["wickets_after"] = grp["wickets_on_delivery"].cumsum()
    df["wickets_before"] = df["wickets_after"] - df["wickets_on_delivery"]

    # Cumulative legal balls
    legal_inc = df["is_legal_delivery"].astype(int)
    df["legal_balls_bowled_after"] = grp[legal_inc.name].cumsum() if legal_inc.name in df else grp.apply(lambda _: legal_inc).reset_index(level=[0, 1], drop=True)
    # Safer vectorized cumsum for legal balls:
    df["_legal_inc"] = legal_inc
    df["legal_balls_bowled_after"] = df.groupby(["match_id", "innings"])["_legal_inc"].cumsum()
    df["legal_balls_bowled_before"] = df["legal_balls_bowled_after"] - df["_legal_inc"]
    df.drop(columns=["_legal_inc"], inplace=True)

    # 3. Overs completed (standard cricket representation: e.g. 5.4 = 5 overs and 4 balls)
    df["overs_completed_before"] = (df["legal_balls_bowled_before"] // 6) + (df["legal_balls_bowled_before"] % 6) / 10.0
    df["overs_completed_after"] = (df["legal_balls_bowled_after"] // 6) + (df["legal_balls_bowled_after"] % 6) / 10.0

    # 4. Legal balls remaining
    df["legal_balls_remaining_before"] = np.maximum(0, df["available_legal_balls"] - df["legal_balls_bowled_before"])
    df["legal_balls_remaining_after"] = np.maximum(0, df["available_legal_balls"] - df["legal_balls_bowled_after"])

    # 5. Runs required (only for chasing innings with a known target)
    has_target = df["target_score"].notna() & df["is_chasing_innings"]
    df["runs_required_before"] = np.where(
        has_target,
        np.maximum(0.0, df["target_score"] - df["runs_before"]),
        np.nan,
    )
    df["runs_required_after"] = np.where(
        has_target,
        np.maximum(0.0, df["target_score"] - df["runs_after"]),
        np.nan,
    )

    # 6. Current run rate (CRR)
    dec_overs_before = df["legal_balls_bowled_before"] / 6.0
    dec_overs_after = df["legal_balls_bowled_after"] / 6.0

    df["current_run_rate_before"] = np.where(
        df["legal_balls_bowled_before"] > 0,
        np.round(df["runs_before"] / dec_overs_before, 3),
        np.nan,
    )
    df["current_run_rate_after"] = np.where(
        df["legal_balls_bowled_after"] > 0,
        np.round(df["runs_after"] / dec_overs_after, 3),
        np.nan,
    )

    # 7. Required run rate (RRR)
    rem_overs_before = df["legal_balls_remaining_before"] / 6.0
    rem_overs_after = df["legal_balls_remaining_after"] / 6.0

    # Before delivery RRR
    df["required_run_rate_before"] = np.where(
        has_target & (df["legal_balls_remaining_before"] > 0),
        np.where(
            df["runs_required_before"] <= 0,
            0.0,
            np.round(df["runs_required_before"] / rem_overs_before, 3),
        ),
        np.nan,
    )

    # After delivery RRR
    df["required_run_rate_after"] = np.where(
        has_target & (df["legal_balls_remaining_after"] > 0),
        np.where(
            df["runs_required_after"] <= 0,
            0.0,
            np.round(df["runs_required_after"] / rem_overs_after, 3),
        ),
        np.nan,
    )

    # 8. Innings progress fraction (0.0 to 1.0)
    denom_balls = np.where(df["available_legal_balls"] > 0, df["available_legal_balls"], 120)
    df["innings_progress_before"] = np.round(df["legal_balls_bowled_before"] / denom_balls, 4)
    df["innings_progress_after"] = np.round(df["legal_balls_bowled_after"] / denom_balls, 4)

    # 9. Innings phase classification
    df["innings_phase_before"] = classify_innings_phase(
        df["legal_balls_bowled_before"],
        df["available_legal_balls"],
        df["is_super_over"],
        phase_config,
    )
    df["innings_phase_after"] = classify_innings_phase(
        df["legal_balls_bowled_after"],
        df["available_legal_balls"],
        df["is_super_over"],
        phase_config,
    )

    # 10. Match situation categorization (Pre-delivery context)
    df["match_situation_category"] = classify_match_situation(df)

    logger.info("Match state calculation completed successfully.")
    return df


def classify_match_situation(df: pd.DataFrame) -> pd.Series:
    """Classify the pre-delivery match situation category."""
    situations = []

    for row in df.itertuples():
        if row.is_super_over:
            situations.append("SUPER_OVER")
            continue

        if not row.is_chasing_innings:
            # 1st Innings situations
            if row.wickets_before >= 7:
                situations.append("TAIL_BATTING")
            elif row.wickets_before >= 4 and row.legal_balls_bowled_before <= 36:
                situations.append("EARLY_COLLAPSE")
            elif row.innings_phase_before == "POWERPLAY":
                situations.append("POWERPLAY_BUILDING")
            elif row.innings_phase_before == "MIDDLE_OVERS":
                situations.append("MIDDLE_CONSOLIDATION")
            else:
                situations.append("DEATH_ACCELERATION")
        else:
            # 2nd Innings chase situations
            if pd.isna(row.runs_required_before) or row.runs_required_before == 0:
                situations.append("TARGET_REACHED")
            elif row.wickets_before >= 9:
                situations.append("LAST_WICKET_STAND")
            elif row.wickets_before >= 7:
                situations.append("BOWLING_DOMINANCE")
            elif pd.notna(row.required_run_rate_before):
                rrr = row.required_run_rate_before
                if rrr > 14.0:
                    situations.append("CHASE_CRITICAL")
                elif rrr > 10.0:
                    situations.append("CHASE_HIGH_PRESSURE")
                elif rrr > 7.5:
                    situations.append("CHASE_MODERATE_PRESSURE")
                else:
                    situations.append("CHASE_COMFORTABLE")
            else:
                situations.append("CHASE_BUILDING")

    return pd.Series(situations, index=df.index)

