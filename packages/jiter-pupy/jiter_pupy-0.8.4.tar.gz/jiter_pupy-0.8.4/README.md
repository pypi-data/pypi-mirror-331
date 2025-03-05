# jiter-pupy: Pure Python jiter Implementation

A drop-in replacement for the [jiter](https://github.com/pydantic/jiter) package that is API-compatible with the original Rust-based implementation, but uses only Python's standard library `json` module.

## Features

- **100% API compatible** with the Rust-based jiter package
- **Pure Python implementation** using only the standard library
- **No compilation required** - works anywhere Python runs
- Supports all jiter features:
  - String caching for performance
  - Partial JSON parsing
  - Different float modes (float, decimal, lossless-float)
  - Special value handling (Infinity, NaN)
  - Duplicate key detection

## Installation

```bash
pip install jiter-pupy
```

## Usage

```python
import jiter_pupy as jiter

# Parse JSON data
data = jiter.from_json(b'{"name": "John", "age": 30}')
print(data)  # {'name': 'John', 'age': 30}

# Use different float modes
from decimal import Decimal
data = jiter.from_json(b'{"value": 123.456}', float_mode="decimal")
print(isinstance(data["value"], Decimal))  # True

# Handle partial JSON
incomplete = b'{"name": "John", "address": {"city": "New Yor'
data = jiter.from_json(incomplete, partial_mode=True)
print(data)  # {'name': 'John'}

# Include trailing strings
data = jiter.from_json(incomplete, partial_mode="trailing-strings")
print(data)  # {'name': 'John', 'address': {'city': 'New Yor'}}

# Catch duplicate keys
try:
    jiter.from_json(b'{"foo": 1, "foo": 2}', catch_duplicate_keys=True)
except ValueError as e:
    print(e)  # Detected duplicate key "foo" at line 1 column 18

# String caching
jiter.cache_clear()
jiter.from_json(b'{"foo": "bar"}')
print(jiter.cache_usage() > 0)  # True
```

## API

```python
def from_json(
    json_data: bytes,
    /,
    *,
    allow_inf_nan: bool = True,
    cache_mode: Literal[True, False, "all", "keys", "none"] = "all",
    partial_mode: Literal[True, False, "off", "on", "trailing-strings"] = False,
    catch_duplicate_keys: bool = False,
    float_mode: Literal["float", "decimal", "lossless-float"] = "float",
) -> Any:
    """Parse input bytes into a JSON object."""

def cache_clear() -> None:
    """Reset the string cache."""

def cache_usage() -> int:
    """Get the size of the string cache in bytes."""

class LosslessFloat:
    """Represents a float from JSON, preserving the exact string representation."""
```

## Performance

While this implementation prioritizes API compatibility over raw performance, it still offers benefits:

- String caching can improve performance in scenarios with repeated strings
- No compilation required, works anywhere Python runs
- Useful as a fallback when the compiled jiter package isn't available

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run benchmarks
hatch run bench

# Run linting
hatch run lint

# Format code
hatch run fix
```

## License

MIT License 