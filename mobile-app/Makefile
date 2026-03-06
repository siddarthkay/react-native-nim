YARN ?= yarn
GRADLEW = android/gradlew
ANDROID_APK = android/app/build/outputs/apk/release/app-release.apk

XCODE_WORKSPACE = ios/nimrnmobileapp.xcworkspace
XCODE_SCHEME = nimrnmobileapp
XCODE_DERIVEDDATA = ios/build

NIM_DIR = nim
NIM_SRC = $(NIM_DIR)/nimbridge.nim
BRIDGE_DIR = modules/nim-bridge
TOOLS_DIR = tools
LIB_NAME = libnim_core.a

# Resolve Nim lib path (nimbase.h location) — works with Nix, Homebrew, system Nim
NIM_LIB_PATH := $(shell nim dump 2>&1 | while read -r line; do \
	if [ -f "$$line/nimbase.h" ]; then echo "$$line"; break; fi; \
done)
# Fallback: follow Nix wrapper
ifeq ($(NIM_LIB_PATH),)
NIM_LIB_PATH := $(shell NIM_EXE=$$(which nim) && \
	if file "$$NIM_EXE" 2>/dev/null | grep -q text; then \
		REAL=$$(grep -oE '"/nix/store/[^"]+/bin/nim"' "$$NIM_EXE" 2>/dev/null | tr -d '"'); \
		for p in $$(echo "$$REAL" | sed 's|/bin/nim||')/nim/lib $$(echo "$$REAL" | sed 's|/bin/nim||')/lib; do \
			[ -f "$$p/nimbase.h" ] && echo "$$p" && break; \
		done; \
	fi)
endif
# Fallback: CI / package manager
ifeq ($(NIM_LIB_PATH),)
NIM_LIB_PATH := $(shell \
	for p in /opt/nim/lib /opt/homebrew/lib/nim /usr/local/lib/nim /usr/lib/nim; do \
		[ -f "$$p/nimbase.h" ] && echo "$$p" && break; \
	done)
endif

.PHONY: install pod-install codegen build-nim nim-deps nim-compile nim-static-lib nim-bindings nim-headers \
	build-ios build-android run-ios run-android \
	clean-nim clean-ios clean-android clean clean-all help

# --- Node / CocoaPods ---

install:
	@echo "Installing Node dependencies..."
	@$(YARN) install
	@echo "✓ Node dependencies installed"

pod-install:
	@echo "Installing CocoaPods dependencies..."
	@cd ios && pod install
	@echo "✓ CocoaPods installed"

codegen:
	@echo "Generating React Native codegen artifacts..."
	@RCT_NEW_ARCH_ENABLED=1 node node_modules/react-native/scripts/generate-codegen-artifacts.js \
		--path . --targetPlatform ios --outputPath ios/build/generated/ios
	@echo "✓ Codegen complete"

# --- Nim build pipeline ---

nim-deps:
	@if [ -f $(NIM_DIR)/nimbridge.nimble ]; then \
		echo "Installing Nim dependencies..."; \
		cd $(NIM_DIR) && nimble install -d -y; \
	fi

nim-compile: nim-deps
	@echo "Compiling Nim to C..."
	@rm -rf $(NIM_DIR)/cache_ios_sim $(NIM_DIR)/cache_android
ifeq ($(shell uname),Darwin)
	@cd $(NIM_DIR) && nim c -c --os:ios --cpu:arm64 -d:ios --app:staticlib --noMain:on --nimcache:cache_ios_sim nimbridge.nim
	@cd $(NIM_DIR) && nim c -c --os:android --cpu:arm64 -d:android --app:staticlib --noMain:on --nimcache:cache_android nimbridge.nim
else
	@cd $(NIM_DIR) && nim c -c --os:android --cpu:arm64 -d:android -d:release --app:staticlib --noMain:on --nimcache:cache_android nimbridge.nim
endif
	@echo "✓ Nim → C compilation complete"

nim-static-lib: nim-compile
ifeq ($(shell uname),Darwin)
	@echo "Building iOS static library..."
	@cd $(NIM_DIR)/cache_ios_sim && \
		for f in *.c; do \
			clang -c -w -ferror-limit=3 -pthread \
				-I"$(NIM_LIB_PATH)" -I.. \
				-target arm64-apple-ios15.1-simulator \
				-o "$$f.o" "$$f"; \
		done && \
		ar rcs ../$(LIB_NAME) *.o
	@mkdir -p $(BRIDGE_DIR)/ios
	@cp $(NIM_DIR)/$(LIB_NAME) $(BRIDGE_DIR)/ios/$(LIB_NAME)
	@echo "✓ Static library: $(BRIDGE_DIR)/ios/$(LIB_NAME)"
else
	@echo "Skipping static lib (Android compiles Nim C files via CMake)"
	@mkdir -p $(BRIDGE_DIR)/android/src/main/cpp
	@mkdir -p $(BRIDGE_DIR)/android/src/main/jniLibs/arm64-v8a
endif

