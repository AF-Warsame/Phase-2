"""Simple tests to improve model sources coverage."""

import pytest
from unittest.mock import MagicMock, patch

from ai_model_catalog.model_sources.hf_model import ModelHandler


def test_model_handler_initialization():
    """Test ModelHandler initialization."""
    handler = ModelHandler("test-model")
    assert handler.model_id == "test-model"


def test_model_handler_format_data_basic():
    """Test ModelHandler format_data with basic data."""
    handler = ModelHandler("test-model")
    
    data = {
        "modelId": "test-model",
        "author": "test-author",
        "license": "MIT",
        "downloads": 1000,
        "lastModified": "2024-01-01T00:00:00Z",
        "readme": "Test README content",
        "repo_size_bytes": 50000000
    }
    
    result = handler.format_data(data)
    
    assert result["source"] == "huggingface"
    assert result["id"] == "test-model"
    assert result["author"] == "test-author"
    assert result["license"] == "MIT"
    assert result["downloads"] == 1000
    assert result["last_modified"] == "2024-01-01T00:00:00Z"
    assert result["has_readme"] is True
    assert result["repo_size_bytes"] == 50000000


def test_model_handler_format_data_alternative_keys():
    """Test ModelHandler format_data with alternative key names."""
    handler = ModelHandler("test-model")
    
    data = {
        "id": "alt-model-id",  # Alternative to modelId
        "owner": "alt-author",  # Alternative to author
        "last_modified": "2024-01-01T00:00:00Z",  # Alternative to lastModified
        "has_readme": True,  # Alternative to readme
        "size_bytes": 75000000,  # Alternative to repo_size_bytes
    }
    
    result = handler.format_data(data)
    
    assert result["id"] == "alt-model-id"
    assert result["author"] == "alt-author"
    assert result["last_modified"] == "2024-01-01T00:00:00Z"
    assert result["has_readme"] is True
    assert result["repo_size_bytes"] == 75000000


def test_model_handler_format_data_with_card_data():
    """Test ModelHandler format_data with card data."""
    handler = ModelHandler("test-model")
    
    data = {
        "modelId": "test-model",
        "cardData": {
            "language": "en",
            "license": "MIT",
            "tags": ["nlp", "text"],
            "pipeline_tag": "text-classification",
            "model_type": "bert",
            "library_name": "transformers",
            "datasets": ["imdb"],
            "metrics": ["accuracy"],
            "co2_eq_emissions": {"emissions": 0.5},
            "model_index": "model_index.json",
            "extra_field": "ignored"  # Should be ignored due to limit
        }
    }
    
    result = handler.format_data(data)
    
    assert "card_keys" in result
    assert len(result["card_keys"]) == 10  # Should be limited to 10 keys
    assert result["card_keys"] == sorted(data["cardData"].keys())[:10]


def test_model_handler_format_data_without_card_data():
    """Test ModelHandler format_data without card data."""
    handler = ModelHandler("test-model")
    
    data = {
        "modelId": "test-model",
        "author": "test-author"
    }
    
    result = handler.format_data(data)
    
    assert "card_keys" not in result


def test_model_handler_format_data_missing_fields():
    """Test ModelHandler format_data with missing fields."""
    handler = ModelHandler("test-model")
    
    data = {}  # Empty data
    
    result = handler.format_data(data)
    
    assert result["source"] == "huggingface"
    assert result["id"] == "test-model"  # Should fall back to model_id
    assert result["author"] == ""
    assert result["license"] == ""
    assert result["downloads"] == 0
    assert result["last_modified"] == ""
    assert result["has_readme"] is False
    assert result["repo_size_bytes"] == 0


def test_model_handler_format_data_type_conversion():
    """Test ModelHandler format_data with type conversion."""
    handler = ModelHandler("test-model")
    
    data = {
        "modelId": "test-model",
        "downloads": "1000",  # String that should be converted to int
        "readme": "true",  # String that should be converted to bool
        "repo_size_bytes": "50000000"  # String that should be converted to int
    }
    
    result = handler.format_data(data)
    
    assert result["downloads"] == 1000
    assert result["has_readme"] is True
    assert result["repo_size_bytes"] == 50000000


def test_model_handler_format_data_invalid_type_conversion():
    """Test ModelHandler format_data with invalid type conversion."""
    handler = ModelHandler("test-model")
    
    data = {
        "modelId": "test-model",
        "downloads": "invalid",  # Should default to 0
        "readme": "invalid",  # Should default to False
        "repo_size_bytes": "invalid"  # Should default to 0
    }
    
    result = handler.format_data(data)
    
    assert result["downloads"] == 0
    assert result["has_readme"] is True  # "invalid" is truthy
    assert result["repo_size_bytes"] == 0


@patch("ai_model_catalog.model_sources.hf_model.typer.echo")
def test_model_handler_display_data(mock_echo):
    """Test ModelHandler display_data functionality."""
    handler = ModelHandler("test-model")
    
    formatted_data = {
        "source": "huggingface",
        "id": "test-model",
        "author": "test-author",
        "license": "MIT",
        "downloads": 1000
    }
    
    raw_data = {
        "modelId": "test-model",
        "author": "test-author"
    }
    
    handler.display_data(formatted_data, raw_data)
    
    # Verify that typer.echo was called
    mock_echo.assert_called_once()


def test_model_handler_edge_cases():
    """Test ModelHandler with edge cases."""
    handler = ModelHandler("test-model")
    
    # Test with None values
    data = {
        "modelId": None,
        "author": None,
        "license": None,
        "downloads": None,
        "lastModified": None,
        "readme": None,
        "repo_size_bytes": None
    }
    
    result = handler.format_data(data)
    
    assert result["id"] == "test-model"  # Should fall back to model_id
    assert result["author"] == ""
    assert result["license"] == ""
    assert result["downloads"] == 0
    assert result["last_modified"] == ""
    assert result["has_readme"] is False
    assert result["repo_size_bytes"] == 0
    
    # Test with boolean values
    data = {
        "modelId": "test-model",
        "downloads": True,  # Boolean that should be converted to int
        "readme": False,  # Boolean that should be converted to bool
        "repo_size_bytes": True  # Boolean that should be converted to int
    }
    
    result = handler.format_data(data)
    
    assert result["downloads"] == 0  # True becomes 0 due to _as_int conversion
    assert result["has_readme"] is False
    assert result["repo_size_bytes"] == 0  # True becomes 0 due to _as_int conversion
