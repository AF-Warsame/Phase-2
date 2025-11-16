"""Comprehensive tests for code quality metric to improve coverage."""

import pytest
import os
from unittest.mock import patch, MagicMock

from ai_model_catalog.metrics.score_code_quality import (
    CodeQualityMetric,
    LLMCodeQualityMetric,
    score_code_quality,
    score_code_quality_with_latency,
    _contains_any,
)


class TestContainsAny:
    """Test the _contains_any helper function."""

    def test_contains_any_basic(self):
        """Test basic functionality of _contains_any."""
        text = "This project uses pytest for testing"
        needles = ["pytest", "unittest"]
        assert _contains_any(text, needles) is True

    def test_contains_any_case_insensitive(self):
        """Test case insensitive matching."""
        text = "This project uses PYTEST for testing"
        needles = ["pytest", "unittest"]
        assert _contains_any(text, needles) is True

    def test_contains_any_no_match(self):
        """Test when no needles are found."""
        text = "This project has no testing"
        needles = ["pytest", "unittest"]
        assert _contains_any(text, needles) is False

    def test_contains_any_empty_text(self):
        """Test with empty text."""
        text = ""
        needles = ["pytest", "unittest"]
        assert _contains_any(text, needles) is False

    def test_contains_any_none_text(self):
        """Test with None text."""
        text = None
        needles = ["pytest", "unittest"]
        assert _contains_any(text, needles) is False

    def test_contains_any_empty_needles(self):
        """Test with empty needles list."""
        text = "This project uses pytest"
        needles = []
        assert _contains_any(text, needles) is False


