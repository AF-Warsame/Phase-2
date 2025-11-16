from unittest.mock import MagicMock, patch

from ai_model_catalog.fetch_repo import fetch_hf_model


def fake_response(json_data, status=200, text_data=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status
    mock_resp.json.return_value = json_data
    mock_resp.text = text_data or ""
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@patch("ai_model_catalog.fetch_repo.create_session")
def test_fetch_hf_model(mock_create_session):
    mock_session = MagicMock()
    mock_create_session.return_value = mock_session
    mock_get = mock_session.get
    model_json = {
        "usedStorage": 54321,
        "license": "apache-2.0",
        "author": "huggingface",
        "cardData": {"content": "This is the model card"},
        "downloads": 9999,
        "lastModified": "2025-08-15T12:34:56Z",
    }
    mock_get.return_value = fake_response(model_json)

    data = fetch_hf_model("bert-base-uncased")

    assert data["modelSize"] == 54321
    assert data["license"] == "apache-2.0"
    assert data["author"] == "huggingface"
    assert "model card" in data["readme"]
    assert data["downloads"] == 9999
    assert data["lastModified"].startswith("2025-08-15")
