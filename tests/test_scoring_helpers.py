"""Tests for scoring helper functions."""

from ai_model_catalog.metrics.scoring_helpers import (
    combine_llm_scores,
    extract_readme_content,
    extract_dataset_info,
    validate_llm_response,
)


def test_combine_llm_scores():
    """Test LLM score combination."""
    # Test with valid scores
    llm_analysis = {
        "installation_quality": 0.8,
        "documentation_completeness": 0.6,
        "example_quality": 0.9,
        "overall_readability": 0.7,
    }
    weights = {
        "installation_quality": 0.3,
        "documentation_completeness": 0.25,
        "example_quality": 0.25,
        "overall_readability": 0.2,
    }
    
    result = combine_llm_scores(llm_analysis, weights)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0
    
    # Test with empty weights
    result = combine_llm_scores(llm_analysis, {})
    assert result == 0.0
    
    # Test with invalid scores
    llm_analysis_invalid = {
        "installation_quality": 1.5,  # Invalid: > 1.0
        "documentation_completeness": -0.1,  # Invalid: < 0.0
        "example_quality": "invalid",  # Invalid: not numeric
    }
    result = combine_llm_scores(llm_analysis_invalid, weights)
    assert result == 0.0


def test_extract_readme_content():
    """Test README content extraction."""
    # Test with readme field
    data = {"readme": "Test README content"}
    result = extract_readme_content(data)
    assert result == "Test README content"
    
    # Test with description field
    data = {"description": "Test description"}
    result = extract_readme_content(data)
    assert result == "Test description"
    
    # Test with cardData
    data = {"cardData": {"content": "Test card content"}}
    result = extract_readme_content(data)
    assert result == "Test card content"
    
    # Test with empty data
    data = {}
    result = extract_readme_content(data)
    assert result == ""


def test_extract_dataset_info():
    """Test dataset info extraction."""
    data = {
        "description": "Test dataset",
        "tags": ["nlp", "text"],
        "taskCategories": ["classification"],
        "downloads": 1000,
        "author": "test-author",
        "license": "mit",
    }
    
    result = extract_dataset_info(data)
    assert result["description"] == "Test dataset"
    assert result["tags"] == ["nlp", "text"]
    assert result["downloads"] == 1000
    
    # Test with missing fields
    data = {}
    result = extract_dataset_info(data)
    assert result["description"] == ""
    assert result["tags"] == []
    assert result["downloads"] == 0


def test_validate_llm_response():
    """Test LLM response validation."""
    # Test valid response
    response = {
        "installation_quality": 0.8,
        "documentation_completeness": 0.6,
    }
    expected_keys = ["installation_quality", "documentation_completeness"]
    assert validate_llm_response(response, expected_keys) is True
    
    # Test invalid response (not dict)
    assert validate_llm_response("invalid", expected_keys) is False
    
    # Test missing key
    response = {"installation_quality": 0.8}
    assert validate_llm_response(response, expected_keys) is False
    
    # Test invalid score type
    response = {
        "installation_quality": "invalid",
        "documentation_completeness": 0.6,
    }
    assert validate_llm_response(response, expected_keys) is False
    
    # Test score out of range
    response = {
        "installation_quality": 1.5,
        "documentation_completeness": 0.6,
    }
    assert validate_llm_response(response, expected_keys) is False
