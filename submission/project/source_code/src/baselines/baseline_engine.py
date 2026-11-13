"""Master coordinator for the Player Baseline Calculation Engine.

Orchestrates:
1. Player registry construction.
2. Batting and bowling overall and low-pressure baseline calculations.
3. Contextual baseline generation (phase, competition, innings, order).
4. Empirical Bayes shrinkage for small-sample mitigation.
5. Baseline reliability assessment and auditing.
6. Validation checks and Parquet export packaging.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple
import pandas as pd

from src.baselines.baseline_config import BaselineConfig
from src.baselines.player_registry import build_player_registry
from src.baselines.batting_baseline import calculate_batting_baselines
from src.baselines.bowling_baseline import calculate_bowling_baselines
from src.baselines.contextual_baseline import calculate_contextual_baselines
from src.baselines.baseline_shrinkage import apply_baseline_shrinkage
from src.baselines.baseline_reliability import assess_baseline_reliability
from src.baselines.baseline_validation import validate_baselines

logger = logging.getLogger(__name__)


def calculate_all_player_baselines(
    deliveries_df: pd.DataFrame,
    mapping_df: pd.DataFrame,
    playing_eleven_df: pd.DataFrame,
    matches_df: pd.DataFrame,
    config: Optional[BaselineConfig] = None,
) -> Dict[str, pd.DataFrame]:
    """Execute the end-to-end player baseline generation pipeline.

    Returns:
        Dictionary of baseline DataFrames:
        - player_registry
        - batting_overall_baseline
        - batting_low_pressure_baseline
        - bowling_overall_baseline
        - bowling_low_pressure_baseline
        - batting_contextual_baseline
        - bowling_contextual_baseline
        - baseline_reliability
        - baseline_metadata
        - shrinkage_report
    """
    cfg = config or BaselineConfig()
    logger.info("Initializing Player Baseline Calculation Engine (version: %s)...", cfg.version)

    # 1. Build Player Registry
    logger.info("Step 1: Building player registry...")
    registry_df = build_player_registry(
        mapping_df=mapping_df,
        playing_eleven_df=playing_eleven_df,
        matches_df=matches_df,
        deliveries_df=deliveries_df,
    )

    # 2. Compute Batting Baselines (Overall & Low Pressure)
    logger.info("Step 2: Calculating batting baselines...")
    bat_overall_raw, bat_lp_raw = calculate_batting_baselines(
        deliveries_df=deliveries_df,
        player_registry_df=registry_df,
        config=cfg,
    )

    # 3. Compute Bowling Baselines (Overall & Low Pressure)
    logger.info("Step 3: Calculating bowling baselines...")
    bowl_overall_raw, bowl_lp_raw = calculate_bowling_baselines(
        deliveries_df=deliveries_df,
        player_registry_df=registry_df,
        config=cfg,
    )

    # 4. Contextual Baselines
    logger.info("Step 4: Calculating contextual baselines...")
    bat_context_df, bowl_context_df = calculate_contextual_baselines(
        deliveries_df=deliveries_df,
        player_registry_df=registry_df,
        config=cfg,
    )

    # 5. Apply Statistical Shrinkage
    logger.info("Step 5: Applying Empirical Bayes shrinkage...")
    bat_overall_shrunk, bowl_overall_shrunk, shrinkage_report_df = apply_baseline_shrinkage(
        batting_df=bat_overall_raw,
        bowling_df=bowl_overall_raw,
        config=cfg,
    )

    # Also shrink low pressure baselines
    bat_lp_shrunk, bowl_lp_shrunk, _ = apply_baseline_shrinkage(
        batting_df=bat_lp_raw,
        bowling_df=bowl_lp_raw,
        config=cfg,
    )

    # 6. Baseline Reliability Assessment
    logger.info("Step 6: Assessing baseline reliability...")
    bat_overall_final, bowl_overall_final, combined_rel_df = assess_baseline_reliability(
        batting_df=bat_overall_shrunk,
        bowling_df=bowl_overall_shrunk,
        config=cfg,
    )

    bat_lp_final, bowl_lp_final, _ = assess_baseline_reliability(
        batting_df=bat_lp_shrunk,
        bowling_df=bowl_lp_shrunk,
        config=cfg,
    )

    # 7. Construct Metadata Dataset
    logger.info("Step 7: Packaging baseline metadata...")
    meta_rows = [
        {"table_name": "player_registry", "record_count": len(registry_df), "description": "Master player registry and participation volume"},
        {"table_name": "batting_overall_baseline", "record_count": len(bat_overall_final), "description": "General historical batting baseline across all deliveries"},
        {"table_name": "batting_low_pressure_baseline", "record_count": len(bat_lp_final), "description": "Reference batting baseline under low pressure (pressure <= 39.99)"},
        {"table_name": "bowling_overall_baseline", "record_count": len(bowl_overall_final), "description": "General historical bowling baseline across all deliveries"},
        {"table_name": "bowling_low_pressure_baseline", "record_count": len(bowl_lp_final), "description": "Reference bowling baseline under low pressure (pressure <= 39.99)"},
        {"table_name": "batting_contextual_baseline", "record_count": len(bat_context_df), "description": "Batting performance partitioned by phase, competition, and innings"},
        {"table_name": "bowling_contextual_baseline", "record_count": len(bowl_context_df), "description": "Bowling performance partitioned by phase, competition, and innings"},
        {"table_name": "baseline_reliability", "record_count": len(combined_rel_df), "description": "Audited player reliability classification and quality flags"},
    ]
    metadata_df = pd.DataFrame(meta_rows)

    # 8. Validation
    logger.info("Step 8: Validating baseline integrity...")
    validation_checks = validate_baselines(
        batting_overall_df=bat_overall_final,
        bowling_overall_df=bowl_overall_final,
        batting_lp_df=bat_lp_final,
        bowling_lp_df=bowl_lp_final,
    )

    logger.info("Player Baseline Engine execution complete.")
    return {
        "player_registry": registry_df,
        "batting_overall_baseline": bat_overall_final,
        "batting_low_pressure_baseline": bat_lp_final,
        "bowling_overall_baseline": bowl_overall_final,
        "bowling_low_pressure_baseline": bowl_lp_final,
        "batting_contextual_baseline": bat_context_df,
        "bowling_contextual_baseline": bowl_context_df,
        "baseline_reliability": combined_rel_df,
        "baseline_metadata": metadata_df,
        "shrinkage_report": shrinkage_report_df,
        "validation_checks": validation_checks,
    }

