"""
Nim source code parser for extracting exported functions.
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional

from .models import NimFunction


class NimParser:
    """Parses Nim files to extract exported functions."""

    def parse_nim_exports(self, nim_file: Path) -> List[NimFunction]:
        """Parse Nim file and extract exported functions."""
        try:
            with open(nim_file, 'r') as f:
                content = f.read()
        except IOError as e:
            print(f"Error reading {nim_file}: {e}")
            return []

        return self._extract_functions(content)

    def _extract_functions(self, content: str) -> List[NimFunction]:
        """Extract functions from Nim source content."""
        functions = []

        # Regex to match exported Nim procs with optional doc comments
        pattern = r'proc\s+(\w+)\*\s*\((.*?)\)\s*:\s*(\w+)\s*{[^}]*exportc[^}]*}'

        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            func_name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3)

            # Parse memory annotation for string returns
            memory_type = self._detect_memory_type(content, match, return_type)

            # Parse parameters
            params = self._parse_parameters(params_str)

            functions.append(NimFunction(func_name, return_type, params, memory_type))

        return functions

    def _detect_memory_type(self, content: str, match: re.Match, return_type: str) -> Optional[str]:
        """Detect memory management type from annotations or implementation."""
        if return_type not in ['cstring', 'string']:
            return None

        # Check for doc comment annotations
        func_start_pos = match.start()
        lines_before = content[:func_start_pos].split('\n')

        for i in range(len(lines_before) - 1, max(0, len(lines_before) - 5), -1):
            line = lines_before[i].strip()
            if '@literal' in line:
                return 'literal'
            elif '@allocated' in line:
                return 'allocated'
            elif line and not line.startswith('##'):
                break

        # Fallback: detect from implementation
        func_start = match.end()
        next_proc = content.find('\nproc ', func_start)
        func_body = content[func_start:next_proc if next_proc != -1 else len(content)]

        return 'allocated' if 'allocCString' in func_body else 'literal'

    @staticmethod
    def _parse_parameters(params_str: str) -> List[Tuple[str, str]]:
        """Parse parameter string into list of (name, type) tuples."""
        params = []
        if params_str.strip():
            for param in params_str.split(','):
                param = param.strip()
                if ':' in param:
                    name, ptype = param.split(':', 1)
                    params.append((name.strip(), ptype.strip()))
        return params