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

# Detect platform and build accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: Build iOS static library AND Android C files
    echo "Building iOS static library..."
    echo "  Building for iOS Simulator (arm64)..."
    nim c -c --os:ios --cpu:arm64 -d:ios --app:staticlib --noMain:on --nimcache:cache_ios_sim nimbridge.nim
    
    echo "Building Android C files..."
    echo "  Building for Android (arm64-v8a)..."
    nim c -c --os:android --cpu:arm64 -d:android --app:staticlib --noMain:on --nimcache:cache_android nimbridge.nim
    
    BUILD_TARGET="ios"
    CACHE_DIR="cache_ios_sim"
    LIB_NAME="libnim_core.a"
else
    # Linux: Generate C files for Android compilation
    echo "Building C files for Android..."
    echo "  Building for Android (multiple architectures)..."
    # Generate C files compatible with both 32-bit and 64-bit
    nim c -c --os:linux --cpu:i386 -d:release --app:staticlib --noMain:on --nimcache:cache_android nimbridge.nim
    BUILD_TARGET="android"
    CACHE_DIR="cache_android" 
    LIB_NAME="libnim_core.a"
    SKIP_COMPILATION=true
fi

NIM_LIB_PATH=""
if command -v nim >/dev/null 2>&1; then
    # Try nim --lib which should give us the lib path
    NIM_LIB_PATH=$(nim --lib 2>/dev/null | head -1 || echo "")
    echo "  nim --lib returned: '$NIM_LIB_PATH'"
    
    # If that fails, try nim dump config  
    if [ -z "$NIM_LIB_PATH" ] || [ ! -d "$NIM_LIB_PATH" ]; then
        NIM_INSTALL_DIR=$(nim dump.d 2>/dev/null | grep "prefixdir" | cut -d'"' -f2 2>/dev/null || echo "")
        echo "  nim dump prefixdir: '$NIM_INSTALL_DIR'"
        if [ -n "$NIM_INSTALL_DIR" ] && [ -d "$NIM_INSTALL_DIR/lib" ]; then
            NIM_LIB_PATH="$NIM_INSTALL_DIR/lib"
        fi
    fi
    
    # Try nim --libpath
    if [ -z "$NIM_LIB_PATH" ] || [ ! -d "$NIM_LIB_PATH" ]; then
        NIM_LIB_PATH=$(nim --libpath 2>/dev/null | head -1 || echo "")
        echo "  nim --libpath returned: '$NIM_LIB_PATH'"
    fi
fi

# Fallback detection methods
if [ -z "$NIM_LIB_PATH" ] || [ ! -d "$NIM_LIB_PATH" ]; then
    # Try Nix store paths (common when using nix develop)
    if command -v nim >/dev/null 2>&1; then
        NIM_EXECUTABLE=$(which nim)
        if [[ "$NIM_EXECUTABLE" == *"/nix/store/"* ]]; then
            # Extract the nix store path and look for lib directory
            NIX_STORE_PATH=$(echo "$NIM_EXECUTABLE" | sed 's|/bin/nim||')
            
            # Try different possible lib locations in Nix store
            POSSIBLE_PATHS=(
                "$NIX_STORE_PATH/nim/lib"
                "$NIX_STORE_PATH/lib"
                "$NIX_STORE_PATH/lib/nim"
                "$(dirname $NIX_STORE_PATH)/*/lib"
                "$(dirname $NIX_STORE_PATH)/*/nim/lib"
            )
            
            for path in "${POSSIBLE_PATHS[@]}"; do
                if [ -d "$path" ] && [ -f "$path/system.nim" -o -f "$path/nim/lib/system.nim" ]; then
                    NIM_LIB_PATH="$path"
                    break
                fi
            done
            
            # Debug: show what we're looking for
            echo "  Debugging Nix paths for: $NIM_EXECUTABLE"
            echo "  Checking: $NIX_STORE_PATH/nim/lib"
            echo "  Checking: $NIX_STORE_PATH/lib"
            
            # If still not found, try to find any nim lib in nix store (but limit search)
            if [ -z "$NIM_LIB_PATH" ] || [ ! -d "$NIM_LIB_PATH" ]; then
                # Look for system.nim in reasonable locations only
                for possible_lib in /nix/store/*/lib /nix/store/*/nim/lib; do
                    if [ -f "$possible_lib/system.nim" ]; then
                        NIM_LIB_PATH="$possible_lib"
                        break
                    fi
                done
            fi
        fi
    fi
    
    # Try traditional package manager locations
    if [ -z "$NIM_LIB_PATH" ] || [ ! -d "$NIM_LIB_PATH" ]; then
        if [ -d "/opt/homebrew/Cellar/nim" ]; then
            NIM_LIB_PATH="/opt/homebrew/Cellar/nim/$(ls /opt/homebrew/Cellar/nim | tail -1)/nim/lib"
        elif [ -d "/usr/local/lib/nim" ]; then
            NIM_LIB_PATH="/usr/local/lib/nim"
        elif [ -d "/opt/homebrew/lib/nim" ]; then
            NIM_LIB_PATH="/opt/homebrew/lib/nim"
        elif [ -d "/usr/lib/nim" ]; then
            NIM_LIB_PATH="/usr/lib/nim"
        else
            echo "❌ Could not find Nim installation. Please ensure Nim is installed and in PATH."
            echo "   Searched in:"
            echo "   - Nix store paths: $NIM_EXECUTABLE"
            echo "   - /opt/homebrew/Cellar/nim, /usr/local/lib/nim, /usr/lib/nim"
            echo "   Current PATH: $PATH"
            exit 1
        fi
    fi
