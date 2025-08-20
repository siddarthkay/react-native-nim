# Package definition for nim-core library

version       = "1.0.0"
author        = "Nim Core Team"
description   = "Core business logic library for React Native integration"
license       = "MIT"
srcDir        = "src"

# Dependencies
requires "nim >= 2.0.0"
requires "json_serialization"

# Tasks for building mobile bindings
task android, "Build Android bindings":
  exec "nim c -d:android --app:lib --noMain --header --nimcache:../bindings/android src/main.nim"
  echo "Android bindings generated in bindings/android/"

task ios, "Build iOS bindings":
  exec "nim c -d:ios --app:lib --noMain --header --nimcache:../bindings/ios src/main.nim"
  echo "iOS bindings generated in bindings/ios/"

task clean, "Clean generated files":
  rmDir "bindings"
  echo "Cleaned generated bindings"

task test, "Run tests":
  exec "nim c -r tests/test_core.nim"