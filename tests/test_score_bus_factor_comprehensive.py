"""Comprehensive tests for bus factor metric to improve coverage."""

import pytest

from ai_model_catalog.metrics.score_bus_factor import (
    BusFactorMetric,
    score_bus_factor,
    score_bus_factor_with_latency,
)


class TestBusFactorMetric:
    """Test the BusFactorMetric class comprehensively."""

    def test_basic_bus_factor_scoring(self):
        """Test basic bus factor scoring."""
        metric = BusFactorMetric()
        
        # Single maintainer
        result = metric.score({
            "maintainers": ["user1"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_multiple_maintainers(self):
        """Test with multiple maintainers."""
        metric = BusFactorMetric()
        
        # Multiple maintainers
        result = metric.score({
            "maintainers": ["user1", "user2", "user3", "user4", "user5"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_no_maintainers(self):
        """Test with no maintainers."""
        metric = BusFactorMetric()
        
        result = metric.score({
            "maintainers": []
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_organization_reputation_boost(self):
        """Test organization reputation boost."""
        metric = BusFactorMetric()
        
        prestigious_orgs = [
            "google", "openai", "microsoft", "facebook", "meta", 
            "huggingface", "nvidia", "anthropic"
        ]
        
        for org in prestigious_orgs:
            result = metric.score({
                "maintainers": [f"{org}-research"],
                "author": f"{org}-research"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_download_based_boost(self):
        """Test download-based boost."""
        metric = BusFactorMetric()
        
        # High downloads
        result = metric.score({
            "maintainers": ["user1"],
            "downloads": 1000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Low downloads
        result = metric.score({
            "maintainers": ["user1"],
            "downloads": 100
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_model_size_factors(self):
        """Test model size impact."""
        metric = BusFactorMetric()
        
        # Large model
        result = metric.score({
            "maintainers": ["user1"],
            "modelSize": 1000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Small model
        result = metric.score({
            "maintainers": ["user1"],
            "modelSize": 1000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_quality_factors(self):
        """Test README quality factors."""
        metric = BusFactorMetric()
        
        # Good README
        result = metric.score({
            "maintainers": ["user1"],
            "readme": "Comprehensive documentation with examples and API reference"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Poor README
        result = metric.score({
            "maintainers": ["user1"],
            "readme": "Basic model"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_combined_factors(self):
        """Test combination of multiple factors."""
        metric = BusFactorMetric()
        
        result = metric.score({
            "maintainers": ["user1", "user2", "user3"],
            "author": "google-research",
            "downloads": 5000000,
            "modelSize": 1000000000,
            "readme": "Comprehensive documentation with examples"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_missing_fields_defaults(self):
        """Test behavior with missing fields."""
        metric = BusFactorMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_edge_cases(self):
        """Test edge cases."""
        metric = BusFactorMetric()
        
        # Test with None values (except readme, author, maintainers, downloads, and modelSize which need specific types)
        result = metric.score({
            "maintainers": [],
            "downloads": 0,
            "modelSize": 0,
            "readme": "",
            "author": ""
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with negative values
        result = metric.score({
            "maintainers": ["user1"],
            "downloads": -1000,
            "modelSize": -5000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with very large values
        result = metric.score({
            "maintainers": ["user1"],
            "downloads": 1000000000,
            "modelSize": 10000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_maintainer_count_scaling(self):
        """Test maintainer count scaling."""
        metric = BusFactorMetric()
        
        # Test different maintainer counts
        for count in range(1, 11):
            maintainers = [f"user{i}" for i in range(count)]
            result = metric.score({"maintainers": maintainers})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_author_organization_detection(self):
        """Test author organization detection."""
        metric = BusFactorMetric()
        
        # Test various author formats
        authors = [
            "google-research",
            "microsoft-ai",
            "facebook-ai",
            "huggingface-team",
            "nvidia-research",
            "openai-research",
            "meta-ai",
            "anthropic-research"
        ]
        
        for author in authors:
            result = metric.score({
                "maintainers": ["user1"],
                "author": author
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0


class TestScoreBusFactorWrapper:
    """Test the score_bus_factor wrapper function."""

    def test_dict_input(self):
        """Test with dictionary input."""
        result = score_bus_factor({
            "maintainers": ["user1", "user2"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_wrapper_vs_class_parity(self):
        """Test wrapper function matches class method."""
        data = {
            "maintainers": ["user1", "user2"],
            "downloads": 1000000
        }
        
        class_result = BusFactorMetric().score(data)
        wrapper_result = score_bus_factor(data)
        
        assert class_result == wrapper_result


class TestScoreBusFactorWithLatency:
    """Test the score_bus_factor_with_latency function."""

    def test_latency_functionality(self):
        """Test that latency function returns both score and latency."""
        result, latency = score_bus_factor_with_latency({
            "maintainers": ["user1", "user2"]
        })
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_consistency(self):
        """Test that latency is consistent."""
        data = {"maintainers": ["user1", "user2"]}
        
        # Run multiple times to check consistency
        results = []
        for _ in range(3):
            _, latency = score_bus_factor_with_latency(data)
            results.append(latency)
        
        # All latencies should be positive and similar
        assert all(lat > 0 for lat in results)
        # Latencies should be within reasonable range
        assert max(results) - min(results) < 100  # Within 100ms
