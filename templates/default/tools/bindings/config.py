"""
Configuration management for Nim bridge generator.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class GeneratorConfig:
    """Configuration for the binding generator."""
    nim_dir: str
    output_dir: str
    package_name: str
    module_name: str
    library_name: str
    generate_ios: bool
    generate_android: bool
    generate_typescript: bool
    data: dict = None

    def __post_init__(self):
        """Initialize data if not provided."""
        if self.data is None:
            self.data = {}

    @classmethod
    def from_file(cls, config_file: Path) -> 'GeneratorConfig':
        """Load configuration from a JSON file."""
        if not config_file.exists():
            raise FileNotFoundError(f"Config file {config_file} not found. Please create it first.")

        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid config file {config_file}: {e}")

        # Extract known fields and keep full data
        known_fields = {
            'nim_dir', 'output_dir', 'package_name', 'module_name',
            'library_name', 'generate_ios', 'generate_android', 'generate_typescript'
        }

        # Validate required fields
        missing_fields = known_fields - set(config_data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields in config: {missing_fields}")

        kwargs = {k: config_data[k] for k in known_fields}
        kwargs['data'] = config_data

        return cls(**kwargs)

    def to_file(self, config_file: Path) -> None:
        """Save configuration to a JSON file."""
        config_data = {
            'nim_dir': self.nim_dir,
            'output_dir': self.output_dir,
            'package_name': self.package_name,
            'module_name': self.module_name,
            'library_name': self.library_name,
            'generate_ios': self.generate_ios,
            'generate_android': self.generate_android,
            'generate_typescript': self.generate_typescript
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)