fi

echo "  Using Nim lib path: $NIM_LIB_PATH"

# Skip compilation on Linux since Android builds handle Nim compilation directly
if [ "$SKIP_COMPILATION" = true ]; then
    echo "  Skipping static library compilation (Android will compile Nim during build)"
    
    # Create empty directories to avoid errors in binding generation
    mkdir -p "$CACHE_DIR"
    mkdir -p "$BRIDGE_DIR/android/src/main/cpp"
    mkdir -p "$BRIDGE_DIR/android/src/main/jniLibs/arm64-v8a"
    
    echo "Generating bindings..."
    python3 "$SCRIPT_DIR/generate_bindings.py"
    
    echo "✅ Android bindings ready!"
    echo ""
    echo "Generated files:"
    echo "  - $BRIDGE_DIR/android/src/main/cpp/NimBridge.cpp (Android JNI bridge)"
    echo "  - $BRIDGE_DIR/android/src/main/java/com/nimbridge/NimBridgeModule.java (Android module)"
    echo "  - $BRIDGE_DIR/src/NimBridge.types.ts (TypeScript interface)"
    echo ""
    echo "Next steps:"
    echo "  1. Run 'npm run android'"
    echo "  2. The Nim code will be compiled during the Android build process"
    exit 0
fi

# Compile C files to object files with platform-specific target (iOS only)
cd "$CACHE_DIR"

echo "  Compiling C files in $(pwd)..."
echo "  All files in cache directory:"
ls -la

echo "  Looking for C files matching @m*.c:"
ls -la @m*.c 2>/dev/null || echo "  No @m*.c files found"

echo "  Looking for any .c files:"
ls -la *.c 2>/dev/null || echo "  No .c files found"

# Count C files
C_FILE_COUNT=0
for file in @m*.c; do
    if [ -f "$file" ]; then
        echo "  Found C file: $file"
        C_FILE_COUNT=$((C_FILE_COUNT + 1))
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS: iOS simulator target
            echo "    Compiling with clang for iOS..."
            clang -c -w -ferror-limit=3 -pthread \
                  -I"$NIM_LIB_PATH" \
                  -I.. \
                  -target arm64-apple-ios15.1-simulator \
                  -o "${file}.o" "$file"
        else
            # Linux: Android target  
            echo "    Compiling with gcc for Android..."
            gcc -c -w -pthread \
                -I"$NIM_LIB_PATH" \
                -I.. \
                -fPIC \
                -o "${file}.o" "$file"
        fi
        
        if [ $? -eq 0 ]; then
            echo "    Successfully compiled: ${file}.o"
        else
            echo "    ❌ Failed to compile: $file"
            exit 1
        fi
    fi
done

echo "  Found and processed $C_FILE_COUNT C files"

# Check for object files
echo "  Object files created:"
ls -la *.o 2>/dev/null || echo "  No .o files found!"

if [ $C_FILE_COUNT -eq 0 ]; then
    echo "  ❌ No C files found to compile. Check Nim compilation output above."
    exit 1
fi

# Create archive only if we have object files
OBJ_FILE_COUNT=$(ls *.o 2>/dev/null | wc -l)
if [ $OBJ_FILE_COUNT -gt 0 ]; then
    echo "  Creating static library with $OBJ_FILE_COUNT object files..."
    ar rcs "../$LIB_NAME" *.o
    if [ $? -eq 0 ]; then
        echo "  ✅ Static library created successfully"
    else
        echo "  ❌ Failed to create static library"
        exit 1
    fi
else
    echo "  ❌ No object files to archive"
    exit 1
fi
cd ..

echo "Generated static library: $LIB_NAME"

echo "Copying library to bridge directory..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    mkdir -p "$BRIDGE_DIR/ios"
    cp "$LIB_NAME" "$BRIDGE_DIR/ios/$LIB_NAME"
else
    mkdir -p "$BRIDGE_DIR/android/src/main/jniLibs/arm64-v8a"
    cp "$LIB_NAME" "$BRIDGE_DIR/android/src/main/jniLibs/arm64-v8a/$LIB_NAME"
fi

echo "Generating bindings..."
python3 "$SCRIPT_DIR/generate_bindings.py"

echo "Copying headers..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    cp cache_ios_sim/nimbridge.h "$BRIDGE_DIR/ios/main.h" 2>/dev/null || true
else
    cp cache_android/nimbridge.h "$BRIDGE_DIR/android/src/main/cpp/nimbridge.h" 2>/dev/null || true
fi

echo "Static library and bindings ready!"

echo "Build complete!"
echo ""
echo "Generated files:"
echo "  - $NIM_DIR/$LIB_NAME (Static library with memory management)"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  - $BRIDGE_DIR/ios/nim_functions.h (Function declarations)"
    echo "  - $BRIDGE_DIR/ios/NimBridge.mm (Objective-C++ bridge with freeString calls)"
else
    echo "  - $BRIDGE_DIR/android/src/main/jniLibs/arm64-v8a/$LIB_NAME (Android native library)"
fi
echo "  - $BRIDGE_DIR/android/src/main/cpp/NimBridge.cpp (Android JNI bridge)"
echo "  - $BRIDGE_DIR/src/NimBridge.types.ts (TypeScript interface)"
echo ""
echo ""
echo "Next steps:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  1. Run 'npm run ios' or 'npm run android'"
else
    echo "  1. Run 'npm run android'"
fi
echo "  2. The static library will be automatically linked"
