"""Simple tests to improve CLI coverage without complex mocking."""

import pytest
from typer.testing import CliRunner

from ai_model_catalog.cli import app, safe_float, safe_int, build_ndjson_line

runner = CliRunner()


def test_safe_float_function():
    """Test safe_float utility function."""
    assert safe_float(1.5) == 1.5
    assert safe_float("2.3") == 2.3
    assert safe_float("invalid") == 0.0
    assert safe_float(None) == 0.0


def test_safe_int_function():
    """Test safe_int utility function."""
    assert safe_int(42) == 42
    assert safe_int("123") == 123
    assert safe_int("invalid") == 0
    assert safe_int(None) == 0


def test_build_ndjson_line_function():
    """Test build_ndjson_line utility function."""
    scores = {
        "net_score": 0.85,
        "ramp_up_time": 1.0,
        "bus_factor": 0.5,
        "performance_claims": 0.8,
        "license": 1.0,
        "size_score": {"raspberry_pi": 0.2},
        "dataset_and_code_score": 0.9,
        "dataset_quality": 0.7,
        "code_quality": 0.6,
    }
    
    result = build_ndjson_line("test-model", "MODEL", scores)
    
    assert result["name"] == "test-model"
    assert result["category"] == "MODEL"
    assert result["net_score"] == 0.85
    assert result["size_score"] == {"raspberry_pi": 0.2}


def test_build_ndjson_line_with_legacy_keys():
    """Test build_ndjson_line with legacy key names."""
    scores = {
        "net_score": 0.85,
        "size": {"raspberry_pi": 0.2},  # legacy size_score key
        "availability": 0.9,  # legacy dataset_and_code_score key
    }
    
    result = build_ndjson_line("test-model", "MODEL", scores)
    
    assert result["size_score"] == {"raspberry_pi": 0.2}
    assert result["dataset_and_code_score"] == 0.9


def test_build_ndjson_line_invalid_size_score():
    """Test build_ndjson_line with invalid size_score."""
    scores = {
        "size_score": "invalid",  # not a dict
    }
    
    result = build_ndjson_line("test-model", "MODEL", scores)
    
    assert result["size_score"] == {}


def test_build_ndjson_line_missing_values():
    """Test build_ndjson_line with missing values."""
    scores = {}
    
    result = build_ndjson_line("test-model", "MODEL", scores)
    
    # All values should default to 0.0 or 0
    assert result["net_score"] == 0.0
    assert result["ramp_up_time"] == 0.0
    assert result["bus_factor"] == 0.0
    assert result["performance_claims"] == 0.0
    assert result["license"] == 0.0
    assert result["size_score"] == {}
    assert result["dataset_and_code_score"] == 0.0
    assert result["dataset_quality"] == 0.0
    assert result["code_quality"] == 0.0
