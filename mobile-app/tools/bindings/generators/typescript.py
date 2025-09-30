"""
TypeScript interface generator for Nim bridge.
"""

from .base import CodeGenerator


class TypeScriptInterfaceGenerator(CodeGenerator):
    """Generates TypeScript TurboModule spec definitions."""

    def generate(self) -> str:
        """Generate TypeScript TurboModule spec."""
        code = "import type { TurboModule } from 'react-native';\n"
        code += "import { TurboModuleRegistry } from 'react-native';\n\n"
        code += "export interface Spec extends TurboModule {\n"

        # Group functions for comments
        core_funcs = []
        math_funcs = []
        data_funcs = []
        version_funcs = []

        for func in self.functions:
            js_name = func.js_name or func.name
            if js_name in ['helloWorld', 'addNumbers', 'getSystemInfo']:
                core_funcs.append(func)
            elif js_name in ['fibonacci', 'isPrime', 'factorize']:
                math_funcs.append(func)
            elif js_name in ['createUser', 'validateEmail']:
                data_funcs.append(func)
            elif js_name in ['getVersion']:
                version_funcs.append(func)

        def generate_functions(funcs, comment=None):
            result = ""
            if comment:
                result += f"  // {comment}\n"
            for func in funcs:
                js_name = func.js_name or func.name
                ret_type = self.type_mapper.nim_to_ts_type(func.return_type)
                params_str = ', '.join([f"{name}: {self.type_mapper.nim_to_ts_type(ptype)}"
                                       for name, ptype in func.params])
                result += f"  readonly {js_name}: ({params_str}) => {ret_type};\n"
            return result

        code += generate_functions(core_funcs, "Core API")
        if math_funcs:
            code += "\n"
            code += generate_functions(math_funcs, "Math operations")
        if data_funcs:
            code += "\n"
            code += generate_functions(data_funcs, "Data operations")
        if version_funcs:
            code += "\n"
            code += generate_functions(version_funcs, "Version info")

        code += "}\n\n"
        code += f"export default TurboModuleRegistry.getEnforcing<Spec>('{self.config.module_name}');"
        return code