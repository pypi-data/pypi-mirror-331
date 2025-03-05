"""Test suite for jiter_pupy's jiter implementation."""
# this_file: tests/test_jiter.py

import math
from decimal import Decimal

import pytest

import jiter_pupy as jiter


def test_basic_parsing():
    """Test basic JSON parsing functionality."""
    parsed = jiter.from_json(b'{"int": 1, "float": 1.2, "str": "hello"}')
    assert parsed == {"int": 1, "float": 1.2, "str": "hello"}


def test_parse_special_values():
    """Test parsing special values like infinity and NaN."""
    parsed = jiter.from_json(
        b'["string", true, false, null, NaN, Infinity, -Infinity]',
        allow_inf_nan=True,
    )

    assert parsed[0] == "string"
    assert parsed[1] is True
    assert parsed[2] is False
    assert parsed[3] is None
    assert math.isnan(parsed[4])
    assert parsed[5] == float("inf")
    assert parsed[6] == float("-inf")


def test_disallow_special_values():
    """Test disallowing special values."""
    with pytest.raises(ValueError):
        jiter.from_json(b"[NaN]", allow_inf_nan=False)


def test_string_caching():
    """Test string caching functionality."""
    jiter.cache_clear()
    assert jiter.cache_usage() == 0

    # Parse with caching enabled
    jiter.from_json(b'{"foo": "bar", "spam": "eggs"}', cache_mode="all")
    assert jiter.cache_usage() > 0

    # Clear cache
    jiter.cache_clear()
    assert jiter.cache_usage() == 0


def test_partial_mode():
    """Test partial parsing modes."""
    incomplete_json = b'["foo", "bar", "baz'

    # Default behavior - should raise an error
    with pytest.raises(ValueError):
        jiter.from_json(incomplete_json, partial_mode=False)

    # Partial mode enabled - should return complete part
    result = jiter.from_json(incomplete_json, partial_mode=True)
    assert result == ["foo", "bar"]

    # Trailing strings mode - should include incomplete part
    result = jiter.from_json(incomplete_json, partial_mode="trailing-strings")
    assert result == ["foo", "bar", "baz"]


def test_duplicate_keys():
    """Test duplicate key detection."""
    json_with_dupes = b'{"foo": 1, "foo": 2}'

    # Default behavior - last value wins
    parsed = jiter.from_json(json_with_dupes)
    assert parsed == {"foo": 2}

    # With duplicate detection enabled
    with pytest.raises(ValueError):
        jiter.from_json(json_with_dupes, catch_duplicate_keys=True)


def test_decimal_mode():
    """Test decimal float mode."""
    json_data = b'{"value": 123.456}'

    # Default float mode
    parsed = jiter.from_json(json_data)
    assert isinstance(parsed["value"], float)

    # Decimal mode
    parsed = jiter.from_json(json_data, float_mode="decimal")
    assert isinstance(parsed["value"], Decimal)
    assert parsed["value"] == Decimal("123.456")


def test_lossless_float():
    """Test lossless float mode and LosslessFloat class."""
    json_data = b'{"value": 123.456789123456789}'

    # LosslessFloat mode
    parsed = jiter.from_json(json_data, float_mode="lossless-float")
    assert isinstance(parsed["value"], jiter.LosslessFloat)

    # LosslessFloat methods
    lf = parsed["value"]
    assert float(lf) == 123.456789123456789
    assert lf.as_decimal() == Decimal("123.456789123456789")
    assert str(lf) == "123.456789123456789"
    assert bytes(lf) == b"123.456789123456789"

    # Direct construction
    lf = jiter.LosslessFloat(b"123.456")
    assert float(lf) == 123.456


def test_error_handling():
    """Test error handling and formatting."""
    # Empty input
    with pytest.raises(ValueError, match="expected value at line 1 column 1"):
        jiter.from_json(b"")

    # Invalid JSON
    with pytest.raises(ValueError):
        jiter.from_json(b'{"incomplete":')

    # Invalid number
    with pytest.raises(ValueError):
        jiter.from_json(b'{"value": 123x}')


def test_unicode():
    """Test Unicode handling."""
    # Unicode characters in keys and values
    json_data = b'{"\\u00A3": "\\u20AC", "emoji": "\\ud83d\\ude00"}'
    parsed = jiter.from_json(json_data)
    assert parsed == {"£": "€", "emoji": "😀"}

    # Direct Unicode characters
    json_data = '{"£": "€", "emoji": "😀"}'.encode()
    parsed = jiter.from_json(json_data)
    assert parsed == {"£": "€", "emoji": "😀"}
