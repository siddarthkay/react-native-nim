"""
iOS platform generators for Nim bridge with TurboModule/JSI support.
"""

from .base import CodeGenerator
from ..models import NimFunction


class CppWrapperGenerator(CodeGenerator):
    """Generates C++ wrapper code for Nim functions."""

    def generate(self) -> str:
        """Generate C++ wrapper code."""
        code = CodeGenerator._generate_header("C++ wrapper for Nim functions")
        code += """#include <string>
#include <cstring>

extern "C" {
    typedef char* NCSTRING;

    // Nim runtime
    void NimMain(void);
    void mobileNimInit(void);
    void mobileNimShutdown(void);

    // Generated function declarations
"""

        # Add function declarations
        for func in self.functions:
            ret_type = self.type_mapper.nim_to_cpp_type(func.return_type)
            params_str = ", ".join(
                [
                    f"{self.type_mapper.nim_to_cpp_type(ptype)} {name}"
                    for name, ptype in func.params
                ]
            )
            code += f"    {ret_type} {func.name}({params_str});\n"

        code += "    \n    // Memory management\n"
        code += "    void freeString(NCSTRING s);\n"
        code += "}\n"

        return code


class ObjcHeaderGenerator(CodeGenerator):
    """Generates Objective-C header file with TurboModule/JSI support."""

    def generate(self) -> str:
        """Generate Objective-C header file for New Architecture."""
        code = CodeGenerator._generate_header("Objective-C++ bridge header")

        code += """#import <React/RCTBridgeModule.h>
#include "NimBridgeSpecJSI.h"

class NimBridgeImpl : public facebook::react::NativeNimBridgeCxxSpec<NimBridgeImpl> {
public:
    NimBridgeImpl(std::shared_ptr<facebook::react::CallInvoker> jsInvoker);

"""

        # Group functions for comments
        core_funcs = []
        math_funcs = []
        data_funcs = []
        version_funcs = []

        for func in self.functions:
            js_name = func.js_name or func.name
            if js_name in ["helloWorld", "addNumbers", "getSystemInfo"]:
                core_funcs.append(func)
            elif js_name in ["fibonacci", "isPrime", "factorize"]:
                math_funcs.append(func)
            elif js_name in ["createUser", "validateEmail"]:
                data_funcs.append(func)
            elif js_name in ["getVersion"]:
                version_funcs.append(func)

        def generate_declarations(funcs, comment=None):
            result = ""
            if comment:
                result += f"    // {comment}\n"
            for func in funcs:
                js_name = func.js_name or func.name
                jsi_ret_type = self._get_jsi_return_type(func.return_type)
                jsi_params = self._build_jsi_params(func)
                result += f"    {jsi_ret_type} {js_name}(facebook::jsi::Runtime &rt{', ' + jsi_params if jsi_params else ''});\n"
            return result

        code += generate_declarations(core_funcs, "Core API")
        if math_funcs:
            code += "\n"
            code += generate_declarations(math_funcs, "Math operations")
        if data_funcs:
            code += "\n"
            code += generate_declarations(data_funcs, "Data operations")
        if version_funcs:
            code += "\n"
            code += generate_declarations(version_funcs, "Version info")

        code += """};\n\n"""
        code += f"""@interface {self.config.module_name} : NSObject <RCTBridgeModule, RCTTurboModule>\n\n@end\n"""
        return code

    def _get_jsi_return_type(self, nim_type: str) -> str:
        """Get JSI return type for a Nim type."""
        if nim_type in ["cstring", "string"]:
            return "facebook::jsi::String"
        elif nim_type == "bool":
            return "bool"
        elif nim_type in ["cint", "int", "int64"]:
            return "double"
        else:
            return "double"

    def _build_jsi_params(self, func: NimFunction) -> str:
        """Build JSI parameter list."""
        params = []
        for name, ptype in func.params:
            if ptype in ["cstring", "string"]:
                params.append(f"facebook::jsi::String {name}")
            elif ptype == "bool":
                params.append(f"bool {name}")
            else:
                params.append(f"double {name}")
        return ", ".join(params)


