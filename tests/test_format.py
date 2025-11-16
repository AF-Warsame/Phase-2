from ai_model_catalog.utils import (
    _format_count_info,
    _format_model_data,
    _format_repository_data,
)


def test_format_repository_data():
    """Test _format_repository_data function."""
    test_data = {
        "full_name": "test/repo",
        "stargazers_count": 100,
        "forks_count": 50,
        "language": "Python",
        "pushed_at": "2023-01-01",
        "open_issues_count": 10,
        "size": 1000,
        "license": {"spdx_id": "MIT"},
        "description": "Test repo",
        "default_branch": "main",
        "readme": "Test readme content",
    }

    result = _format_repository_data(test_data, "test", "repo")

    assert result["full_name"] == "test/repo"
    assert result["stars"] == 100
    assert result["forks"] == 50
    assert result["language"] == "Python"
    assert result["license_name"] == "MIT"


def test_format_model_data():
    """Test _format_model_data function."""
    test_data = {
        "modelId": "test-model",
        "author": "test-author",
        "description": "Test model",
        "modelSize": 5000000,
        "downloads": 1000,
        "lastModified": "2023-01-01",
        "readme": "Test model readme",
        "license": {"spdx_id": "Apache-2.0"},
        "tags": ["nlp", "transformer"],
        "pipeline_tag": "text-classification",
    }

    result = _format_model_data(test_data, "test-model")

    assert result["model_name"] == "test-model"
    assert result["author"] == "test-author"
    assert result["model_size"] == 5000000
    assert result["license_name"] == "Apache-2.0"
    assert result["tags"] == ["nlp", "transformer"]


def test_format_count_info():
    """Test _format_count_info function."""
    data = {"commits_count": 100, "commits": ["commit1", "commit2"]}
    result = _format_count_info(data, "commits", "commits")
    assert "Total commits: 100" in result

    # Test with zero count
    data_zero = {"commits_count": 0, "commits": ["commit1", "commit2"]}
    result_zero = _format_count_info(data_zero, "commits", "commits")
    assert "Recent commits: 2" in result_zero
