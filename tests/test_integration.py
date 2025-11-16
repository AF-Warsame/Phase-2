import pytest

from ai_model_catalog.fetch_repo import GitHubAPIError, fetch_hf_model, fetch_repo_data


def test_fetch_repo_data_integration():
    try:
        data = fetch_repo_data("huggingface", "transformers")
    except GitHubAPIError as e:
        if "rate limit exceeded" in str(e).lower():
            pytest.skip("GitHub API rate limit exceeded - skipping integration test")
        raise

    # Basic repo metadata
    assert data["full_name"] == "huggingface/transformers"
    assert isinstance(data["size"], int) and data["size"] > 0
    assert isinstance(data["license"], dict)
    assert "spdx_id" in data["license"]

    # Stars, forks, issues, updated_at
    assert isinstance(data["stars"], int)
    assert data["stars"] > 0
    assert isinstance(data["forks"], int)
    assert isinstance(data["open_issues"], int)
    assert isinstance(data["updated_at"], str)

    # README content
    assert isinstance(data["readme"], str)
    assert len(data["readme"]) > 100  # at least some text

    # Commits and contributors
    assert isinstance(data["commits"], list)
    assert len(data["commits"]) > 0
    assert "sha" in data["commits"][0] or "commit" in data["commits"][0]

    assert isinstance(data["contributors"], list)
    assert len(data["contributors"]) > 0
    assert "login" in data["contributors"][0]

    # Issues
    assert isinstance(data["issues"], list)

    # Pull requests
    assert isinstance(data["pulls"], list)

    # Actions runs
    assert isinstance(data["actions"], list)
    if data["actions"]:  # only check if there are runs
        run = data["actions"][0]
        assert "id" in run
        assert "status" in run
        assert "conclusion" in run


def test_fetch_hf_model_integration():
    data = fetch_hf_model("bert-base-uncased")

    # Hugging Face metadata
    assert isinstance(data["modelSize"], int)
    assert data["modelSize"] > 0

    assert isinstance(data["license"], str)
    assert len(data["license"]) > 0

    assert isinstance(data["author"], str)

    assert isinstance(data["readme"], str)
    assert len(data["readme"]) > 50

    assert isinstance(data["downloads"], int)

    assert isinstance(data["lastModified"], str)
