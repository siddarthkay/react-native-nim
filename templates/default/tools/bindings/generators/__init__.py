"""
Platform-specific code generators for Nim bridge bindings.
"""

from .base import CodeGenerator
from .ios import CppWrapperGenerator, ObjcHeaderGenerator, ObjcBridgeGenerator
from .android import AndroidKotlinGenerator, AndroidKotlinPackageGenerator, AndroidJNIGenerator
from .typescript import TypeScriptInterfaceGenerator
from .cmake import CMakeGenerator

__all__ = [
    'CodeGenerator',
    'CppWrapperGenerator',
    'ObjcHeaderGenerator', 
    'ObjcBridgeGenerator',
    'AndroidKotlinGenerator',
    'AndroidKotlinPackageGenerator',
    'AndroidJNIGenerator',
    'TypeScriptInterfaceGenerator',
    'CMakeGenerator'
]