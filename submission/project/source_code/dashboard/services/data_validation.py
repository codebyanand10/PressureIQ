"""PressureIQ Validation Gate and Integrity Auditor.

Ensures that dashboard displays adhere to Section 1 completion gate requirements.
Monitors Phase 9 scorecard outcomes and triggers warnings if any dimension fails.
"""

from __future__ import annotations
from typing import Any, Dict, List
import pandas as pd
from dashboard.services.data_loader import load_validation_scorecard, load_leakage_audit


def get_validation_health_summary() -> Dict[str, Any]:
    """Audit Phase 9 scorecard and leakage results to determine validation gate status.
    
    Returns:
        dict with overall status (PASS, WARNING, FAIL), failure lists, and counts.
    """
    scorecard = load_validation_scorecard()
    leakage = load_leakage_audit()

    critical_failures: List[str] = []
    warnings: List[str] = []
    batting_pass = True
    bowling_pass = True

    if not scorecard.empty:
        for _, row in scorecard.iterrows():
            dim = row.get("dimension", "Unknown")
            bat_res = str(row.get("batting_result", "FAIL")).upper()
            bowl_res = str(row.get("bowling_result", "FAIL")).upper()

            if "FAIL" in bat_res:
                critical_failures.append(f"Batting: {dim}")
                batting_pass = False
            elif "WARN" in bat_res:
                warnings.append(f"Batting: {dim}")

            if "FAIL" in bowl_res:
                critical_failures.append(f"Bowling: {dim}")
                bowling_pass = False
            elif "WARN" in bowl_res:
                warnings.append(f"Bowling: {dim}")

    # Check leakage audit
    if not leakage.empty:
        for _, row in leakage.iterrows():
            cid = row.get("check_id", "")
            res = str(row.get("result", "PASS")).upper()
            sev = str(row.get("severity", "HIGH")).upper()
            if "FAIL" in res:
                critical_failures.append(f"Leakage Check {cid} ({sev})")

    is_fully_validated = len(critical_failures) == 0

    return {
        "is_fully_validated": is_fully_validated,
        "batting_robustness_status": "PASS" if batting_pass else "FAIL",
        "bowling_robustness_status": "PASS" if bowling_pass else "FAIL",
        "critical_failures": critical_failures,
        "warnings": warnings,
        "total_tests_passed": 10 if is_fully_validated else 10 - len(critical_failures),
        "total_dimensions": 10,
        "leakage_audit_status": "PASS" if not any("Leakage" in f for f in critical_failures) else "FAIL",
    }

