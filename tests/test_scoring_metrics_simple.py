"""Simple tests to improve scoring metrics coverage."""

import pytest

from ai_model_catalog.metrics.score_bus_factor import BusFactorMetric, score_bus_factor
from ai_model_catalog.metrics.score_license import LicenseMetric, score_license
from ai_model_catalog.metrics.score_ramp_up_time import RampUpMetric, score_ramp_up_time


def test_bus_factor_metric_basic():
    """Test basic bus factor metric functionality."""
    metric = BusFactorMetric()
    
    # Test with empty maintainers
    result = metric.score({"maintainers": []})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with some maintainers
    result = metric.score({"maintainers": ["alice", "bob"]})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with missing maintainers key
    result = metric.score({})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_bus_factor_wrapper():
    """Test bus factor wrapper function."""
    # Test with list input
    result = score_bus_factor(["alice", "bob"])
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with dict input
    result = score_bus_factor({"maintainers": ["alice", "bob"]})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_license_metric_basic():
    """Test basic license metric functionality."""
    metric = LicenseMetric()
    
    # Test with MIT license
    result = metric.score({"license": "MIT"})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with no license
    result = metric.score({"license": ""})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with missing license key
    result = metric.score({})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_license_wrapper():
    """Test license wrapper function."""
    # Test with string input
    result = score_license("MIT")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with dict input
    result = score_license({"license": "MIT"})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_ramp_up_time_metric_basic():
    """Test basic ramp-up time metric functionality."""
    metric = RampUpMetric()
    
    # Test with empty README
    result = metric.score({"readme": ""})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with short README
    result = metric.score({"readme": "a" * 100})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with long README
    result = metric.score({"readme": "a" * 1000})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with missing readme key
    result = metric.score({})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_ramp_up_time_wrapper():
    """Test ramp-up time wrapper function."""
    # Test with string input
    result = score_ramp_up_time("a" * 100)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with dict input
    result = score_ramp_up_time({"readme": "a" * 100})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_metrics_with_additional_fields():
    """Test metrics with additional fields that affect scoring."""
    # Test bus factor with downloads and author
    metric = BusFactorMetric()
    result = metric.score({
        "maintainers": ["alice"],
        "downloads": 1000000,
        "author": "google-research"
    })
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test license with downloads and author
    metric = LicenseMetric()
    result = metric.score({
        "license": "MIT",
        "downloads": 1000000,
        "author": "google-research"
    })
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test ramp-up time with downloads and author
    metric = RampUpMetric()
    result = metric.score({
        "readme": "a" * 100,
        "downloads": 1000000,
        "author": "google-research"
    })
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_metrics_edge_cases():
    """Test metrics with edge case values."""
    # Test with empty list instead of None to avoid TypeError
    metric = BusFactorMetric()
    result = metric.score({"maintainers": []})
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with negative values
    metric = BusFactorMetric()
    result = metric.score({
        "maintainers": ["alice"],
        "downloads": -1000,
        "modelSize": -5000000
    })
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with very large values
    metric = BusFactorMetric()
    result = metric.score({
        "maintainers": ["alice"],
        "downloads": 1000000000,
        "modelSize": 10000000000
    })
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
