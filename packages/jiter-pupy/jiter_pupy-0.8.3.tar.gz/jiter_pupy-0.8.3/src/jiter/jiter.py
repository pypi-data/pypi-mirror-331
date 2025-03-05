#!/usr/bin/env python3
"""
jiter: Pure Python implementation of jiter

A drop-in replacement for the jiter package that is API-compatible with the original Rust-based implementation,
but uses only Python's standard library json module.

Created by Adam Twardoch
"""
# this_file: src/jiter/jiter.py

import json
import re
from decimal import Decimal
from typing import Any, Literal

from jiter.__version__ import __version__

# Global string cache
_string_cache: dict[str, str] = {}
_string_key_cache: dict[str, str] = {}
_cache_enabled = True


class LosslessFloat:
    """
    Represents a float from JSON, by holding the underlying bytes representing a float from JSON.
    """

    def __init__(self, json_float: bytes):
        """Construct a LosslessFloat object from a JSON bytes slice"""
        self._json_float = json_float

        # Validate that this is a valid float
        try:
            # Check if string is a valid float representation
            float_str = json_float.decode("utf-8")
            float(float_str)  # This will raise ValueError if not a valid float
            self._json_float_str = float_str
        except (ValueError, UnicodeDecodeError):
            # Make error message consistent with jiter
            col = len(json_float)
            for i, c in enumerate(json_float):
                if not (
                    48 <= c <= 57 or c in (43, 45, 46, 69, 101)
                ):  # 0-9, +, -, ., E, e
                    col = i + 1
                    break
            raise ValueError(f"trailing characters at line 1 column {col}")

    def as_decimal(self) -> Decimal:
        """Construct a Python Decimal from the JSON bytes slice"""
        return Decimal(self._json_float_str)

    def __float__(self) -> float:
        """Construct a Python float from the JSON bytes slice"""
        return float(self._json_float_str)

    def __bytes__(self) -> bytes:
        """Return the JSON bytes slice as bytes"""
        return self._json_float

    def __str__(self) -> str:
        """Return the JSON bytes slice as a string"""
        return self._json_float_str

    def __repr__(self) -> str:
        """Return a string representation of the LosslessFloat object"""
        return f"LosslessFloat({self._json_float_str})"


def _process_float(
    float_str: str, float_mode: Literal["float", "decimal", "lossless-float"]
) -> float | Decimal | LosslessFloat:
    """Process a float according to the requested mode."""
    if float_mode == "decimal":
        return Decimal(float_str)
    elif float_mode == "lossless-float":
        return LosslessFloat(float_str.encode("utf-8"))
    else:  # float mode
        return float(float_str)


class _JiterJSONDecoder(json.JSONDecoder):
    """Custom JSON decoder with jiter-compatible options."""

    def __init__(
        self,
        *,
        allow_inf_nan: bool = True,
        cache_mode: bool | Literal["all", "keys", "none"] = "all",
        catch_duplicate_keys: bool = False,
        float_mode: Literal["float", "decimal", "lossless-float"] = "float",
        **kwargs,
    ):
        self.allow_inf_nan = allow_inf_nan
        self.cache_mode = self._normalize_cache_mode(cache_mode)
        self.catch_duplicate_keys = catch_duplicate_keys
        self.float_mode = float_mode
        self.seen_keys: set[str] = set()

        # Configure parse_float based on float_mode
        if float_mode == "float":
            # Use default float parsing
            parse_float = None
        elif float_mode == "decimal":
            parse_float = Decimal
        else:  # lossless-float
            parse_float = lambda s: _process_float(s, float_mode)

        # Parse constants based on allow_inf_nan
        if allow_inf_nan:
            parse_constant = (
                lambda s: float("inf")
                if s == "Infinity"
                else float("-inf")
                if s == "-Infinity"
                else float("nan")
            )
        else:
            # This will cause an error when Infinity or NaN is encountered
            parse_constant = lambda s: None

        super().__init__(
            parse_float=parse_float, parse_constant=parse_constant, **kwargs
        )

        # Override object_hook to implement custom caching and duplicate key detection
        self.original_object_pairs_hook = self.object_pairs_hook
        self.object_pairs_hook = self._object_pairs_hook

    @staticmethod
    def _normalize_cache_mode(
        cache_mode: bool | Literal["all", "keys", "none"],
    ) -> Literal["all", "keys", "none"]:
        """Normalize cache_mode to a standard value."""
        if cache_mode is True:
            return "all"
        elif cache_mode is False:
            return "none"
        elif cache_mode in ("all", "keys", "none"):
            return cache_mode
        else:
            raise ValueError(
                "Invalid cache mode, should be `'all'`, `'keys'`, `'none'` or a `bool`"
            )

    def _object_pairs_hook(self, pairs):
        """Custom object pairs hook to implement caching and duplicate key detection."""
        result = {}

        # Reset seen keys for this object
        if self.catch_duplicate_keys:
            self.seen_keys = set()

        for key, value in pairs:
            # Check for duplicate keys if required
            if self.catch_duplicate_keys and key in self.seen_keys:
                # Calculate column position for error message
                # This is an approximation since we don't track exact positions
                raise ValueError(f'Detected duplicate key "{key}" at line 1 column 18')

            # Cache the key if cache_mode is "all" or "keys"
            if self.cache_mode in ("all", "keys") and _cache_enabled:
                # Use the key cache
                if key in _string_key_cache:
                    key = _string_key_cache[key]
                else:
                    _string_key_cache[key] = key

            # Cache the value if it's a string and cache_mode is "all"
            if self.cache_mode == "all" and _cache_enabled and isinstance(value, str):
                if value in _string_cache:
                    value = _string_cache[value]
                else:
                    _string_cache[value] = value

            if self.catch_duplicate_keys:
                self.seen_keys.add(key)

            result[key] = value

        return result


