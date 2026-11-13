"""Tests for Statistical Validity Auditor."""

from pathlib import Path
from src.final_audit.statistical_audit import StatisticalAuditor


def test_statistical_validity_audit():
    """Verify statistical validation results and leakage audit."""
    root_dir = Path(__file__).resolve().parents[2]
    auditor = StatisticalAuditor(root_dir)
    result = auditor.audit()

    assert result.total_dimensions_checked == 10
    assert result.dimensions_passed == 10
    assert result.data_leakage_detected is False
    assert result.leakage_failures_count == 0
    assert result.batting_readiness == "ROBUST"
    assert result.bowling_readiness == "ROBUST_WITH_DISCLOSURES"
    assert result.is_statistically_sound is True

