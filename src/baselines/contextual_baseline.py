"""Contextual player baseline calculation module.

Calculates context-specific performance across:
- Innings phases (powerplay, middle, death)
- Competition types (IPL, T20I, Domestic)
- Innings numbers (1st innings, 2nd innings)
- Batting order groups (top, middle, lower)
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import pandas as pd

from src.baselines.baseline_config import BaselineConfig
from src.baselines.batting_metrics import compute_batting_metrics
from src.baselines.bowling_metrics import compute_bowling_metrics

logger = logging.getLogger(__name__)


def map_batting_position_group(order: pd.Series, config: BaselineConfig) -> pd.Series:
    """Map numeric batting order (1-11) to position group."""
    conditions = [
        order.isin(config.top_order_positions),
        order.isin(config.middle_order_positions),
        order.isin(config.lower_order_positions),
    ]
    choices = ["top_order", "middle_order", "lower_order"]
    return pd.Series(pd.Categorical(pd.Series(np_select := pd.Series(conditions[0]).map({True: choices[0]}).fillna(
        pd.Series(conditions[1]).map({True: choices[1]}).fillna(
            pd.Series(conditions[2]).map({True: choices[2]}).fillna("unassigned")
        )
    ))), index=order.index)


def calculate_contextual_baselines(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate contextual baselines for batting and bowling.

    Returns:
        Tuple of (batting_contextual_df, bowling_contextual_df).
    """
    cfg = config or BaselineConfig()
    logger.info("Computing contextual player baselines...")

    df = deliveries_df.copy()
    registry_map = player_registry_df.set_index("player_id")["player_name"].to_dict()

    # Add context columns
    df["striker_id"] = df["striker_id"].astype(str)
    df["bowler_id"] = df["bowler_id"].astype(str)

    # 1. Innings number string
    df["innings_context"] = df["innings"].map({1: "1st_innings", 2: "2nd_innings"}).fillna("other")

    # 2. Position group for batting
    if "batting_order" in df.columns:
        b_order = df["batting_order"].fillna(0).astype(int)
        df["position_group"] = pd.Series(
            pd.Series(b_order.isin(cfg.top_order_positions)).map({True: "top_order"}).fillna(
                pd.Series(b_order.isin(cfg.middle_order_positions)).map({True: "middle_order"}).fillna(
                    pd.Series(b_order.isin(cfg.lower_order_positions)).map({True: "lower_order"}).fillna("unassigned")
                )
            )
        )
    else:
        df["position_group"] = "unassigned"

    # Batting Context Aggregations
    bat_contexts = []

    # A. Innings Phase
    phase_bat = compute_batting_metrics(df, group_col=["striker_id", "innings_phase_before"])
    phase_bat = phase_bat.rename(columns={"striker_id": "player_id", "innings_phase_before": "context_value"})
    phase_bat["context_type"] = "innings_phase"
    bat_contexts.append(phase_bat)

    # B. Competition Type
    if "competition_type" in df.columns:
        comp_bat = compute_batting_metrics(df, group_col=["striker_id", "competition_type"])
        comp_bat = comp_bat.rename(columns={"striker_id": "player_id", "competition_type": "context_value"})
        comp_bat["context_type"] = "competition_type"
        bat_contexts.append(comp_bat)

    # C. Innings Number
    inn_bat = compute_batting_metrics(df[df["innings"].isin([1, 2])], group_col=["striker_id", "innings_context"])
    inn_bat = inn_bat.rename(columns={"striker_id": "player_id", "innings_context": "context_value"})
    inn_bat["context_type"] = "innings_number"
    bat_contexts.append(inn_bat)

    # D. Batting Position Group
    pos_df = df[df["position_group"] != "unassigned"]
    if len(pos_df) > 0:
        pos_bat = compute_batting_metrics(pos_df, group_col=["striker_id", "position_group"])
        pos_bat = pos_bat.rename(columns={"striker_id": "player_id", "position_group": "context_value"})
        pos_bat["context_type"] = "batting_position_group"
        bat_contexts.append(pos_bat)

    batting_context_df = pd.concat(bat_contexts, ignore_index=True)
    batting_context_df["player_name"] = batting_context_df["player_id"].map(registry_map).fillna("Unknown")
    batting_context_df["sample_deliveries"] = batting_context_df["total_balls_faced"]
    batting_context_df["sample_innings"] = batting_context_df["innings_batted"]
    batting_context_df["sample_matches"] = batting_context_df["matches_batted"]
    batting_context_df["baseline_version"] = cfg.version

    # Bowling Context Aggregations
    bowl_contexts = []

    # A. Innings Phase
    phase_bowl = compute_bowling_metrics(df, group_col=["bowler_id", "innings_phase_before"])
    phase_bowl = phase_bowl.rename(columns={"bowler_id": "player_id", "innings_phase_before": "context_value"})
    phase_bowl["context_type"] = "innings_phase"
    bowl_contexts.append(phase_bowl)

    # B. Competition Type
    if "competition_type" in df.columns:
        comp_bowl = compute_bowling_metrics(df, group_col=["bowler_id", "competition_type"])
        comp_bowl = comp_bowl.rename(columns={"bowler_id": "player_id", "competition_type": "context_value"})
        comp_bowl["context_type"] = "competition_type"
        bowl_contexts.append(comp_bowl)

    # C. Innings Number
    inn_bowl = compute_bowling_metrics(df[df["innings"].isin([1, 2])], group_col=["bowler_id", "innings_context"])
    inn_bowl = inn_bowl.rename(columns={"bowler_id": "player_id", "innings_context": "context_value"})
    inn_bowl["context_type"] = "innings_number"
    bowl_contexts.append(inn_bowl)

    bowling_context_df = pd.concat(bowl_contexts, ignore_index=True)
    bowling_context_df["player_name"] = bowling_context_df["player_id"].map(registry_map).fillna("Unknown")
    bowling_context_df["sample_deliveries"] = bowling_context_df["legal_balls_bowled"]
    bowling_context_df["sample_innings"] = bowling_context_df["innings_bowled"]
    bowling_context_df["sample_matches"] = bowling_context_df["matches_bowled"]
    bowling_context_df["baseline_version"] = cfg.version

    logger.info(
        "Contextual baselines generated: %d batting contexts, %d bowling contexts.",
        len(batting_context_df),
        len(bowling_context_df),
    )

    return batting_context_df, bowling_context_df