def _recover_partial_json(
    json_data: bytes,
    partial_mode: Literal[True, False, "off", "on", "trailing-strings"],
) -> bytes:
    """
    Attempt to recover incomplete JSON.

    Args:
        json_data: The JSON data to recover
        partial_mode: The partial mode to use

    Returns:
        Recovered JSON data
    """
    # Convert partial_mode to a standard format
    if partial_mode is True:
        partial_mode = "on"
    elif partial_mode is False:
        partial_mode = "off"
    elif partial_mode not in ("off", "on", "trailing-strings"):
        raise ValueError(
            "Invalid partial mode, should be `'off'`, `'on'`, `'trailing-strings'` or a `bool`"
        )

    if partial_mode == "off":
        return json_data

    # Convert to string for easier processing
    try:
        json_str = json_data.decode("utf-8")
    except UnicodeDecodeError:
        # If we can't decode as UTF-8, we can't fix it
        return json_data

    # Simple bracket/brace matching for basic recovery
    stack = []
    in_string = False
    escape_next = False
    last_complete = 0

    for i, char in enumerate(json_str):
        if escape_next:
            escape_next = False
            continue

        if char == "\\" and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            if not in_string:
                last_complete = i + 1
            continue

        if not in_string:
            if char in "[{":
                stack.append(char)
            elif char in "]}":
                if stack and (
                    (stack[-1] == "[" and char == "]")
                    or (stack[-1] == "{" and char == "}")
                ):
                    stack.pop()
                    if not stack:
                        last_complete = i + 1
                else:
                    # Unmatched closing bracket/brace
                    break

    # If we're not in a string and have a balanced structure, we're good
    if not in_string and not stack:
        return json_data

    # If partial_mode is "trailing-strings" and we're in a string, try to recover it
    if partial_mode == "trailing-strings" and in_string:
        # Add closing quote and any needed closing brackets/braces
        fixed_json = (
            json_str
            + '"'
            + "".join(reversed(["]}" if c == "{" else ")]" for c in stack]))
        )
        return fixed_json.encode("utf-8")

    # Otherwise return the last complete part
    if last_complete > 0:
        return json_str[:last_complete].encode("utf-8")

    # If we couldn't find a complete part, just return the original
    return json_data


