#!/usr/bin/env python3
"""
Automatic binding generator for Nim -> React Native
Parses Nim exported functions and generates all necessary bridge code
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class GeneratorConfig:
    """Configuration for the binding generator."""
    nim_dir: str = "nim"
    output_dir: str = "modules/nim-bridge"
    package_name: str = "com.nimbridge"
    module_name: str = "NimBridge"
    library_name: str = "nim_functions"
    generate_ios: bool = True
    generate_android: bool = True
    generate_typescript: bool = True
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'GeneratorConfig':
        """Load configuration from a JSON file."""
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                return cls(**config_data)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Invalid config file {config_file}: {e}")
                print("Using default configuration.")
        return cls()
    
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

@dataclass
class NimFunction:
    """Represents a Nim function with its metadata."""
    name: str
    return_type: str
    params: List[Tuple[str, str]]  # List of (name, type) tuples
    memory_type: Optional[str] = None  # 'literal' or 'allocated' for string returns

class TypeMapper:
    """Handles type conversions between Nim and target languages."""
    
    @staticmethod
    def nim_to_cpp_type(nim_type: str) -> str:
        """Convert Nim type to C++ type."""
        type_map = {
            'cstring': 'NCSTRING',
            'cint': 'int',
            'int': 'int',
            'int64': 'long long',
            'string': 'NCSTRING',
            'bool': 'int',
            'float': 'double',
        }
        return type_map.get(nim_type, nim_type)

    @staticmethod
    def nim_to_objc_type(nim_type: str) -> str:
        """Convert Nim type to Objective-C type."""
        type_map = {
            'cstring': 'NSString *',
            'string': 'NSString *',
            'cint': 'NSNumber *',
            'int': 'NSNumber *',
            'int64': 'NSNumber *',
            'bool': 'NSNumber *',
            'float': 'NSNumber *',
        }
        return type_map.get(nim_type, 'id')

    @staticmethod
    def nim_to_ts_type(nim_type: str) -> str:
        """Convert Nim type to TypeScript type."""
        type_map = {
            'cstring': 'string',
            'string': 'string',
            'cint': 'number',
            'int': 'number',
            'int64': 'number',
            'bool': 'boolean',
            'float': 'number',
        }
        return type_map.get(nim_type, 'any')

    @staticmethod
    def nim_to_kotlin_type(nim_type: str) -> str:
        """Convert Nim type to Kotlin type."""
        type_map = {
            'cstring': 'String',
            'string': 'String', 
            'cint': 'Double',
            'int': 'Double',
            'int64': 'Double',
            'bool': 'Double',
            'float': 'Double',
        }
        return type_map.get(nim_type, 'String')

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
    
    def _parse_parameters(self, params_str: str) -> List[Tuple[str, str]]:
        """Parse parameter string into list of (name, type) tuples."""
        params = []
        if params_str.strip():
            for param in params_str.split(','):
                param = param.strip()
                if ':' in param:
                    name, ptype = param.split(':', 1)
                    params.append((name.strip(), ptype.strip()))
        return params

class CodeGenerator:
    """Base class for code generators."""
    
    def __init__(self, functions: List[NimFunction]):
        self.functions = functions
        self.type_mapper = TypeMapper()
    
    def generate(self) -> str:
        """Generate code for the target platform."""
        raise NotImplementedError
    
    def _generate_header(self, description: str) -> str:
        """Generate standardized file header."""
        return f"""// Auto-generated {description}
// DO NOT EDIT MANUALLY - Generated by tools/generate_bindings.py
// This file will be overwritten when bindings are regenerated

"""

class CppWrapperGenerator(CodeGenerator):
    """Generates C++ wrapper code for Nim functions."""
    
    def generate(self) -> str:
        """Generate C++ wrapper code."""
        code = self._generate_header("C++ wrapper for Nim functions")
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
            params_str = ', '.join([f"{self.type_mapper.nim_to_cpp_type(ptype)} {name}" 
                                   for name, ptype in func.params])
            code += f"    {ret_type} {func.name}({params_str});\n"
        
        code += "    \n    // Memory management\n"
        code += "    void freeString(NCSTRING s);\n"
        code += "}\n"
        
        return code

class ObjcHeaderGenerator(CodeGenerator):
    """Generates Objective-C header file."""
    
    def generate(self) -> str:
        """Generate Objective-C header file."""
        code = self._generate_header("Objective-C++ bridge header")
        code += """#import <React/RCTBridgeModule.h>

