"""Match-level block bootstrap validation module for Phase 9.

Implements match-level block bootstrap resampling (preserving match-level dependence)
to evaluate rating uncertainty, derive empirical confidence intervals, and compute
top-10 / top-5 membership probabilities across resampling iterations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from src.validation.validation_config import ValidationConfig

logger = logging.getLogger(__name__)


def run_match_level_bootstrap(
    ranked_batters: pd.DataFrame,
    ranked_bowlers: pd.DataFrame,
    bat_match_agg: pd.DataFrame,
    bowl_match_agg: pd.DataFrame,
    config: ValidationConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Execute match-level block bootstrap validation for batters and bowlers.

    Args:
        ranked_batters: Official Phase 8 ranked eligible batters.
        ranked_bowlers: Official Phase 8 ranked eligible bowlers.
        bat_match_agg: Match-level aggregated high-pressure batting stats.
        bowl_match_agg: Match-level aggregated high-pressure bowling stats.
        config: Validation configuration.

    Returns:
        Tuple of (batting_bootstrap_results, bowling_bootstrap_results).
    """
    rng = np.random.default_rng(config.random_seed)
    n_iter = config.bootstrap_iterations

    logger.info(
        "Starting match-level block bootstrap (%d iterations, seed=%d)...",
        n_iter,
        config.random_seed,
    )

    # 1. Batting Bootstrap
    bat_results = _run_batting_bootstrap(
        ranked_batters=ranked_batters,
        bat_match_agg=bat_match_agg,
        n_iter=n_iter,
        rng=rng,
        top_n=config.top_n,
    )

    # 2. Bowling Bootstrap
    bowl_results = _run_bowling_bootstrap(
        ranked_bowlers=ranked_bowlers,
        bowl_match_agg=bowl_match_agg,
        n_iter=n_iter,
        rng=rng,
        top_n=config.top_n,
    )

    logger.info("Match-level block bootstrap completed successfully.")
    return bat_results, bowl_results


