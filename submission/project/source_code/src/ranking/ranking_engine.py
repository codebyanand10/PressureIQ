"""Master coordinator for Phase 8 Unified Player Rating & Ranking Engine.

Orchestrates:
1. Data loading and cross-phase dataset integration.
2. Separate batting and bowling eligibility evaluation.
3. Multi-component rating computation for both roles.
4. Empirical Bayes shrinkage and statistical reliability adjustment.
5. Deterministic tie-breaking and rank assignment.
6. Extraction of Top 10 Batters and Top 10 Bowlers under pressure.
7. Explainable narrative generation.
8. Mathematical validation and initial fairness audit.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple
import pandas as pd

from src.ranking.ranking_config import RankingConfig
from src.ranking.data_loader import load_ranking_inputs
from src.ranking.eligibility import evaluate_batting_eligibility, evaluate_bowling_eligibility
from src.ranking.batting_rating import calculate_batting_rating_components
from src.ranking.bowling_rating import calculate_bowling_rating_components
from src.ranking.reliability import (
    apply_reliability_adjustment_batting,
    apply_reliability_adjustment_bowling,
)
from src.ranking.ranking_explainability import (
    generate_batting_ranking_explanations,
    generate_bowling_ranking_explanations,
)
from src.ranking.ranking_validation import validate_rankings, audit_ranking_fairness

logger = logging.getLogger(__name__)


def calculate_unified_player_rankings(
    inputs: Optional[Dict[str, pd.DataFrame]] = None,
    config: Optional[RankingConfig] = None,
    weights_profile: str = "primary",
) -> Dict[str, Any]:
    """Execute end-to-end Phase 8 Unified Player Rating & Ranking Engine.

    Args:
        inputs: Optional pre-loaded input dictionary. If None, loaded from disk.
        config: Optional ranking configuration.
        weights_profile: Weight profile name ('primary', 'balanced', etc.).

    Returns:
        Dictionary containing:
        - top_10_batters
        - top_10_bowlers
        - all_batter_rankings
        - all_bowler_rankings
        - batting_eligibility
        - bowling_eligibility
        - excluded_players
        - ranking_components
        - ranking_explanations
        - validation_checks
        - fairness_audit
        - configuration_summary
    """
    cfg = config or RankingConfig()
    data = inputs or load_ranking_inputs()

    logger.info("Starting Unified Player Rating & Ranking Engine (version: %s)...", cfg.version)

    # 1. Prepare Batting and Bowling Merged Input Views
    # Merge Phase 6 Batting Datasets
    bat_bppi = data["batting_bppi"].copy()
    bat_hp = data["batting_hp"].copy()
    bat_comp = data["batting_comparison"].copy()
    bat_rel = data["batting_reliability"].copy()

    # Drop duplicate columns before merging
    cols_to_add_bat = [c for c in bat_hp.columns if c not in bat_bppi.columns]
    bat_merged = bat_bppi.merge(bat_hp[["player_id"] + cols_to_add_bat], on="player_id", how="left")
    for df_sub in [bat_comp, bat_rel]:
        cols = [c for c in df_sub.columns if c not in bat_merged.columns]
        bat_merged = bat_merged.merge(df_sub[["player_id"] + cols], on="player_id", how="left")

    # Merge Phase 7 Bowling Datasets
    bowl_bppi = data["bowling_bppi"].copy()
    bowl_hp = data["bowling_hp"].copy()
    bowl_comp = data["bowling_comparison"].copy()
    bowl_rel = data["bowling_reliability"].copy()
    bowl_roles = data.get("bowling_roles", pd.DataFrame())

    cols_to_add_bowl = [c for c in bowl_hp.columns if c not in bowl_bppi.columns]
    bowl_merged = bowl_bppi.merge(bowl_hp[["player_id"] + cols_to_add_bowl], on="player_id", how="left")
    for df_sub in [bowl_comp, bowl_rel]:
        cols = [c for c in df_sub.columns if c not in bowl_merged.columns]
        bowl_merged = bowl_merged.merge(df_sub[["player_id"] + cols], on="player_id", how="left")

    if not bowl_roles.empty:
        role_cols = [c for c in bowl_roles.columns if c not in bowl_merged.columns]
        bowl_merged = bowl_merged.merge(bowl_roles[["player_id"] + role_cols], on="player_id", how="left")

    # 2. Evaluate Eligibility
    logger.info("Evaluating eligibility for batters and bowlers...")
    bat_eligibility = evaluate_batting_eligibility(
        batting_df=bat_merged,
        baseline_df=data["batting_baseline"],
        registry_df=data["player_registry"],
        config=cfg,
    )

    bowl_eligibility = evaluate_bowling_eligibility(
        bowling_df=bowl_merged,
        baseline_df=data["bowling_baseline"],
        registry_df=data["player_registry"],
        config=cfg,
    )

    # Excluded players
    bat_excl = bat_eligibility[~bat_eligibility["is_eligible"]]
    bowl_excl = bowl_eligibility[~bowl_eligibility["is_eligible"]]
    excluded_players = pd.concat([bat_excl, bowl_excl], ignore_index=True)

    # 3. Filter to Eligible Candidates
    eligible_bat_ids = set(bat_eligibility[bat_eligibility["is_eligible"]]["player_id"])
    eligible_bowl_ids = set(bowl_eligibility[bowl_eligibility["is_eligible"]]["player_id"])

    bat_candidates = bat_merged[bat_merged["player_id"].astype(str).isin(eligible_bat_ids)].copy()
    bowl_candidates = bowl_merged[bowl_merged["player_id"].astype(str).isin(eligible_bowl_ids)].copy()

    logger.info(
        "Candidate cohorts for official ranking: %d batters, %d bowlers.",
        len(bat_candidates),
        len(bowl_candidates),
    )

    # 4. Calculate Batting Components and Apply Reliability Shrinkage
    logger.info("Computing batting ratings and shrinkage adjustments...")
    bat_scored = calculate_batting_rating_components(bat_candidates, cfg, weights_profile=weights_profile)
    bat_rated = apply_reliability_adjustment_batting(bat_scored, cfg)

    # Deterministic Batting Tie-Breaking Sort:
    # 1. ranking_score desc
    # 2. score_batting_resilience desc
    # 3. score_batting_absolute desc
    # 4. balls_faced desc
    # 5. player_id asc
    bat_sorted = bat_rated.sort_values(
        by=["ranking_score", "score_batting_resilience", "score_batting_absolute", "balls_faced", "player_id"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    bat_sorted["rank"] = bat_sorted.index + 1
    top_10_batters = bat_sorted.head(cfg.top_n).copy()

    # 5. Calculate Bowling Components and Apply Reliability Shrinkage
    logger.info("Computing bowling ratings and shrinkage adjustments...")
    bowl_scored = calculate_bowling_rating_components(bowl_candidates, cfg, weights_profile=weights_profile)
    bowl_rated = apply_reliability_adjustment_bowling(bowl_scored, cfg)

    # Deterministic Bowling Tie-Breaking Sort:
    # 1. ranking_score desc
    # 2. score_bowling_resilience desc
    # 3. score_bowling_absolute desc
    # 4. legal_balls_bowled desc
    # 5. player_id asc
    bowl_sorted = bowl_rated.sort_values(
        by=["ranking_score", "score_bowling_resilience", "score_bowling_absolute", "legal_balls_bowled", "player_id"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    bowl_sorted["rank"] = bowl_sorted.index + 1
    top_10_bowlers = bowl_sorted.head(cfg.top_n).copy()

    # 6. Generate Explanations
    logger.info("Generating narrative explanations for all ranked players...")
    bat_exp = generate_batting_ranking_explanations(bat_sorted)
    bowl_exp = generate_bowling_ranking_explanations(bowl_sorted)
    all_explanations = pd.concat([bat_exp, bowl_exp], ignore_index=True)

    # Attach explanation fields to ranked tables
    bat_sorted = bat_sorted.merge(
        bat_exp[["player_id", "ranking_explanation", "key_strengths", "baseline_comparison", "reliability_summary", "pressure_exposure", "ranking_limitations"]],
        on="player_id",
        how="left",
    )
    bowl_sorted = bowl_sorted.merge(
        bowl_exp[["player_id", "ranking_explanation", "key_strengths", "baseline_comparison", "reliability_summary", "pressure_exposure", "ranking_limitations"]],
        on="player_id",
        how="left",
    )
    top_10_batters = bat_sorted.head(cfg.top_n).copy()
    top_10_bowlers = bowl_sorted.head(cfg.top_n).copy()

    # 7. Validation & Fairness Audit
    logger.info("Executing mathematical and integrity validation...")
    validation_checks = validate_rankings(
        ranked_batters_df=bat_sorted,
        ranked_bowlers_df=bowl_sorted,
        top_10_batters_df=top_10_batters,
        top_10_bowlers_df=top_10_bowlers,
    )

    fairness_audit = audit_ranking_fairness(
        ranked_batters_df=bat_sorted,
        ranked_bowlers_df=bowl_sorted,
    )

    # 8. Combined Components View
    bat_comp_export = bat_sorted[[
        "player_id", "player_name", "rank", "final_fbpr", "raw_fbpr", "bppi",
        "score_batting_resilience", "score_batting_absolute", "score_batting_consistency", "score_batting_context",
        "balls_faced", "strike_rate", "ci_lower_fbpr", "ci_upper_fbpr", "reliability_level"
    ]].copy().rename(columns={"final_fbpr": "final_rating", "raw_fbpr": "raw_rating", "bppi": "bppi_score"})
    bat_comp_export["role"] = "batter"

    bowl_comp_export = bowl_sorted[[
        "player_id", "player_name", "rank", "final_fbor", "raw_fbor", "bppi_b",
        "score_bowling_resilience", "score_bowling_absolute", "score_bowling_consistency", "score_bowling_context",
        "legal_balls_bowled", "economy_rate", "ci_lower_fbor", "ci_upper_fbor", "reliability_level"
    ]].copy().rename(columns={
        "final_fbor": "final_rating",
        "raw_fbor": "raw_rating",
        "bppi_b": "bppi_score",
        "legal_balls_bowled": "balls_faced",
        "economy_rate": "strike_rate",
        "ci_lower_fbor": "ci_lower_fbpr",
        "ci_upper_fbor": "ci_upper_fbpr",
    })
    bowl_comp_export["role"] = "bowler"
    ranking_components = pd.concat([bat_comp_export, bowl_comp_export], ignore_index=True)

    cfg_dict = {
        "version": cfg.version,
        "weights": cfg.weight_profiles,
        "active_profile": weights_profile,
        "batting_eligibility": {
            "min_balls_faced": cfg.bat_min_balls,
            "min_matches": cfg.bat_min_matches,
            "min_innings": cfg.bat_min_innings,
        },
        "bowling_eligibility": {
            "min_legal_balls": cfg.bowl_min_balls,
            "min_matches": cfg.bowl_min_matches,
            "min_innings": cfg.bowl_min_innings,
        },
        "reliability": {
            "method": cfg.uncertainty_method,
            "batting_prior_weight": cfg.shrinkage_prior_weight_batting,
            "bowling_prior_weight": cfg.shrinkage_prior_weight_bowling,
        },
    }

    logger.info("Unified Player Rating & Ranking Engine executed successfully.")
    return {
        "top_10_batters": top_10_batters,
        "top_10_bowlers": top_10_bowlers,
        "all_batter_rankings": bat_sorted,
        "all_bowler_rankings": bowl_sorted,
        "batting_eligibility": bat_eligibility,
        "bowling_eligibility": bowl_eligibility,
        "excluded_players": excluded_players,
        "ranking_components": ranking_components,
        "ranking_explanations": all_explanations,
        "validation_checks": validation_checks,
        "fairness_audit": fairness_audit,
        "configuration_summary": cfg_dict,
    }

