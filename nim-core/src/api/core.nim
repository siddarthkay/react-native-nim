# Core API definitions for mobile consumption
# This module defines the public interface that will be exposed to mobile apps

import std/strformat

proc allocCString*(s: string): cstring =
  ## Allocates a new C string from a Nim string that persists beyond function scope
  ## The caller is responsible for freeing this memory
  let cstr = cast[cstring](alloc0(s.len + 1))
  copyMem(cstr, s.cstring, s.len)
  return cstr

proc helloWorld*(): cstring {.exportc, dynlib.} =
  ## Returns a greeting message from Nim core
  ## Note: Returns a static string literal which is safe
  return "Hello from Nim Core! 🎉"

proc addNumbers*(a: cint, b: cint): cint {.exportc, dynlib.} =
  ## Adds two integers and returns the result
  return a + b

proc getSystemInfo*(): cstring {.exportc, dynlib.} =
  ## Returns basic system information
  ## Allocates memory that must be freed by the caller
  let info = fmt"Nim {NimVersion} on {hostOS} ({hostCPU})"
  return allocCString(info)

proc freeString*(s: cstring) {.exportc, dynlib.} =
  ## Frees a string allocated by Nim functions
  ## Call this from the mobile side after consuming the string
  if s != nil:
    dealloc(s)