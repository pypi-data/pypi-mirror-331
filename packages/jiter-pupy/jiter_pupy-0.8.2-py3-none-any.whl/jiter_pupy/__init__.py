#!/usr/bin/env python3
"""
jiter_pupy: Pure Python implementation of jiter

A drop-in replacement for the jiter package that is API-compatible with the original Rust-based implementation,
but uses only Python's standard library json module.
"""
# this_file: src/jiter_pupy/__init__.py

from .jiter import (LosslessFloat, __version__, cache_clear, cache_usage,
                    from_json)

__all__ = [
                    "LosslessFloat",
                    "__version__",
                    "cache_clear",
                    "cache_usage",
                    "from_json",
]
