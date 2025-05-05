# Core API definitions for mobile consumption
# This module defines the public interface that will be exposed to mobile apps

import std/strformat

proc helloWorld*(): cstring {.exportc, dynlib.} =
  ## Returns a greeting message from Nim core
  return "Hello from Nim Core! 🎉"

proc addNumbers*(a: cint, b: cint): cint {.exportc, dynlib.} =
  ## Adds two integers and returns the result
  return a + b

proc getSystemInfo*(): cstring {.exportc, dynlib.} =
  ## Returns basic system information
  let info = fmt"Nim {NimVersion} on {hostOS} ({hostCPU})"
  return info.cstring