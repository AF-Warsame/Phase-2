import logging
from unittest.mock import MagicMock, patch

from ai_model_catalog.fetch_repo import GitHubAPIError, RepositoryDataError
from ai_model_catalog.interactive import (
    _display_available_owners,
    _display_main_menu,
    _display_owner_repositories,
    _get_user_input,
    _handle_github_repository_interactive,
    _handle_huggingface_model_interactive,
    _should_continue,
    interactive_main,
)

# Suppress logging during tests
logging.getLogger("catalog").setLevel(logging.CRITICAL)


def test_display_main_menu(capsys):
    _display_main_menu()
    captured = capsys.readouterr()
    assert "Welcome" in captured.out
    assert "1. Browse GitHub repositories" in captured.out


def test_display_available_owners(capsys):
    _display_available_owners()
    captured = capsys.readouterr()
    assert "huggingface" in captured.out
    assert "5. microsoft" in captured.out


def test_display_owner_repositories_valid_owner(capsys):
    _display_owner_repositories(1)  # huggingface
    captured = capsys.readouterr()
    assert "Available repositories for huggingface" in captured.out
    assert "1. transformers" in captured.out


def test_display_owner_repositories_invalid_owner(capsys):
    _display_owner_repositories(10)
    captured = capsys.readouterr()
    assert "Invalid owner choice" in captured.out


def test_get_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    result = _get_user_input("Enter something", "default")
    assert result == "default"

    monkeypatch.setattr("builtins.input", lambda prompt: "userinput")
    result = _get_user_input("Enter something", "default")
    assert result == "userinput"


def test_should_continue_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "y")
    assert _should_continue() is True

    monkeypatch.setattr("builtins.input", lambda prompt: "yes")
    assert _should_continue() is True


def test_should_continue_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    assert _should_continue() is False

    monkeypatch.setattr("builtins.input", lambda prompt: "no")
    assert _should_continue() is False

    monkeypatch.setattr("builtins.input", lambda prompt: "random")
    assert _should_continue() is False


@patch("ai_model_catalog.interactive._should_continue")
@patch("ai_model_catalog.interactive._handle_huggingface_model_interactive")
@patch("ai_model_catalog.interactive._handle_github_repository_interactive")
def test_interactive_main_flows(
    mock_github, mock_hf, mock_continue, monkeypatch, capsys
):
    inputs = iter(["1", "2", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_continue.side_effect = [True, False]

    interactive_main()

    assert mock_github.call_count == 1
    assert mock_hf.call_count == 1
    captured = capsys.readouterr()
    assert "Goodbye" in captured.out


def test_interactive_main_invalid_choice(monkeypatch, capsys):
    inputs = iter(["bad", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    with patch("ai_model_catalog.interactive._should_continue") as mock_continue:
        mock_continue.return_value = False
        interactive_main()

    captured = capsys.readouterr()
    assert "Invalid choice" in captured.out
    assert "Goodbye" in captured.out


def test_interactive_main_keyboard_interrupt(monkeypatch, capsys):
    def raise_keyboard_interrupt(prompt):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", raise_keyboard_interrupt)
    interactive_main()
    captured = capsys.readouterr()
    assert "Goodbye" in captured.out


@patch("ai_model_catalog.interactive.RepositoryHandler")
def test_handle_github_repository_interactive_success(
    mock_repo_handler, monkeypatch, capsys
):
    inputs = iter(["1", "transformers"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    monkeypatch.setattr(
        "ai_model_catalog.interactive._pick_repo_for_owner", lambda o, r: r
    )

    mock_instance = MagicMock()
    mock_instance.fetch_data.return_value = {"dummy": "data"}
    mock_instance.format_data.return_value = {"formatted": "data"}
    mock_repo_handler.return_value = mock_instance

    _handle_github_repository_interactive()

    captured = capsys.readouterr()
    assert "GitHub Repository Browser" in captured.out
    assert "Fetching data for huggingface/transformers" in captured.out

    mock_instance.fetch_data.assert_called_once()
    mock_instance.display_data.assert_called_once()


@patch("ai_model_catalog.interactive.RepositoryHandler")
def test_handle_github_repository_interactive_error(
    mock_repo_handler, monkeypatch, capsys
):
    inputs = iter(["1", "transformers"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(
        "ai_model_catalog.interactive._pick_repo_for_owner", lambda o, r: r
    )

    mock_instance = MagicMock()
    mock_instance.fetch_data.side_effect = GitHubAPIError("API error")
    mock_repo_handler.return_value = mock_instance

    _handle_github_repository_interactive()

    captured = capsys.readouterr()
    assert "Error fetching or displaying repository data" in captured.out


@patch("ai_model_catalog.interactive.ModelHandler")
def test_handle_huggingface_model_interactive_success(
    mock_model_handler, monkeypatch, capsys
):
    inputs = iter(["bert-base-uncased"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_instance = MagicMock()
    mock_instance.fetch_data.return_value = {"dummy": "data"}
    mock_instance.format_data.return_value = {"formatted": "data"}
    mock_model_handler.return_value = mock_instance

    _handle_huggingface_model_interactive()

    captured = capsys.readouterr()
    assert "Hugging Face Model Search" in captured.out
    assert "Fetching data for model: bert-base-uncased" in captured.out

    mock_instance.fetch_data.assert_called_once()
    mock_instance.display_data.assert_called_once()


@patch("ai_model_catalog.interactive.ModelHandler")
def test_handle_huggingface_model_interactive_error(
    mock_model_handler, monkeypatch, capsys
):
    inputs = iter(["bert-base-uncased"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    mock_instance = MagicMock()
    mock_instance.fetch_data.side_effect = RepositoryDataError("Data error")
    mock_model_handler.return_value = mock_instance

    _handle_huggingface_model_interactive()

    captured = capsys.readouterr()
    assert "Error fetching or displaying model data" in captured.out
