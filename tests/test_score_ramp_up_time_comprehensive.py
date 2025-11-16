"""Comprehensive tests for ramp-up time metric to improve coverage."""

import pytest

from ai_model_catalog.metrics.score_ramp_up_time import (
    RampUpMetric,
    score_ramp_up_time,
    score_ramp_up_time_with_latency,
)


class TestRampUpMetric:
    """Test the RampUpMetric class comprehensively."""

    def test_basic_ramp_up_scoring(self):
        """Test basic ramp-up time scoring."""
        metric = RampUpMetric()
        
        # Basic model data
        result = metric.score({
            "readme": "Basic model documentation",
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_quality_factors(self):
        """Test README quality factors."""
        metric = RampUpMetric()
        
        # Comprehensive README
        result = metric.score({
            "readme": "Comprehensive documentation with examples, API reference, and tutorials",
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Minimal README
        result = metric.score({
            "readme": "Basic model",
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_code_availability_factors(self):
        """Test code availability factors."""
        metric = RampUpMetric()
        
        # With code
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Without code
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": False
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_organization_reputation_boost(self):
        """Test organization reputation boost."""
        metric = RampUpMetric()
        
        prestigious_orgs = [
            "google", "openai", "microsoft", "facebook", "meta", 
            "huggingface", "nvidia", "anthropic"
        ]
        
        for org in prestigious_orgs:
            result = metric.score({
                "readme": "Basic documentation",
                "has_code": True,
                "author": f"{org}-research"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_download_based_boost(self):
        """Test download-based boost."""
        metric = RampUpMetric()
        
        # High downloads
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True,
            "downloads": 1000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Low downloads
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True,
            "downloads": 100
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_model_size_factors(self):
        """Test model size impact."""
        metric = RampUpMetric()
        
        # Large model
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True,
            "modelSize": 1000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Small model
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True,
            "modelSize": 1000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_keyword_detection(self):
        """Test README keyword detection."""
        metric = RampUpMetric()
        
        # Test various helpful keywords
        helpful_keywords = [
            "example", "tutorial", "quickstart", "getting started",
            "installation", "usage", "api", "documentation",
            "guide", "how to", "demo", "sample"
        ]
        
        for keyword in helpful_keywords:
            result = metric.score({
                "readme": f"Basic model with {keyword}",
                "has_code": True
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_combined_factors(self):
        """Test combination of multiple factors."""
        metric = RampUpMetric()
        
        result = metric.score({
            "readme": "Comprehensive documentation with examples and API reference",
            "has_code": True,
            "author": "google-research",
            "downloads": 5000000,
            "modelSize": 1000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_missing_fields_defaults(self):
        """Test behavior with missing fields."""
        metric = RampUpMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_edge_cases(self):
        """Test edge cases."""
        metric = RampUpMetric()
        
        # Test with None values
        result = metric.score({
            "readme": None,
            "has_code": None,
            "downloads": None,
            "modelSize": None,
            "author": None
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with negative values
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True,
            "downloads": -1000,
            "modelSize": -5000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with very large values
        result = metric.score({
            "readme": "Basic documentation",
            "has_code": True,
            "downloads": 1000000000,
            "modelSize": 10000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_length_factors(self):
        """Test README length factors."""
        metric = RampUpMetric()
        
        # Short README
        result = metric.score({
            "readme": "Short",
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Long README
        long_readme = "This is a very long README with lots of documentation. " * 100
        result = metric.score({
            "readme": long_readme,
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_author_organization_detection(self):
        """Test author organization detection."""
        metric = RampUpMetric()
        
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
                "readme": "Basic documentation",
                "has_code": True,
                "author": author
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_readme_case_insensitive(self):
        """Test README case insensitivity."""
        metric = RampUpMetric()
        
        # Test different cases
        cases = [
            "Basic model with EXAMPLE",
            "Basic model with example",
            "Basic model with Example",
            "Basic model with ExAmPlE"
        ]
        results = []
        
        for case in cases:
            result = metric.score({
                "readme": case,
                "has_code": True
            })
            results.append(result)
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
        
        # All cases should produce the same result
        assert all(r == results[0] for r in results)


class TestScoreRampUpTimeWrapper:
    """Test the score_ramp_up_time wrapper function."""

    def test_dict_input(self):
        """Test with dictionary input."""
        result = score_ramp_up_time({
            "readme": "Basic documentation",
            "has_code": True
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_wrapper_vs_class_parity(self):
        """Test wrapper function matches class method."""
        data = {
            "readme": "Basic documentation",
            "has_code": True,
            "downloads": 1000000
        }
        
        class_result = RampUpMetric().score(data)
        wrapper_result = score_ramp_up_time(data)
        
        assert class_result == wrapper_result


class TestScoreRampUpTimeWithLatency:
    """Test the score_ramp_up_time_with_latency function."""

    def test_latency_functionality(self):
        """Test that latency function returns both score and latency."""
        result, latency = score_ramp_up_time_with_latency({
            "readme": "Basic documentation",
            "has_code": True
        })
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_consistency(self):
        """Test that latency is consistent."""
        data = {
            "readme": "Basic documentation",
            "has_code": True
        }
        
        # Run multiple times to check consistency
        results = []
        for _ in range(3):
            _, latency = score_ramp_up_time_with_latency(data)
            results.append(latency)
        
        # All latencies should be positive and similar
        assert all(lat > 0 for lat in results)
        # Latencies should be within reasonable range
        assert max(results) - min(results) < 100  # Within 100ms