def _run_batting_bootstrap(
    ranked_batters: pd.DataFrame,
    bat_match_agg: pd.DataFrame,
    n_iter: int,
    rng: np.random.Generator,
    top_n: int = 10,
) -> pd.DataFrame:
    """Run match-level bootstrap for eligible batters."""
    eligible_pids = ranked_batters["player_id"].astype(str).tolist()
    # Pre-group matches by player_id
    player_matches: Dict[str, List[Dict[str, Any]]] = {}
    for pid, group in bat_match_agg.groupby("player_id"):
        if pid in eligible_pids:
            player_matches[pid] = group.to_dict("records")

    prior_mean = float(ranked_batters["raw_fbpr"].median())
    n0 = 25.0  # Phase 8 batting prior weight

    # Matrix to record ratings: shape (n_players, n_iter)
    ratings_matrix = np.zeros((len(eligible_pids), n_iter))
    pid_to_idx = {pid: i for i, pid in enumerate(eligible_pids)}

    # Base reference ratings and baseline SR
    base_info = ranked_batters.set_index(ranked_batters["player_id"].astype(str))

    for b in range(n_iter):
        iter_ratings = []
        for pid in eligible_pids:
            matches = player_matches.get(pid, [])
            n_m = len(matches)
            if n_m == 0:
                # If no matches found, fallback to reference raw score
                iter_ratings.append(float(base_info.loc[pid, "final_fbpr"]))
                continue

            # Resample matches with replacement
            sampled_indices = rng.choice(n_m, size=n_m, replace=True)
            sampled_matches = [matches[idx] for idx in sampled_indices]

            tot_balls = sum(m["hp_balls"] for m in sampled_matches)
            tot_runs = sum(m["hp_runs"] for m in sampled_matches)
            tot_fours = sum(m["hp_fours"] for m in sampled_matches)
            tot_sixes = sum(m["hp_sixes"] for m in sampled_matches)

            # Recompute Strike Rate
            sr = (tot_runs / tot_balls * 100.0) if tot_balls > 0 else 120.0
            bnd_pct = ((tot_fours * 4 + tot_sixes * 6) / tot_runs * 100.0) if tot_runs > 0 else 40.0

            # Absolute score (scaled)
            sr_scaled = np.clip((sr - 80.0) / (200.0 - 80.0) * 100.0, 0.0, 100.0)
            bnd_scaled = np.clip((bnd_pct - 20.0) / (70.0 - 20.0) * 100.0, 0.0, 100.0)
            score_abs = 0.60 * sr_scaled + 0.40 * bnd_scaled

            # Retention score relative to baseline
            base_sr = float(base_info.loc[pid, "overall_strike_rate"]) if "overall_strike_rate" in base_info.columns else 135.0
            sr_ret = np.clip((sr / max(base_sr, 50.0)) * 50.0, 0.0, 100.0)

            # Composite raw rating
            raw_rating = (
                0.50 * sr_ret
                + 0.20 * score_abs
                + 0.15 * float(base_info.loc[pid, "score_batting_consistency"])
                + 0.15 * float(base_info.loc[pid, "score_batting_context"])
            )

            # Empirical Bayes shrinkage
            lam = tot_balls / (tot_balls + n0)
            shrunk_rating = np.clip(lam * raw_rating + (1.0 - lam) * prior_mean, 0.0, 100.0)
            iter_ratings.append(shrunk_rating)

        ratings_matrix[:, b] = iter_ratings

    # Calculate ranks per iteration: shape (n_players, n_iter)
    # Higher rating = better rank (rank 1 is best)
    ranks_matrix = np.zeros_like(ratings_matrix)
    for b in range(n_iter):
        ranks_matrix[:, b] = pd.Series(ratings_matrix[:, b]).rank(ascending=False, method="min").values

    # Compute statistics for each player
    rows = []
    for pid, i in pid_to_idx.items():
        r_dist = ratings_matrix[i, :]
        rank_dist = ranks_matrix[i, :]
        n_matches = len(player_matches.get(pid, []))

        mean_rating = float(np.mean(r_dist))
        median_rating = float(np.median(r_dist))
        std_rating = float(np.std(r_dist))
        ci_90 = [float(np.percentile(r_dist, 5.0)), float(np.percentile(r_dist, 95.0))]
        ci_95 = [float(np.percentile(r_dist, 2.5)), float(np.percentile(r_dist, 97.5))]

        prob_top_10 = float(np.mean(rank_dist <= 10))
        prob_top_5 = float(np.mean(rank_dist <= 5))
        mean_rank = float(np.mean(rank_dist))
        median_rank = float(np.median(rank_dist))
        best_rank = int(np.min(rank_dist))
        worst_rank = int(np.max(rank_dist))

        official_row = base_info.loc[pid]
        rows.append({
            "player_id": pid,
            "player_name": official_row["player_name"],
            "official_rank": int(official_row["rank"]),
            "official_fbpr": float(official_row["final_fbpr"]),
            "bootstrap_mean_fbpr": round(mean_rating, 2),
            "bootstrap_median_fbpr": round(median_rating, 2),
            "bootstrap_std_fbpr": round(std_rating, 2),
            "ci_90_lower": round(ci_90[0], 2),
            "ci_90_upper": round(ci_90[1], 2),
            "ci_95_lower": round(ci_95[0], 2),
            "ci_95_upper": round(ci_95[1], 2),
            "ci_95_width": round(ci_95[1] - ci_95[0], 2),
            "median_bootstrap_rank": round(median_rank, 1),
            "mean_bootstrap_rank": round(mean_rank, 1),
            "best_bootstrap_rank": best_rank,
            "worst_bootstrap_rank": worst_rank,
            "prob_in_top_10": round(prob_top_10, 3),
            "prob_in_top_5": round(prob_top_5, 3),
            "matches_resampled": n_matches,
            "insufficient_bootstrap_evidence": n_matches < 3,
        })

    df_out = pd.DataFrame(rows).sort_values("official_rank").reset_index(drop=True)
    return df_out


