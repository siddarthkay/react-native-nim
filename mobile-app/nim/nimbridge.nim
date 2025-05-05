# Nim module with exported functions for React Native
import strutils, json

proc helloWorld*(): cstring {.exportc.} =
  return "Hello from Nim!"

proc addNumbers*(a: cint, b: cint): cint {.exportc.} =
  return a + b

proc getSystemInfo*(): cstring {.exportc.} =
  return "Nim 2.0 on iOS"

proc mobileFibonacci*(n: cint): cint {.exportc.} =
  if n <= 1: return n
  return mobileFibonacci(n - 1) + mobileFibonacci(n - 2)

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
  return ($factors).cstring

proc mobileCreateUser*(id: cint, name: cstring, email: cstring): cstring {.exportc.} =
  let userJson = %* {"id": id, "name": $name, "email": $email}
  return ($userJson).cstring

proc mobileValidateEmail*(email: cstring): cint {.exportc.} =
  let emailStr = $email
  if "@" in emailStr and "." in emailStr:
    return 1
  return 0

proc getNimCoreVersion*(): cstring {.exportc.} =
  return "1.0.0"

proc mobileNimInit*() {.exportc.} =
  discard

proc mobileNimShutdown*() {.exportc.} =
  discard
