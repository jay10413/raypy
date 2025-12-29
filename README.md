# Raypy: Rust-Powered Parallel Python Execution

A hybrid Rust + Python library that automatically parallelizes Python functions across CPU cores using Rayon.

## Overview

**Raypy** lets you write pure Python code, decorate it with `@boost`, and have it automatically execute in parallel using Rust and Rayon. No changes to your function implementation needed.

```python
from raypy import boost

@boost
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# Run fib(30) across 1000 inputs in parallel
results = fib([30] * 1000)
print(results)
```

## Features

- **Zero-copy parallelization**: Uses Rust + Rayon for CPU-bound workloads
- **GIL management**: Properly releases and reacquires Python's Global Interpreter Lock
- **Simple decorator**: Just add `@boost` to enable parallelization
- **Automatic fallback**: Falls back to Python execution if Rust unavailable
- **Optimized release builds**: LTO and single codegen unit for maximum performance

## Architecture

### Rust Side (`src/lib.rs`)

- **`run_parallel(py_func, inputs)`**: Core function that:
  - Takes a Python callable and list of integers
  - Releases the GIL while running Rayon threads
  - Re-acquires GIL in each thread to call the Python function
  - Returns list of results
  - Compiled as a PyO3 extension module

### Python Side (`raypy.py`)

- **`@boost` decorator**: Wraps any Python function to:
  - Intercept list inputs
  - Call Rust `run_parallel` for parallel execution
  - Fall back to sequential Python if needed
  - Support both single integers and lists of integers

## Building

### Prerequisites

- Rust (with `cargo`)
- Python 3.8+
- `maturin` for building wheels

### Installation

1. Clone the repository:

```bash
git clone https://pro-grammer-SD/raypy.git
cd raypy
```

1. Build the Rust extension:

```bash
# On Windows
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin build --release

# On Linux/macOS
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin build --release
```

1. Install the wheel:

```bash
pip install target/wheels/raypy*.whl
```

Or develop locally:

```bash
maturin develop
```

## Usage

### Basic Example

```python
from raypy import boost

@boost
def square(n):
    return n * n

# Single value (uses Python)
result = square(5)  # Returns 25

# Multiple values (uses Rust + Rayon)
results = square([1, 2, 3, 4, 5])  # Returns [1, 4, 9, 16, 25]
```

### CPU-Intensive Example

```python
from raypy import boost

@boost
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# Run expensive computation in parallel
nums = [30] * 8
results = fib(nums)
print(results)  # [832040, 832040, 832040, 832040, 832040, 832040, 832040, 832040]
```

### Complex Function Example

```python
from raypy import boost
import math

@boost
def is_prime(n):
    if n < 2:
        return 0
    if n == 2:
        return 1
    if n % 2 == 0:
        return 0
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return 0
    return 1

# Check primality in parallel
numbers = [97, 100, 101, 103, 104, 105, 107]
results = is_prime(numbers)  # [1, 0, 1, 1, 0, 0, 1]
```

## Performance Tips

1. **Best for CPU-bound functions**: Functions that do heavy computation
2. **Input overhead**: Works best with lists of 10+ items (parallelization overhead)
3. **Function simplicity**: Simpler functions show better speedup
4. **Release mode**: Always use `--release` for production builds

## Project Structure

```bash
raypy/
├── Cargo.toml           # Rust dependencies
├── src/
│   └── lib.rs           # Rust + PyO3 implementation
├── raypy.py             # Python decorator wrapper
└── README.md            # This file
```

## Dependencies

### Rust

- **pyo3** (0.21+): Python bindings
- **rayon** (1.8+): Data parallelism

### Python

- Python 3.8+

## Advanced: How It Works

1. User calls `@boost` decorated function with a list of integers
2. The decorator calls `run_parallel(func, inputs)` from the Rust module
3. Rust releases the Python GIL with `py.allow_threads()`
4. Rayon spawns threads and maps `py_func` across all inputs in parallel
5. Each thread re-acquires the GIL to call the Python function
6. Results are collected and returned to Python
7. Python decorator returns the result list

This design allows:

- Full parallelization of Python code
- Proper GIL management (not holding it during parallel work)
- Transparent integration with existing Python code

## Limitations

- Function must accept a single `i32` and return `i32`
- Works only with lists of integers
- Requires Rust/Cargo toolchain to build
- GIL re-acquisition per thread has overhead for very quick functions

## License

MIT

## Contributing

Contributions welcome! Please ensure:

1. Code builds with `maturin build --release`
2. Examples work as documented
3. Tests pass
