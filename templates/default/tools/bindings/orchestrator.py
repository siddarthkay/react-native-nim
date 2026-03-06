"""
Main orchestrator for binding generation process.
"""

from pathlib import Path
from typing import List

from .config import GeneratorConfig
from .models import NimFunction
from .parser import NimParser
from .generators import (
    CppWrapperGenerator, ObjcHeaderGenerator, ObjcBridgeGenerator,
    AndroidKotlinGenerator, AndroidKotlinPackageGenerator, AndroidJNIGenerator,
    TypeScriptInterfaceGenerator, CMakeGenerator
)


class BindingGenerator:
    """Main binding generator that orchestrates the generation process."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        base_dir = Path(__file__).parent.parent.parent
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

        # Apply function name mappings from config
        name_mappings = self.config.data.get('function_name_mappings', {})
        boolean_returns = self.config.data.get('boolean_returns', [])

        for func in self.functions:
            # Apply name mapping
            if func.name in name_mappings:
                func.js_name = name_mappings[func.name]
            else:
                func.js_name = func.name

            # Mark functions that should return booleans
            if func.name in boolean_returns:
                func.return_type = 'bool'

        return True

    def generate_all(self) -> None:
        """Generate all binding files based on configuration."""
        generators = {}

        if self.config.generate_ios:
            generators.update({
                "C++ wrapper": (CppWrapperGenerator(self.functions, self.config),
                               self.output_dir / "ios" / f"{self.config.library_name}.h"),
                "Objective-C++ header": (ObjcHeaderGenerator(self.functions, self.config),
                                        self.output_dir / "ios" / f"{self.config.module_name}.h"),
                "Objective-C++ bridge": (ObjcBridgeGenerator(self.functions, self.config),
                                        self.output_dir / "ios" / f"{self.config.module_name}.mm"),
            })

        if self.config.generate_typescript:
            generators["TypeScript TurboModule spec"] = (
                TypeScriptInterfaceGenerator(self.functions, self.config),
                self.output_dir / "src" / f"Native{self.config.module_name}.ts"
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
                "Android CMake configuration": (CMakeGenerator(self.functions, self.config),
                                              self.output_dir / "android" / "src" / "main" / "cpp" / "CMakeLists.txt"),
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
        print("  Android: NimBridgeModule.kt, NimBridgePackage.kt, NimBridge.cpp, CMakeLists.txt")
        print("  TypeScript: NativeNimBridge.ts (TurboModule spec)")
        print("\nNext steps:")
        print("1. Review the generated files")
        print("2. Run 'pod install' in ios/ directory (for iOS)")
        print("3. Rebuild the app")