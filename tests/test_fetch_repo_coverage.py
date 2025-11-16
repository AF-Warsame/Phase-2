"""Additional tests for fetch_repo.py to improve coverage."""

from unittest.mock import MagicMock, patch
import requests
from requests.exceptions import (
    RequestException,
    ConnectionError as RequestsConnectionError,
)
import pytest

from ai_model_catalog.fetch_repo import (
    time_request,
    _make_github_request,
    _extract_page_count_from_link_header,
    _get_total_count_from_link_header,
    _fetch_github_endpoint,
    _fetch_readme_content,
    _fetch_repository_counts,
    GitHubAPIError,
    RepositoryDataError,
    fetch_hf_model,
    fetch_repo_data,
)


class TestFetchRepoCoverage:
    """Test cases to improve coverage for fetch_repo.py."""

    def test_time_request_exception(self):
        """Test time_request when exception occurs."""

        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            time_request(failing_func)

    def test_make_github_request_403_error(self):
        """Test _make_github_request with 403 error."""
        with patch("ai_model_catalog.fetch_repo.create_session") as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_session.return_value.get.return_value = mock_response

            with pytest.raises(GitHubAPIError, match="rate limit exceeded"):
                _make_github_request("https://api.github.com/test")

    def test_make_github_request_connection_error(self):
        """Test _make_github_request with connection error."""
        with patch("ai_model_catalog.fetch_repo.create_session") as mock_session:
            mock_session_instance = MagicMock()
            mock_session_instance.get.side_effect = RequestsConnectionError(
                "Connection failed"
            )
            mock_session.return_value = mock_session_instance

            with pytest.raises(GitHubAPIError, match="Network connection failed"):
                _make_github_request("https://api.github.com/test")

    def test_make_github_request_request_exception(self):
        """Test _make_github_request with request exception."""
        with patch("ai_model_catalog.fetch_repo.create_session") as mock_session:
            mock_session_instance = MagicMock()
            mock_session_instance.get.side_effect = RequestException("Request failed")
            mock_session.return_value = mock_session_instance

            with pytest.raises(GitHubAPIError, match="Failed to fetch data"):
                _make_github_request("https://api.github.com/test")

    def test_extract_page_count_no_last_rel(self):
        """Test _extract_page_count_from_link_header with no last rel."""
        result = _extract_page_count_from_link_header('rel="first"')
        assert result == 0

    def test_extract_page_count_no_page_param(self):
        """Test _extract_page_count_from_link_header with no page param."""
        link_header = '<https://api.github.com/test>; rel="last"'
        result = _extract_page_count_from_link_header(link_header)
        assert result == 0

    def test_extract_page_count_no_page_matches(self):
        """Test _extract_page_count_from_link_header with no page matches."""
        link_header = '<https://api.github.com/test?other=1>; rel="last"'
        result = _extract_page_count_from_link_header(link_header)
        assert result == 0

    def test_get_total_count_from_link_header_no_link_header(self):
        """Test _get_total_count_from_link_header with no link header."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_response = MagicMock()
            mock_response.headers = {}
            mock_response.json.return_value = [{"id": 1}, {"id": 2}]
            mock_request.return_value = mock_response

            result = _get_total_count_from_link_header("https://api.github.com/test")
            assert result == 2

    def test_get_total_count_from_link_header_exception(self):
        """Test _get_total_count_from_link_header with exception."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_request.side_effect = Exception("Test error")

            with pytest.raises(RepositoryDataError, match="Failed to get count"):
                _get_total_count_from_link_header("https://api.github.com/test")

    def test_fetch_github_endpoint_exception(self):
        """Test _fetch_github_endpoint with exception."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_request.side_effect = Exception("Test error")

            with pytest.raises(RepositoryDataError, match="Failed to fetch endpoint"):
                _fetch_github_endpoint("https://api.github.com/test")

    def test_fetch_readme_content_no_download_url(self):
        """Test _fetch_readme_content with no download_url."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"name": "README.md"}
            mock_request.return_value = mock_response

            with pytest.raises(
                RepositoryDataError, match="README metadata missing download_url"
            ):
                _fetch_readme_content("owner", "repo")

    def test_fetch_readme_content_download_error(self):
        """Test _fetch_readme_content with download error."""
        with (
            patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request,
            patch("requests.get") as mock_get,
        ):
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "download_url": "https://example.com/readme.md"
            }
            mock_request.return_value = mock_response
            mock_get.side_effect = RequestException("Download failed")

            with pytest.raises(
                RepositoryDataError, match="Failed to download README content"
            ):
                _fetch_readme_content("owner", "repo")

    def test_fetch_readme_content_general_exception(self):
        """Test _fetch_readme_content with general exception."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_request.side_effect = Exception("Test error")

            with pytest.raises(RepositoryDataError, match="Failed to fetch README"):
                _fetch_readme_content("owner", "repo")

    def test_fetch_repository_counts_exception(self):
        """Test _fetch_repository_counts with RepositoryDataError."""
        with patch(
            "ai_model_catalog.fetch_repo._get_total_count_from_link_header"
        ) as mock_count:
            mock_count.side_effect = RepositoryDataError("Test error")

            result = _fetch_repository_counts("owner", "repo")
            # Should return counts with 0 for failed items
            assert result["commits_count"] == 0
            assert result["contributors_count"] == 0

    def test_fetch_hf_model_success(self):
        """Test fetch_hf_model success case."""
        with (
            patch("ai_model_catalog.fetch_repo.create_session") as mock_session,
            patch("ai_model_catalog.fetch_repo._calculate_model_size") as mock_size,
        ):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "author": "test",
                "downloads": 1000,
                "cardData": {"content": "Test content"},
                "license": "mit",
                "likes": 50,
                "lastModified": "2023-01-01",
                "tags": ["pytorch", "nlp"],
            }
            mock_session.return_value.get.return_value = mock_response
            mock_size.return_value = 1000

            result = fetch_hf_model("test/model")
            assert result["author"] == "test"
            assert result["downloads"] == 1000
            assert result["license"] == "mit"

    def test_fetch_hf_model_404_error(self):
        """Test fetch_hf_model with 404 error."""
        with patch("ai_model_catalog.fetch_repo.create_session") as mock_session:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                "404 Not Found"
            )
            mock_session.return_value.get.return_value = mock_response

            with pytest.raises(RepositoryDataError, match="Failed to fetch model data"):
                fetch_hf_model("test/model")

    def test_fetch_hf_model_request_exception(self):
        """Test fetch_hf_model with request exception."""
        with patch("ai_model_catalog.fetch_repo.create_session") as mock_session:
            mock_session.return_value.get.side_effect = RequestException(
                "Request failed"
            )

            with pytest.raises(RepositoryDataError, match="Failed to fetch model data"):
                fetch_hf_model("test/model")

    def test_fetch_repo_data_github_error(self):
        """Test fetch_repo_data with GitHub API error."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_request.side_effect = GitHubAPIError("API error")

            with pytest.raises(GitHubAPIError):
                fetch_repo_data("owner", "repo")

    def test_fetch_repo_data_repository_error(self):
        """Test fetch_repo_data with repository data error."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_request.side_effect = RepositoryDataError("Data error")

            with pytest.raises(RepositoryDataError):
                fetch_repo_data("owner", "repo")

    def test_fetch_repo_data_general_exception(self):
        """Test fetch_repo_data with general exception."""
        with patch("ai_model_catalog.fetch_repo._make_github_request") as mock_request:
            mock_request.side_effect = Exception("General error")

            with pytest.raises(Exception):
                fetch_repo_data("owner", "repo")
