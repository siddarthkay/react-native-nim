# create-react-native-nim

Scaffold a React Native app with Nim business logic in seconds. Write functions in Nim, get automatic iOS/Android/TypeScript bindings via TurboModules (New Architecture).

## Usage

```bash
npx create-react-native-nim my-app --bundleId com.mycompany.myapp
cd my-app
yarn install
make build-nim
yarn ios    # or: yarn android
```

If you omit `--bundleId`, the CLI will prompt you interactively.

## What You Get

```
my-app/
├── Makefile                          # Build orchestrator
├── nim/
│   ├── nimbridge.nim                 # Nim business logic ({.exportc.})
│   └── nimbridge.nimble              # Nim dependencies
├── modules/nim-bridge/
│   ├── src/NativeNimBridge.ts        # TurboModule spec (auto-generated)
│   ├── ios/                          # Objective-C++ bridge (auto-generated)
│   └── android/                      # Kotlin/JNI bridge (auto-generated)
├── tools/
│   ├── generate_bindings.py          # Binding generator
│   └── generator_config.json         # Type mappings and config
├── src/App.tsx                       # React Native app
├── ios/                              # iOS native project
└── android/                          # Android native project
```

## Prerequisites

- Node.js 18+
- Nim 2.0+ (`brew install nim`)
- Python 3 (for binding generator)
- iOS: Xcode, CocoaPods
- Android: Android SDK, JDK 17+

Or use the included Nix flake: `nix develop`

## Options

| Flag | Description | Example |
|------|-------------|---------|
| `--bundleId` | App bundle identifier | `com.mycompany.myapp` |

The first positional argument is the app name (e.g. `my-app`).

## How It Works

1. Write Nim functions with `{.exportc.}` pragma
2. Run `make build-nim` to compile Nim to C and auto-generate all bridge code
3. iOS/Android apps call Nim functions directly via TurboModules/JSI — no bridge overhead

## Links

- [GitHub Repository](https://github.com/siddarthkay/react-native-nim)
- [Issues](https://github.com/siddarthkay/react-native-nim/issues)

## License

MIT
