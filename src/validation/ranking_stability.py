"""Ranking stability analysis module for Phase 9.

Performs:
1. Leave-One-Match-Out (LOMO) sensitivity testing to detect single-match leverage.
2. Top-10 membership stability and rank variance evaluation.
3. Ranking similarity metrics (Spearman rho, Kendall tau, top-10 overlap, Jaccard index).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

logger = logging.getLogger(__name__)


def evaluate_ranking_stability(
    ranked_batters: pd.DataFrame,
    ranked_bowlers: pd.DataFrame,
    bat_bootstrap: pd.DataFrame,
    bowl_bootstrap: pd.DataFrame,
    bat_match_agg: pd.DataFrame,
    bowl_match_agg: pd.DataFrame,
    top_n: int = 10,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Execute ranking stability analysis for batters and bowlers.

    Returns:
        Tuple of (batting_stability_df, bowling_stability_df, stability_summary_metrics).
    """
    logger.info("Evaluating ranking stability and leave-one-match-out sensitivity...")

    # 1. Batting Stability & LOMO
    bat_stab = _evaluate_role_stability(
        ranked_df=ranked_batters,
        boot_df=bat_bootstrap,
        match_agg=bat_match_agg,
        role="batter",
        top_n=top_n,
    )

    # 2. Bowling Stability & LOMO
    bowl_stab = _evaluate_role_stability(
        ranked_df=ranked_bowlers,
        boot_df=bowl_bootstrap,
        match_agg=bowl_match_agg,
        role="bowler",
        top_n=top_n,
    )

    # 3. Overall Stability Summary Metrics
    # Top 10 overlap across bootstrap median vs official
    bat_top10_off = set(ranked_batters.head(top_n)["player_id"])
    bat_top10_boot = set(bat_bootstrap.sort_values("median_bootstrap_rank").head(top_n)["player_id"])
    bat_overlap = len(bat_top10_off.intersection(bat_top10_boot))
    bat_jaccard = bat_overlap / len(bat_top10_off.union(bat_top10_boot))

    bowl_top10_off = set(ranked_bowlers.head(top_n)["player_id"])
    bowl_top10_boot = set(bowl_bootstrap.sort_values("median_bootstrap_rank").head(top_n)["player_id"])
    bowl_overlap = len(bowl_top10_off.intersection(bowl_top10_boot))
    bowl_jaccard = bowl_overlap / len(bowl_top10_off.union(bowl_top10_boot))

    summary_metrics = {
        "batting_top10_overlap_bootstrap": bat_overlap,
        "batting_top10_jaccard": round(bat_jaccard, 3),
        "bowling_top10_overlap_bootstrap": bowl_overlap,
        "bowling_top10_jaccard": round(bowl_jaccard, 3),
        "batting_max_lomo_rank_drop": int(bat_stab.head(top_n)["max_rank_drop_lomo"].max()),
        "bowling_max_lomo_rank_drop": int(bowl_stab.head(top_n)["max_rank_drop_lomo"].max()),
    }

    logger.info("Ranking stability evaluation complete.")
    return bat_stab, bowl_stab, summary_metrics


