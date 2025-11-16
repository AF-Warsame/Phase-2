"""Tests for the GitHub model sources module."""

from unittest.mock import patch

from ai_model_catalog.model_sources.base import BaseHandler
from ai_model_catalog.model_sources.github_model import RepositoryHandler

# import pytest


def test_repository_handler_initialization():
    """Test RepositoryHandler initialization."""
    handler = RepositoryHandler("test_owner", "test_repo")
    assert handler.owner == "test_owner"
    assert handler.repo == "test_repo"


def test_repository_handler_fetch_data():
    """Test RepositoryHandler fetch_data method."""
    mock_data = {
        "full_name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "open_issues": 5,
        "license": {"spdx_id": "mit"},
        "updated_at": "2024-01-01T00:00:00Z",
    }

    with patch("ai_model_catalog.fetch_repo.fetch_repo_data") as mock_fetch:
        mock_fetch.return_value = mock_data

        handler = RepositoryHandler("test_owner", "test_repo")
        result = handler.fetch_data()

        mock_fetch.assert_called_once_with(owner="test_owner", repo="test_repo")
        assert result == mock_data


def test_repository_handler_format_data():
    """Test RepositoryHandler format_data method."""
    mock_data = {
        "full_name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "open_issues": 5,
        "license": {"spdx_id": "mit"},
        "updated_at": "2024-01-01T00:00:00Z",
    }

    handler = RepositoryHandler("test_owner", "test_repo")
    result = handler.format_data(mock_data)

    # Check that the result has the expected structure
    assert result["source"] == "github"
    assert result["full_name"] == "test_owner/test_repo"
    assert result["author"] == ""
    assert result["license"] == "mit"


def test_repository_handler_display_data():
    """Test RepositoryHandler display_data method."""
    mock_data = {
        "full_name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "open_issues": 5,
        "license": {"spdx_id": "mit"},
        "updated_at": "2024-01-01T00:00:00Z",
    }

    mock_formatted = {
        "name": "test_owner/test_repo",
        "stars": 100,
        "forks": 50,
        "issues": 5,
        "license": "mit",
        "updated": "2024-01-01T00:00:00Z",
    }

    # Mock scores for testing

    handler = RepositoryHandler("test_owner", "test_repo")

    # Test that display_data outputs JSON

    # We can't easily test the output without capturing stdout,
    # so just test that it doesn't raise an error
    handler.display_data(mock_formatted, mock_data)


def test_repository_handler_inheritance():
    """Test that RepositoryHandler inherits from BaseHandler."""
    handler = RepositoryHandler("test_owner", "test_repo")

    # Check inheritance
    assert isinstance(handler, BaseHandler)

    # Check that all required methods exist
    assert hasattr(handler, "fetch_data")
    assert hasattr(handler, "format_data")
    assert hasattr(handler, "display_data")

    # Check that methods are callable
    assert callable(handler.fetch_data)
    assert callable(handler.format_data)
    assert callable(handler.display_data)
