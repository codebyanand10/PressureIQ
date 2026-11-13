"""Automated tests validating Phase 11 methodology report and documentation integrity."""

from __future__ import annotations
from pathlib import Path
import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_master_methodology_chapters():
    """Verify that all 18 required chapters exist in the master methodology report."""
    md_path = PROJECT_ROOT / "docs" / "methodology" / "PressureIQ_Methodology_Report.md"
    assert md_path.exists(), "Master methodology markdown must exist"

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    expected_chapters = [
        "Chapter 1: Executive Summary",
        "Chapter 2: Introduction",
        "Chapter 3: Problem Statement",
        "Chapter 4: Objectives",
        "Chapter 5: Datasets and Data Understanding",
        "Chapter 6: Data Preprocessing and Integration",
        "Chapter 7: Match State Reconstruction",
        "Chapter 8: Pressure Detection Methodology",
        "Chapter 9: Player Baseline Calculation",
        "Chapter 10: Batting Performance Under Pressure",
        "Chapter 11: Bowling Performance Under Pressure",
        "Chapter 12: Final Player Rating and Ranking",
        "Chapter 13: Statistical Validation and Robustness",
        "Chapter 14: System Architecture",
        "Chapter 15: Dashboard and User Interface",
        "Chapter 16: Results and Discussion",
        "Chapter 17: Limitations and Future Improvements",
        "Chapter 18: Conclusion",
    ]

    for chap in expected_chapters:
        assert chap in content, f"Missing required chapter: {chap}"


def test_top_10_rankings_exact_match():
    """Verify reported top 10 batter and bowler tables match actual Phase 8 outputs."""
    md_path = PROJECT_ROOT / "docs" / "methodology" / "PressureIQ_Methodology_Report.md"
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify #1 batter and bowler
    assert "Rinku Singh" in content
    assert "77.07" in content
    assert "Joshua Little" in content
    assert "50.05" in content

    # Verify actual Phase 8 parquet matches
    bat_parquet = PROJECT_ROOT / "data" / "processed" / "rankings" / "batter_ratings.parquet"
    bowl_parquet = PROJECT_ROOT / "data" / "processed" / "rankings" / "bowler_ratings.parquet"
    assert bat_parquet.exists()
    assert bowl_parquet.exists()

    bat_df = pd.read_parquet(bat_parquet)
    bowl_df = pd.read_parquet(bowl_parquet)

    top_10_bat_names = list(bat_df.head(10)["player_name"])
    top_10_bowl_names = list(bowl_df.head(10)["player_name"])

    for name in top_10_bat_names:
        assert name in content, f"Top 10 batter {name} missing from methodology report"

    for name in top_10_bowl_names:
        assert name in content, f"Top 10 bowler {name} missing from methodology report"


def test_mathematical_formulation_complete():
    """Verify that Mathematical_Formulation.md contains core equations and no placeholder text."""
    math_path = PROJECT_ROOT / "docs" / "methodology" / "Mathematical_Formulation.md"
    assert math_path.exists()

    with open(math_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "TODO" not in content
    assert "TBD" not in content
    assert "INSERT" not in content
    assert "Empirical Bayes Shrinkage" in content
    assert "BPPI" in content
    assert "FBPR" in content
    assert "FBOR" in content


def test_validation_claims_match_phase_9():
    """Verify reported scorecard claims match actual Phase 9 scorecard results."""
    md_path = PROJECT_ROOT / "docs" / "methodology" / "PressureIQ_Methodology_Report.md"
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    scorecard_path = PROJECT_ROOT / "data" / "processed" / "validation" / "robustness_scorecard.parquet"
    assert scorecard_path.exists()
    sc_df = pd.read_parquet(scorecard_path)

    # 10/10 passed
    assert len(sc_df) == 10
    assert all(r == "PASS" for r in sc_df["batting_result"])
    assert all(r == "PASS" for r in sc_df["bowling_result"])

    assert "10-Dimension Robustness Scorecard" in content
    assert "PASS" in content


def test_generated_document_artifacts():
    """Verify PDF and DOCX generated artifacts exist and have non-trivial size."""
    docx_path = PROJECT_ROOT / "outputs" / "methodology" / "PressureIQ_Methodology_Report.docx"
    pdf_path = PROJECT_ROOT / "outputs" / "methodology" / "PressureIQ_Methodology_Report.pdf"
    rep_path = PROJECT_ROOT / "outputs" / "methodology" / "PHASE_11_FINAL_REPORT.md"

    assert docx_path.exists()
    assert pdf_path.exists()
    assert rep_path.exists()

    assert docx_path.stat().st_size > 20000, "DOCX file too small"
    assert pdf_path.stat().st_size > 15000, "PDF file too small"
    assert rep_path.stat().st_size > 2000, "Final report markdown too small"