@interface NimBridge : NSObject <RCTBridgeModule>

@end
"""
        return code

class ObjcBridgeGenerator(CodeGenerator):
    """Generates Objective-C++ bridge code."""
    
    def generate(self) -> str:
        """Generate Objective-C++ bridge code."""
        code = self._generate_header("Objective-C++ bridge")
        code += """#import "NimBridge.h"
#include "nim_functions.h"

@implementation NimBridge

RCT_EXPORT_MODULE()

+ (BOOL)requiresMainQueueSetup
{
    return NO;
}

- (instancetype)init
{
    self = [super init];
    if (self) {
        // Initialize Nim runtime
        NimMain();
        mobileNimInit();
    }
    return self;
}

- (void)dealloc
{
    mobileNimShutdown();
}

// Generated method exports
"""
        
        for func in self.functions:
            code += self._generate_objc_method(func)
        
        code += "@end\n"
        return code
    
    def _generate_objc_method(self, func: NimFunction) -> str:
        """Generate a single Objective-C method."""
        ret_type = self.type_mapper.nim_to_objc_type(func.return_type)
        
        # Build method signature
        if not func.params:
            method_sig = func.name
        else:
            parts = []
            for i, (name, ptype) in enumerate(func.params):
                objc_type = self.type_mapper.nim_to_objc_type(ptype)
                if i == 0:
                    parts.append(f"{func.name}:(nonnull {objc_type}){name}")
                else:
                    parts.append(f"with{name.capitalize()}:(nonnull {objc_type}){name}")
            method_sig = ' '.join(parts)
        
        method_code = f"RCT_EXPORT_SYNCHRONOUS_TYPED_METHOD({ret_type}, {method_sig})\n"
        method_code += "{\n"
        method_code += self._generate_objc_method_body(func)
        method_code += "}\n\n"
        
        return method_code
    
    def _generate_objc_method_body(self, func: NimFunction) -> str:
        """Generate the body of an Objective-C method."""
        args = self._build_objc_args(func)
        
        if func.return_type in ['cstring', 'string']:
            body = f"    NCSTRING result = {func.name}({args});\n"
            if func.memory_type == 'allocated':
                body += f"    NSString *objcString = result ? [NSString stringWithUTF8String:result] : @\"\";\n"
                body += f"    if (result) freeString(result);\n"
                body += f"    return objcString;\n"
            else:
                body += f"    return result ? [NSString stringWithUTF8String:result] : @\"\";\n"
        elif func.return_type == 'int64':
            body = f"    long long result = {func.name}({args});\n"
            body += f"    return @(result);\n"
        else:
            body = f"    int result = {func.name}({args});\n"
            body += f"    return @(result);\n"
        
        return body
    
    def _build_objc_args(self, func: NimFunction) -> str:
        """Build argument list for Objective-C method call."""
        args = []
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                args.append(f"(NCSTRING)[{name} UTF8String]")
            elif ptype in ['cint', 'int']:
                args.append(f"[{name} intValue]")
            else:
                args.append(name)
        return ', '.join(args)

class TypeScriptInterfaceGenerator(CodeGenerator):
    """Generates TypeScript interface definitions."""
    
    def generate(self) -> str:
        """Generate TypeScript interface."""
        code = self._generate_header("TypeScript interface for Nim bridge")
        code += "export interface NimBridge {\n"
        
        for func in self.functions:
            ret_type = self.type_mapper.nim_to_ts_type(func.return_type)
            params_str = ', '.join([f"{name}: {self.type_mapper.nim_to_ts_type(ptype)}" 
                                   for name, ptype in func.params])
            code += f"  {func.name}({params_str}): {ret_type};\n"
        
        code += "}\n"
        return code

class AndroidKotlinGenerator(CodeGenerator):
    """Generates Android Kotlin module code."""
    
    def __init__(self, functions: List[NimFunction], config: GeneratorConfig):
        super().__init__(functions)
        self.config = config
    
    def generate(self) -> str:
        """Generate Android Kotlin module."""
        code = self._generate_kotlin_header()
        code += self._generate_native_declarations()
        code += self._generate_kotlin_methods()
        code += "}"
        return code
    
    def _generate_kotlin_header(self) -> str:
        """Generate the Kotlin module header."""
        header = self._generate_header("Kotlin module for Nim bridge")
        return f"""{header}package {self.config.package_name}

