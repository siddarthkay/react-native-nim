"""
iOS platform generators for Nim bridge (Objective-C++).
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
        code = CodeGenerator._generate_header("Objective-C++ bridge header")
        code += """#import <React/RCTBridgeModule.h>

@interface NimBridge : NSObject <RCTBridgeModule>

@end
"""
        return code


class ObjcBridgeGenerator(CodeGenerator):
    """Generates Objective-C++ bridge code."""

    def generate(self) -> str:
        """Generate Objective-C++ bridge code."""
        code = CodeGenerator._generate_header("Objective-C++ bridge")
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

    @staticmethod
    def _build_objc_args(func: NimFunction) -> str:
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