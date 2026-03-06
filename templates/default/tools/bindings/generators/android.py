"""
Android platform generators for Nim bridge (Kotlin/JNI).
"""

from typing import List

from .base import CodeGenerator
from ..models import NimFunction
from ..config import GeneratorConfig


class AndroidKotlinGenerator(CodeGenerator):
    """Generates Android Kotlin module code."""

    def __init__(self, functions: List[NimFunction], config: GeneratorConfig):
        super().__init__(functions, config)

    def generate(self) -> str:
        """Generate Android Kotlin module."""
        code = self._generate_kotlin_header()
        code += self._generate_native_declarations()
        code += self._generate_kotlin_methods()
        code += "}"
        return code

    def _generate_kotlin_header(self) -> str:
        """Generate the Kotlin module header with TurboModule support."""
        header = self._generate_header("Kotlin module for Nim bridge")
        return f"""{header}package {self.config.package_name}

import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.module.annotations.ReactModule
import {self.config.package_name}.Native{self.config.module_name}Spec

@ReactModule(name = {self.config.module_name}Module.NAME)
class {self.config.module_name}Module(reactContext: ReactApplicationContext) : Native{self.config.module_name}Spec(reactContext) {{

    companion object {{
        const val NAME = "{self.config.module_name}"

        init {{
            try {{
                System.loadLibrary("{self.config.library_name}")
                android.util.Log.d("{self.config.module_name}", "Native library {self.config.library_name} loaded successfully")
            }} catch (e: Exception) {{
                android.util.Log.e("{self.config.module_name}", "Failed to load native library {self.config.library_name}: ${{e.message}}")
                e.printStackTrace()
            }}
        }}

"""

    def _generate_native_declarations(self) -> str:
        """Generate native method declarations."""
        declarations = ""
        for func in self.functions:
            ret_type = self._get_kotlin_native_return_type(func.return_type)
            params_str = self._build_kotlin_native_params(func)
            declarations += f"        @JvmStatic\n"
            declarations += f"        private external fun native{func.name[0].upper() + func.name[1:]}({params_str}): {ret_type}\n"
        declarations += "    }\n    \n    override fun getName(): String = NAME\n\n"
        return declarations

    def _generate_kotlin_methods(self) -> str:
        """Generate Kotlin TurboModule override methods."""
        methods = ""
        for func in self.functions:
            js_name = func.js_name or func.name
            params_str = self._build_kotlin_method_params(func)
            ret_type = self._get_kotlin_return_type(func.return_type)

            methods += f"\n    override fun {js_name}({params_str}): {ret_type} {{\n"
            methods += f"        return try {{\n"
            methods += self._generate_kotlin_method_call(func)
            methods += self._generate_kotlin_error_handling(func)
            methods += f"    }}\n"
        return methods

    def _get_kotlin_return_type(self, nim_type: str) -> str:
        """Get Kotlin return type for TurboModule spec."""
        if nim_type in ['cstring', 'string']:
            return "String"
        elif nim_type == 'bool':
            return "Boolean"
        else:
            return "Double"

    @staticmethod
    def _get_kotlin_native_return_type(nim_type: str) -> str:
        """Get the native return type for Kotlin."""
        if nim_type in ['cstring', 'string']:
            return "String"
        elif nim_type == 'int64':
            return "Long"
        return "Int"

    @staticmethod
    def _build_kotlin_native_params(func: NimFunction) -> str:
        """Build parameter string for native Kotlin method."""
        params = []
        for name, ptype in func.params:
            if ptype in ['cint', 'int']:
                params.append(f"{name}: Int")
            elif ptype in ['cstring', 'string']:
                params.append(f"{name}: String")
            else:
                params.append(f"{name}: Int")
        return ', '.join(params)

    @staticmethod
    def _build_kotlin_method_params(func: NimFunction) -> str:
        """Build parameter string for Kotlin React method."""
        params = []
        for name, ptype in func.params:
            if ptype in ['cint', 'int']:
                params.append(f"{name}: Double")
            elif ptype in ['cstring', 'string']:
                params.append(f"{name}: String")
            else:
                params.append(f"{name}: Double")
        return ', '.join(params)

    def _generate_kotlin_method_call(self, func: NimFunction) -> str:
        """Generate the native method call."""
        args = []
        for name, ptype in func.params:
            if ptype in ['cint', 'int']:
                args.append(f"{name}.toInt()")
            else:
                args.append(name)
        args_str = ', '.join(args)

        method_name = f"native{func.name[0].upper() + func.name[1:]}"

        # Generate return based on return type
        if func.return_type == 'bool':
            return f"            {method_name}({args_str}) != 0\n"
        elif func.return_type in ['cstring', 'string']:
            return f"            {method_name}({args_str})\n"
        else:
            return f"            {method_name}({args_str}).toDouble()\n"

    def _generate_kotlin_error_handling(self, func: NimFunction) -> str:
        """Generate error handling for Kotlin method."""
        error_code = "        } catch (e: Exception) {\n"
        if func.return_type == 'bool':
            error_code += "            false\n"
        elif func.return_type in ['cstring', 'string']:
            error_code += '            "Error: ${e.message}"\n'
        else:
            error_code += "            0.0\n"
        error_code += "        }\n"
        return error_code


