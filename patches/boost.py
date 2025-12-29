"""
raypy: Rust-powered parallel execution for Python functions

This module provides the @boost decorator which automatically runs
Python functions in parallel using Rust and Rayon.
"""

from functools import wraps
from raypy import run_parallel


def boost(func):
    """
    Decorator that accelerates a Python function using Rust + Rayon parallelization.
    
    The decorated function will run the original function in parallel across
    all available CPU cores for each input in a list.
    
    Example:
        @boost
        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)
        
        results = fib([30, 30, 30, 30])  # Runs 4 fib(30) calls in parallel
    
    Args:
        func: A callable that takes a single integer and returns an integer
        
    Returns:
        A wrapped function that accepts either:
        - A list of integers (runs in parallel via Rust)
        - A single integer (falls back to regular Python execution)
    """
    
    @wraps(func)
    def wrapper(inputs):
        # Handle single integer input
        if isinstance(inputs, int):
            return func(inputs)
        
        # Handle list of integers - use Rust parallelization
        if isinstance(inputs, (list, tuple)):
            try:
                results = run_parallel(func, list(inputs)) # pyright: ignore[reportCallIssue]
                return results
            except Exception as e:
                print(f"Rust parallelization failed: {e}")
                print("Falling back to Python execution...")
                return [func(x) for x in inputs]
        
        raise TypeError(
            f"@boost expects integer or list of integers, got {type(inputs)}"
        )
    
    return wrapper


__all__ = ["boost"]
