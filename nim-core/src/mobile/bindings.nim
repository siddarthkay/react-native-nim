# Mobile-specific bindings that wrap business logic for React Native
# This module provides C-compatible functions for mobile consumption

import ../business/math
import ../business/data
import ../api/core  # Import for allocCString
import std/strformat

# Math operations bindings
proc mobileFibonacci*(n: cint): cint {.exportc, dynlib.} =
  ## Mobile wrapper for Fibonacci calculation
  return fibonacci(n.int).cint

proc mobileIsPrime*(n: cint): cint {.exportc, dynlib.} =
  ## Mobile wrapper for prime number check (returns 1 for true, 0 for false)
  return if isPrime(n.int): 1 else: 0

proc mobileFactorize*(n: cint): cstring {.exportc, dynlib.} =
  ## Mobile wrapper for factorization (returns comma-separated string)
  ## Allocates memory that must be freed by the caller
  let factors = factorize(n.int)
  var result = ""
  for i, factor in factors:
    if i > 0: result.add(",")
    result.add($factor)
  return allocCString(result)

# Data operations bindings
proc mobileCreateUser*(id: cint, name: cstring, email: cstring): cstring {.exportc, dynlib.} =
  ## Mobile wrapper for user creation (returns JSON string)
  ## Allocates memory that must be freed by the caller
  let user = createUser(id.int, $name, $email)
  return allocCString(userToJson(user))

proc mobileValidateEmail*(email: cstring): cint {.exportc, dynlib.} =
  ## Mobile wrapper for email validation (returns 1 for valid, 0 for invalid)
  return if validateEmail($email): 1 else: 0

# Memory management helper for mobile
proc mobileNimInit*() {.exportc, dynlib.} =
  ## Initialize Nim runtime for mobile
  # This should be called before any other Nim functions
  discard

proc mobileNimShutdown*() {.exportc, dynlib.} =
  ## Cleanup Nim runtime for mobile
  # This should be called when shutting down
  discard