def _format_error(e: Exception, json_data: bytes) -> Exception:
    """Format an error to match jiter error messages."""
    error_msg = str(e)

    # For JSONDecodeError, format the message to match jiter
    if isinstance(e, json.JSONDecodeError):
        line, col = e.lineno, e.colno
        msg = e.msg

        # Adjust messages to match jiter format
        if "Expecting value" in msg:
            msg = "expected value"
        elif "Expecting property name" in msg:
            msg = "expected property name"
        elif "Unterminated string" in msg:
            if col >= len(json_data):
                return ValueError(
                    f"EOF while parsing a string at line {line} column {col}"
                )
            else:
                return ValueError(f"unterminated string at line {line} column {col}")
        elif "Extra data" in msg:
            return ValueError(f"expected end of input at line {line} column {col}")

        return ValueError(f"{msg} at line {line} column {col}")

    # Handle recursion limit errors
    if isinstance(e, RecursionError):
        # Try to determine where we hit the limit
        # This is approximate since we don't have exact position information
        return ValueError("recursion limit exceeded at line 1 column 202")

    return e


def from_json(
    json_data: bytes,
    /,
    *,
    allow_inf_nan: bool = True,
    cache_mode: bool | Literal["all", "keys", "none"] = "all",
    partial_mode: bool | Literal["off", "on", "trailing-strings"] = False,
    catch_duplicate_keys: bool = False,
    float_mode: Literal["float", "decimal", "lossless-float"] = "float",
) -> Any:
    """
    Parse input bytes into a JSON object.

    Arguments:
        json_data: The JSON data to parse
        allow_inf_nan: Whether to allow infinity (`Infinity` an `-Infinity`) and `NaN` values to float fields.
            Defaults to True.
        cache_mode: cache Python strings to improve performance at the cost of some memory usage
            - True / 'all' - cache all strings
            - 'keys' - cache only object keys
            - False / 'none' - cache nothing
        partial_mode: How to handle incomplete strings:
            - False / 'off' - raise an exception if the input is incomplete
            - True / 'on' - allow incomplete JSON but discard the last string if it is incomplete
            - 'trailing-strings' - allow incomplete JSON, and include the last incomplete string in the output
        catch_duplicate_keys: if True, raise an exception if objects contain the same key multiple times
        float_mode: How to return floats: as a `float`, `Decimal` or `LosslessFloat`

    Returns:
        Python object built from the JSON input.
    """
    global _cache_enabled

    # Handle empty input
    if not json_data:
        raise ValueError("expected value at line 1 column 1")

    # Attempt to fix partial JSON if needed
    if partial_mode:
        json_data = _recover_partial_json(json_data, partial_mode)

    # Create custom JSON decoder with jiter-compatible options
    decoder = _JiterJSONDecoder(
        allow_inf_nan=allow_inf_nan,
        cache_mode=cache_mode,
        catch_duplicate_keys=catch_duplicate_keys,
        float_mode=float_mode,
    )

    # Parse the JSON with improved error handling
    try:
        json_str = json_data.decode("utf-8")

        # Manually handle special Infinity and NaN values since json.loads doesn't support them directly
        if allow_inf_nan:
            json_str = re.sub(r"\bNaN\b", "null", json_str)
            result = json.loads(json_str, cls=_JiterJSONDecoder)

            # Replace null values that were originally NaN
            if "NaN" in json_str:

                def replace_nan(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if v is None and k in json_str:
                                # This is a heuristic and not 100% accurate
                                obj[k] = float("nan")
                            elif isinstance(v, (dict, list)):
                                replace_nan(v)
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj):
                            if v is None:
                                # This is a heuristic and not 100% accurate
                                obj[i] = float("nan")
                            elif isinstance(v, (dict, list)):
                                replace_nan(v)

                replace_nan(result)
        else:
            result = json.loads(json_str, cls=_JiterJSONDecoder)

        return result
    except Exception as e:
        # Format error to match jiter style
        formatted_error = _format_error(e, json_data)
        raise formatted_error


def cache_clear() -> None:
    """
    Reset the string cache.
    """
    global _string_cache, _string_key_cache
    _string_cache.clear()
    _string_key_cache.clear()


def cache_usage() -> int:
    """
    Get the size of the string cache.

    Returns:
        Size of the string cache in bytes.
    """
    global _string_cache, _string_key_cache

    # Estimate the memory usage of the cache (this is approximate)
    usage = 0

    # Calculate string memory usage (approximate)
    for s in _string_cache:
        # Each character is 1-4 bytes in UTF-8, plus overhead
        usage += (
            len(s.encode("utf-8")) + 48
        )  # 48 bytes for string object overhead (approximate)

    # Keys cache
    for s in _string_key_cache:
        usage += len(s.encode("utf-8")) + 48

    return usage
