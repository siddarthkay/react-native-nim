#!/usr/bin/env python3
"""
Automatic binding generator for Nim -> React Native
Parses Nim exported functions and generates all necessary bridge code
"""

from pathlib import Path
from bindings import GeneratorConfig, BindingGenerator


def main():
    """Main entry point."""
    config_file = Path(__file__).parent / "generator_config.json"

    try:
        config = GeneratorConfig.from_file(config_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        print("Please ensure generator_config.json exists and contains all required fields.")
        return

    generator = BindingGenerator(config)

    if not generator.discover_functions():
        return

    generator.generate_all()
    generator.print_summary()


if __name__ == "__main__":
    main()