import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.module.annotations.ReactModule

@ReactModule(name = {self.config.module_name}Module.NAME)
class {self.config.module_name}Module(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {{
    
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
        """Generate Kotlin React methods."""
        methods = ""
        for func in self.functions:
            params_str = self._build_kotlin_method_params(func)
            ret_type = "String" if func.return_type in ['cstring', 'string'] else "Double"
            
            methods += f"    @ReactMethod(isBlockingSynchronousMethod = true)\n"
            methods += f"    fun {func.name}({params_str}): {ret_type} {{\n"
            methods += f"        return try {{\n"
            methods += self._generate_kotlin_method_call(func)
            methods += self._generate_kotlin_error_handling(func)
            methods += f"    }}\n"
        return methods
    
    def _get_kotlin_native_return_type(self, nim_type: str) -> str:
        """Get the native return type for Kotlin."""
        if nim_type in ['cstring', 'string']:
            return "String"
        elif nim_type == 'int64':
            return "Long"
        return "Int"
    
    def _build_kotlin_native_params(self, func: NimFunction) -> str:
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
    
    def _build_kotlin_method_params(self, func: NimFunction) -> str:
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
        if func.return_type in ['cstring', 'string']:
            return f"            {method_name}({args_str})\n"
        else:
            return f"            {method_name}({args_str}).toDouble()\n"
    
    def _generate_kotlin_error_handling(self, func: NimFunction) -> str:
        """Generate error handling for Kotlin method."""
        error_code = "        } catch (e: Exception) {\n"
        if func.return_type in ['cstring', 'string']:
            error_code += '            "Error: ${e.message}"\n'
        else:
            error_code += "            0.0\n"
        error_code += "        }\n"
        return error_code

class AndroidKotlinPackageGenerator:
    """Generates Android Kotlin package file."""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
    
    def _generate_header(self, description: str) -> str:
        """Generate standardized file header."""
        return f"""// Auto-generated {description}
// DO NOT EDIT MANUALLY - Generated by tools/generate_bindings.py
// This file will be overwritten when bindings are regenerated

"""
    
    def generate(self) -> str:
        """Generate Android Kotlin package file."""
        header = self._generate_header("Kotlin package for Nim bridge")
        return f"""{header}package {self.config.package_name}

import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.uimanager.ViewManager

class {self.config.module_name}Package : ReactPackage {{
    
    override fun createNativeModules(reactContext: ReactApplicationContext): List<NativeModule> {{
        return listOf({self.config.module_name}Module(reactContext))
    }}
    
    override fun createViewManagers(reactContext: ReactApplicationContext): List<ViewManager<*, *>> {{
        return emptyList()
    }}
}}"""

class AndroidJNIGenerator(CodeGenerator):
    """Generates Android JNI C++ bridge code."""
    
    def __init__(self, functions: List[NimFunction], config: GeneratorConfig):
        super().__init__(functions)
        self.config = config
    
    def generate(self) -> str:
        """Generate Android JNI C++ bridge."""
        code = self._generate_jni_header()
        code += self._generate_jni_initialization()
        code += self._generate_jni_methods()
        return code
    
    def _generate_jni_header(self) -> str:
        """Generate JNI header and function declarations."""
        code = self._generate_header("JNI C++ bridge for Android")
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
    
    def _build_jni_function_params(self, func: NimFunction) -> str:
        """Build parameter string for function declaration."""
        params = []
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                params.append(f"const char* {name}")
            else:
                params.append(f"int {name}")
        return ', '.join(params)
    
    def _get_jni_function_return_type(self, nim_type: str) -> str:
        """Get C function return type."""
        if nim_type in ['cstring', 'string']:
            return "const char*"
        elif nim_type == 'int64':
            return "long long"
        return "int"
    
    def _build_jni_method_params(self, func: NimFunction) -> str:
        """Build parameter string for JNI method."""
        jni_params = ['JNIEnv *env', 'jclass clazz']
        for name, ptype in func.params:
            if ptype in ['cstring', 'string']:
                jni_params.append(f"jstring {name}")
            else:
                jni_params.append(f"jint {name}")
        return ', '.join(jni_params)
    
    def _get_jni_return_type(self, nim_type: str) -> str:
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
    

class BindingGenerator:
    """Main binding generator that orchestrates the generation process."""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        base_dir = Path(__file__).parent.parent
        self.nim_dir = base_dir / config.nim_dir
        self.output_dir = base_dir / config.output_dir
        self.parser = NimParser()
        self.functions: List[NimFunction] = []
    
    def discover_functions(self) -> bool:
        """Discover all exported functions from Nim files."""
        nim_files = list(self.nim_dir.glob("*.nim"))
        if not nim_files:
            print(f"No Nim files found in {self.nim_dir}")
            return False
        
        for nim_file in nim_files:
            functions = self.parser.parse_nim_exports(nim_file)
            self.functions.extend(functions)
            if functions:
                print(f"Found {len(functions)} exported functions in {nim_file.name}")
        
        if not self.functions:
            print("No exported functions found!")
            return False
        
        return True
    
    def generate_all(self) -> None:
        """Generate all binding files based on configuration."""
        generators = {}
        
        if self.config.generate_ios:
            generators.update({
                "C++ wrapper": (CppWrapperGenerator(self.functions), 
                               self.output_dir / "ios" / f"{self.config.library_name}.h"),
                "Objective-C++ header": (ObjcHeaderGenerator(self.functions), 
                                        self.output_dir / "ios" / f"{self.config.module_name}.h"),
                "Objective-C++ bridge": (ObjcBridgeGenerator(self.functions), 
                                        self.output_dir / "ios" / f"{self.config.module_name}.mm"),
            })
        
        if self.config.generate_typescript:
            generators["TypeScript interface"] = (
                TypeScriptInterfaceGenerator(self.functions), 
                self.output_dir / "src" / f"{self.config.module_name}.types.ts"
            )
        
        if self.config.generate_android:
            package_path = self.config.package_name.replace('.', '/')
            generators.update({
                "Android Kotlin module": (AndroidKotlinGenerator(self.functions, self.config),
                                        self.output_dir / "android" / "src" / "main" / "java" / package_path / f"{self.config.module_name}Module.kt"),
                "Android Kotlin package": (AndroidKotlinPackageGenerator(self.config),
                                         self.output_dir / "android" / "src" / "main" / "java" / package_path / f"{self.config.module_name}Package.kt"),
                "Android JNI bridge": (AndroidJNIGenerator(self.functions, self.config),
                                      self.output_dir / "android" / "src" / "main" / "cpp" / f"{self.config.module_name}.cpp"),
            })
        
        for name, (generator, file_path) in generators.items():
            try:
                code = generator.generate()
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(code)
                print(f"Generated {file_path}")
            except Exception as e:
                print(f"Error generating {name}: {e}")
    
    def print_summary(self) -> None:
        """Print generation summary."""
        print(f"\n✅ Successfully generated bindings for {len(self.functions)} functions!")
        print("\nGenerated files:")
        print("  iOS: nim_functions.h, NimBridge.h, NimBridge.mm")
        print("  Android: NimBridgeModule.kt, NimBridgePackage.kt, NimBridge.cpp")
        print("  TypeScript: NimBridge.types.ts")
        print("\nNext steps:")
        print("1. Review the generated files")
        print("2. Run 'pod install' in ios/ directory")
        print("3. Rebuild the app")

def main():
    """Main entry point."""
    config_file = Path(__file__).parent / "generator_config.json"
    config = GeneratorConfig.from_file(config_file)
    
    # Save default config if it doesn't exist
    if not config_file.exists():
        config.to_file(config_file)
        print(f"Created default config file: {config_file}")
    
    generator = BindingGenerator(config)
    
    if not generator.discover_functions():
        return
    
    generator.generate_all()
    generator.print_summary()

if __name__ == "__main__":
    main()