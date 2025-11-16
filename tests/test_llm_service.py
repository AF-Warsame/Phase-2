"""Tests for LLM service functionality."""

import json
from unittest.mock import patch

from requests import RequestException

from ai_model_catalog.llm_service import LLMService


class TestLLMService:
    """Test cases for LLMService."""

    def test_init_without_api_key(self):
        """Test LLM service initialization without API key."""
        with patch.dict("os.environ", {}, clear=True):
            service = LLMService()
            assert service.api_key is None

    def test_init_with_api_key(self):
        """Test LLM service initialization with API key."""
        with patch.dict("os.environ", {"GEN_AI_STUDIO_API_KEY": "test_key"}):
            service = LLMService()
            assert service.api_key == "test_key"

    def test_cache_key_generation(self):
        """Test cache key generation."""
        service = LLMService()
        # pylint: disable=protected-access
        key1 = service._get_cache_key("test content", "analysis_type")
        key2 = service._get_cache_key("test content", "analysis_type")
        key3 = service._get_cache_key("different content", "analysis_type")

        assert key1 == key2
        assert key1 != key3

    def test_basic_readme_analysis(self):
        """Test basic README analysis fallback."""
        service = LLMService()
        readme = "This is a test README with installation instructions."

        # pylint: disable=protected-access
        result = service._basic_readme_analysis(readme)

        assert isinstance(result, dict)
        assert "installation_quality" in result
        assert "documentation_completeness" in result
        assert "example_quality" in result
        assert "overall_readability" in result
        assert "technical_depth" in result
        assert "reasoning" in result

        # Check score ranges
        for key in [
            "installation_quality",
            "documentation_completeness",
            "example_quality",
            "overall_readability",
            "technical_depth",
        ]:
            assert 0.0 <= result[key] <= 1.0

    def test_basic_code_quality_analysis(self):
        """Test basic code quality analysis fallback."""
        service = LLMService()
        readme = "This project uses pytest for testing and black for formatting."

        # pylint: disable=protected-access
        result = service._basic_code_quality_analysis(readme)

        assert isinstance(result, dict)
        assert "testing_framework" in result
        assert "ci_cd_mentions" in result
        assert "linting_tools" in result
        assert "documentation_quality" in result
        assert "code_organization" in result
        assert "reasoning" in result

        # Check score ranges
        for key in [
            "testing_framework",
            "ci_cd_mentions",
            "linting_tools",
            "documentation_quality",
            "code_organization",
        ]:
            assert 0.0 <= result[key] <= 1.0

    def test_basic_dataset_analysis(self):
        """Test basic dataset analysis fallback."""
        service = LLMService()
        dataset_info = {
            "description": "A comprehensive dataset for testing",
            "tags": ["nlp", "text", "classification", "benchmark"],
            "downloads": 1000,
        }

        # pylint: disable=protected-access
        result = service._basic_dataset_analysis(dataset_info)

        assert isinstance(result, dict)
        assert "documentation_completeness" in result
        assert "usage_examples" in result
        assert "metadata_quality" in result
        assert "data_description" in result
        assert "overall_quality" in result
        assert "reasoning" in result

        # Check score ranges
        for key in [
            "documentation_completeness",
            "usage_examples",
            "metadata_quality",
            "data_description",
            "overall_quality",
        ]:
            assert 0.0 <= result[key] <= 1.0

    @patch("ai_model_catalog.llm_service.requests.post")
    def test_api_call_success(self, mock_post):
        """Test successful API call."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "installation_quality": 0.8,
                                "documentation_completeness": 0.9,
                                "example_quality": 0.7,
                                "overall_readability": 0.8,
                                "technical_depth": 0.6,
                                "reasoning": "Good documentation",
                            }
                        )
                    }
                }
            ]
        }
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status.return_value = None

        with patch.dict("os.environ", {"GEN_AI_STUDIO_API_KEY": "test_key"}):
            service = LLMService()
            # pylint: disable=protected-access
            result = service._call_api("test prompt", "test content")

            assert result is not None
            assert "installation_quality" in result
            assert result["installation_quality"] == 0.8

    @patch("ai_model_catalog.llm_service.requests.post")
    def test_api_call_failure(self, mock_post):
        """Test API call failure."""
        mock_post.side_effect = RequestException("API Error")

        with patch.dict("os.environ", {"GEN_AI_STUDIO_API_KEY": "test_key"}):
            service = LLMService()
            # pylint: disable=protected-access
            result = service._call_api("test prompt", "test content")

            assert result is None

    def test_analyze_readme_quality_without_api_key(self):
        """Test README analysis without API key (fallback)."""
        with patch.dict("os.environ", {}, clear=True):
            service = LLMService()
            result = service.analyze_readme_quality("Test README content")

            assert isinstance(result, dict)
            assert "installation_quality" in result
            assert "reasoning" in result
            assert "Basic keyword-based analysis" in result["reasoning"]

    def test_analyze_code_quality_without_api_key(self):
        """Test code quality analysis without API key (fallback)."""
        with patch.dict("os.environ", {}, clear=True):
            service = LLMService()
            result = service.analyze_code_quality_indicators("Test README with pytest")

            assert isinstance(result, dict)
            assert "testing_framework" in result
            assert "reasoning" in result
            assert "Basic keyword-based analysis" in result["reasoning"]

    def test_analyze_dataset_quality_without_api_key(self):
        """Test dataset quality analysis without API key (fallback)."""
        with patch.dict("os.environ", {}, clear=True):
            service = LLMService()
            dataset_info = {"description": "Test dataset", "tags": ["test"]}
            result = service.analyze_dataset_quality(dataset_info)

            assert isinstance(result, dict)
            assert "documentation_completeness" in result
            assert "reasoning" in result
            assert "Basic analysis" in result["reasoning"]

    def test_caching_behavior(self):
        """Test that results are cached."""
        with patch.dict("os.environ", {}, clear=True):
            service = LLMService()
            content = "Test content for caching"

            # First call
            result1 = service.analyze_readme_quality(content)

            # Second call should use cache
            result2 = service.analyze_readme_quality(content)

            assert result1 == result2
            assert len(service.cache) == 1
