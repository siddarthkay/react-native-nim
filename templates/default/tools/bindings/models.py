"""
Data models and type mapping for Nim bridge generator.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

from .config import GeneratorConfig


@dataclass
class NimFunction:
    """Represents a Nim function with its metadata."""
    name: str
    return_type: str
    params: List[Tuple[str, str]]  # List of (name, type) tuples
    memory_type: Optional[str] = None  # 'literal' or 'allocated' for string returns
    js_name: Optional[str] = None  # Optional JavaScript/TypeScript name mapping


class TypeMapper:
    """Handles type conversions between Nim and target languages."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.type_mappings = config.data.get('type_mappings', {})

    def nim_to_cpp_type(self, nim_type: str) -> str:
        """Convert Nim type to C++ type."""
        cpp_mappings = self.type_mappings.get('cpp', {})
        return cpp_mappings.get(nim_type, nim_type)

    def nim_to_ts_type(self, nim_type: str) -> str:
        """Convert Nim type to TypeScript type."""
        ts_mappings = self.type_mappings.get('typescript', {})
        return ts_mappings.get(nim_type, 'any')