nim-bindings:
	@echo "Generating bridge bindings..."
	@python3 $(TOOLS_DIR)/generate_bindings.py
	@echo "✓ Bindings generated"

nim-headers:
	@echo "Copying headers..."
ifeq ($(shell uname),Darwin)
	@cp $(NIM_DIR)/cache_ios_sim/nimbridge.h $(BRIDGE_DIR)/ios/main.h 2>/dev/null || true
	@[ -f "$(NIM_LIB_PATH)/nimbase.h" ] && cp "$(NIM_LIB_PATH)/nimbase.h" $(BRIDGE_DIR)/ios/nimbase.h
	@[ -f "$(NIM_LIB_PATH)/nimbase.h" ] && [ -d "$(NIM_DIR)/cache_android" ] && \
		cp "$(NIM_LIB_PATH)/nimbase.h" $(NIM_DIR)/cache_android/nimbase.h
else
	@cp $(NIM_DIR)/cache_android/nimbridge.h $(BRIDGE_DIR)/android/src/main/cpp/nimbridge.h 2>/dev/null || true
	@[ -f "$(NIM_LIB_PATH)/nimbase.h" ] && cp "$(NIM_LIB_PATH)/nimbase.h" $(BRIDGE_DIR)/android/src/main/cpp/nimbase.h
endif
	@echo "✓ Headers copied"

build-nim: nim-static-lib nim-bindings nim-headers
	@echo "✓ Nim build complete (lib path: $(NIM_LIB_PATH))"

# --- Platform builds ---

build-ios: install build-nim codegen pod-install
	@echo "Building iOS Simulator app..."
	@set -o pipefail && env -i HOME=$(HOME) PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=en_US.UTF-8 \
		xcodebuild -workspace $(XCODE_WORKSPACE) \
		-scheme $(XCODE_SCHEME) \
		-sdk iphonesimulator \
		-configuration Release \
		-destination 'generic/platform=iOS Simulator' \
		-derivedDataPath $(XCODE_DERIVEDDATA) \
		CODE_SIGNING_ALLOWED=NO \
		ARCHS=arm64 \
		ONLY_ACTIVE_ARCH=YES
	@echo "✓ iOS app built at $(XCODE_DERIVEDDATA)/Build/Products/Release-iphonesimulator/$(XCODE_SCHEME).app"

build-android: install build-nim
	@echo "Building Android Release APK..."
	@chmod +x $(GRADLEW)
	@cd android && ./gradlew assembleRelease --no-daemon
	@echo "✓ Android APK built at $(ANDROID_APK)"

run-ios:
	@env -i HOME=$(HOME) LANG=en_US.UTF-8 TERM=$(TERM) \
		PATH="/usr/bin:/bin:/usr/sbin:/sbin:$$(dirname $$(which node)):$$(pwd)/node_modules/.bin" \
		npx expo run:ios

run-android:
	@npx expo run:android

# --- Cleanup ---

clean-nim:
	@echo "Cleaning Nim build artifacts..."
	@rm -rf $(NIM_DIR)/cache_ios_sim $(NIM_DIR)/cache_android
	@rm -f $(NIM_DIR)/$(LIB_NAME)
	@echo "✓ Nim clean complete"

clean-ios:
	@echo "Cleaning iOS build..."
	@rm -rf $(XCODE_DERIVEDDATA)
	@echo "✓ iOS clean complete"

clean-android:
	@echo "Cleaning Android build..."
	@cd android && ./gradlew clean --no-daemon 2>/dev/null || true
	@echo "✓ Android clean complete"

clean: clean-nim clean-ios clean-android

clean-all: clean
	@echo "Cleaning Node modules and Pods..."
	@rm -rf node_modules
	@rm -rf ios/Pods
	@echo "✓ Full clean complete"

# --- Help ---

help:
	@echo "Available targets:"
	@echo "  make install        - Install Node dependencies"
	@echo "  make pod-install    - Install CocoaPods dependencies"
	@echo "  make codegen        - Generate React Native codegen artifacts"
	@echo ""
	@echo "  make build-nim      - Full Nim pipeline (compile + static lib + bindings + headers)"
	@echo "  make nim-deps       - Install Nim dependencies (nimble)"
	@echo "  make nim-compile    - Compile Nim to C files"
	@echo "  make nim-static-lib - Compile C files into static library"
	@echo "  make nim-bindings   - Generate TypeScript/iOS/Android bridge code"
	@echo "  make nim-headers    - Copy nimbase.h and generated headers"
	@echo ""
	@echo "  make build-ios      - Build iOS Simulator app (full pipeline)"
	@echo "  make build-android  - Build Android Release APK (full pipeline)"
	@echo "  make run-ios        - Dev build + deploy to iOS Simulator"
	@echo "  make run-android    - Dev build + deploy to Android emulator"
	@echo ""
	@echo "  make clean-nim      - Clean Nim build artifacts"
	@echo "  make clean-ios      - Clean iOS build artifacts"
	@echo "  make clean-android  - Clean Android build artifacts"
	@echo "  make clean          - Clean all build artifacts"
	@echo "  make clean-all      - Clean everything including node_modules"
