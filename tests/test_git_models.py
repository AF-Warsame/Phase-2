from unittest.mock import MagicMock, patch

from ai_model_catalog.fetch_repo import (
    SAMPLE_ACTION_RUN,
    fetch_repo_data,
)


# --- Helpers ---
def fake_response(json_data, status=200, text_data=None, headers=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status
    mock_resp.json.return_value = json_data
    mock_resp.text = text_data or ""
    mock_resp.headers = headers or {}
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@patch("ai_model_catalog.fetch_repo.create_session")
@patch("requests.get")
def test_fetch_repo_data(mock_requests_get, mock_create_session):
    mock_session = MagicMock()
    mock_create_session.return_value = mock_session
    mock_get = mock_session.get
    repo_json = {
        "full_name": "huggingface/transformers",
        "size": 12345,
        "license": {"spdx_id": "Apache-2.0"},
        "owner": {"login": "huggingface"},
        "stargazers_count": 1337,
        "forks_count": 42,
        "open_issues_count": 7,
        "updated_at": "2025-09-16T00:00:00Z",
    }
    readme_json = {"download_url": "https://fakeurl/readme.md"}
    readme_text = "# Transformers README"
    commits_json = [{"sha": "abc123", "commit": {"message": "Test commit"}}]
    contributors_json = [{"login": "user1", "contributions": 100}]
    issues_json = [{"number": 1, "title": "Test issue"}]
    pulls_json = [{"number": 1, "title": "Test PR"}]
    actions_json = {"workflow_runs": [SAMPLE_ACTION_RUN]}

    mock_get.side_effect = [
        fake_response(repo_json),  # repo
        fake_response(readme_json, status=200),  # readme meta
        fake_response(
            commits_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/huggingface/transformers/"
                    'commits?per_page=1&page=100>; rel="last"'
                )
            },
        ),  # commits count
        fake_response(
            contributors_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/huggingface/transformers/"
                    'contributors?per_page=1&page=50>; rel="last"'
                )
            },
        ),  # contributors count
        fake_response(
            issues_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/huggingface/transformers/"
                    'issues?per_page=1&page=25>; rel="last"'
                )
            },
        ),  # issues count
        fake_response(
            pulls_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/huggingface/transformers/"
                    'pulls?per_page=1&page=75>; rel="last"'
                )
            },
        ),  # pulls count
        fake_response(
            actions_json,
            headers={
                "Link": (
                    "<https://api.github.com/repos/huggingface/transformers/"
                    'actions/runs?per_page=1&page=200>; rel="last"'
                )
            },
        ),  # actions count
        fake_response(commits_json),  # commits sample
        fake_response(contributors_json),  # contributors sample
        fake_response(issues_json),  # issues sample
        fake_response(pulls_json),  # pulls sample
        fake_response(actions_json),  # actions sample
    ]

    # Mock the direct requests.get call for README download
    mock_requests_get.return_value = fake_response(text_data=readme_text, json_data={})

    data = fetch_repo_data("huggingface", "transformers")

    assert data["full_name"] == "huggingface/transformers"
    assert data["license"]["spdx_id"] == "Apache-2.0"
    assert data["stars"] == 1337
    assert data["forks"] == 42
    assert data["open_issues"] == 7
    assert "Transformers README" in data["readme"]
    assert data["actions"][0]["conclusion"] == "success"
    assert data["commits_count"] == 100
    assert data["contributors_count"] == 50
    assert data["issues_count"] == 25
    assert data["pulls_count"] == 75
    assert data["actions_count"] == 200
