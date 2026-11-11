"""Unit tests for src/config.py.

Verifies project root resolution, YAML loading, directory path generation,
and missing configuration handling.
"""

from __future__ import annotations

import os
from pathlib import Path
import pytest
import yaml

from src.config import Config, ConfigurationError


def test_config_singleton_and_root():
    """Verify that Config correctly resolves project root."""
    config = Config.get_instance()
    assert config.project_root.is_dir()
    assert (config.project_root / "config" / "settings.yaml").is_file()
    assert config.project_name == "PressureIQ"
    assert config.version == "0.1.0"


def test_config_paths_generation():
    """Verify that all core path properties are valid Path objects."""
    config = Config.get_instance()
    assert isinstance(config.data_raw_dir, Path)
    assert isinstance(config.data_processed_dir, Path)
    assert isinstance(config.data_intermediate_dir, Path)
    assert isinstance(config.rankings_dir, Path)
    assert isinstance(config.charts_dir, Path)
    assert isinstance(config.reports_dir, Path)
    assert isinstance(config.logs_dir, Path)
    assert isinstance(config.notebooks_dir, Path)
    assert isinstance(config.dashboard_dir, Path)


def test_config_directory_validation(tmp_path: Path):
    """Verify that directory validation succeeds and creates missing dirs when asked."""
    dummy_yaml = tmp_path / "settings.yaml"
    settings_data = {
        "project": {"name": "TestIQ", "version": "0.0.1"},
        "data": {
            "raw_dir": str(tmp_path / "raw"),
            "processed_dir": str(tmp_path / "processed"),
            "intermediate_dir": str(tmp_path / "intermediate"),
            "external_dir": str(tmp_path / "external"),
        },
        "outputs": {
            "rankings_dir": str(tmp_path / "rankings"),
            "charts_dir": str(tmp_path / "charts"),
            "reports_dir": str(tmp_path / "reports"),
            "logs_dir": str(tmp_path / "logs"),
        },
        "logging": {"level": "DEBUG", "filename": "test.log"},
    }
    with open(dummy_yaml, "w", encoding="utf-8") as f:
        yaml.dump(settings_data, f)

    cfg = Config(config_file=dummy_yaml)
    status = cfg.validate_directories(create_missing=True)
    assert all(status.values())
    assert (tmp_path / "raw").is_dir()
    assert (tmp_path / "logs").is_dir()


def test_config_missing_file_handling(tmp_path: Path):
    """Verify that ConfigurationError is raised when config file does not exist."""
    missing_file = tmp_path / "non_existent_config.yaml"
    with pytest.raises(ConfigurationError) as exc_info:
        Config(config_file=missing_file)
    assert "Configuration file not found" in str(exc_info.value)


def test_config_invalid_yaml(tmp_path: Path):
    """Verify that ConfigurationError is raised on invalid YAML syntax."""
    corrupted_yaml = tmp_path / "corrupted.yaml"
    corrupted_yaml.write_text("invalid: yaml: [unclosed", encoding="utf-8")
    with pytest.raises(ConfigurationError) as exc_info:
        Config(config_file=corrupted_yaml)
    assert "Error parsing YAML" in str(exc_info.value)