class ObjcBridgeGenerator(CodeGenerator):
    """Generates Objective-C++ bridge code with TurboModule/JSI support."""

    def generate(self) -> str:
        """Generate Objective-C++ bridge code for New Architecture."""
        code = CodeGenerator._generate_header("Objective-C++ bridge")
        code += f"""#import "{self.config.module_name}.h"
#include "{self.config.library_name}.h"
#import <ReactCommon/RCTTurboModule.h>

{self.config.module_name}Impl::{self.config.module_name}Impl(std::shared_ptr<facebook::react::CallInvoker> jsInvoker)
    : Native{self.config.module_name}CxxSpec(std::move(jsInvoker)) {{
    // Initialize Nim runtime
    NimMain();
    mobileNimInit();
}}

"""

        # Generate JSI method implementations
        for i, func in enumerate(self.functions):
            code += self._generate_jsi_method(
                func, is_last=(i == len(self.functions) - 1)
            )

        code += (
            """
@implementation """
            + self.config.module_name
            + """

RCT_EXPORT_MODULE()

+ (BOOL)requiresMainQueueSetup
{
    return NO;
}

- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:(const facebook::react::ObjCTurboModule::InitParams &)params
{
    return std::make_shared<"""
            + self.config.module_name
            + """Impl>(params.jsInvoker);
}

- (void)dealloc
{
    mobileNimShutdown();
}

@end
"""
        )
        return code

    def _generate_jsi_method(self, func: NimFunction, is_last: bool = False) -> str:
        """Generate JSI method implementation for New Architecture."""
        js_name = func.js_name or func.name
        ret_type = self._get_jsi_return_type(func.return_type)
        params_str = self._build_jsi_params(func)

        method_code = f"{ret_type} {self.config.module_name}Impl::{js_name}(facebook::jsi::Runtime &rt"
        if params_str:
            method_code += f", {params_str}"
        method_code += ") {\n"

        # Generate method body
        method_code += self._generate_jsi_method_body(func, js_name)
        # Last method gets one blank line, others get two
        method_code += "}\n\n" if not is_last else "}\n\n"

        return method_code

    def _generate_jsi_method_body(self, func: NimFunction, js_name: str) -> str:
        """Generate the body of a JSI method."""
        body = ""

        # Convert JSI parameters to C types and build arguments
        args = []
        for name, ptype in func.params:
            if ptype in ["cstring", "string"]:
                body += f"    std::string {name}Str = {name}.utf8(rt);\n"
                args.append(f"const_cast<NCSTRING>({name}Str.c_str())")
            elif ptype in ["cint", "int", "int64"]:
                args.append(f"static_cast<int>({name})")
            else:
                args.append(name)

        args_str = ", ".join(args)

        # Generate return statement based on return type
        # Use :: prefix only when Nim name == JS name to avoid ambiguity
        prefix = "::" if func.name == js_name else ""

        if func.return_type in ["cstring", "string"]:
            body += f"    NCSTRING result = {prefix}{func.name}({args_str});\n"
            body += f'    std::string str = result ? std::string(result) : "";\n'
            if func.memory_type == "allocated":
                body += f"    if (result) freeString(result);\n"
            body += f"    return facebook::jsi::String::createFromUtf8(rt, str);\n"
        elif func.return_type == "bool":
            body += f"    return {prefix}{func.name}({args_str}) != 0;\n"
        elif func.return_type == "int64":
            body += (
                f"    return static_cast<double>({prefix}{func.name}({args_str}));\n"
            )
        else:
            body += f"    return {prefix}{func.name}({args_str});\n"

        return body

    def _get_jsi_return_type(self, nim_type: str) -> str:
        """Get JSI return type."""
        if nim_type in ["cstring", "string"]:
            return "facebook::jsi::String"
        elif nim_type == "bool":
            return "bool"
        else:
            return "double"

    def _build_jsi_params(self, func: NimFunction) -> str:
        """Build JSI parameter list."""
        params = []
        for name, ptype in func.params:
            if ptype in ["cstring", "string"]:
                params.append(f"facebook::jsi::String {name}")
            elif ptype == "bool":
                params.append(f"bool {name}")
            else:
                params.append(f"double {name}")
        return ", ".join(params)

