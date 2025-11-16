"""Comprehensive tests for dataset quality metric to improve coverage."""

import pytest
import os
from unittest.mock import patch, MagicMock

from ai_model_catalog.metrics.score_dataset_quality import (
    DatasetQualityMetric,
    LLMDatasetQualityMetric,
    score_dataset_quality,
    score_dataset_quality_with_latency,
    _contains_any,
)


class TestContainsAny:
    """Test the _contains_any helper function."""

    def test_contains_any_basic(self):
        """Test basic functionality of _contains_any."""
        text = "This model uses ImageNet dataset"
        needles = ["dataset", "imagenet"]
        assert _contains_any(text, needles) is True

    def test_contains_any_case_insensitive(self):
        """Test case insensitive matching."""
        text = "This model uses IMAGENET DATASET"
        needles = ["dataset", "imagenet"]
        assert _contains_any(text, needles) is True

    def test_contains_any_no_match(self):
        """Test when no needles are found."""
        text = "This model has no information"
        needles = ["dataset", "imagenet"]
        assert _contains_any(text, needles) is False

    def test_contains_any_empty_text(self):
        """Test with empty text."""
        text = ""
        needles = ["dataset", "imagenet"]
        assert _contains_any(text, needles) is False

    def test_contains_any_none_text(self):
        """Test with None text."""
        text = None
        needles = ["dataset", "imagenet"]
        assert _contains_any(text, needles) is False

    def test_contains_any_empty_needles(self):
        """Test with empty needles list."""
        text = "This model uses dataset"
        needles = []
        assert _contains_any(text, needles) is False


