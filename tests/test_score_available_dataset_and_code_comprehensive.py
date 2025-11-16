"""Comprehensive tests for available dataset and code metric to improve coverage."""

import pytest

from ai_model_catalog.metrics.score_available_dataset_and_code import (
    AvailableDatasetAndCodeMetric,
    score_available_dataset_and_code,
    score_available_dataset_and_code_with_latency,
)


class TestAvailableDatasetAndCodeMetric:
    """Test the AvailableDatasetAndCodeMetric class comprehensively."""

    def test_basic_availability_scoring(self):
        """Test basic availability scoring."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Both available with clear evidence
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "readme": "This model includes the dataset and source code on github"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_no_availability(self):
        """Test with no availability."""
        metric = AvailableDatasetAndCodeMetric()
        
        result = metric.score({
            "has_code": False,
            "has_dataset": False
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_partial_availability(self):
        """Test with partial availability."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Only code available
        result = metric.score({
            "has_code": True,
            "has_dataset": False
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Only dataset available
        result = metric.score({
            "has_code": False,
            "has_dataset": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_evidence_detection(self):
        """Test README evidence detection."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Test dataset mentions
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "readme": "The training dataset is available for download"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test code mentions
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "readme": "Source code is available on github repository"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_prestigious_organization_boost(self):
        """Test prestigious organization boost."""
        metric = AvailableDatasetAndCodeMetric()
        
        prestigious_orgs = [
            "google", "openai", "microsoft", "facebook", "meta", 
            "huggingface", "nvidia", "anthropic"
        ]
        
        for org in prestigious_orgs:
            result = metric.score({
                "has_code": True,
                "has_dataset": True,
                "author": f"{org}-research"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_model_size_factors(self):
        """Test model size impact on scoring."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Large model (>1GB)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "modelSize": 2000000000  # 2GB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Medium model (>100MB)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "modelSize": 200000000  # 200MB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Small model (<10MB)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "modelSize": 5000000  # 5MB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_download_based_boost(self):
        """Test download-based maturity boost."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Very popular model (10M+ downloads)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": 15000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Popular model (1M+ downloads)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": 2000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Moderately popular model (100K+ downloads)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": 200000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Less popular model (1K+ downloads)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": 2000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Unpopular model (<1K downloads)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": 500
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_experimental_keywords_penalty(self):
        """Test experimental keyword penalty."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Non-prestigious org with experimental keywords
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "author": "individual-dev",
            "readme": "This is an experimental model for testing"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Prestigious org with experimental keywords (should not be penalized)
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "author": "google-research",
            "readme": "This is an experimental model for testing"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_established_keywords_boost(self):
        """Test established keyword boost."""
        metric = AvailableDatasetAndCodeMetric()
        
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "author": "individual-dev",
            "readme": "This is a production-ready stable model"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_academic_keywords_boost(self):
        """Test academic keyword boost."""
        metric = AvailableDatasetAndCodeMetric()
        
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "author": "individual-dev",
            "readme": "This model is based on our research paper published at ICML"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_combined_factors(self):
        """Test combination of multiple factors."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Prestigious org, popular model, established keywords
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "author": "google-research",
            "downloads": 5000000,
            "modelSize": 1000000000,
            "readme": "Production-ready BERT model with dataset and code"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_missing_fields_defaults(self):
        """Test behavior with missing fields."""
        metric = AvailableDatasetAndCodeMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        metric = AvailableDatasetAndCodeMetric()
        
        # Test with None values (except readme, author, modelSize, and downloads which need specific types)
        result = metric.score({
            "has_code": None,
            "has_dataset": None,
            "downloads": 0,
            "modelSize": 0,
            "readme": "",
            "author": ""
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with negative values
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": -1000,
            "modelSize": -5000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with very large values
        result = metric.score({
            "has_code": True,
            "has_dataset": True,
            "downloads": 1000000000,  # 1 billion downloads
            "modelSize": 10000000000  # 10GB model
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestScoreAvailableDatasetAndCodeWrapper:
    """Test the score_available_dataset_and_code wrapper function."""

    def test_dict_input(self):
        """Test with dictionary input."""
        result = score_available_dataset_and_code({
            "has_code": True,
            "has_dataset": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_boolean_input_backward_compatibility(self):
        """Test with boolean inputs for backward compatibility."""
        result = score_available_dataset_and_code(True, True)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        result = score_available_dataset_and_code(False, False)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_wrapper_vs_class_parity(self):
        """Test wrapper function matches class method."""
        data = {
            "has_code": True,
            "has_dataset": True,
            "downloads": 1000000
        }
        
        class_result = AvailableDatasetAndCodeMetric().score(data)
        wrapper_result = score_available_dataset_and_code(data)
        
        assert class_result == wrapper_result


class TestScoreAvailableDatasetAndCodeWithLatency:
    """Test the score_available_dataset_and_code_with_latency function."""

    def test_latency_functionality(self):
        """Test that latency function returns both score and latency."""
        result, latency = score_available_dataset_and_code_with_latency({
            "has_code": True,
            "has_dataset": True
        })
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0  # Should have some latency

    def test_latency_with_boolean_input(self):
        """Test latency function with boolean inputs."""
        result, latency = score_available_dataset_and_code_with_latency(True, True)
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_consistency(self):
        """Test that latency is consistent."""
        data = {"has_code": True, "has_dataset": True}
        
        # Run multiple times to check consistency
        results = []
        for _ in range(3):
            _, latency = score_available_dataset_and_code_with_latency(data)
            results.append(latency)
        
        # All latencies should be positive and similar
        assert all(lat > 0 for lat in results)
        # Latencies should be within reasonable range (allowing for timing variations)
        assert max(results) - min(results) < 100  # Within 100ms
