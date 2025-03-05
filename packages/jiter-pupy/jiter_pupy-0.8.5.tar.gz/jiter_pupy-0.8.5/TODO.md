# jiter_pupy (Pure Python jiter) Implementation Plan

## 1. Overview

Create a pure-Python implementation of the `jiter` package that is API-compatible with the original Rust-based `jiter`, but relies only on Python's standard library `json` module. This will serve as a drop-in replacement for environments where the compiled version cannot be used.

## 2. Key Features to Implement

1. **Main Functions**:
   - `from_json()` - Parse JSON bytes with all the original parameters
   - `cache_clear()` - Clear the string cache
   - `cache_usage()` - Get the size of the string cache in bytes
   - `LosslessFloat` class - Represent float values without precision loss

2. **API Compatibility**:
   - Ensure the function signatures match exactly
   - Support all the same parameter options
   - Replicate error messages where possible
   - Match return types and behaviors

## 3. Implementation Steps

### 3.1. Project Structure

```
jiter_pupy/
├── __init__.py        # Exports the API
├── __version__.py     # Version tracking
├── parser.py          # Core JSON parsing implementation
├── caching.py         # String caching functionality
├── partial.py         # Partial JSON parsing
├── float_handling.py  # Float handling (normal, decimal, lossless)
└── exceptions.py      # Custom error handling to match jiter
```

### 3.2. LosslessFloat Class

Implement a `LosslessFloat` class that:
- Stores the original JSON bytes representation
- Implements `__float__()`, `__str__()`, `__repr__()`, `as_decimal()`, and `__bytes__()`
- Preserves the exact string representation from JSON

### 3.3. String Caching System

Implement a caching system that:
- Supports the same modes: `"all"`, `"keys"`, `"none"` (also True/False)
- Preserves strings to avoid repeated creation
- Tracks memory usage for `cache_usage()`
- Can be cleared via `cache_clear()`

### 3.4. Partial JSON Parsing

Create a partial JSON parsing system that:
- Handles incomplete JSON strings
- Supports modes: `"off"`, `"on"`, `"trailing-strings"` (also True/False)
- Correctly handles incomplete arrays, objects, and strings

### 3.5. Custom JSON Decoder

Create a customized `json.JSONDecoder` that:
- Catches duplicate keys when requested
- Supports infinite/NaN values when allowed
- Handles different float modes (float, decimal, lossless-float)

### 3.6. Error Handling

Implement error handling that:
- Provides line and column information in error messages
- Formats error messages to match jiter's style
- Handles recursion limits similarly

### 3.7. Integration with stdlib json

- Use `json.loads()` as the core parser
- Add pre-processing to handle features not supported by the standard library
- Add post-processing to ensure return values match expectations

### 3.8. Performance Optimizations

- Minimize unnecessary string copies
- Use efficient data structures for caching
- Optimize partial parsing for common cases

### 3.9. Detailed Tasks

1. **Core `from_json` function**:
   - Create parameter validation and normalization
   - Implement preprocessing for special values (Infinity, NaN)
   - Handle different cache modes
   - Support different float modes
   - Implement duplicate key detection

2. **Caching Implementation**:
   - Create a global cache for strings
   - Implement cache size tracking
   - Support different caching modes
   - Create cache clearing functionality

3. **Float Handling**:
   - Implement standard float parsing
   - Add Decimal support
   - Create LosslessFloat class with all required methods

4. **Partial JSON Processing**:
   - Implement recovery for incomplete JSON
   - Create special handling for trailing strings
   - Ensure proper error messages when partial mode is off

5. **Error Messages**:
   - Format errors to include line and column information
   - Match jiter's error message formats
   - Provide helpful context in error messages

### 3.10. Testing Plan

1. Port existing tests from the original jiter package
2. Create additional tests for edge cases
3. Ensure all features have comprehensive test coverage:
   - Caching modes
   - Partial parsing modes
   - Float handling modes
   - Error cases
   - Unicode handling
   - Large JSON handling

### 3.11. Documentation

1. Create docstrings that match the original implementation
2. Add implementation notes for differences between pure Python and Rust versions
3. Document any performance considerations

## 4. Implementation Challenges

1. **Performance Gap**: The pure Python implementation will be slower than the Rust version
2. **Error Reporting**: Matching exact line/column numbers in error messages
3. **Partial Parsing**: Implementing this without a custom parser is challenging
4. **LosslessFloat**: Ensuring exact preservation of float representation

## 5. Timeline

1. **Phase 1**: Basic implementation of from_json with standard features (1-2 days)
2. **Phase 2**: Implement LosslessFloat and advanced float handling (1 day)
3. **Phase 3**: Add caching system (1 day)
4. **Phase 4**: Implement partial parsing (1-2 days)
5. **Phase 5**: Error handling and formatting (1 day)
6. **Phase 6**: Testing and compatibility verification (1-2 days)
7. **Phase 7**: Performance optimization (1-2 days)
8. **Phase 8**: Documentation and final adjustments (1 day)

## 6. Notes on Implementation Strategy

- Focus on API compatibility first, then optimize performance
- Use standard library tools as much as possible
- Consider future maintainability when choosing implementation approaches
- Document clearly where behavior might subtly differ from the Rust implementation