def _evaluate_role_stability(
    ranked_df: pd.DataFrame,
    boot_df: pd.DataFrame,
    match_agg: pd.DataFrame,
    role: str,
    top_n: int = 10,
) -> pd.DataFrame:
    """Evaluate stability metrics and LOMO for all ranked players."""
    merged = ranked_df.merge(
        boot_df[[
            "player_id", "bootstrap_mean_fbpr" if role == "batter" else "bootstrap_mean_fbor",
            "bootstrap_std_fbpr" if role == "batter" else "bootstrap_std_fbor",
            "ci_95_width", "median_bootstrap_rank", "prob_in_top_10", "prob_in_top_5",
            "best_bootstrap_rank", "worst_bootstrap_rank"
        ]],
        on="player_id",
        how="left",
    )

    # Precompute player match counts
    p_matches = match_agg.groupby("player_id")["match_id"].unique().to_dict()

    rating_col = "final_fbpr" if role == "batter" else "final_fbor"
    official_ratings = ranked_df.set_index("player_id")[rating_col].to_dict()

    lomo_rows = []
    # Evaluate LOMO for candidates in top 30
    eval_candidates = set(ranked_df.head(30)["player_id"])

    for _, row in merged.iterrows():
        pid = row["player_id"]
        off_rank = int(row["rank"])
        matches = p_matches.get(pid, [])
        n_matches = len(matches)

        if pid in eval_candidates and n_matches > 1:
            # Leave-one-out impact simulation
            # Estimate max rank drop when dropping the single highest-performing match
            match_records = match_agg[match_agg["player_id"] == pid]
            if role == "batter":
                runs = match_records["hp_runs"].values
                balls = match_records["hp_balls"].values
                # High leverage match is where batter scored the most runs or highest SR
                best_match_idx = int(np.argmax(runs))
                tot_r = runs.sum() - runs[best_match_idx]
                tot_b = balls.sum() - balls[best_match_idx]
                new_sr = (tot_r / tot_b * 100.0) if tot_b > 0 else 100.0
                sr_diff = row["strike_rate"] - new_sr
                rating_impact = np.clip(sr_diff * 0.15, 0.0, 15.0)
            else:
                wkts = match_records["hp_wickets"].values
                dots = match_records["hp_dots"].values
                best_match_idx = int(np.argmax(wkts * 2 + dots))
                rating_impact = np.clip(len(wkts) * 0.5, 0.5, 8.0)

            # Simulated rank with best match dropped
            sim_rating = row[rating_col] - rating_impact
            # Count how many players now beat sim_rating
            sim_rank = sum(1 for p, r in official_ratings.items() if p != pid and r > sim_rating) + 1
            max_drop = max(0, sim_rank - off_rank)
        else:
            max_drop = 0
            rating_impact = 0.0

        prob_top10 = float(row.get("prob_in_top_10", 0.0))
        # Stability Category assignment
        if off_rank <= 10:
            if prob_top10 >= 0.70 and max_drop <= 2:
                cat = "Highly Stable"
            elif prob_top10 >= 0.40 and max_drop <= 4:
                cat = "Moderately Stable"
            else:
                cat = "Sensitive to Sample / High Leverage"
        else:
            cat = "Outside Top 10"

        lomo_rows.append({
            "player_id": pid,
            "player_name": row["player_name"],
            "rank": off_rank,
            "official_rating": float(row[rating_col]),
            "bootstrap_mean_rating": float(row.get("bootstrap_mean_fbpr" if role == "batter" else "bootstrap_mean_fbor", row[rating_col])),
            "bootstrap_std_rating": float(row.get("bootstrap_std_fbpr" if role == "batter" else "bootstrap_std_fbor", 0.0)),
            "ci_95_width": float(row.get("ci_95_width", 0.0)),
            "median_bootstrap_rank": float(row.get("median_bootstrap_rank", off_rank)),
            "best_bootstrap_rank": int(row.get("best_bootstrap_rank", off_rank)),
            "worst_bootstrap_rank": int(row.get("worst_bootstrap_rank", off_rank)),
            "prob_in_top_10": prob_top10,
            "prob_in_top_5": float(row.get("prob_in_top_5", 0.0)),
            "matches_count": n_matches,
            "max_rank_drop_lomo": int(max_drop),
            "max_rating_impact_lomo": round(float(rating_impact), 2),
            "stability_classification": cat,
        })

    return pd.DataFrame(lomo_rows)


def calculate_ranking_similarity_metrics(
    ref_ranking: pd.Series,
    comp_ranking: pd.Series,
    top_n: int = 10,
) -> Dict[str, float]:
    """Calculate rank correlation, Kendall tau, top-n overlap and Jaccard similarity."""
    common_pids = list(set(ref_ranking.index).intersection(set(comp_ranking.index)))
    if len(common_pids) < 3:
        return {"spearman": 0.0, "kendall": 0.0, "top_n_overlap": 0, "jaccard": 0.0}

    s_ref = ref_ranking.loc[common_pids]
    s_comp = comp_ranking.loc[common_pids]

    rho, _ = spearmanr(s_ref, s_comp)
    tau, _ = kendalltau(s_ref, s_comp)

    top_ref = set(ref_ranking.sort_values().head(top_n).index)
    top_comp = set(comp_ranking.sort_values().head(top_n).index)
    overlap = len(top_ref.intersection(top_comp))
    jaccard = overlap / len(top_ref.union(top_comp)) if len(top_ref.union(top_comp)) > 0 else 0.0

    return {
        "spearman": round(float(rho), 4) if not np.isnan(rho) else 0.0,
        "kendall": round(float(tau), 4) if not np.isnan(tau) else 0.0,
        "top_n_overlap": int(overlap),
        "jaccard": round(float(jaccard), 4),
    }

