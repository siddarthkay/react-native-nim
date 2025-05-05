# Main entry point for nim-core library
# This module imports all public APIs and mobile bindings

# Import core API
import api/core
export core

# Import mobile bindings
import mobile/bindings
export bindings

# Import business logic (for internal use)
import business/math, business/data

# Version information
const NimCoreVersion* = "1.0.0"

proc getNimCoreVersion*(): cstring {.exportc, dynlib.} =
  ## Returns the version of nim-core library
  return NimCoreVersion.cstring

# Library initialization (required for mobile platforms)
proc NimMain() {.exportc, dynlib.} =
  ## Initialize the Nim runtime - must be called before any other functions
  # This is automatically called on library load for most platforms
  discard