"""Unit tests for Phase 9 robustness scorecard synthesis."""

import pandas as pd
import pytest

from src.validation.robustness_scorecard import generate_robustness_scorecard


def test_generate_robustness_scorecard():
    """Verify that the 10-dimension robustness scorecard compiles all dimensions with PASS/WARNING/FAIL."""
    stab_metrics = {"batting_top10_overlap_bootstrap": 9, "bowling_top10_overlap_bootstrap": 9}
    weight_summary = pd.DataFrame()
    eligibility_summary = pd.DataFrame()
    pressure_summary = pd.DataFrame()
    comp_fairness_metrics = {"ipl_top10_batters_count": 6, "t20i_top10_batters_count": 4}
    role_summary_metrics = {"pace_bowlers_in_top10": 5, "spin_bowlers_in_top10": 5}
    sample_size_metrics = {"batting_volume_correlation": 0.463, "bowling_volume_correlation": 0.231}
    baseline_metrics = {"batting_baseline_spearman": 0.94, "batting_baseline_top10_overlap": 9}
    leakage_audit_df = pd.DataFrame([{"result": "PASS"} for _ in range(12)])

    scorecard_df = generate_robustness_scorecard(
        bat_stability_metrics=stab_metrics,
        weight_summary=weight_summary,
        eligibility_summary=eligibility_summary,
        pressure_summary=pressure_summary,
        comp_fairness_metrics=comp_fairness_metrics,
        role_summary_metrics=role_summary_metrics,
        sample_size_metrics=sample_size_metrics,
        baseline_metrics=baseline_metrics,
        leakage_audit_df=leakage_audit_df,
    )

    assert len(scorecard_df) == 10
    assert "dimension" in scorecard_df.columns
    assert "batting_result" in scorecard_df.columns
    assert "bowling_result" in scorecard_df.columns
    assert "supporting_evidence" in scorecard_df.columns
    assert (scorecard_df["batting_result"].isin(["PASS", "WARNING", "FAIL"])).all()
    assert (scorecard_df["bowling_result"].isin(["PASS", "WARNING", "FAIL"])).all()

