from typer.testing import CliRunner

from ai_model_catalog.utils import (
    _display_model_info,
    _display_repository_info,
    _display_scores,
    _extract_license_name,
    _format_count_info,
    _format_model_data,
    _format_repository_data,
    _get_repository_counts_info,
    _pick_repo_for_owner,
)

runner = CliRunner()

REPO_SAMPLE = {
    "full_name": "test_owner/test_repo",
    "stargazers_count": 42,
    "forks_count": 10,
    "language": "Python",
    "pushed_at": "2023-01-01T00:00:00Z",
    "open_issues_count": 5,
    "size": 123,
    "license": {"spdx_id": "MIT"},
    "description": "Test repository",
    "default_branch": "main",
    "readme": "# Sample README",
    "commits_count": 100,
    "contributors_count": 5,
    "issues_count": 12,
    "pulls_count": 3,
    "actions_count": 4,
    "commits": [{}] * 3,
    "contributors": [{}] * 2,
    "issues": [{}] * 3,
    "pulls": [{}] * 2,
    "actions": [{}] * 4,
}

MODEL_SAMPLE = {
    "modelId": "test-model",
    "author": "tester",
    "description": "A test model",
    "modelSize": 1024,
    "downloads": 1000,
    "lastModified": "2023-01-01T00:00:00Z",
    "readme": "This is a README",
    "license": {"spdx_id": "apache-2.0"},
    "tags": ["nlp", "transformer"],
    "pipeline_tag": "text-classification",
}


def test_extract_license_name_dict():
    assert _extract_license_name({"spdx_id": "MIT"}) == "MIT"


def test_extract_license_name_str():
    assert _extract_license_name("BSD-3-Clause") == "BSD-3-Clause"


def test_extract_license_name_none():
    assert _extract_license_name(None) == "None"


def test_format_repository_data():
    result = _format_repository_data(REPO_SAMPLE, "test_owner", "test_repo")
    assert result["full_name"] == "test_owner/test_repo"
    assert result["stars"] == 42
    assert result["language"] == "Python"
    assert result["license_name"] == "MIT"


def test_format_model_data():
    result = _format_model_data(MODEL_SAMPLE, "test-model")
    assert result["model_name"] == "test-model"
    assert result["author"] == "tester"
    assert result["license_name"] == "apache-2.0"


def test_format_count_info_with_total_count():
    data = {"commits_count": 100, "commits": [{}] * 5}
    result = _format_count_info(data, "commits", "commits")
    assert "Total commits" in result


def test_format_count_info_with_sample_only():
    data = {"commits": [{}] * 3}
    result = _format_count_info(data, "commits", "commits")
    assert "Recent commits" in result


def test_get_repository_counts_info():
    counts = _get_repository_counts_info(REPO_SAMPLE)
    assert "commits" in counts
    assert "contributors" in counts


def test_display_repository_info(capsys):
    formatted = _format_repository_data(REPO_SAMPLE, "test_owner", "test_repo")
    counts = _get_repository_counts_info(REPO_SAMPLE)
    _display_repository_info(formatted, counts)
    out = capsys.readouterr().out
    assert "Repo: test_owner/test_repo" in out
    assert "Stars: 42" in out


def test_display_model_info(capsys):
    formatted = _format_model_data(MODEL_SAMPLE, "test-model")
    _display_model_info(formatted)
    out = capsys.readouterr().out
    assert "Model: test-model" in out
    assert "Downloads: 1,000" in out


def test_pick_repo_for_owner_by_index():
    repo = _pick_repo_for_owner("huggingface", "1")
    assert repo == "transformers"


def test_pick_repo_for_owner_by_name():
    repo = _pick_repo_for_owner("openai", "whisper")
    assert repo == "whisper"


def test_pick_repo_for_owner_invalid_input():
    repo = _pick_repo_for_owner("microsoft", "invalid-repo")
    assert repo == "transformers"  # fallback


def test_display_scores_mocked_net_score(monkeypatch, capsys):
    def mock_score(_data):
        return {
            "license": 1.0,
            "size": 0.85,  # Changed from dict to float
            "bus_factor": 0.5,
        }

    monkeypatch.setattr("ai_model_catalog.utils.net_score", mock_score)

    _display_scores(REPO_SAMPLE)
    captured = capsys.readouterr()
    assert "NetScore Breakdown" in captured.out
    assert "license: 1.000" in captured.out
    assert "size: 0.850" in captured.out
