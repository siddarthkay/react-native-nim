#!/bin/bash

# Mobile build script for Nim-React Native integration
# This script automates the entire build process similar to go-mobile

set -e

echo "🚀 Nim-React Native Mobile Build Script"
echo "======================================="

# Configuration
NIM_CORE_DIR="nim-core"
BINDINGS_DIR="bindings"
MOBILE_APP_DIR="mobile-app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Nim is installed
    if ! command -v nim &> /dev/null; then
        log_error "Nim compiler not found. Please install Nim first."
        exit 1
    fi
    
    local nim_version=$(nim --version | head -n1)
    log_success "Found $nim_version"
    
    # Check if we're in the right directory
    if [ ! -d "$NIM_CORE_DIR" ]; then
        log_error "nim-core directory not found. Please run from monorepo root."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate bindings
generate_bindings() {
    log_info "Generating Nim bindings..."
    
    # Compile the binding generator
    nim c tools/generate_bindings.nim
    
    # Run the binding generator
    ./tools/generate_bindings
    
    log_success "Bindings generated"
}

# Build Android bindings
build_android() {
    log_info "Building Android-specific bindings..."
    
    local android_dir="$BINDINGS_DIR/android"
    
    if [ ! -d "$android_dir" ]; then
        log_error "Android bindings not found. Run generate_bindings first."
        exit 1
    fi
    
    # Copy bindings to mobile app
    if [ -d "$MOBILE_APP_DIR/android/app/src/main/cpp" ]; then
        cp -r "$android_dir"/* "$MOBILE_APP_DIR/android/app/src/main/cpp/"
        cp "$BINDINGS_DIR/headers/nim_core.h" "$MOBILE_APP_DIR/android/app/src/main/cpp/"
        log_success "Android bindings copied to mobile app"
    else
        log_warning "Mobile app Android directory not found"
    fi
}

# Build iOS bindings
build_ios() {
    log_info "Building iOS-specific bindings..."
    
    local ios_dir="$BINDINGS_DIR/ios"
    
    if [ ! -d "$ios_dir" ]; then
        log_error "iOS bindings not found. Run generate_bindings first."
        exit 1
    fi
    
    # Copy bindings to mobile app
    if [ -d "$MOBILE_APP_DIR/ios" ]; then
        cp -r "$ios_dir"/* "$MOBILE_APP_DIR/ios/"
        cp "$BINDINGS_DIR/headers/nim_core.h" "$MOBILE_APP_DIR/ios/"
        log_success "iOS bindings copied to mobile app"
    else
        log_warning "Mobile app iOS directory not found"
    fi
}

# Update TypeScript definitions
update_typescript() {
    log_info "Updating TypeScript definitions..."
    
    if [ -f "$BINDINGS_DIR/headers/nim_core.d.ts" ]; then
        cp "$BINDINGS_DIR/headers/nim_core.d.ts" "$MOBILE_APP_DIR/src/"
        log_success "TypeScript definitions updated"
    else
        log_warning "TypeScript definitions not found"
    fi
}

# Clean build artifacts
clean() {
    log_info "Cleaning build artifacts..."
    
    rm -rf "$BINDINGS_DIR"
    rm -f tools/generate-bindings
    
    log_success "Clean complete"
}

# Main execution
main() {
    case "${1:-all}" in
        "clean")
            clean
            ;;
        "check")
            check_prerequisites
            ;;
        "generate")
            check_prerequisites
            generate_bindings
            ;;
        "android")
            check_prerequisites
            generate_bindings
            build_android
            update_typescript
            ;;
        "ios")
            check_prerequisites
            generate_bindings
            build_ios
            update_typescript
            ;;
        "all"|"")
            check_prerequisites
            generate_bindings
            build_android
            build_ios
            update_typescript
            log_success "🎉 Full build complete!"
            ;;
        *)
            echo "Usage: $0 [clean|check|generate|android|ios|all]"
            echo ""
            echo "Commands:"
            echo "  clean     - Clean build artifacts"
            echo "  check     - Check prerequisites only"
            echo "  generate  - Generate bindings only"
            echo "  android   - Build Android bindings"
            echo "  ios       - Build iOS bindings"
            echo "  all       - Build everything (default)"
            exit 1
            ;;
    esac
}

main "$@"