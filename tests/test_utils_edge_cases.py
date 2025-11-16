"""Edge case tests for utils.py to boost coverage."""

# No imports needed for this test file

from ai_model_catalog.utils import (
    _as_bool,
    _as_int,
    _format_model_data,
    _format_repository_data,
)


def test_as_int_with_valid_string():
    """Test _as_int with valid string."""
    assert _as_int("123") == 123
    assert _as_int("0") == 0
    assert _as_int("-5") == -5


def test_as_int_with_invalid_string():
    """Test _as_int with invalid string."""
    assert _as_int("invalid") == 0
    assert _as_int("") == 0
    assert _as_int("abc123") == 0


def test_as_int_with_none():
    """Test _as_int with None."""
    assert _as_int(None) == 0


def test_as_int_with_number():
    """Test _as_int with number."""
    assert _as_int(123) == 123
    assert _as_int(0) == 0


def test_as_bool_with_truthy_values():
    """Test _as_bool with truthy values."""
    assert _as_bool(True) is True
    assert _as_bool(1) is True
    assert _as_bool("true") is True
    assert _as_bool("yes") is True
    assert _as_bool("on") is True


def test_as_bool_with_falsy_values():
    """Test _as_bool with falsy values."""
    assert _as_bool(False) is False
    assert _as_bool(0) is False
    assert _as_bool("false") is False
    assert _as_bool("0") is False
    assert _as_bool("none") is False
    assert _as_bool("null") is False
    assert _as_bool("") is False
    assert _as_bool(None) is False


def test_format_repository_data_with_minimal_data():
    """Test _format_repository_data with minimal data."""
    data = {
        "full_name": "test/repo",
        "stars": 100,
    }

    result = _format_repository_data(data, "test", "repo")

    assert result["full_name"] == "test/repo"
    assert result["stars"] == 100


def test_format_repository_data_with_complete_data():
    """Test _format_repository_data with complete data."""
    data = {
        "full_name": "test/repo",
        "stars": 200,
        "forks": 75,
        "open_issues": 10,
        "license": {"spdx_id": "apache-2.0"},
        "updated_at": "2024-02-01T00:00:00Z",
        "description": "Test repository",
        "topics": ["ai", "ml"],
        "default_branch": "main",
    }

    result = _format_repository_data(data, "test", "repo")

    assert result["full_name"] == "test/repo"
    assert result["stars"] == 200
    assert result["forks"] == 75
    assert result["open_issues"] == 10
    assert result["license_name"] == "apache-2.0"
    assert result["updated"] == "2024-02-01T00:00:00Z"
    assert result["description"] == "Test repository"
    assert result["default_branch"] == "main"


def test_format_model_data_with_minimal_data():
    """Test _format_model_data with minimal data."""
    data = {
        "modelSize": 123,
        "license": "mit",
    }

    result = _format_model_data(data, "test-model")

    assert result["model_name"] == "test-model"
    assert result["model_size"] == 123


def test_format_model_data_with_complete_data():
    """Test _format_model_data with complete data."""
    data = {
        "modelSize": 123,
        "license": "mit",
        "author": "test",
        "downloads": 1000,
        "lastModified": "2024-01-01",
        "has_readme": True,
        "cardData": {"content": "# Model Card"},
        "description": "Test model",
        "tags": ["nlp", "text"],
    }

    result = _format_model_data(data, "test-model")

    assert result["model_name"] == "test-model"
    assert result["author"] == "test"
    assert result["description"] == "Test model"
    assert result["model_size"] == 123
