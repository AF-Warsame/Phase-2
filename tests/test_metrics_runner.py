"""Tests for the metrics runner module."""

import json
from io import StringIO

from ai_model_catalog.metrics.runner import print_ndjson, run_metrics
from ai_model_catalog.metrics.types import MetricResult

# from unittest.mock import MagicMock, patch

# import pytest


def create_mock_metric(name, score_value=None, error=None):
    """Create a mock metric with a specific class name."""

    class MockMetric:
        def __init__(self, score_val=None, err=None):
            self.score_value = score_val
            self.error = err

        def score(self, _ctx=None):  # Make ctx optional and unused
            if self.error:
                raise ValueError(self.error)  # Use more specific exception
            return self.score_value

    # Set the class name
    MockMetric.__name__ = f"{name}Metric"
    return MockMetric(score_value, error)


def test_run_metrics_success():
    """Test run_metrics with successful metrics."""
    mock_metrics = [
        create_mock_metric("Test1", score_value=0.8),
        create_mock_metric("Test2", score_value=0.6),
    ]

    ctx = {"test": "context"}

    results = run_metrics(mock_metrics, ctx, max_workers=2)

    assert len(results) == 2

    # Debug: print actual names
    print(f"Actual result names: {[r.name for r in results]}")

    # Create a dictionary for easier lookup
    results_dict = {r.name: r for r in results}

    # Test test1 results (should be "test1" after lowercase conversion)
    test1_result = results_dict["test1"]
    assert test1_result.score == 0.8
    assert test1_result.passed is True
    assert test1_result.error is None

    # Test test2 results (should be "test2" after lowercase conversion)
    test2_result = results_dict["test2"]
    assert test2_result.score == 0.6
    assert test2_result.passed is True


def test_run_metrics_with_error():
    """Test run_metrics with metrics that raise exceptions."""
    mock_metrics = [
        create_mock_metric("Test1", score_value=0.8),
        create_mock_metric("Test2", error="Test error"),
    ]

    ctx = {"test": "context"}

    results = run_metrics(mock_metrics, ctx, max_workers=2)

    assert len(results) == 2

    # Create a dictionary for easier lookup
    results_dict = {r.name: r for r in results}

    # Test test1 results (successful)
    test1_result = results_dict["test1"]
    assert test1_result.score == 0.8
    assert test1_result.passed is True
    assert test1_result.error is None

    # Test test2 results (error)
    test2_result = results_dict["test2"]
    assert test2_result.score == 0.0
    assert test2_result.passed is False
    assert test2_result.error == "Test error"


def test_run_metrics_score_clamping():
    """Test that scores are clamped to [0, 1] range."""
    mock_metrics = [
        create_mock_metric("Test1", score_value=1.5),  # Above 1.0
        create_mock_metric("Test2", score_value=-0.5),  # Below 0.0
    ]

    ctx = {"test": "context"}

    results = run_metrics(mock_metrics, ctx, max_workers=2)

    assert len(results) == 2

    # Create a dictionary for easier lookup
    results_dict = {r.name: r for r in results}

    # Test test1 results (clamped to 1.0)
    test1_result = results_dict["test1"]
    assert test1_result.score == 1.0

    # Test test2 results (clamped to 0.0)
    test2_result = results_dict["test2"]
    assert test2_result.score == 0.0


def test_run_metrics_max_workers():
    """Test run_metrics with different max_workers values."""
    mock_metrics = [create_mock_metric("Test1", score_value=0.8)]

    ctx = {"test": "context"}

    # Test with max_workers=1
    results = run_metrics(mock_metrics, ctx, max_workers=1)
    assert len(results) == 1

    # Test with max_workers=0 (should be clamped to 1)
    results = run_metrics(mock_metrics, ctx, max_workers=0)
    assert len(results) == 1


def test_print_ndjson():
    """Test print_ndjson function."""
    results = [
        MetricResult(
            name="test1",
            score=0.8,
            passed=True,
            details={"key": "value"},
            error=None,
            elapsed_s=0.1,
        ),
        MetricResult(
            name="test2",
            score=0.3,
            passed=False,
            details={},
            error="Test error",
            elapsed_s=0.2,
        ),
    ]

    stream = StringIO()
    print_ndjson(results, stream)

    output = stream.getvalue()
    lines = output.strip().split("\n")

    assert len(lines) == 2

    # Parse first line

    line1 = json.loads(lines[0])
    assert line1["name"] == "test1"
    assert line1["score"] == 0.8
    assert line1["passed"] is True
    assert line1["latency_ms"] == 100.0
    assert line1["error"] is None
    assert line1["key"] == "value"

    # Parse second line
    line2 = json.loads(lines[1])
    assert line2["name"] == "test2"
    assert line2["score"] == 0.3
    assert line2["passed"] is False
    assert line2["latency_ms"] == 200.0
    assert line2["error"] == "Test error"


def test_print_ndjson_empty_results():
    """Test print_ndjson with empty results."""
    results = []
    stream = StringIO()
    print_ndjson(results, stream)

    output = stream.getvalue()
    assert output == ""
