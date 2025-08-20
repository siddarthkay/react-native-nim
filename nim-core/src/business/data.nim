# Business logic for data processing operations
# This demonstrates data manipulation and JSON handling

import json_serialization, std/strutils

type
  User* = object
    id*: int
    name*: string
    email*: string
    active*: bool

proc createUser*(id: int, name: string, email: string): User =
  ## Create a new user object
  return User(id: id, name: name, email: email, active: true)

proc userToJson*(user: User): string =
  return Json.encode(user)

proc userFromJson*(jsonStr: string): User =
  return Json.decode(jsonStr, User)

proc validateEmail*(email: string): bool =
  ## Simple email validation
  return "@" in email and "." in email
