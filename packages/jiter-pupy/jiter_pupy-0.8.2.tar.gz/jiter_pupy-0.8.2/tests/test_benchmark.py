"""Benchmark tests for jiter_pupy."""

# this_file: tests/test_benchmark.py

import json
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import jiter_pupy as jiter


# Sample JSON data for benchmarking
SAMPLE_JSON = {
    "simple": b'{"name": "John", "age": 30, "city": "New York"}',
    "array": b"[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
    "nested": b'{"person": {"name": "John", "address": {"city": "New York", "zip": "10001"}}}',
    "large_array": b"["
    + b", ".join([b'"item' + str(i).encode() + b'"' for i in range(100)])
    + b"]",
}


@pytest.mark.benchmark(group="simple")
def test_benchmark_jiter_simple(benchmark):
    """Benchmark jiter with simple JSON."""
    benchmark(jiter.from_json, SAMPLE_JSON["simple"])


@pytest.mark.benchmark(group="simple")
def test_benchmark_stdlib_simple(benchmark):
    """Benchmark stdlib json with simple JSON."""
    benchmark(json.loads, SAMPLE_JSON["simple"])


@pytest.mark.benchmark(group="array")
def test_benchmark_jiter_array(benchmark):
    """Benchmark jiter with array JSON."""
    benchmark(jiter.from_json, SAMPLE_JSON["array"])


@pytest.mark.benchmark(group="array")
def test_benchmark_stdlib_array(benchmark):
    """Benchmark stdlib json with array JSON."""
    benchmark(json.loads, SAMPLE_JSON["array"])


@pytest.mark.benchmark(group="nested")
def test_benchmark_jiter_nested(benchmark):
    """Benchmark jiter with nested JSON."""
    benchmark(jiter.from_json, SAMPLE_JSON["nested"])


@pytest.mark.benchmark(group="nested")
def test_benchmark_stdlib_nested(benchmark):
    """Benchmark stdlib json with nested JSON."""
    benchmark(json.loads, SAMPLE_JSON["nested"])


@pytest.mark.benchmark(group="large_array")
def test_benchmark_jiter_large_array(benchmark):
    """Benchmark jiter with large array JSON."""
    benchmark(jiter.from_json, SAMPLE_JSON["large_array"])


@pytest.mark.benchmark(group="large_array")
def test_benchmark_stdlib_large_array(benchmark):
    """Benchmark stdlib json with large array JSON."""
    benchmark(json.loads, SAMPLE_JSON["large_array"])


# Test different cache modes
@pytest.mark.benchmark(group="cache_modes")
def test_benchmark_jiter_all_cache(benchmark):
    """Benchmark jiter with all cache mode."""
    jiter.cache_clear()
    benchmark(jiter.from_json, SAMPLE_JSON["nested"], cache_mode="all")


@pytest.mark.benchmark(group="cache_modes")
def test_benchmark_jiter_keys_cache(benchmark):
    """Benchmark jiter with keys cache mode."""
    jiter.cache_clear()
    benchmark(jiter.from_json, SAMPLE_JSON["nested"], cache_mode="keys")


@pytest.mark.benchmark(group="cache_modes")
def test_benchmark_jiter_no_cache(benchmark):
    """Benchmark jiter with no cache mode."""
    jiter.cache_clear()
    benchmark(jiter.from_json, SAMPLE_JSON["nested"], cache_mode="none")


# Test different float modes
@pytest.mark.benchmark(group="float_modes")
def test_benchmark_jiter_float_mode(benchmark):
    """Benchmark jiter with float mode."""
    json_data = b'{"value": 123.456789}'
    benchmark(jiter.from_json, json_data, float_mode="float")


@pytest.mark.benchmark(group="float_modes")
def test_benchmark_jiter_decimal_mode(benchmark):
    """Benchmark jiter with decimal mode."""
    json_data = b'{"value": 123.456789}'
    benchmark(jiter.from_json, json_data, float_mode="decimal")


@pytest.mark.benchmark(group="float_modes")
def test_benchmark_jiter_lossless_float_mode(benchmark):
    """Benchmark jiter with lossless float mode."""
    json_data = b'{"value": 123.456789}'
    benchmark(jiter.from_json, json_data, float_mode="lossless-float")
