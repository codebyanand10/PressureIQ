"""Unit tests for Phase 9 ranking stability and LOMO analysis."""

import pandas as pd
import pytest

from src.validation.ranking_stability import (
    calculate_ranking_similarity_metrics,
    evaluate_ranking_stability,
)


def test_ranking_similarity_metrics():
    """Verify Spearman, Kendall, overlap, and Jaccard metrics."""
    s1 = pd.Series([1, 2, 3, 4, 5], index=["p1", "p2", "p3", "p4", "p5"])
    s2 = pd.Series([1, 2, 3, 4, 5], index=["p1", "p2", "p3", "p4", "p5"])

    metrics = calculate_ranking_similarity_metrics(s1, s2, top_n=3)
    assert metrics["spearman"] == 1.0
    assert metrics["kendall"] == 1.0
    assert metrics["top_n_overlap"] == 3
    assert metrics["jaccard"] == 1.0

    # Inverted ranking
    s_inv = pd.Series([5, 4, 3, 2, 1], index=["p1", "p2", "p3", "p4", "p5"])
    metrics_inv = calculate_ranking_similarity_metrics(s1, s_inv, top_n=2)
    assert metrics_inv["spearman"] == -1.0
    assert metrics_inv["top_n_overlap"] == 0


def test_evaluate_ranking_stability_structure():
    """Verify stability evaluation outputs expected columns and bounds."""
    r_bat = pd.DataFrame({
        "player_id": ["b1", "b2"],
        "player_name": ["Batter 1", "Batter 2"],
        "rank": [1, 2],
        "final_fbpr": [75.0, 70.0],
        "strike_rate": [180.0, 160.0],
    })
    r_bowl = pd.DataFrame({
        "player_id": ["bw1", "bw2"],
        "player_name": ["Bowler 1", "Bowler 2"],
        "rank": [1, 2],
        "final_fbor": [50.0, 48.0],
        "economy_rate": [7.5, 8.0],
    })
    boot_bat = pd.DataFrame({
        "player_id": ["b1", "b2"],
        "bootstrap_mean_fbpr": [74.5, 69.8],
        "bootstrap_std_fbpr": [2.1, 2.5],
        "ci_95_width": [8.2, 9.8],
        "median_bootstrap_rank": [1.0, 2.0],
        "best_bootstrap_rank": [1, 2],
        "worst_bootstrap_rank": [2, 3],
        "prob_in_top_10": [1.0, 0.9],
        "prob_in_top_5": [1.0, 0.9],
    })
    boot_bowl = pd.DataFrame({
        "player_id": ["bw1", "bw2"],
        "bootstrap_mean_fbor": [49.8, 47.9],
        "bootstrap_std_fbor": [1.2, 1.4],
        "ci_95_width": [4.7, 5.5],
        "median_bootstrap_rank": [1.0, 2.0],
        "best_bootstrap_rank": [1, 2],
        "worst_bootstrap_rank": [2, 3],
        "prob_in_top_10": [1.0, 0.9],
        "prob_in_top_5": [1.0, 0.9],
    })
    m_bat = pd.DataFrame([
        {"player_id": "b1", "match_id": 101, "hp_runs": 40, "hp_balls": 20},
        {"player_id": "b1", "match_id": 102, "hp_runs": 30, "hp_balls": 15},
        {"player_id": "b2", "match_id": 101, "hp_runs": 25, "hp_balls": 15},
    ])
    m_bowl = pd.DataFrame([
        {"player_id": "bw1", "match_id": 101, "hp_wickets": 2, "hp_dots": 10, "hp_legal_balls": 24, "hp_runs_conceded": 25},
        {"player_id": "bw2", "match_id": 101, "hp_wickets": 1, "hp_dots": 8, "hp_legal_balls": 24, "hp_runs_conceded": 30},
    ])

    bat_s, bowl_s, metrics = evaluate_ranking_stability(
        r_bat, r_bowl, boot_bat, boot_bowl, m_bat, m_bowl, top_n=2
    )

    assert "stability_classification" in bat_s.columns
    assert "max_rank_drop_lomo" in bat_s.columns
    assert len(bat_s) == 2
    assert "batting_top10_overlap_bootstrap" in metrics

