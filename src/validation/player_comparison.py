"""Statistical significance and player comparison module for Phase 9.

Performs pairwise uncertainty comparisons across Top 10 batters and Top 10 bowlers,
evaluates confidence interval overlap, derives pairwise dominance probabilities,
and identifies statistically indistinguishable performance tiers.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from src.validation.validation_config import ValidationConfig

logger = logging.getLogger(__name__)


def compare_top_players(
    bat_bootstrap: pd.DataFrame,
    bowl_bootstrap: pd.DataFrame,
    config_val: ValidationConfig,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Perform pairwise comparisons and tier clustering for Top 10 players.

    Returns:
        Tuple of (pairwise_comparisons_df, player_tier_summary).
    """
    logger.info("Evaluating statistical significance and pairwise player comparison tiers...")

    top_bat = bat_bootstrap.head(config_val.top_n).reset_index(drop=True)
    top_bowl = bowl_bootstrap.head(config_val.top_n).reset_index(drop=True)

    comparison_records: List[Dict[str, Any]] = []

    # 1. Batting Adjacent Pairwise Comparisons
    for i in range(len(top_bat) - 1):
        p1 = top_bat.iloc[i]
        p2 = top_bat.iloc[i + 1]

        diff = p1["official_fbpr"] - p2["official_fbpr"]
        # CI overlap check
        ci_overlap = not (p1["ci_95_lower"] > p2["ci_95_upper"] or p2["ci_95_lower"] > p1["ci_95_upper"])
        overlap_pct = max(0.0, min(p1["ci_95_upper"], p2["ci_95_upper"]) - max(p1["ci_95_lower"], p2["ci_95_lower"]))
        avg_width = (p1["ci_95_width"] + p2["ci_95_width"]) / 2.0
        overlap_ratio = round(overlap_pct / avg_width, 2) if avg_width > 0 else 0.0

        # Estimated dominance probability from normal approximation of diff
        se_diff = np.sqrt(p1["bootstrap_std_fbpr"]**2 + p2["bootstrap_std_fbpr"]**2)
        z = diff / se_diff if se_diff > 0 else 1.0
        prob_p1_better = round(float(0.5 * (1.0 + math.erf(z / np.sqrt(2)))), 3)

        if not ci_overlap and prob_p1_better >= 0.95:
            conclusion = f"{p1['player_name']} demonstrates statistically distinguished superior pressure rating over {p2['player_name']}."
            tier_status = "Distinct Tiers"
        elif prob_p1_better >= 0.75:
            conclusion = f"{p1['player_name']} has stronger observed clutch rating, but moderate statistical uncertainty overlap exists."
            tier_status = "Weakly Distinct"
        else:
            conclusion = f"{p1['player_name']} and {p2['player_name']} are statistically indistinguishable within uncertainty bounds."
            tier_status = "Same Statistical Tier"

        comparison_records.append({
            "role": "batter",
            "rank_pair": f"#{int(p1['official_rank'])} vs #{int(p2['official_rank'])}",
            "player_a": p1["player_name"],
            "player_b": p2["player_name"],
            "rating_a": float(p1["official_fbpr"]),
            "rating_b": float(p2["official_fbpr"]),
            "rating_difference": round(float(diff), 2),
            "ci_overlap": bool(ci_overlap),
            "ci_overlap_ratio": overlap_ratio,
            "prob_a_superior": prob_p1_better,
            "tier_classification": tier_status,
            "statistical_verdict": conclusion,
        })

    # 2. Bowling Adjacent Pairwise Comparisons
    for i in range(len(top_bowl) - 1):
        p1 = top_bowl.iloc[i]
        p2 = top_bowl.iloc[i + 1]

        diff = p1["official_fbor"] - p2["official_fbor"]
        ci_overlap = not (p1["ci_95_lower"] > p2["ci_95_upper"] or p2["ci_95_lower"] > p1["ci_95_upper"])
        overlap_pct = max(0.0, min(p1["ci_95_upper"], p2["ci_95_upper"]) - max(p1["ci_95_lower"], p2["ci_95_lower"]))
        avg_width = (p1["ci_95_width"] + p2["ci_95_width"]) / 2.0
        overlap_ratio = round(overlap_pct / avg_width, 2) if avg_width > 0 else 0.0

        se_diff = np.sqrt(p1["bootstrap_std_fbor"]**2 + p2["bootstrap_std_fbor"]**2)
        z = diff / se_diff if se_diff > 0 else 1.0
        prob_p1_better = round(float(0.5 * (1.0 + math.erf(z / np.sqrt(2)))), 3)

        if not ci_overlap and prob_p1_better >= 0.95:
            conclusion = f"{p1['player_name']} demonstrates statistically distinguished superior pressure rating over {p2['player_name']}."
            tier_status = "Distinct Tiers"
        elif prob_p1_better >= 0.75:
            conclusion = f"{p1['player_name']} has stronger observed clutch rating, but moderate statistical uncertainty overlap exists."
            tier_status = "Weakly Distinct"
        else:
            conclusion = f"{p1['player_name']} and {p2['player_name']} are statistically indistinguishable within uncertainty bounds."
            tier_status = "Same Statistical Tier"

        comparison_records.append({
            "role": "bowler",
            "rank_pair": f"#{int(p1['official_rank'])} vs #{int(p2['official_rank'])}",
            "player_a": p1["player_name"],
            "player_b": p2["player_name"],
            "rating_a": float(p1["official_fbor"]),
            "rating_b": float(p2["official_fbor"]),
            "rating_difference": round(float(diff), 2),
            "ci_overlap": bool(ci_overlap),
            "ci_overlap_ratio": overlap_ratio,
            "prob_a_superior": prob_p1_better,
            "tier_classification": tier_status,
            "statistical_verdict": conclusion,
        })

    df_comp = pd.DataFrame(comparison_records)

    tier_summary = {
        "batting_top1_clear_lead": bool(top_bat.iloc[0]["ci_95_lower"] > top_bat.iloc[1]["official_fbpr"]),
        "batting_indistinguishable_pairs": int((df_comp[(df_comp["role"] == "batter") & (df_comp["tier_classification"] == "Same Statistical Tier")].shape[0])),
        "bowling_indistinguishable_pairs": int((df_comp[(df_comp["role"] == "bowler") & (df_comp["tier_classification"] == "Same Statistical Tier")].shape[0])),
    }

    logger.info("Pairwise player comparison complete.")
    return df_comp, tier_summary
