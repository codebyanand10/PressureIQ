"""Tests for dashboard validation gate and integrity monitoring."""

from __future__ import annotations
import pytest
from dashboard.services.data_validation import get_validation_health_summary


def test_validation_health_summary():
    """Verify that Phase 9 validation gate correctly detects PASS/FAIL status."""
    health = get_validation_health_summary()
    assert isinstance(health, dict)
    assert "is_fully_validated" in health
    assert "batting_robustness_status" in health
    assert "bowling_robustness_status" in health
    assert "critical_failures" in health
    # In Phase 9, all 10 passed
    assert health["is_fully_validated"] is True
    assert health["batting_robustness_status"] == "PASS"
    assert health["bowling_robustness_status"] == "PASS"
    assert len(health["critical_failures"]) == 0

