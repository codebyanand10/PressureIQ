"""Master coordinator for the Bowling Performance Under Pressure Engine.

Orchestrates:
1. Pressure category aggregation (Very Low, Low, Moderate, High, Extreme).
2. Dedicated high-pressure cohort evaluation (pressure >= 60.0).
3. Baseline comparison differentials against overall and low-pressure bowling baselines.
4. Situational contextual analysis (phase, innings, competition, stage, style, intensity).
5. Evidence-based bowling role analysis (Powerplay, Middle, Death, Multi-Phase).
6. Bowling Pressure Performance Index (BPPI-B: 0 to 100) computation.
7. Sample size and block bootstrap reliability assessment.
8. Evidence-based bowler classification.
9. Dynamic narrative explanation generation.
10. Mathematical and domain validation.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional
import pandas as pd

from src.bowling_pressure.bowling_pressure_config import BowlingPressureConfig
from src.bowling_pressure.pressure_category_aggregator import aggregate_by_bowling_pressure_category
from src.bowling_pressure.baseline_comparator import compare_with_bowling_baselines
from src.bowling_pressure.situational_analyzer import analyze_situational_bowling
from src.bowling_pressure.bowler_role_analyzer import analyze_bowler_roles
from src.bowling_pressure.bppi_b_calculator import calculate_bppi_b
from src.bowling_pressure.bowling_reliability import assess_bowling_reliability
from src.bowling_pressure.bowler_classifier import classify_bowlers
from src.bowling_pressure.explanation_generator import generate_bowler_explanations
from src.bowling_pressure.statistical_validation import validate_bowling_pressure_datasets

logger = logging.getLogger(__name__)


def calculate_bowling_pressure_performance(
    deliveries_df: pd.DataFrame,
    player_registry_df: pd.DataFrame,
    overall_baseline_df: pd.DataFrame,
    low_pressure_baseline_df: pd.DataFrame,
    config: Optional[BowlingPressureConfig] = None,
) -> Dict[str, pd.DataFrame]:
    """Execute end-to-end Phase 7 Bowling Performance Under Pressure Engine.

    Returns:
        Dictionary containing:
        - bowler_pressure_category_metrics
        - bowler_high_pressure_performance
        - bowler_baseline_comparison
        - bowler_situational_performance
        - bowler_role_analysis
        - bowler_pressure_reliability
        - bowler_pressure_performance_index
        - bowler_pressure_explanations
        - validation_checks
    """
    cfg = config or BowlingPressureConfig()
    logger.info("Initializing Bowling Performance Under Pressure Engine (version: %s)...", cfg.version)

    # 1. Aggregate by Pressure Category
    logger.info("Step 1: Aggregating bowling metrics across pressure categories...")
    cat_metrics_df, hp_performance_df = aggregate_by_bowling_pressure_category(
        deliveries_df=deliveries_df,
        player_registry_df=player_registry_df,
        config=cfg,
    )

    # 2. Compare with Baselines
    logger.info("Step 2: Comparing high-pressure bowling with historical baselines...")
    comparison_df = compare_with_bowling_baselines(
        high_pressure_df=hp_performance_df,
        overall_baseline_df=overall_baseline_df,
        low_pressure_baseline_df=low_pressure_baseline_df,
        config=cfg,
    )

    # 3. Situational Analysis
    logger.info("Step 3: Analyzing situational bowling performance under pressure...")
    situational_df = analyze_situational_bowling(
        deliveries_df=deliveries_df,
        player_registry_df=player_registry_df,
        config=cfg,
    )

    # 4. Bowling Role Analysis
    logger.info("Step 4: Analyzing historical bowling roles and phase distributions...")
    role_df = analyze_bowler_roles(
        deliveries_df=deliveries_df,
        player_registry_df=player_registry_df,
        config=cfg,
    )

    # 5. Calculate BPPI-B
    logger.info("Step 5: Calculating Bowling Pressure Performance Index (BPPI-B)...")
    bppi_df = calculate_bppi_b(
        comparison_df=comparison_df,
        config=cfg,
    )

    # 6. Assess Reliability and Bootstrap
    logger.info("Step 6: Assessing reliability and computing bootstrap confidence intervals...")
    hp_deliveries = deliveries_df[deliveries_df["bowling_pressure_score"] >= cfg.high_pressure_threshold]
    reliability_df = assess_bowling_reliability(
        bppi_df=bppi_df,
        high_pressure_deliveries_df=hp_deliveries,
        config=cfg,
    )

    # 7. Classify Bowlers
    logger.info("Step 7: Classifying bowlers by pressure performance evidence...")
    classified_df = classify_bowlers(
        reliability_df=reliability_df,
        config=cfg,
    )

    # 8. Generate Explanations
    logger.info("Step 8: Generating explainable bowling performance narratives...")
    explanations_df = generate_bowler_explanations(
        classified_df=classified_df,
    )

    # 9. Validation Checks
    logger.info("Step 9: Auditing mathematical consistency and constraints...")
    validation_checks = validate_bowling_pressure_datasets(
        category_df=cat_metrics_df,
        hp_performance_df=hp_performance_df,
        comparison_df=comparison_df,
        bppi_df=classified_df,
        situational_df=situational_df,
    )

    logger.info("Bowling Performance Under Pressure Engine completed successfully.")
    return {
        "bowler_pressure_category_metrics": cat_metrics_df,
        "bowler_high_pressure_performance": hp_performance_df,
        "bowler_baseline_comparison": comparison_df,
        "bowler_situational_performance": situational_df,
        "bowler_role_analysis": role_df,
        "bowler_pressure_reliability": reliability_df,
        "bowler_pressure_performance_index": classified_df,
        "bowler_pressure_explanations": explanations_df,
        "validation_checks": validation_checks,
    }

