"""Tests for Data Integrity Auditor."""

from pathlib import Path
from src.final_audit.data_integrity_audit import DataIntegrityAuditor


def test_data_integrity_audit():
    """Verify raw datasets, delivery cardinality, and temporal causality."""
    root_dir = Path(__file__).resolve().parents[2]
    auditor = DataIntegrityAuditor(root_dir)
    report = auditor.audit()

    assert report.raw_files_intact is True
    assert report.delivery_count == 200999
    assert report.match_count == 867
    assert report.duplicate_deliveries_count == 0
    assert report.causality_valid is True
    assert report.is_valid is True
    assert len(report.raw_file_checksums) == 6

