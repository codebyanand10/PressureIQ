"""Master orchestrator for Phase 9: Statistical Validation & Robustness Testing.

Executes all 15 validation components and returns structured datasets and metrics.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import pandas as pd

from src.validation.validation_config import ValidationConfig
from src.validation.data_loader import load_validation_inputs
from src.validation.bootstrap_validation import run_match_level_bootstrap
from src.validation.ranking_stability import evaluate_ranking_stability
from src.validation.sensitivity_analysis import run_weight_sensitivity_analysis
from src.validation.eligibility_sensitivity import evaluate_eligibility_sensitivity
from src.validation.pressure_sensitivity import evaluate_pressure_model_sensitivity
from src.validation.competition_fairness import evaluate_competition_fairness
from src.validation.role_fairness import evaluate_role_fairness
from src.validation.sample_size_validation import validate_sample_size_effects
from src.validation.baseline_sensitivity import evaluate_baseline_sensitivity
from src.validation.leakage_audit import execute_leakage_audit
from src.validation.influence_analysis import evaluate_influential_matches
from src.validation.player_comparison import compare_top_players
from src.validation.robustness_scorecard import generate_robustness_scorecard

logger = logging.getLogger(__name__)


def execute_statistical_validation(
    inputs: Optional[Dict[str, pd.DataFrame]] = None,
    config: Optional[ValidationConfig] = None,
    quick_mode: bool = False,
) -> Dict[str, Any]:
    """Execute the end-to-end Phase 9 validation pipeline.

    Args:
        inputs: Optional pre-loaded inputs dictionary.
        config: Optional validation configuration.
        quick_mode: If True, executes reduced bootstrap iterations.

    Returns:
        Dictionary containing all generated validation DataFrames and summary metrics.
    """
    cfg = config or ValidationConfig(quick_mode=quick_mode)
    data = inputs or load_validation_inputs()

    logger.info("Executing Phase 9 Statistical Validation Pipeline (version: %s)...", cfg.version)

    # 1. Match-level block bootstrap
    bat_boot, bowl_boot = run_match_level_bootstrap(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        bat_match_agg=data["bat_match_agg"],
        bowl_match_agg=data["bowl_match_agg"],
        config=cfg,
    )

    # 2. Ranking stability & LOMO
    bat_stab, bowl_stab, stab_metrics = evaluate_ranking_stability(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        bat_bootstrap=bat_boot,
        bowl_bootstrap=bowl_boot,
        bat_match_agg=data["bat_match_agg"],
        bowl_match_agg=data["bowl_match_agg"],
        top_n=cfg.top_n,
    )

    # 3. Weight sensitivity
    bat_weight_sens, bowl_weight_sens, weight_summary = run_weight_sensitivity_analysis(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        config=cfg,
    )

    # 4. Eligibility threshold sensitivity
    elig_summary, elig_movement = evaluate_eligibility_sensitivity(
        batting_el_df=data["batting_eligibility"],
        bowling_el_df=data["bowling_eligibility"],
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        config=cfg,
    )

    # 5. Pressure model sensitivity
    pressure_summary, _ = evaluate_pressure_model_sensitivity(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        val_config=cfg,
    )

    # 6. Competition & format fairness
    comp_fairness, comp_metrics = evaluate_competition_fairness(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        match_meta=data["match_metadata"],
        config_val=cfg,
    )

    # 7. Role and situation fairness
    role_bat_summary, role_bowl_summary, role_metrics = evaluate_role_fairness(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        config_val=cfg,
    )

    # 8. Sample size validation
    sample_size_df, sample_size_metrics = validate_sample_size_effects(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
    )

    # 9. Baseline sensitivity
    baseline_sens_df, baseline_metrics = evaluate_baseline_sensitivity(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        ctx_bat_baseline=data["contextual_batting_baseline"],
        ctx_bowl_baseline=data["contextual_bowling_baseline"],
        config_val=cfg,
    )

    # 10. Data leakage audit
    leakage_audit_df = execute_leakage_audit()

    # 11. Single-match influence analysis
    influence_df, influence_metrics = evaluate_influential_matches(
        ranked_batters=data["batter_ratings"],
        ranked_bowlers=data["bowler_ratings"],
        bat_match_agg=data["bat_match_agg"],
        bowl_match_agg=data["bowl_match_agg"],
        match_meta=data["match_metadata"],
        config_val=cfg,
    )

    # 12. Pairwise player comparisons & significance
    player_comp_df, player_tier_summary = compare_top_players(
        bat_bootstrap=bat_boot,
        bowl_bootstrap=bowl_boot,
        config_val=cfg,
    )

    # 13. Official 10-dimension robustness scorecard
    scorecard_df = generate_robustness_scorecard(
        bat_stability_metrics=stab_metrics,
        weight_summary=weight_summary,
        eligibility_summary=elig_summary,
        pressure_summary=pressure_summary,
        comp_fairness_metrics=comp_metrics,
        role_summary_metrics=role_metrics,
        sample_size_metrics=sample_size_metrics,
        baseline_metrics=baseline_metrics,
        leakage_audit_df=leakage_audit_df,
    )

    logger.info("Phase 9 Statistical Validation execution completed.")

    return {
        "batting_bootstrap_results": bat_boot,
        "bowling_bootstrap_results": bowl_boot,
        "batting_rank_stability": bat_stab,
        "bowling_rank_stability": bowl_stab,
        "batting_sensitivity_results": bat_weight_sens,
        "bowling_sensitivity_results": bowl_weight_sens,
        "weight_summary": weight_summary,
        "eligibility_sensitivity": elig_summary,
        "eligibility_movement": elig_movement,
        "pressure_sensitivity": pressure_summary,
        "competition_fairness": comp_fairness,
        "batting_role_fairness": role_bat_summary,
        "bowling_role_fairness": role_bowl_summary,
        "sample_size_validation": sample_size_df,
        "baseline_sensitivity": baseline_sens_df,
        "leakage_audit": leakage_audit_df,
        "influence_analysis": influence_df,
        "player_comparison_results": player_comp_df,
        "robustness_scorecard": scorecard_df,
        "metrics": {
            **stab_metrics,
            **comp_metrics,
            **role_metrics,
            **sample_size_metrics,
            **baseline_metrics,
            **influence_metrics,
            **player_tier_summary,
        },
    }

