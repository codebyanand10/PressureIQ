"""Tests for Competition Requirements Traceability Auditor."""

from pathlib import Path
from src.final_audit.competition_requirements import CompetitionRequirementsAuditor


def test_competition_requirements_audit():
    """Verify all 11 competition requirements pass."""
    root_dir = Path(__file__).resolve().parents[2]
    auditor = CompetitionRequirementsAuditor(root_dir)
    result = auditor.audit()

    assert result.total_requirements == 11
    assert result.fail_count == 0
    assert result.pass_count >= 10
    assert result.is_fully_passing

    # Verify markdown generation without tabulate
    md = result.to_markdown()
    assert "| Requirement ID |" in md
    assert "REQ-01" in md
    assert "REQ-02" in md

