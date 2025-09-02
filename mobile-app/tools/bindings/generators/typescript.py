"""
TypeScript interface generator for Nim bridge.
"""

from .base import CodeGenerator


class TypeScriptInterfaceGenerator(CodeGenerator):
    """Generates TypeScript interface definitions."""

    def generate(self) -> str:
        """Generate TypeScript interface."""
        code = CodeGenerator._generate_header("TypeScript interface for Nim bridge")
        code += "export interface NimBridge {\n"

        for func in self.functions:
            ret_type = self.type_mapper.nim_to_ts_type(func.return_type)
            params_str = ', '.join([f"{name}: {self.type_mapper.nim_to_ts_type(ptype)}"
                                   for name, ptype in func.params])
            code += f"  {func.name}({params_str}): {ret_type};\n"

        code += "}\n"
        return code