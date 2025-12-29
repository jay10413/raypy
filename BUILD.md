# Build Instructions for Raypy

## Quick Start

### 1. Install Maturin

```bash
pip install maturin
```

### 2. Build the Extension

#### On Windows (PowerShell)

```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY = "1"
maturin build --release
```

#### On Linux/macOS (Bash)

```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin build --release
```

### 3. Install the Wheel

```bash
pip install target/wheels/raypy*.whl
```

### 4. Run Examples

```bash
python examples.py
```

## Development Mode

For development, use `maturin develop` instead of building wheels:

```bash
# Windows
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY = "1"
maturin develop

# Linux/macOS
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
maturin develop
```

This allows you to edit `raypy.py` and see changes immediately without rebuilding.

## Why PYO3_USE_ABI3_FORWARD_COMPATIBILITY?

This environment variable enables the ABI3 stable API, which:

- Builds wheels compatible with multiple Python versions
- Reduces binary size
- Simplifies distribution

## Build System Details

- **Maturin**: Builds PyO3 extension modules and packages them as wheels
- **Cargo**: Manages Rust dependencies and compilation
- **Profile**: Release mode with:
  - `opt-level = 3`: Maximum optimization
  - `lto = true`: Link-time optimization
  - `codegen-units = 1`: Better optimization (slower build)

## Troubleshooting

### Module not found error

- Ensure you've installed the wheel: `pip install target/wheels/raypy*.whl`
- Verify the wheel file exists after building

### Build fails

- Update Rust: `rustup update`
- Update maturin: `pip install --upgrade maturin`
- Check Python version compatibility (3.8+)

### Permission denied on Linux

- Use `sudo pip install ...` or use a virtual environment (recommended)

## Testing Your Build

```python
# test_build.py
from raypy import boost

@boost
def double(n):
    return n * 2

result = double([1, 2, 3, 4, 5])
print(result)  # Should print [2, 4, 6, 8, 10]
```

Run with: `python test_build.py`
