# Automated binding generation tool for React Native
# This tool generates platform-specific C bindings from Nim code
# Similar to how go-mobile works for Go projects

import os, strutils, strformat

type
  Platform = enum
    Android, iOS

  GeneratorConfig = object
    platform: Platform
    sourceDir: string
    outputDir: string
    libName: string

proc generateAndroidBindings(config: GeneratorConfig) =
  echo "🤖 Generating Android bindings..."
  
  let nimcacheDir = config.outputDir / "android"
  createDir(nimcacheDir)
  
  # Compile Nim to C with Android-specific flags
  let cmd = fmt"""nim c \
    --define:android \
    --cpu:arm64 \
    --os:android \
    --app:lib \
    --noMain \
    --header \
    --nimcache:{nimcacheDir} \
    --out:{nimcacheDir}/{config.libName} \
    {config.sourceDir}/main.nim"""
  
  echo fmt"Executing: {cmd}"
  let result = execShellCmd(cmd)
  
  if result == 0:
    echo "✅ Android bindings generated successfully"
    echo fmt"📁 Output: {nimcacheDir}"
  else:
    echo "❌ Failed to generate Android bindings"
    quit(1)

proc generateiOSBindings(config: GeneratorConfig) =
  echo "🍎 Generating iOS bindings..."
  
  let nimcacheDir = config.outputDir / "ios"
  createDir(nimcacheDir)
  
  # Compile Nim to C with iOS-specific flags
  let cmd = fmt"""nim c \
    --define:ios \
    --cpu:arm64 \
    --os:ios \
    --app:lib \
    --noMain \
    --header \
    --nimcache:{nimcacheDir} \
    --out:{nimcacheDir}/{config.libName} \
    {config.sourceDir}/main.nim"""
  
  echo fmt"Executing: {cmd}"
  let result = execShellCmd(cmd)
  
  if result == 0:
    echo "✅ iOS bindings generated successfully"
    echo fmt"📁 Output: {nimcacheDir}"
  else:
    echo "❌ Failed to generate iOS bindings"
    quit(1)

proc generateSharedHeaders(config: GeneratorConfig) =
  echo "📄 Generating shared headers..."
  
  let headerDir = config.outputDir / "headers"
  createDir(headerDir)
  
  # Create a unified header file for React Native
  let headerContent = fmt"""
#ifndef NIM_CORE_BINDINGS_H
#define NIM_CORE_BINDINGS_H

#ifdef __cplusplus
extern "C" {{
#endif

// Core API functions
const char* helloWorld(void);
int addNumbers(int a, int b);
const char* getSystemInfo(void);

// Math operations
int mobileFibonacci(int n);
int mobileIsPrime(int n);
const char* mobileFactorize(int n);

// Data operations
const char* mobileCreateUser(int id, const char* name, const char* email);
int mobileValidateEmail(const char* email);

// Runtime management
void mobileNimInit(void);
void mobileNimShutdown(void);
void NimMain(void);

// Version info
const char* getNimCoreVersion(void);

#ifdef __cplusplus
}}
#endif

#endif // NIM_CORE_BINDINGS_H
"""
  
  writeFile(headerDir / "nim_core.h", headerContent)
  echo "✅ Shared header generated"

proc generateTypeScriptBindings(config: GeneratorConfig) =
  echo "📝 Generating TypeScript definitions..."
  
  let tsContent = """
// TypeScript definitions for Nim Core bindings
// Auto-generated - do not edit manually

export interface NimCore {
  // Core API
  helloWorld(): string;
  addNumbers(a: number, b: number): number;
  getSystemInfo(): string;
  
  // Math operations
  fibonacci(n: number): number;
  isPrime(n: number): boolean;
  factorize(n: number): number[];
  
  // Data operations
  createUser(id: number, name: string, email: string): string;
  validateEmail(email: string): boolean;
  
  // Version info
  getVersion(): string;
}

declare global {
  var NimCore: NimCore;
}

export default global.NimCore;
"""
  
  let headerDir = config.outputDir / "headers"
  writeFile(headerDir / "nim_core.d.ts", tsContent)
  echo "✅ TypeScript definitions generated"

proc main() =
  echo "🚀 Nim-React Native Binding Generator"
  echo "====================================="
  
  let config = GeneratorConfig(
    sourceDir: "nim-core/src",
    outputDir: "bindings",
    libName: "nim_core"
  )
  
  # Clean previous bindings
  if dirExists(config.outputDir):
    removeDir(config.outputDir)
  
  createDir(config.outputDir)
  
  # Generate platform-specific bindings
  generateAndroidBindings(config)
  generateiOSBindings(config)
  
  # Generate shared files
  generateSharedHeaders(config)
  generateTypeScriptBindings(config)
  
  echo ""
  echo "🎉 Binding generation complete!"
  echo fmt"📁 All bindings available in: {config.outputDir}/"

when isMainModule:
  main()