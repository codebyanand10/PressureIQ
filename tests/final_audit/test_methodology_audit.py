"""Tests for Methodology & Mathematical Auditor."""

from pathlib import Path
from src.final_audit.methodology_audit import MethodologyAuditor


def test_methodology_audit():
    """Verify mathematical formula alignment and pressure separation."""
    root_dir = Path(__file__).resolve().parents[2]
    auditor = MethodologyAuditor(root_dir)
    report = auditor.audit()

    assert report.is_fully_aligned is True
    assert report.pressure_model_valid is True
    assert report.baseline_model_valid is True
    assert report.rating_weights_aligned is True
    assert len(report.verification_items) == 8
    assert len(report.unresolved_edge_cases) >= 3

