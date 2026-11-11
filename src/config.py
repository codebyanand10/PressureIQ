"""Central Configuration Management for PressureIQ.

Provides cross-platform path resolution, YAML configuration loading,
directory validation, and centralized settings access using pathlib.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class ConfigurationError(Exception):
    """Raised when configuration loading, validation, or path resolution fails."""
    pass


class Config:
    """Central configuration class managing project paths and settings."""

    _instance: Optional["Config"] = None

    def __init__(self, config_file: Optional[Path | str] = None) -> None:
        """Initialize project configuration.

        Args:
            config_file: Optional explicit path to settings YAML file.
                         If omitted, resolves relative to project root.
        """
        # Resolve project root dynamically (two levels above this file: src/.. -> PressureIQ/)
        self.project_root: Path = Path(__file__).resolve().parent.parent

        # Locate settings file
        if config_file is not None:
            self.config_path: Path = Path(config_file).resolve()
        else:
            self.config_path = self.project_root / "config" / "settings.yaml"

        # Load YAML settings
        self.raw_settings: Dict[str, Any] = self._load_yaml(self.config_path)

        # Parse sections
        self.project_settings: Dict[str, Any] = self.raw_settings.get("project", {})
        self.data_settings: Dict[str, Any] = self.raw_settings.get("data", {})
        self.output_settings: Dict[str, Any] = self.raw_settings.get("outputs", {})
        self.dashboard_settings: Dict[str, Any] = self.raw_settings.get("dashboard", {})
        self.logging_settings: Dict[str, Any] = self.raw_settings.get("logging", {})

        # Resolve core project directories
        self.data_raw_dir: Path = self.project_root / self.data_settings.get("raw_dir", "data/raw")
        self.data_processed_dir: Path = self.project_root / self.data_settings.get(
            "processed_dir", "data/processed"
        )
        self.data_intermediate_dir: Path = self.project_root / self.data_settings.get(
            "intermediate_dir", "data/intermediate"
        )
        self.data_external_dir: Path = self.project_root / self.data_settings.get(
            "external_dir", "data/external"
        )

        self.rankings_dir: Path = self.project_root / self.output_settings.get(
            "rankings_dir", "outputs/rankings"
        )
        self.charts_dir: Path = self.project_root / self.output_settings.get(
            "charts_dir", "outputs/charts"
        )
        self.reports_dir: Path = self.project_root / self.output_settings.get(
            "reports_dir", "outputs/reports"
        )
        self.logs_dir: Path = self.project_root / self.output_settings.get(
            "logs_dir", "outputs/logs"
        )

        self.notebooks_dir: Path = self.project_root / "notebooks"
        self.dashboard_dir: Path = self.project_root / "dashboard"
        self.src_dir: Path = self.project_root / "src"
        self.tests_dir: Path = self.project_root / "tests"

        # Log file path
        log_filename = self.logging_settings.get("filename", "pressureiq.log")
        self.log_file: Path = self.logs_dir / log_filename

    @classmethod
    def get_instance(cls, config_file: Optional[Path | str] = None) -> "Config":
        """Singleton accessor for global configuration."""
        if cls._instance is None:
            cls._instance = cls(config_file=config_file)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for unit testing)."""
        cls._instance = None

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file with clear error handling."""
        if not path.is_file():
            raise ConfigurationError(
                f"Configuration file not found at: {path}. "
                f"Please ensure config/settings.yaml exists in the project root."
            )
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if not isinstance(content, dict):
                    raise ConfigurationError(
                        f"Configuration file at {path} must contain a valid YAML dictionary."
                    )
                return content
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing YAML configuration file {path}: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Unexpected error loading configuration from {path}: {e}") from e

    def validate_directories(self, create_missing: bool = True) -> Dict[str, bool]:
        """Verify and optionally create key application directories.

        Args:
            create_missing: If True, automatically creates missing directories.

        Returns:
            Dictionary of directory names and their existence status.
        """
        dirs_to_check = {
            "data_raw": self.data_raw_dir,
            "data_processed": self.data_processed_dir,
            "data_intermediate": self.data_intermediate_dir,
            "data_external": self.data_external_dir,
            "outputs_rankings": self.rankings_dir,
            "outputs_charts": self.charts_dir,
            "outputs_reports": self.reports_dir,
            "outputs_logs": self.logs_dir,
            "notebooks": self.notebooks_dir,
            "dashboard": self.dashboard_dir,
        }

        status: Dict[str, bool] = {}
        for name, dir_path in dirs_to_check.items():
            if create_missing and not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
            status[name] = dir_path.is_dir()

        return status

    @property
    def project_name(self) -> str:
        """Name of the project."""
        return str(self.project_settings.get("name", "PressureIQ"))

    @property
    def version(self) -> str:
        """Project version string."""
        return str(self.project_settings.get("version", "0.1.0"))

    @property
    def environment(self) -> str:
        """Runtime environment name."""
        return os.getenv("APP_ENV", self.project_settings.get("environment", "development"))

    @property
    def log_level(self) -> str:
        """Effective logging level string."""
        return os.getenv("LOG_LEVEL", self.logging_settings.get("level", "INFO")).upper()


# Default singleton instance
config = Config.get_instance()

