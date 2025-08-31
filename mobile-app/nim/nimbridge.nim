# Nim module with exported functions for React Native
import strutils, json_serialization, strformat

type
  User = object
    id: int
    name: string
    email: string
    active: bool

proc allocCString(s: string): cstring =
  ## Allocates a new C string that persists beyond function scope
  let cstr = cast[cstring](alloc0(s.len + 1))
  copyMem(cstr, s.cstring, s.len)
  return cstr

proc helloWorld*(): cstring {.exportc.} =
  return "Hello from Nim!"

proc addNumbers*(a: cint, b: cint): cint {.exportc.} =
  return a + b

proc getSystemInfo*(): cstring {.exportc.} =
  let info = fmt"Nim {NimVersion} on iOS (arm64)"
  return allocCString(info)

proc mobileFibonacci*(n: cint): int64 {.exportc.} =
  if n <= 1: return n.int64
  var a: int64 = 0
  var b: int64 = 1
  for i in 2..n:
    let temp = a + b
    a = b
    b = temp
  return b

proc mobileIsPrime*(n: cint): cint {.exportc.} =
  if n <= 1: return 0
  for i in 2..<n:
    if n mod i == 0: return 0
  return 1

proc mobileFactorize*(n: cint): cstring {.exportc.} =
  var factors: seq[int] = @[]
  var num = n.int
  var d = 2
  while d * d <= num:
    while num mod d == 0:
      factors.add(d)
      num = num div d
    d += 1
  if num > 1:
    factors.add(num)
  return allocCString($factors)

proc mobileCreateUser*(id: cint, name: cstring, email: cstring): cstring {.exportc.} =
  let user = User(id: id.int, name: $name, email: $email, active: true)
  return allocCString(Json.encode(user))

proc mobileValidateEmail*(email: cstring): cint {.exportc.} =
  let emailStr = $email
  if "@" in emailStr and "." in emailStr:
    return 1
  return 0

proc getNimCoreVersion*(): cstring {.exportc.} =
  return "1.0.0"

proc freeString*(s: cstring) {.exportc.} =
  ## Frees a string allocated by Nim functions
  if s != nil:
    dealloc(s)

proc mobileNimInit*() {.exportc.} =
  discard

proc mobileNimShutdown*() {.exportc.} =
  discard
