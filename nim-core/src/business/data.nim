# Business logic for data processing operations
# This demonstrates data manipulation and JSON handling

import std/json, std/tables, std/strutils

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
  ## Convert user object to JSON string
  let jsonObj = %*{
    "id": user.id,
    "name": user.name,
    "email": user.email,
    "active": user.active
  }
  return $jsonObj

proc userFromJson*(jsonStr: string): User =
  ## Parse user object from JSON string
  let jsonObj = parseJson(jsonStr)
  return User(
    id: jsonObj["id"].getInt(),
    name: jsonObj["name"].getStr(),
    email: jsonObj["email"].getStr(),
    active: jsonObj["active"].getBool()
  )

proc validateEmail*(email: string): bool =
  ## Simple email validation
  return "@" in email and "." in email