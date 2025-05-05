# Business logic for mathematical operations
# This demonstrates how core business logic is separated from mobile bindings

proc fibonacci*(n: int): int =
  ## Calculate the nth Fibonacci number
  if n <= 1:
    return n
  else:
    return fibonacci(n - 1) + fibonacci(n - 2)

proc isPrime*(n: int): bool =
  ## Check if a number is prime
  if n < 2:
    return false
  for i in 2..(n div 2):
    if n mod i == 0:
      return false
  return true

proc factorize*(n: int): seq[int] =
  ## Return all factors of a number
  result = @[]
  for i in 1..n:
    if n mod i == 0:
      result.add(i)