class AndroidKotlinPackageGenerator:
    """Generates Android Kotlin package file."""

    def __init__(self, config: GeneratorConfig):
        self.config = config

    def generate(self) -> str:
        """Generate Android Kotlin package file."""
        header = CodeGenerator._generate_header("Kotlin package for Nim bridge")
        return f"""{header}package {self.config.package_name}

import com.facebook.react.TurboReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.module.model.ReactModuleInfo
import com.facebook.react.module.model.ReactModuleInfoProvider
import com.facebook.react.turbomodule.core.interfaces.TurboModule

class {self.config.module_name}Package : TurboReactPackage() {{

    override fun getModule(name: String, reactContext: ReactApplicationContext): NativeModule? {{
        return if (name == {self.config.module_name}Module.NAME) {{
            {self.config.module_name}Module(reactContext)
        }} else {{
            null
        }}
    }}

    override fun getReactModuleInfoProvider(): ReactModuleInfoProvider {{
        return ReactModuleInfoProvider {{
            mapOf(
                {self.config.module_name}Module.NAME to ReactModuleInfo(
                    {self.config.module_name}Module.NAME,
                    {self.config.module_name}Module::class.java.name,
                    false, // canOverrideExistingModule
                    false, // needsEagerInit
                    true,  // isCxxModule
                    true   // isTurboModule
                )
            )
        }}
    }}
}}"""


class AndroidJNIGenerator(CodeGenerator):
    """Generates Android JNI C++ bridge code."""

    def __init__(self, functions: List[NimFunction], config: GeneratorConfig):
        super().__init__(functions, config)

    def generate(self) -> str:
        """Generate Android JNI C++ bridge."""
        code = self._generate_jni_header()
        code += self._generate_jni_initialization()
        code += self._generate_jni_methods()
        return code

    def _generate_jni_header(self) -> str:
        """Generate JNI header and function declarations."""
        code = CodeGenerator._generate_header("JNI C++ bridge for Android")
        code += "#include <jni.h>\n#include <string>\n\n"
        code += "// Import the Nim functions\nextern \"C\" {\n"

        for func in self.functions:
            params_str = self._build_jni_function_params(func)
            ret_type = self._get_jni_function_return_type(func.return_type)
            code += f"    {ret_type} {func.name}({params_str});\n"

        return code

    def _generate_jni_initialization(self) -> str:
        """Generate JNI initialization code."""
        return """    void mobileNimInit();
    void mobileNimShutdown();
    void freeString(const char* s);
}

// Initialize Nim when the library loads
static bool nimInitialized = false;

void initializeNim() {
    if (!nimInitialized) {
        mobileNimInit();
        nimInitialized = true;
    }
}

"""

    def _generate_jni_methods(self) -> str:
        """Generate all JNI method implementations."""
        methods = ""
        for func in self.functions:
            methods += self._generate_jni_method(func)
        return methods

    def _generate_jni_method(self, func: NimFunction) -> str:
        """Generate a single JNI method."""
        package_path = self.config.package_name.replace('.', '_')
        class_name = f"{package_path}_{self.config.module_name}Module"
        method_name = f"native{func.name[0].upper() + func.name[1:]}"

        jni_params = self._build_jni_method_params(func)
        ret_type = self._get_jni_return_type(func.return_type)

        method_code = f'extern "C" JNIEXPORT {ret_type} JNICALL\n'
        method_code += f'Java_{class_name}_{method_name}({jni_params}) {{\n'
        method_code += '    initializeNim();\n'
        method_code += self._generate_jni_method_body(func)
        method_code += '}\n\n'

        return method_code

    @staticmethod
    def _build_jni_function_params(func: NimFunction) -> str:
        """Build parameter string for function declaration."""
        params = []
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                params.append(f"const char* {name}")
            else:
                params.append(f"int {name}")
        return ', '.join(params)

    @staticmethod
    def _get_jni_function_return_type(nim_type: str) -> str:
        """Get C function return type."""
        if nim_type in ['cstring', 'string']:
            return "const char*"
        elif nim_type == 'int64':
            return "long long"
        return "int"

    @staticmethod
    def _build_jni_method_params(func: NimFunction) -> str:
        """Build parameter string for JNI method."""
        jni_params = ['JNIEnv *env', 'jclass clazz']
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                jni_params.append(f"jstring {name}")
            else:
                jni_params.append(f"jint {name}")
        return ', '.join(jni_params)

    @staticmethod
    def _get_jni_return_type(nim_type: str) -> str:
        """Get JNI return type."""
        if nim_type in ['cstring', 'string']:
            return "jstring"
        elif nim_type == 'int64':
            return "jlong"
        return "jint"

    def _generate_jni_method_body(self, func: NimFunction) -> str:
        """Generate the body of a JNI method."""
        body = ""

        # Handle string parameter conversion
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                body += f"    const char* {name}Str = env->GetStringUTFChars({name}, 0);\n"

        # Build function call
        actual_params = []
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                actual_params.append(f"{name}Str")
            else:
                actual_params.append(name)
        actual_params_str = ', '.join(actual_params)

        # Generate call and return based on type
        if func.return_type in ['cstring', 'string']:
            body += f"    const char* result = {func.name}({actual_params_str});\n"
            body += f"    jstring javaString = env->NewStringUTF(result);\n"
            if func.memory_type == 'allocated':
                body += f"    if (result) freeString(result);\n"
            # Release string parameters before return
            for name, ptype in func.params:
                if ptype in ['cstring', 'string']:
                    body += f"    env->ReleaseStringUTFChars({name}, {name}Str);\n"
            body += f"    return javaString;\n"
        elif func.return_type == 'int64':
            body += f"    long long result = {func.name}({actual_params_str});\n"
            # Release string parameters before return
            for name, ptype in func.params:
                if ptype in ['cstring', 'string']:
                    body += f"    env->ReleaseStringUTFChars({name}, {name}Str);\n"
            body += "    return (jlong)result;\n"
        else:
            body += f"    int result = {func.name}({actual_params_str});\n"
            # Release string parameters before return
            for name, ptype in func.params:
                if ptype in ['cstring', 'string']:
                    body += f"    env->ReleaseStringUTFChars({name}, {name}Str);\n"
            body += "    return result;\n"

        return body