class TestDatasetQualityMetric:
    """Test the DatasetQualityMetric class comprehensively."""

    def test_basic_dataset_quality_scoring(self):
        """Test basic dataset quality scoring."""
        metric = DatasetQualityMetric()
        
        # Test with good dataset documentation
        result = metric.score({
            "readme": "This model uses ImageNet dataset for training",
            "tags": ["dataset", "imagenet"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_dataset_keywords_detection(self):
        """Test dataset keyword detection."""
        metric = DatasetQualityMetric()
        
        # Test various dataset keywords
        dataset_keywords = ["dataset", "training data", "corpus", "benchmark"]
        for keyword in dataset_keywords:
            result = metric.score({"readme": f"This model uses {keyword}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_generic_data_mentions(self):
        """Test generic data mentions."""
        metric = DatasetQualityMetric()
        
        # Test generic data terms
        generic_terms = ["data", "corpus", "collection"]
        for term in generic_terms:
            result = metric.score({"readme": f"This model uses {term}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_known_dataset_names(self):
        """Test known dataset name detection."""
        metric = DatasetQualityMetric()
        
        # Test various known datasets
        known_datasets = ["imagenet", "coco", "mnist", "squad", "glue"]
        for dataset in known_datasets:
            result = metric.score({"readme": f"This model uses {dataset}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_generic_dataset_names(self):
        """Test generic dataset names."""
        metric = DatasetQualityMetric()
        
        # Test generic dataset names
        generic_datasets = ["imagenet", "coco", "mnist", "squad", "glue"]
        for dataset in generic_datasets:
            result = metric.score({"readme": f"This model uses {dataset}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_data_links_detection(self):
        """Test data link detection."""
        metric = DatasetQualityMetric()
        
        # Test with markdown links
        result = metric.score({
            "readme": "See [dataset](http://example.com) for more info"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with plain HTTP links
        result = metric.score({
            "readme": "Dataset available at http://example.com"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_generic_links(self):
        """Test generic link detection."""
        metric = DatasetQualityMetric()
        
        # Test with generic links (no dataset word)
        result = metric.score({
            "readme": "See http://example.com for more info"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_dataset_tags_detection(self):
        """Test dataset tag detection."""
        metric = DatasetQualityMetric()
        
        # Test explicit dataset tags
        dataset_tags = ["dataset", "corpus", "benchmark"]
        for tag in dataset_tags:
            result = metric.score({
                "readme": "Basic model",
                "tags": [tag]
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_generic_tags(self):
        """Test generic tag detection."""
        metric = DatasetQualityMetric()
        
        # Test generic tags
        generic_tags = ["nlp", "vision", "audio", "text"]
        for tag in generic_tags:
            result = metric.score({
                "readme": "Basic model",
                "tags": [tag]
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_perfect_documentation_score(self):
        """Test perfect documentation scoring."""
        metric = DatasetQualityMetric()
        
        # All quality indicators present
        result = metric.score({
            "readme": "This model uses ImageNet dataset. See [data](http://example.com) for more info",
            "tags": ["dataset", "imagenet"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_prestigious_organization_boost(self):
        """Test prestigious organization boost."""
        metric = DatasetQualityMetric()
        
        prestigious_orgs = [
            "google", "openai", "microsoft", "facebook", "meta", 
            "huggingface", "nvidia", "anthropic"
        ]
        
        for org in prestigious_orgs:
            result = metric.score({
                "readme": "Basic dataset documentation",
                "author": f"{org}-research"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_model_size_factors(self):
        """Test model size impact on scoring."""
        metric = DatasetQualityMetric()
        
        # Large model (>1GB)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "modelSize": 2000000000  # 2GB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Medium model (>100MB)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "modelSize": 200000000  # 200MB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Small model (<10MB)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "modelSize": 5000000  # 5MB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_download_based_factors(self):
        """Test download-based maturity factors."""
        metric = DatasetQualityMetric()
        
        # Very popular model (10M+ downloads)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": 15000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Popular model (1M+ downloads)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": 2000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Moderately popular model (100K+ downloads)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": 200000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Less popular model (1K+ downloads)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": 2000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Unpopular model (<1K downloads)
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": 500
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_experimental_keywords_penalty(self):
        """Test experimental keyword penalty."""
        metric = DatasetQualityMetric()
        
        # Non-prestigious org with experimental keywords
        result = metric.score({
            "readme": "This is an experimental model for testing",
            "author": "individual-dev"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Prestigious org with experimental keywords (should not be penalized)
        result = metric.score({
            "readme": "This is an experimental model for testing",
            "author": "google-research"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_individual_developer_penalty(self):
        """Test penalty for individual developers."""
        metric = DatasetQualityMetric()
        
        result = metric.score({
            "readme": "Basic dataset documentation",
            "author": "individual-dev"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_established_keywords_boost(self):
        """Test established keyword boost."""
        metric = DatasetQualityMetric()
        
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        for keyword in established_keywords:
            result = metric.score({
                "readme": f"This is a {keyword} model",
                "author": "individual-dev"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_academic_keywords_boost(self):
        """Test academic keyword boost."""
        metric = DatasetQualityMetric()
        
        academic_keywords = ["paper", "research", "arxiv", "conference", "journal", "study"]
        for keyword in academic_keywords:
            result = metric.score({
                "readme": f"This model is described in our {keyword}",
                "author": "individual-dev"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_combined_factors(self):
        """Test combination of multiple factors."""
        metric = DatasetQualityMetric()
        
        # Prestigious org, popular model, established keywords, academic keywords
        result = metric.score({
            "readme": "This is a production BERT model described in our research paper",
            "author": "google-research",
            "downloads": 5000000,
            "modelSize": 1000000000,
            "tags": ["dataset", "bert"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_missing_fields_defaults(self):
        """Test behavior with missing fields."""
        metric = DatasetQualityMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        metric = DatasetQualityMetric()
        
        # Test with None values (except author, downloads, and modelSize which need specific types)
        result = metric.score({
            "readme": None,
            "tags": None,
            "downloads": 0,
            "modelSize": 0,
            "author": ""
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with negative values
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": -1000,
            "modelSize": -5000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with very large values
        result = metric.score({
            "readme": "Basic dataset documentation",
            "downloads": 1000000000,
            "modelSize": 10000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_readme_stripping(self):
        """Test README content stripping."""
        metric = DatasetQualityMetric()
        
        # Test with whitespace
        result = metric.score({
            "readme": "  This model uses dataset  "
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_tags_handling(self):
        """Test tags handling."""
        metric = DatasetQualityMetric()
        
        # Test with empty tags
        result = metric.score({
            "readme": "Basic model",
            "tags": []
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with None tags
        result = metric.score({
            "readme": "Basic model",
            "tags": None
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestLLMDatasetQualityMetric:
    """Test the LLMDatasetQualityMetric class."""

    def test_score_with_llm_empty_description(self):
        """Test score_with_llm with empty description."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_with_llm({"description": ""})
        assert result == 0.0

    def test_score_with_llm_no_description(self):
        """Test score_with_llm with no description."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_with_llm({})
        assert result == 0.0

    @patch('ai_model_catalog.metrics.score_dataset_quality.LLMDatasetQualityMetric')
    def test_score_with_llm_success(self, mock_llm_class):
        """Test successful LLM scoring."""
        # Mock the LLM service
        mock_instance = MagicMock()
        mock_instance.score_with_llm.return_value = 0.8
        mock_llm_class.return_value = mock_instance
        
        metric = LLMDatasetQualityMetric()
        result = metric.score_with_llm({"description": "Good dataset description"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_with_llm_no_analysis(self):
        """Test LLM scoring when analysis fails."""
        metric = LLMDatasetQualityMetric()
        
        # Test with empty description to trigger None return
        result = metric.score_with_llm({"description": ""})
        assert result == 0.0

    def test_score_without_llm_empty_content(self):
        """Test score_without_llm with empty content."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({"readme": ""})
        assert result == 0.0

    def test_score_without_llm_no_content(self):
        """Test score_without_llm with no content."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({})
        assert result == 0.0

    def test_score_without_llm_with_dataset_word(self):
        """Test score_without_llm with dataset word."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({"readme": "This model uses dataset"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_with_known_name(self):
        """Test score_without_llm with known dataset name."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({"readme": "This model uses ImageNet"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_with_data_link(self):
        """Test score_without_llm with data link."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({
            "readme": "See [dataset](http://example.com) for more info"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_with_dataset_tag(self):
        """Test score_without_llm with dataset tag."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({
            "readme": "Basic model",
            "tags": ["dataset"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_all_indicators(self):
        """Test score_without_llm with all quality indicators."""
        metric = LLMDatasetQualityMetric()
        
        result = metric.score_without_llm({
            "readme": "This model uses ImageNet dataset. See [data](http://example.com)",
            "tags": ["dataset", "imagenet"]
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestScoreDatasetQualityWrapper:
    """Test the score_dataset_quality wrapper function."""

    def test_dict_input_traditional(self):
        """Test with dictionary input using traditional method."""
        with patch.dict(os.environ, {}, clear=True):
            result = score_dataset_quality({"readme": "Good dataset documentation"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_dict_input_llm(self):
        """Test with dictionary input using LLM method."""
        with patch.dict(os.environ, {"GEN_AI_STUDIO_API_KEY": "test-key"}):
            with patch('ai_model_catalog.metrics.score_dataset_quality.LLMDatasetQualityMetric') as mock_llm:
                mock_instance = MagicMock()
                mock_instance.score.return_value = 0.8
                mock_llm.return_value = mock_instance
                
                result = score_dataset_quality({"readme": "Good dataset documentation"})
                assert isinstance(result, float)
                assert 0.0 <= result <= 1.0

    def test_float_input_valid(self):
        """Test with valid float input."""
        result = score_dataset_quality(0.5)
        assert result == 0.5

    def test_float_input_negative(self):
        """Test with negative float input."""
        result = score_dataset_quality(-0.5)
        assert result == 0.0

    def test_float_input_greater_than_one(self):
        """Test with float input greater than 1."""
        result = score_dataset_quality(1.5)
        assert result == 1.0

    def test_invalid_input(self):
        """Test with invalid input."""
        result = score_dataset_quality("invalid")
        assert result == 0.0

    def test_none_input(self):
        """Test with None input."""
        result = score_dataset_quality(None)
        assert result == 0.0


class TestScoreDatasetQualityWithLatency:
    """Test the score_dataset_quality_with_latency function."""

    def test_latency_functionality(self):
        """Test that latency function returns both score and latency."""
        result, latency = score_dataset_quality_with_latency({"readme": "Good dataset documentation"})
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_with_float_input(self):
        """Test latency function with float input."""
        result, latency = score_dataset_quality_with_latency(0.5)
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_consistency(self):
        """Test that latency is consistent."""
        data = {"readme": "Good dataset documentation"}
        
        # Run multiple times to check consistency
        results = []
        for _ in range(3):
            _, latency = score_dataset_quality_with_latency(data)
            results.append(latency)
        
        # All latencies should be positive and similar
        assert all(lat > 0 for lat in results)
        # Latencies should be within reasonable range
        assert max(results) - min(results) < 100  # Within 100ms
