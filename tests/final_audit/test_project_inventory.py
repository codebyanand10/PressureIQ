"""Tests for Project Inventory Scanner."""

from pathlib import Path
from src.final_audit.project_inventory import ProjectInventory, compute_sha256


def test_project_inventory_scan():
    """Verify inventory scanning finds files and categorizes them."""
    root_dir = Path(__file__).resolve().parents[2]
    scanner = ProjectInventory(root_dir)
    result = scanner.scan()

    assert result.total_files > 100
    assert result.total_size_bytes > 1_000_000
    assert len(result.missing_required_files) == 0
    assert "source_code" in result.category_counts
    assert "raw_data" in result.category_counts
    assert "rankings" in result.category_counts


def test_compute_sha256(tmp_path):
    """Verify SHA-256 computation."""
    test_file = tmp_path / "sample.txt"
    test_file.write_text("PressureIQ Cricket Analytics", encoding="utf-8")

    digest = compute_sha256(test_file)
    assert isinstance(digest, str)
    assert len(digest) == 64

