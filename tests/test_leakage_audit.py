"""Unit tests for Phase 9 data leakage and methodology audit."""

import pandas as pd
import pytest

from src.validation.leakage_audit import execute_leakage_audit


def test_execute_leakage_audit():
    """Verify that the 12-dimension leakage audit runs and returns expected format."""
    df_audit = execute_leakage_audit()

    assert len(df_audit) == 12
    assert "check_id" in df_audit.columns
    assert "test_performed" in df_audit.columns
    assert "result" in df_audit.columns
    assert "severity" in df_audit.columns
    assert "evidence" in df_audit.columns

    # Verify all results are valid status strings
    assert df_audit["result"].isin(["PASS", "WARNING", "FAIL", "NOT TESTABLE"]).all()

    # Zero critical FAILs allowed
    critical_fails = df_audit[(df_audit["severity"] == "CRITICAL") & (df_audit["result"] == "FAIL")]
    assert len(critical_fails) == 0, f"Critical leakage check failed: {critical_fails.to_dict('records')}"

