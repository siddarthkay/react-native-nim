# Test suite for nim-core library
# Run with: nimble test

import unittest
import ../src/business/math
import ../src/business/data

suite "Math Operations":
  test "fibonacci calculation":
    check fibonacci(0) == 0
    check fibonacci(1) == 1
    check fibonacci(5) == 5
    check fibonacci(10) == 55

  test "prime number detection":
    check isPrime(2) == true
    check isPrime(3) == true
    check isPrime(4) == false
    check isPrime(17) == true
    check isPrime(25) == false

  test "factorization":
    let factors12 = factorize(12)
    check 1 in factors12
    check 2 in factors12
    check 3 in factors12
    check 4 in factors12
    check 6 in factors12
    check 12 in factors12

suite "Data Operations":
  test "user creation":
    let user = createUser(1, "John Doe", "john@example.com")
    check user.id == 1
    check user.name == "John Doe"
    check user.email == "john@example.com"
    check user.active == true

  test "email validation":
    check validateEmail("test@example.com") == true
    check validateEmail("invalid-email") == false
    check validateEmail("") == false
    check validateEmail("user@domain.co.uk") == true

  test "JSON serialization":
    let user = createUser(2, "Jane Smith", "jane@test.com")
    let jsonStr = userToJson(user)
    check "Jane Smith" in jsonStr
    check "jane@test.com" in jsonStr
    
    let parsedUser = userFromJson(jsonStr)
    check parsedUser.id == user.id
    check parsedUser.name == user.name
    check parsedUser.email == user.email