"""Tests for LLM ramp-up time functionality."""

import os
from unittest.mock import patch, MagicMock

from ai_model_catalog.metrics.score_ramp_up_time import LLMRampUpMetric


def test_llm_ramp_up_metric_with_llm():
    """Test LLM ramp-up metric with LLM analysis."""
    metric = LLMRampUpMetric()
    
    # Mock the LLM service
    mock_llm_service = MagicMock()
    mock_llm_service.analyze_readme_quality.return_value = {
        "installation_quality": 0.8,
        "documentation_completeness": 0.6,
        "example_quality": 0.9,
        "overall_readability": 0.7,
    }
    metric.llm_service = mock_llm_service
    
    # Test data
    data = {
        "readme": "This is a comprehensive README with installation instructions and examples.",
        "cardData": {"content": "Additional documentation content."}
    }
    
    result = metric.score_with_llm(data)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Verify LLM service was called
    mock_llm_service.analyze_readme_quality.assert_called_once()


def test_llm_ramp_up_metric_without_llm():
    """Test LLM ramp-up metric fallback to traditional method."""
    metric = LLMRampUpMetric()
    
    # Test with empty content
    data = {"readme": ""}
    result = metric.score_without_llm(data)
    assert result == 0.0
    
    # Test with short content
    data = {"readme": "Short README"}
    result = metric.score_without_llm(data)
    assert result < 1.0
    
    # Test with long content
    data = {"readme": "A" * 300}  # Longer than 250 chars
    result = metric.score_without_llm(data)
    assert result == 1.0


def test_llm_ramp_up_metric_no_llm_response():
    """Test LLM ramp-up metric when LLM returns None."""
    metric = LLMRampUpMetric()
    
    # Mock the LLM service to return None
    mock_llm_service = MagicMock()
    mock_llm_service.analyze_readme_quality.return_value = None
    metric.llm_service = mock_llm_service
    
    data = {"readme": "Test README content"}
    result = metric.score_with_llm(data)
    assert result is None  # Should return None when LLM fails


def test_llm_ramp_up_metric_empty_readme():
    """Test LLM ramp-up metric with empty README."""
    metric = LLMRampUpMetric()
    
    # Mock the LLM service
    mock_llm_service = MagicMock()
    metric.llm_service = mock_llm_service
    
    data = {"readme": ""}
    result = metric.score_with_llm(data)
    assert result == 0.0
    
    # LLM service should not be called for empty content
    mock_llm_service.analyze_readme_quality.assert_not_called()
