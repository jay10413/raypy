"""
Example usage of the @boost decorator
"""

from raypy import boost
import time


@boost
def fib(n):
    """Fibonacci calculation - CPU-bound"""
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)


@boost
def square(n):
    """Simple square calculation"""
    return n * n


@boost
def is_prime(n):
    """Check if number is prime"""
    if n < 2:
        return 0
    if n == 2:
        return 1
    if n % 2 == 0:
        return 0
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return 0
    return 1


if __name__ == "__main__":
    # Example 1: Simple computation
    print("Example 1: Square calculation")
    results = square([1, 2, 3, 4, 5])
    print(f"square([1, 2, 3, 4, 5]) = {results}")
    print()

    # Example 2: Single value (uses Python)
    print("Example 2: Single value")
    single_result = square(7)
    print(f"square(7) = {single_result}")
    print()

    # Example 3: Prime checking
    print("Example 3: Prime checking")
    nums = [97, 100, 101, 103, 104, 105, 107]
    results = is_prime(nums)
    print(f"is_prime({nums}) = {results}")
    print()

    # Example 4: CPU-intensive Fibonacci
    print("Example 4: Fibonacci (CPU-intensive)")
    print("Running fib(30) on 8 parallel inputs...")
    start = time.time()
    results = fib([30] * 8)
    elapsed = time.time() - start
    print(f"Results: {results}")
    print(f"Time: {elapsed:.2f}s")
    