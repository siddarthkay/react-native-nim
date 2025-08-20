#!/bin/bash
# Automated build script for Nim -> React Native
# Compiles Nim code and generates all bindings automatically

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
NIM_DIR="$PROJECT_ROOT/nim"
BRIDGE_DIR="$PROJECT_ROOT/modules/nim-bridge"

echo "Building Nim-React Native Bridge..."

echo "Compiling Nim code..."
cd "$NIM_DIR"

# Compile Nim to static library for iOS
echo "Building iOS static library..."

# Build for iOS simulator (arm64)
echo "  Building for iOS Simulator (arm64)..."
nim c -c --os:ios --cpu:arm64 -d:ios --app:staticlib --noMain:on --nimcache:cache_ios_sim nimbridge.nim

NIM_LIB_PATH=""
if command -v nim >/dev/null 2>&1; then
    # Try to get nim lib path using nim config
    NIM_INSTALL_DIR=$(nim dump.d 2>/dev/null | grep "prefixdir" | cut -d'"' -f2 2>/dev/null || echo "")
    if [ -n "$NIM_INSTALL_DIR" ] && [ -d "$NIM_INSTALL_DIR/lib" ]; then
        NIM_LIB_PATH="$NIM_INSTALL_DIR/lib"
    fi
fi

# Fallback detection methods
if [ -z "$NIM_LIB_PATH" ] || [ ! -d "$NIM_LIB_PATH" ]; then
    if [ -d "/opt/homebrew/Cellar/nim" ]; then
        NIM_LIB_PATH="/opt/homebrew/Cellar/nim/$(ls /opt/homebrew/Cellar/nim | tail -1)/nim/lib"
    elif [ -d "/usr/local/lib/nim" ]; then
        NIM_LIB_PATH="/usr/local/lib/nim"
    elif [ -d "/opt/homebrew/lib/nim" ]; then
        NIM_LIB_PATH="/opt/homebrew/lib/nim"
    else
        echo "❌ Could not find Nim installation. Please ensure Nim is installed and in PATH."
        echo "   Tried looking in common locations like /opt/homebrew/Cellar/nim and /usr/local/lib/nim"
        exit 1
    fi
fi

echo "  Using Nim lib path: $NIM_LIB_PATH"

# Compile C files to object files with iOS simulator target
cd cache_ios_sim
for file in @m*.c; do
    if [ -f "$file" ]; then
        clang -c -w -ferror-limit=3 -pthread \
              -I"$NIM_LIB_PATH" \
              -I.. \
              -target arm64-apple-ios15.1-simulator \
              -o "${file}.o" "$file"
    fi
done
ar rcs ../libnim_core.a *.o
cd ..

echo "Generated static library: libnim_core.a"

echo "Copying library to bridge directory..."
mkdir -p "$BRIDGE_DIR/ios"
cp libnim_core.a "$BRIDGE_DIR/ios/libnim_core.a"

echo "Generating bindings..."
python3 "$SCRIPT_DIR/generate_bindings.py"

echo "Copying headers..."
cp cache_ios/nimbridge.h "$BRIDGE_DIR/ios/main.h" 2>/dev/null || true

echo "Static library and bindings ready!"

echo "Build complete!"
echo ""
echo "Generated files:"
echo "  - $NIM_DIR/libnimbridge.a (Static library with memory management)"
echo "  - $BRIDGE_DIR/ios/nim_functions.h (Function declarations)"
echo "  - $BRIDGE_DIR/ios/NimBridge.mm (Objective-C++ bridge with freeString calls)"
echo "  - $BRIDGE_DIR/android/src/main/cpp/NimBridge.cpp (Android JNI bridge)"
echo "  - $BRIDGE_DIR/src/NimBridge.types.ts (TypeScript interface)"
echo ""
echo ""
echo "Next steps:"
echo "  1. Run 'npm run ios' or 'npm run android'"
echo "  2. The static library will be automatically linked"
