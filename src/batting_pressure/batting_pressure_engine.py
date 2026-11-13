"""Master coordinator for the Batting Performance Under Pressure Engine.

Orchestrates:
1. Pressure category aggregation (Very Low, Low, Moderate, High, Extreme).
2. Dedicated high-pressure cohort evaluation (pressure >= 60.0).
3. Baseline comparison differentials against overall and low-pressure baselines.
4. Situational contextual analysis (phase, innings, competition, stage, position, intensity).
5. Batting Pressure Performance Index (BPPI) computation.
6. Sample size and block bootstrap reliability assessment.
7. Evidence-based batter classification.
8. Dynamic narrative explanation generation.
9. Mathematical and domain validation.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional
import pandas as pd

from src.batting_pressure.batting_pressure_config import BattingPressureConfig
from src.batting_pressure.pressure_category_aggregator import aggregate_by_pressure_category
from src.batting_pressure.baseline_comparator import compare_with_baselines
from src.batting_pressure.situational_analyzer import analyze_situational_batting
from src.batting_pressure.bppi_calculator import calculate_bppi
from src.batting_pressure.batting_reliability import assess_batting_reliability
from src.batting_pressure.batter_classifier import classify_batters
from src.batting_pressure.explanation_generator import generate_batter_explanations
from src.batting_pressure.statistical_validation import validate_batting_pressure_datasets

logger = logging.getLogger(__name__)


def calculate_batting_pressure_performance(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    overall_baseline_df: pd.DataFrame,
    low_pressure_baseline_df: pd.DataFrame,
    config: Optional[BattingPressureConfig] = None,
) -> Dict[str, pd.DataFrame]:
    """Execute end-to-end Phase 6 Batting Performance Under Pressure Engine.

    Returns:
        Dictionary containing:
        - batter_pressure_category_metrics
        - batter_high_pressure_performance
        - batter_baseline_comparison
        - batter_situational_performance
        - batter_pressure_reliability
        - batter_pressure_performance_index
        - batter_pressure_explanations
        - validation_checks
    """
    cfg = config or BattingPressureConfig()
    logger.info("Initializing Batting Performance Under Pressure Engine (version: %s)...", cfg.version)

    # 1. Aggregate by Pressure Category
    logger.info("Step 1: Aggregating by pressure categories...")
    cat_metrics_df, hp_performance_df = aggregate_by_pressure_category(
        deliveries_df=deliveries_df,
        player_registry_df=player_registry_df,
        config=cfg,
    )

    # 2. Compare with Baselines
    logger.info("Step 2: Comparing high-pressure metrics with historical baselines...")
    comparison_df = compare_with_baselines(
        high_pressure_df=hp_performance_df,
        overall_baseline_df=overall_baseline_df,
        low_pressure_baseline_df=low_pressure_baseline_df,
        config=cfg,
    )

    # 3. Situational Analysis
    logger.info("Step 3: Analyzing situational performance under pressure...")
    situational_df = analyze_situational_batting(
        deliveries_df=deliveries_df,
        player_registry_df=player_registry_df,
        config=cfg,
    )

    # 4. Calculate BPPI
    logger.info("Step 4: Calculating Batting Pressure Performance Index (BPPI)...")
    bppi_df = calculate_bppi(
        comparison_df=comparison_df,
        config=cfg,
    )

    # 5. Assess Reliability and Bootstrap
    logger.info("Step 5: Assessing reliability and computing bootstrap confidence intervals...")
    hp_deliveries = deliveries_df[deliveries_df["batting_pressure_score"] >= cfg.high_pressure_threshold]
    reliability_df = assess_batting_reliability(
        bppi_df=bppi_df,
        high_pressure_deliveries_df=hp_deliveries,
        config=cfg,
    )

    # 6. Classify Batters
    logger.info("Step 6: Classifying batters by pressure performance evidence...")
    classified_df = classify_batters(
        reliability_df=reliability_df,
        config=cfg,
    )

    # 7. Generate Explanations
    logger.info("Step 7: Generating explainable performance narratives...")
    explanations_df = generate_batter_explanations(
        classified_df=classified_df,
    )

    # 8. Validation Checks
    logger.info("Step 8: Auditing mathematical consistency and constraints...")
    validation_checks = validate_batting_pressure_datasets(
        category_df=cat_metrics_df,
        hp_performance_df=hp_performance_df,
        comparison_df=comparison_df,
        bppi_df=classified_df,
        situational_df=situational_df,
    )

    logger.info("Batting Performance Under Pressure Engine completed successfully.")
    return {
        "batter_pressure_category_metrics": cat_metrics_df,
        "batter_high_pressure_performance": hp_performance_df,
        "batter_baseline_comparison": comparison_df,
        "batter_situational_performance": situational_df,
        "batter_pressure_reliability": reliability_df,
        "batter_pressure_performance_index": classified_df,
        "batter_pressure_explanations": explanations_df,
        "validation_checks": validation_checks,
    }

