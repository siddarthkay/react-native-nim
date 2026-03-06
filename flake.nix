{
  description = "React Native + Nim development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            android_sdk.accept_license = true;
          };
        };

        # Android SDK configuration
        androidComposition = pkgs.androidenv.composeAndroidPackages {
          buildToolsVersions = [ "33.0.0" "34.0.0" "35.0.0" ];
          platformVersions = [ "33" "34" "35" ];
          abiVersions = [ "armeabi-v7a" "arm64-v8a" "x86" "x86_64" ];
          includeNDK = true;
          ndkVersions = [ "25.1.8937393" ];
          includeSystemImages = false;
          includeEmulator = false;
        };

        androidSdk = androidComposition.androidsdk;
      in
      {
        devShells.default = pkgs.mkShellNoCC {
          buildInputs = with pkgs; [
            # Node.js (yarn managed by project's corepack)
            nodejs_20

            # Python for generate_bindings.py
            python3
            python3Packages.pip
            nim

            # Build essentials
            git
            gnumake

            # Mobile development tools
            watchman

            # Android development (Linux/macOS)
            androidSdk
            jdk17

            # Additional useful tools
            ripgrep
            jq
            curl
            wget
          ] ++ lib.optionals stdenv.isLinux [
            nimble
            gcc
          ] ++ lib.optionals stdenv.isDarwin [
            # macOS specific tools for iOS development
            cocoapods
          ];

          shellHook = ''
            # Enable Corepack so Yarn v4 (from packageManager field) is used
            # Nix store is read-only, so install corepack shims to a writable directory
            export COREPACK_INSTALL_DIR="$HOME/.corepack-bin"
            mkdir -p "$COREPACK_INSTALL_DIR"
            corepack enable --install-directory "$COREPACK_INSTALL_DIR" 2>/dev/null || true
            export PATH="$COREPACK_INSTALL_DIR:$PATH"
            export COREPACK_ENABLE_STRICT=0
            
            # Create writable Android SDK directory
            export ANDROID_SDK_ROOT="$HOME/.android-sdk-nix"
            export ANDROID_HOME="$ANDROID_SDK_ROOT"
            
            # Set up Android SDK if it doesn't exist
            if [ ! -d "$ANDROID_SDK_ROOT" ]; then
              echo "Setting up Android SDK in $ANDROID_SDK_ROOT..."
              mkdir -p "$ANDROID_SDK_ROOT"
              
              # Copy the Nix Android SDK to writable location
              cp -r ${androidSdk}/libexec/android-sdk/* "$ANDROID_SDK_ROOT/" 2>/dev/null || true
              
              # Make it writable (nix store files are read-only)
              chmod -R u+w "$ANDROID_SDK_ROOT" 2>/dev/null || true

              # Remove nix-copied licenses dir (may be immutable) and recreate fresh
              rm -rf "$ANDROID_SDK_ROOT/licenses" 2>/dev/null || true
              mkdir -p "$ANDROID_SDK_ROOT/licenses"
              mkdir -p "$ANDROID_SDK_ROOT/platforms"
              mkdir -p "$ANDROID_SDK_ROOT/build-tools"
              mkdir -p "$ANDROID_SDK_ROOT/ndk"

              # Accept licenses
              echo "8933bad161af4178b1185d1a37fbf41ea5269c55" > "$ANDROID_SDK_ROOT/licenses/android-sdk-license"
              echo "d56f5187479451eabf01fb78af6dfcb131a6481e" >> "$ANDROID_SDK_ROOT/licenses/android-sdk-license"
              echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" >> "$ANDROID_SDK_ROOT/licenses/android-sdk-license"
              echo "84831b9409646a918e30573bab4c9c91346d8abd" > "$ANDROID_SDK_ROOT/licenses/android-sdk-preview-license"
              echo "79120722343a6f314e0719f863036c702b0e6b2a" > "$ANDROID_SDK_ROOT/licenses/android-googletv-license"
              echo "33b6a2b64607f11b759f320ef9dff4ae5c47d97a" > "$ANDROID_SDK_ROOT/licenses/google-gdk-license"
            fi
            
            # Update PATH to use our writable SDK
            export PATH="$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/tools/bin:${androidSdk}/libexec/android-sdk/platform-tools:${androidSdk}/libexec/android-sdk/tools:${androidSdk}/libexec/android-sdk/tools/bin:$PATH"

            # Platform-specific setup
            if [[ "$OSTYPE" == "darwin"* ]]; then
              # Nix transitive deps (e.g. nim → apple-sdk) set SDKROOT/DEVELOPER_DIR
              # to the Nix SDK and put a broken xcrun wrapper in PATH, unset these
              # and prepend /usr/bin so system Xcode tools take priority.
              unset DEVELOPER_DIR SDKROOT
              unset NIX_CFLAGS_COMPILE NIX_ENFORCE_NO_NATIVE
              unset NIX_IGNORE_LD_THROUGH_GCC NIX_DONT_SET_RPATH NIX_DONT_SET_RPATH_FOR_BUILD NIX_NO_SELF_RPATH
              export PATH="/usr/bin:$PATH"
              echo "  • macOS: iOS and Android development available"
              echo "  • CocoaPods: $(pod --version 2>/dev/null || echo 'not available')"
            else
              echo "  • Linux: Android development only (iOS requires macOS)"
            fi
            
            echo "  • Android SDK: $ANDROID_SDK_ROOT"
            echo "  • Java: $(java -version 2>&1 | head -1)"
            
            # Check for project's Yarn version
            if [ -f "mobile-app/.yarnrc.yml" ]; then
              echo "  • Yarn: v4 (via Corepack)"
            else
              echo "  • Yarn: $(yarn --version 2>/dev/null || echo 'not available')"
            fi

            echo "To get started:"
            echo "  1. cd mobile-app"
            echo "  2. yarn install"
            echo "  3. yarn build:nim"
            if [[ "$OSTYPE" == "darwin"* ]]; then
              echo "  4. yarn ios or yarn android"
            else
              echo "  4. yarn android"
            fi
            echo ""
          '';

          LANG = "en_US.UTF-8";

          NIM_PATH = "${pkgs.nim}/nim";

          # Node.js memory limit for large projects
          NODE_OPTIONS = "--max-old-space-size=8192";
        };
      });
}
