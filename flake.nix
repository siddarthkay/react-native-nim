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
          buildToolsVersions = [ "33.0.0" "34.0.0" ];
          platformVersions = [ "33" "34" ];
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
            cocoapods

            # Android development (if on Linux/macOS)
            androidSdk
            jdk17

            # Additional useful tools
            ripgrep
            jq
            curl
            wget
          ] ++ lib.optionals stdenv.isDarwin [
            # macOS specific tools
            darwin.apple_sdk.frameworks.CoreServices
            darwin.libobjc
          ];

          shellHook = ''
            # Set up Android environment variables
            export ANDROID_SDK_ROOT="${androidSdk}/libexec/android-sdk"
            export ANDROID_HOME="$ANDROID_SDK_ROOT"
            export PATH="$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/tools/bin:$PATH"

            # Set up iOS environment variables (macOS only)
            if [[ "$OSTYPE" == "darwin"* ]]; then
              echo "  • CocoaPods: $(pod --version 2>/dev/null || echo 'not available')"
            fi

            echo "To get started:"
            echo "  1. cd mobile-app"
            echo "  2. npm install"
            echo "  3. npm run build:nim"
            echo "  4. npm run ios/android"
            echo ""
          '';

          LANG = "en_US.UTF-8";

          NIM_PATH = "${pkgs.nim}/nim";

          # Node.js memory limit for large projects
          NODE_OPTIONS = "--max-old-space-size=8192";
        };
      });
}
