#!/usr/bin/env python3
"""
Test script to verify both import styles work.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test importing as jiter
print("Testing import as jiter:")
import jiter

print(f"jiter.__version__: {jiter.__version__}")
print(f"jiter.from_json: {jiter.from_json}")
print()

# Test importing as jiter_pupy
print("Testing import as jiter_pupy:")
import jiter_pupy

print(f"jiter_pupy.__version__: {jiter_pupy.__version__}")
print(f"jiter_pupy.from_json: {jiter_pupy.from_json}")
print()

# Test that they're the same
print("Verifying they're the same:")
print(
    f"jiter.__version__ == jiter_pupy.__version__: {jiter.__version__ == jiter_pupy.__version__}"
)
print(
    f"jiter.from_json is jiter_pupy.from_json: {jiter.from_json is jiter_pupy.from_json}"
)