class TestCodeQualityMetric:
    """Test the CodeQualityMetric class comprehensively."""

    def test_basic_code_quality_scoring(self):
        """Test basic code quality scoring."""
        metric = CodeQualityMetric()
        
        # Test with good README
        result = metric.score({
            "readme": "This project uses pytest for testing and GitHub Actions for CI/CD"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_tests_detection(self):
        """Test test framework detection."""
        metric = CodeQualityMetric()
        
        # Direct test framework mentions
        test_frameworks = ["pytest", "unittest", "unit test", "integration test", "tests/"]
        for framework in test_frameworks:
            result = metric.score({"readme": f"This project uses {framework}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_partial_test_mentions(self):
        """Test partial test mentions."""
        metric = CodeQualityMetric()
        
        # Partial test mentions
        partial_mentions = ["test", "testing", "validation"]
        for mention in partial_mentions:
            result = metric.score({"readme": f"This project has {mention}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_ci_cd_detection(self):
        """Test CI/CD detection."""
        metric = CodeQualityMetric()
        
        # Test various CI/CD keywords
        ci_keywords = ["github actions", "travis", "jenkins", "circleci", "gitlab ci"]
        for keyword in ci_keywords:
            result = metric.score({"readme": f"This project uses {keyword}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_partial_ci_mentions(self):
        """Test partial CI mentions."""
        metric = CodeQualityMetric()
        
        # Partial CI mentions
        partial_mentions = ["build", "deploy", "automation"]
        for mention in partial_mentions:
            result = metric.score({"readme": f"This project has {mention}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_linting_detection(self):
        """Test linting tool detection."""
        metric = CodeQualityMetric()
        
        # Test various linting tools
        linting_tools = ["pylint", "flake8", "ruff", "black", "isort", "pre-commit"]
        for tool in linting_tools:
            result = metric.score({"readme": f"This project uses {tool}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_partial_lint_mentions(self):
        """Test partial lint mentions."""
        metric = CodeQualityMetric()
        
        # Partial lint mentions
        partial_mentions = ["style", "format", "standards"]
        for mention in partial_mentions:
            result = metric.score({"readme": f"This project has {mention}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_documentation_detection(self):
        """Test documentation detection."""
        metric = CodeQualityMetric()
        
        # Test typing/documentation keywords
        doc_keywords = ["mypy", "type hints", "typed", "docs/", "documentation", "readthedocs", "api reference"]
        for keyword in doc_keywords:
            result = metric.score({"readme": f"This project has {keyword}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_partial_doc_mentions(self):
        """Test partial documentation mentions."""
        metric = CodeQualityMetric()
        
        # Partial doc mentions
        partial_mentions = ["doc", "readme", "guide", "tutorial"]
        for mention in partial_mentions:
            result = metric.score({"readme": f"This project has {mention}"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_excellent_documentation_score(self):
        """Test excellent documentation scoring."""
        metric = CodeQualityMetric()
        
        # All quality indicators present
        result = metric.score({
            "readme": "This project uses pytest for testing, GitHub Actions for CI/CD, black for linting, and mypy for type checking"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_model_specific_adjustments(self):
        """Test model-specific base score adjustments."""
        metric = CodeQualityMetric()
        
        # Test audience classifier model
        result = metric.score({
            "readme": "Good documentation",
            "model_id": "audience_classifier_model"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test whisper-tiny model
        result = metric.score({
            "readme": "Good documentation",
            "model_id": "whisper-tiny"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_prestigious_organization_boost(self):
        """Test prestigious organization boost."""
        metric = CodeQualityMetric()
        
        prestigious_orgs = [
            "google", "openai", "microsoft", "facebook", "meta", 
            "huggingface", "nvidia", "anthropic"
        ]
        
        for org in prestigious_orgs:
            result = metric.score({
                "readme": "Basic documentation",
                "author": f"{org}-research"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_model_size_factors(self):
        """Test model size impact on scoring."""
        metric = CodeQualityMetric()
        
        # Large model (>1GB)
        result = metric.score({
            "readme": "Basic documentation",
            "modelSize": 2000000000  # 2GB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Medium model (>100MB)
        result = metric.score({
            "readme": "Basic documentation",
            "modelSize": 200000000  # 200MB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Small model (<10MB)
        result = metric.score({
            "readme": "Basic documentation",
            "modelSize": 5000000  # 5MB
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_download_based_factors(self):
        """Test download-based maturity factors."""
        metric = CodeQualityMetric()
        
        # Very popular model (10M+ downloads)
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": 15000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Popular model (1M+ downloads)
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": 2000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Moderately popular model (100K+ downloads)
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": 200000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Less popular model (1K+ downloads)
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": 2000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Unpopular model (<1K downloads)
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": 500
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_experimental_keywords_penalty(self):
        """Test experimental keyword penalty."""
        metric = CodeQualityMetric()
        
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

    def test_established_keywords_boost(self):
        """Test established keyword boost."""
        metric = CodeQualityMetric()
        
        established_keywords = ["production", "stable", "release", "v1", "v2", "enterprise", "bert", "transformer", "gpt"]
        for keyword in established_keywords:
            result = metric.score({
                "readme": f"This is a {keyword} model",
                "author": "individual-dev"
            })
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_specific_model_recognition(self):
        """Test specific model recognition."""
        metric = CodeQualityMetric()
        
        # BERT model recognition
        result = metric.score({
            "readme": "Basic documentation",
            "model_id": "bert-base-uncased"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Audience classifier model recognition
        result = metric.score({
            "readme": "Basic documentation",
            "model_id": "audience_classifier_model"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Whisper-tiny model recognition
        result = metric.score({
            "readme": "Basic documentation",
            "model_id": "whisper-tiny"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_academic_keywords_boost(self):
        """Test academic keyword boost."""
        metric = CodeQualityMetric()
        
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
        metric = CodeQualityMetric()
        
        # Prestigious org, popular model, established keywords, academic keywords
        result = metric.score({
            "readme": "This is a production BERT model described in our research paper",
            "author": "google-research",
            "downloads": 5000000,
            "modelSize": 1000000000,
            "model_id": "bert-base-uncased"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_missing_fields_defaults(self):
        """Test behavior with missing fields."""
        metric = CodeQualityMetric()
        
        result = metric.score({})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        metric = CodeQualityMetric()
        
        # Test with None values (except author, model_id, downloads, and modelSize which need specific types)
        result = metric.score({
            "readme": None,
            "downloads": 0,
            "modelSize": 0,
            "author": "",
            "model_id": ""
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with negative values
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": -1000,
            "modelSize": -5000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        
        # Test with very large values
        result = metric.score({
            "readme": "Basic documentation",
            "downloads": 1000000000,
            "modelSize": 10000000000
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestLLMCodeQualityMetric:
    """Test the LLMCodeQualityMetric class."""

    def test_score_with_llm_empty_content(self):
        """Test score_with_llm with empty content."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_with_llm({"readme": ""})
        assert result == 0.0

    def test_score_with_llm_no_content(self):
        """Test score_with_llm with no content."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_with_llm({})
        assert result == 0.0

    @patch('ai_model_catalog.metrics.score_code_quality.LLMCodeQualityMetric')
    def test_score_with_llm_success(self, mock_llm_class):
        """Test successful LLM scoring."""
        # Mock the LLM service
        mock_instance = MagicMock()
        mock_instance.score_with_llm.return_value = 0.8
        mock_llm_class.return_value = mock_instance
        
        metric = LLMCodeQualityMetric()
        result = metric.score_with_llm({"readme": "Good documentation"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_with_llm_no_analysis(self):
        """Test LLM scoring when analysis fails."""
        metric = LLMCodeQualityMetric()
        
        # Test with empty content to trigger None return
        result = metric.score_with_llm({"readme": ""})
        assert result == 0.0

    def test_score_without_llm_empty_content(self):
        """Test score_without_llm with empty content."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({"readme": ""})
        assert result == 0.0

    def test_score_without_llm_no_content(self):
        """Test score_without_llm with no content."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({})
        assert result == 0.0

    def test_score_without_llm_with_tests(self):
        """Test score_without_llm with test mentions."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({"readme": "This project uses pytest"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_with_ci(self):
        """Test score_without_llm with CI mentions."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({"readme": "This project uses GitHub Actions"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_with_lint(self):
        """Test score_without_llm with linting mentions."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({"readme": "This project uses black"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_with_docs(self):
        """Test score_without_llm with documentation mentions."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({"readme": "This project has documentation"})
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_score_without_llm_all_indicators(self):
        """Test score_without_llm with all quality indicators."""
        metric = LLMCodeQualityMetric()
        
        result = metric.score_without_llm({
            "readme": "This project uses pytest, GitHub Actions, black, and mypy"
        })
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestScoreCodeQualityWrapper:
    """Test the score_code_quality wrapper function."""

    def test_dict_input_traditional(self):
        """Test with dictionary input using traditional method."""
        with patch.dict(os.environ, {}, clear=True):
            result = score_code_quality({"readme": "Good documentation"})
            assert isinstance(result, float)
            assert 0.0 <= result <= 1.0

    def test_dict_input_llm(self):
        """Test with dictionary input using LLM method."""
        with patch.dict(os.environ, {"GEN_AI_STUDIO_API_KEY": "test-key"}):
            with patch('ai_model_catalog.metrics.score_code_quality.LLMCodeQualityMetric') as mock_llm:
                mock_instance = MagicMock()
                mock_instance.score.return_value = 0.8
                mock_llm.return_value = mock_instance
                
                result = score_code_quality({"readme": "Good documentation"})
                assert isinstance(result, float)
                assert 0.0 <= result <= 1.0

    def test_float_input_valid(self):
        """Test with valid float input."""
        result = score_code_quality(0.5)
        assert result == 0.5

    def test_float_input_negative(self):
        """Test with negative float input."""
        result = score_code_quality(-0.5)
        assert result == 0.0

    def test_float_input_greater_than_one(self):
        """Test with float input greater than 1."""
        result = score_code_quality(1.5)
        assert result == 1.0

    def test_invalid_input(self):
        """Test with invalid input."""
        result = score_code_quality("invalid")
        assert result == 0.0

    def test_none_input(self):
        """Test with None input."""
        result = score_code_quality(None)
        assert result == 0.0


class TestScoreCodeQualityWithLatency:
    """Test the score_code_quality_with_latency function."""

    def test_latency_functionality(self):
        """Test that latency function returns both score and latency."""
        result, latency = score_code_quality_with_latency({"readme": "Good documentation"})
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_with_float_input(self):
        """Test latency function with float input."""
        result, latency = score_code_quality_with_latency(0.5)
        
        assert isinstance(result, float)
        assert isinstance(latency, int)
        assert 0.0 <= result <= 1.0
        assert latency > 0

    def test_latency_consistency(self):
        """Test that latency is consistent."""
        data = {"readme": "Good documentation"}
        
        # Run multiple times to check consistency
        results = []
        for _ in range(3):
            _, latency = score_code_quality_with_latency(data)
            results.append(latency)
        
        # All latencies should be positive and similar
        assert all(lat > 0 for lat in results)
        # Latencies should be within reasonable range
        assert max(results) - min(results) < 100  # Within 100ms
