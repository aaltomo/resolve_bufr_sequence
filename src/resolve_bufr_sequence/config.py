#!/usr/bin/env python3
"""
Configuration module for BUFR sequence resolution.
Handles paths and version information for eccodes.
"""

import os
from pathlib import Path
from typing import Dict


class Config:
    """Configuration class for BUFR sequence resolution."""

    def __init__(self) -> None:
        # Default configuration
        self.codes_version = os.environ.get("ECCODES_VERSION", "2.41.0")
        self.wmo_table_number = os.environ.get("WMO_TABLE_NUMBER", "37")

        # Determine the root path based on OS
        self.root_path = self._get_root_path()

        # Configure file paths
        self.sequence_file = self._build_path("sequence.def")
        self.element_file = self._build_path("element.table")
        self.centre_file = self._build_path("codetables/1033.table")

        # Validation
        self._validate_paths()

    def _get_root_path(self) -> Path:
        """Determine the root path for eccodes definitions based on environment and OS."""
        # Try to get from environment variable first
        if "ECCODES_DEFINITION_PATH" in os.environ:
            return Path(os.environ["ECCODES_DEFINITION_PATH"])

        # Default paths based on common installations
        if os.path.exists("/opt/homebrew"):  # macOS with Homebrew
            return Path(
                f"/opt/homebrew/Cellar/eccodes/{self.codes_version}/share/eccodes/definitions/bufr/tables/0/wmo"
            )
        elif os.path.exists("/usr/share/eccodes"):  # Linux with system-installed eccodes
            return Path("/usr/share/eccodes/definitions/bufr/tables/0/wmo")
        else:
            # Fallback to current directory (will fail validation if files don't exist)
            return Path.cwd()

    def _build_path(self, relative_path: str) -> Path:
        """Build a path relative to the root path and WMO table number."""
        return self.root_path / self.wmo_table_number / relative_path

    def _validate_paths(self) -> None:
        """Validate that the configured paths exist."""
        required_files = [self.sequence_file, self.element_file, self.centre_file]
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}. Is eccodes installed?")

    def to_dict(self) -> Dict[str, str]:
        """Convert configuration to dictionary for display."""
        return {
            "codes_version": self.codes_version,
            "wmo_table_number": self.wmo_table_number,
            "root_path": str(self.root_path),
            "sequence_file": str(self.sequence_file),
            "element_file": str(self.element_file),
            "centre_file": str(self.centre_file),
        }


# Global configuration instance
config = Config()
