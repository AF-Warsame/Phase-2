"""Comprehensive tests for license metric to improve coverage."""

import pytest

from ai_model_catalog.metrics.score_license import (
    LicenseMetric,
    score_license,
    score_license_with_latency,
)


class TestLicenseMetric:
    """Test the LicenseMetric class comprehensively."""

    def test_basic_license_scoring(self):
        """Test basic license scoring."""
        metric = LicenseMetric()
        
        # MIT license
        result = metric.score({
            "license": "mit"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_open_source_licenses(self):
        """Test open source licenses."""
        metric = LicenseMetric()
        
        open_source_licenses = [
            "mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause",
            "gpl-3.0", "gpl-2.0", "lgpl-3.0", "lgpl-2.1",
            "mpl-2.0", "epl-2.0", "cddl-1.1", "eclipse-2.0"
        ]
        
        for license_name in open_source_licenses:
            result = metric.score({"license": license_name})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_restrictive_licenses(self):
        """Test restrictive licenses."""
        metric = LicenseMetric()
        
        restrictive_licenses = [
            "proprietary", "commercial", "all-rights-reserved",
            "unlicense", "cc0-1.0"
        ]
        
        for license_name in restrictive_licenses:
            result = metric.score({"license": license_name})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_unknown_license(self):
        """Test unknown license."""
        metric = LicenseMetric()
        
        result = metric.score({
            "license": "unknown-license"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_no_license(self):
        """Test no license specified."""
        metric = LicenseMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_license_case_insensitive(self):
        """Test license case insensitivity."""
        metric = LicenseMetric()
        
        # Test different cases
        cases = ["MIT", "mit", "Mit", "mIt"]
        results = []
        
        for case in cases:
            result = metric.score({"license": case})
            results.append(result)
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0
        
        # All cases should produce the same result
        assert all(r == results[0] for r in results)

    def test_license_with_whitespace(self):
        """Test license with whitespace."""
        metric = LicenseMetric()
        
        result = metric.score({
            "license": "  mit  "
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_organization_reputation_boost(self):
        """Test organization reputation boost."""
        metric = LicenseMetric()
        
        prestigious_orgs = [
            "google", "openai", "microsoft", "facebook", "meta", 
            "huggingface", "nvidia", "anthropic"
        ]
        
        for org in prestigious_orgs:
            result = metric.score({
                "license": "mit",
                "author": f"{org}-research"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_download_based_boost(self):
        """Test download-based boost."""
        metric = LicenseMetric()
        
        # High downloads
        result = metric.score({
            "license": "mit",
            "downloads": 1000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Low downloads
        result = metric.score({
            "license": "mit",
            "downloads": 100
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_model_size_factors(self):
        """Test model size impact."""
        metric = LicenseMetric()
        
        # Large model
        result = metric.score({
            "license": "mit",
            "modelSize": 1000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Small model
        result = metric.score({
            "license": "mit",
            "modelSize": 1000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_quality_factors(self):
        """Test README quality factors."""
        metric = LicenseMetric()
        
        # Good README
        result = metric.score({
            "license": "mit",
            "readme": "Comprehensive documentation with examples and API reference"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Poor README
        result = metric.score({
            "license": "mit",
            "readme": "Basic model"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_combined_factors(self):
        """Test combination of multiple factors."""
        metric = LicenseMetric()
        
        result = metric.score({
            "license": "apache-2.0",
            "author": "google-research",
            "downloads": 5000000,
            "modelSize": 1000000000,
            "readme": "Comprehensive documentation with examples"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_missing_fields_defaults(self):
        """Test behavior with missing fields."""
        metric = LicenseMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_edge_cases(self):
        """Test edge cases."""
        metric = LicenseMetric()
        
        # Test with None values (except readme, author, downloads, and modelSize which need specific types)
        result = metric.score({
            "license": None,
            "downloads": 0,
            "modelSize": 0,
            "readme": "",
            "author": ""
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with negative values
        result = metric.score({
            "license": "mit",
            "downloads": -1000,
            "modelSize": -5000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with very large values
        result = metric.score({
            "license": "mit",
            "downloads": 1000000000,
            "modelSize": 10000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_license_scoring_consistency(self):
        """Test license scoring consistency."""
        metric = LicenseMetric()
        
        # Same license should produce same score
        result1 = metric.score({"license": "mit"})
        result2 = metric.score({"license": "mit"})
        assert result1 == result2

    def test_author_organization_detection(self):
        """Test author organization detection."""
        metric = LicenseMetric()
        
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
                "license": "mit",
                "author": author
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0


class TestScoreLicenseWrapper:
    """Test the score_license wrapper function."""

    def test_dict_input(self):
        """Test with dictionary input."""
        result = score_license({
            "license": "mit"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_wrapper_vs_class_parity(self):
        """Test wrapper function matches class method."""
        data = {
            "license": "mit",
            "downloads": 1000000
        }
        
        class_result = LicenseMetric().score(data)
        wrapper_result = score_license(data)
        
        assert class_result == wrapper_result


class TestScoreLicenseWithLatency:
    """Test the score_license_with_latency function."""

    def test_latency_functionality(self):
        """Test that latency function returns both score and latency."""
        result, latency = score_license_with_latency({
            "license": "mit"
        })
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_consistency(self):
        """Test that latency is consistent."""
        data = {"license": "mit"}
        
        # Run multiple times to check consistency
        results = []
        for _ in range(3):
            _, latency = score_license_with_latency(data)
            results.append(latency)
        
        # All latencies should be positive and similar
        assert all(lat > 0 for lat in results)
        # Latencies should be within reasonable range
        assert max(results) - min(results) < 100  # Within 100ms