def _run_bowling_bootstrap(
    ranked_bowlers: pd.DataFrame,
    bowl_match_agg: pd.DataFrame,
    n_iter: int,
    rng: np.random.Generator,
    top_n: int = 10,
) -> pd.DataFrame:
    """Run match-level bootstrap for eligible bowlers."""
    eligible_pids = ranked_bowlers["player_id"].astype(str).tolist()
    player_matches: Dict[str, List[Dict[str, Any]]] = {}
    for pid, group in bowl_match_agg.groupby("player_id"):
        if pid in eligible_pids:
            player_matches[pid] = group.to_dict("records")

    prior_mean = float(ranked_bowlers["raw_fbor"].median())
    n0 = 30.0  # Phase 8 bowling prior weight

    ratings_matrix = np.zeros((len(eligible_pids), n_iter))
    pid_to_idx = {pid: i for i, pid in enumerate(eligible_pids)}
    base_info = ranked_bowlers.set_index(ranked_bowlers["player_id"].astype(str))

    for b in range(n_iter):
        iter_ratings = []
        for pid in eligible_pids:
            matches = player_matches.get(pid, [])
            n_m = len(matches)
            if n_m == 0:
                iter_ratings.append(float(base_info.loc[pid, "final_fbor"]))
                continue

            sampled_indices = rng.choice(n_m, size=n_m, replace=True)
            sampled_matches = [matches[idx] for idx in sampled_indices]

            tot_lb = sum(m["hp_legal_balls"] for m in sampled_matches)
            tot_runs = sum(m["hp_runs_conceded"] for m in sampled_matches)
            tot_dots = sum(m["hp_dots"] for m in sampled_matches)
            tot_wkts = sum(m["hp_wickets"] for m in sampled_matches)

            econ = (tot_runs / tot_lb * 6.0) if tot_lb > 0 else 9.5
            dot_pct = (tot_dots / tot_lb * 100.0) if tot_lb > 0 else 35.0
            wkt_rate = (tot_wkts / tot_lb) if tot_lb > 0 else 0.04

            # Scaled components
            econ_score = np.clip((13.0 - econ) / (13.0 - 6.0) * 100.0, 0.0, 100.0)
            dot_score = np.clip((dot_pct - 20.0) / (60.0 - 20.0) * 100.0, 0.0, 100.0)
            wkt_score = np.clip((wkt_rate - 0.01) / (0.10 - 0.01) * 100.0, 0.0, 100.0)
            score_abs = 0.45 * econ_score + 0.35 * dot_score + 0.20 * wkt_score

            # Retention score relative to baseline economy
            base_econ = float(base_info.loc[pid, "overall_economy_rate"]) if "overall_economy_rate" in base_info.columns else 8.2
            econ_ret = np.clip((base_econ / max(econ, 4.0)) * 50.0, 0.0, 100.0)

            raw_rating = (
                0.50 * econ_ret
                + 0.20 * score_abs
                + 0.15 * float(base_info.loc[pid, "score_bowling_consistency"])
                + 0.15 * float(base_info.loc[pid, "score_bowling_context"])
            )

            lam = tot_lb / (tot_lb + n0)
            shrunk_rating = np.clip(lam * raw_rating + (1.0 - lam) * prior_mean, 0.0, 100.0)
            iter_ratings.append(shrunk_rating)

        ratings_matrix[:, b] = iter_ratings

    ranks_matrix = np.zeros_like(ratings_matrix)
    for b in range(n_iter):
        ranks_matrix[:, b] = pd.Series(ratings_matrix[:, b]).rank(ascending=False, method="min").values

    rows = []
    for pid, i in pid_to_idx.items():
        r_dist = ratings_matrix[i, :]
        rank_dist = ranks_matrix[i, :]
        n_matches = len(player_matches.get(pid, []))

        mean_rating = float(np.mean(r_dist))
        median_rating = float(np.median(r_dist))
        std_rating = float(np.std(r_dist))
        ci_90 = [float(np.percentile(r_dist, 5.0)), float(np.percentile(r_dist, 95.0))]
        ci_95 = [float(np.percentile(r_dist, 2.5)), float(np.percentile(r_dist, 97.5))]

        prob_top_10 = float(np.mean(rank_dist <= 10))
        prob_top_5 = float(np.mean(rank_dist <= 5))
        mean_rank = float(np.mean(rank_dist))
        median_rank = float(np.median(rank_dist))
        best_rank = int(np.min(rank_dist))
        worst_rank = int(np.max(rank_dist))

        official_row = base_info.loc[pid]
        rows.append({
            "player_id": pid,
            "player_name": official_row["player_name"],
            "official_rank": int(official_row["rank"]),
            "official_fbor": float(official_row["final_fbor"]),
            "bootstrap_mean_fbor": round(mean_rating, 2),
            "bootstrap_median_fbor": round(median_rating, 2),
            "bootstrap_std_fbor": round(std_rating, 2),
            "ci_90_lower": round(ci_90[0], 2),
            "ci_90_upper": round(ci_90[1], 2),
            "ci_95_lower": round(ci_95[0], 2),
            "ci_95_upper": round(ci_95[1], 2),
            "ci_95_width": round(ci_95[1] - ci_95[0], 2),
            "median_bootstrap_rank": round(median_rank, 1),
            "mean_bootstrap_rank": round(mean_rank, 1),
            "best_bootstrap_rank": best_rank,
            "worst_bootstrap_rank": worst_rank,
            "prob_in_top_10": round(prob_top_10, 3),
            "prob_in_top_5": round(prob_top_5, 3),
            "matches_resampled": n_matches,
            "insufficient_bootstrap_evidence": n_matches < 3,
        })

    df_out = pd.DataFrame(rows).sort_values("official_rank").reset_index(drop=True)
    return df_out

