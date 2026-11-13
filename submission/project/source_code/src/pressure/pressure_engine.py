"""Master coordinator for the Pressure Detection Engine.

Orchestrates feature extraction, chase and first-innings pressure modeling,
batting and bowling pressure scoring, explainability derivation, reliability assessment,
and zero-leakage validation across delivery events.
"""

from __future__ import annotations

import logging
from typing import Optional
import pandas as pd

from src.pressure.pressure_config import PressureConfig
from src.pressure.batting_pressure import calculate_batting_pressure
from src.pressure.bowling_pressure import calculate_bowling_pressure
from src.pressure.pressure_validator import (
    validate_pressure_scores,
    audit_leakage,
    calculate_pressure_reliability,
)

logger = logging.getLogger(__name__)


def calculate_pressure_scores(
    match_states_df: pd.DataFrame,
    matches_meta_df: Optional[pd.DataFrame] = None,
    config: Optional[PressureConfig] = None,
) -> pd.DataFrame:
    """Coordinate the complete delivery-level pressure detection pipeline.

    Args:
        match_states_df: Reconstructed match state dataset from Phase 3.
        matches_meta_df: Optional matches metadata DataFrame containing knock_out, stage.
        config: Optional PressureConfig instance.

    Returns:
        DataFrame enriched with pressure indicators, scores, levels, reasons, and reliability tags.
    """
    cfg = config or PressureConfig()
    logger.info("Initializing Pressure Detection Engine (version: %s)...", cfg.version)

    df = match_states_df.copy()

    # Merge metadata if needed and not already present
    if "knock_out" not in df.columns or "stage" not in df.columns:
        if matches_meta_df is not None:
            meta_cols = [c for c in ["match_id", "knock_out", "stage"] if c in matches_meta_df.columns]
            df = df.merge(matches_meta_df[meta_cols], on="match_id", how="left")
            logger.info("Merged knock_out and stage metadata from matches metadata.")
        else:
            if "knock_out" not in df.columns:
                df["knock_out"] = 0
            if "stage" not in df.columns:
                df["stage"] = "League"

    # 1. Batting Pressure calculation
    logger.info("Calculating batting pressure scores and indicators for %d deliveries...", len(df))
    df = calculate_batting_pressure(df, config=cfg)

    # 2. Bowling Pressure calculation
    logger.info("Calculating bowling pressure scores and indicators...")
    df = calculate_bowling_pressure(df, config=cfg)

    # 3. Reliability Assessment
    logger.info("Calculating delivery-level pressure reliability...")
    rel_score, rel_level, rel_flags = calculate_pressure_reliability(df)
    df["batting_pressure_reliability"] = rel_level
    df["bowling_pressure_reliability"] = rel_level
    df["pressure_reliability_score"] = rel_score
    df["pressure_reliability_level"] = rel_level
    df["pressure_reliability_flags"] = rel_flags

    # 4. Model Versioning
    df["pressure_model_version"] = cfg.version

    # 5. Validation and Leakage Audit
    logger.info("Running zero-leakage audit and boundary validation...")
    leakage_metrics = audit_leakage(df)
    logger.info("Leakage metrics: %s", leakage_metrics)
    validation_checks = validate_pressure_scores(df)
    logger.info("Pressure score validation checks passed: %s", validation_checks)

    logger.info("Pressure detection pipeline complete for %d deliveries.", len(df))
    return df

