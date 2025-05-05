#!/bin/bash

# Build Nim for Android (multiple architectures)
set -e

echo "Building Nim code for Android..."

cd ../nim

# Clean previous builds
rm -rf cache_android_*
mkdir -p cache_android

# Compile Nim to C files for Android (generic - let NDK handle architecture)
# We compile for Linux as base OS and let Android NDK handle the cross-compilation
nim c --os:linux --compileOnly --nimcache:cache_android nimbridge.nim

echo "Nim Android build completed!"
echo "C files generated in nim/cache_android/"