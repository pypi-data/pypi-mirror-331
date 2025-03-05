"""Basic test for jiter_pupy."""

# this_file: tests/test_basic.py

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import jiter_pupy as jiter


def test_basic_parsing():
    """Test basic JSON parsing functionality."""
    parsed = jiter.from_json(b'{"int": 1, "float": 1.2, "str": "hello"}')
    assert parsed == {"int": 1, "float": 1.2, "str": "hello"}


def test_version():
    """Test version is available."""
    assert jiter.__version__ == "0.1.0"
