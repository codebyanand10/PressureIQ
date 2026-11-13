"""Unit tests for Phase 9 sample size effects validation."""

import pandas as pd
import pytest

from src.validation.sample_size_validation import validate_sample_size_effects


def test_validate_sample_size_effects():
    """Verify that sample size validation checks shrinkage and volume correlation."""
    r_bat = pd.DataFrame({
        "player_id": [f"p{i}" for i in range(20)],
        "balls_faced": [40 + i * 10 for i in range(20)],
        "matches_count": [4 + (i // 2) for i in range(20)],
        "final_fbpr": [60.0 + i * 0.5 for i in range(20)],
        "raw_fbpr": [62.0 + i * 0.4 for i in range(20)],
        "shrinkage_factor": [0.6 + i * 0.015 for i in range(20)],
        "ci_width_fbpr": [15.0 - i * 0.3 for i in range(20)],
        "rank": list(range(1, 21)),
    })

    r_bowl = pd.DataFrame({
        "player_id": [f"b{i}" for i in range(20)],
        "legal_balls_bowled": [48 + i * 12 for i in range(20)],
        "matches_bowled": [4 + (i // 2) for i in range(20)],
        "final_fbor": [45.0 + i * 0.3 for i in range(20)],
        "raw_fbor": [46.0 + i * 0.25 for i in range(20)],
        "shrinkage_factor": [0.6 + i * 0.015 for i in range(20)],
        "ci_width_fbor": [10.0 - i * 0.2 for i in range(20)],
        "rank": list(range(1, 21)),
    })

    df_bins, metrics = validate_sample_size_effects(r_bat, r_bowl)

    assert "sample_size_tier" in df_bins.columns
    assert "mean_shrinkage_factor" in df_bins.columns
    assert "batting_volume_correlation" in metrics
    assert "bowling_volume_correlation" in metrics
    # CI width correlation should be negative (larger sample -> narrower CI)
    assert metrics["batting_ci_width_correlation"] < 0
    assert metrics["bowling_ci_width_correlation"] < 0

