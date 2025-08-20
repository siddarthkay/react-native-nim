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
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Node.js and package managers
            nodejs_20
            nodePackages.npm
            nodePackages.yarn

            # Python for generate_bindings.py
            python3
            python3Packages.pip

            # Nim compiler
            nim

            # Build essentials
            git
            gnumake
            gcc

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
          ] ++ lib.optionals stdenv.isDarwin [
            # macOS specific tools for iOS development
            cocoapods
            darwin.apple_sdk.frameworks.CoreServices
            darwin.libobjc
          ];

          shellHook = ''
            # Create writable Android SDK directory
            export ANDROID_SDK_ROOT="$HOME/.android-sdk-nix"
            export ANDROID_HOME="$ANDROID_SDK_ROOT"
            
            # Set up Android SDK if it doesn't exist
            if [ ! -d "$ANDROID_SDK_ROOT" ]; then
              echo "Setting up Android SDK in $ANDROID_SDK_ROOT..."
              mkdir -p "$ANDROID_SDK_ROOT"
              
              # Copy the Nix Android SDK to writable location
              cp -r ${androidSdk}/libexec/android-sdk/* "$ANDROID_SDK_ROOT/" 2>/dev/null || true
              
              # Make it writable
              chmod -R u+w "$ANDROID_SDK_ROOT" 2>/dev/null || true
              
              # Create necessary directories
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
              echo "  • macOS: iOS and Android development available"
              echo "  • CocoaPods: $(pod --version 2>/dev/null || echo 'not available')"
            else
              echo "  • Linux: Android development only (iOS requires macOS)"
            fi
            
            echo "  • Android SDK: $ANDROID_SDK_ROOT"
            echo "  • Java: $(java -version 2>&1 | head -1)"

            echo "To get started:"
            echo "  1. cd mobile-app"
            echo "  2. npm install"
            echo "  3. npm run build:nim"
            if [[ "$OSTYPE" == "darwin"* ]]; then
              echo "  4. npm run ios or npm run android"
            else
              echo "  4. npm run android"
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
