from unittest.mock import patch

from ai_model_catalog.interactive import (
    _display_available_owners,
    _display_owner_repositories,
)


def test_display_available_owners():
    """Test that _display_available_owners displays the correct owners."""
    with patch("builtins.print") as mock_print:
        _display_available_owners()

        calls = mock_print.call_args_list
        assert any("huggingface" in str(call) for call in calls)
        assert any("openai" in str(call) for call in calls)
        assert any("facebookresearch" in str(call) for call in calls)
        assert any("google-research" in str(call) for call in calls)
        assert any("microsoft" in str(call) for call in calls)


def test_display_owner_repositories_valid_input():
    """Test _display_owner_repositories with valid input (1-5)."""
    with patch("builtins.print") as mock_print:
        _display_owner_repositories(1)  # huggingface

        calls = mock_print.call_args_list
        assert any("huggingface" in str(call) for call in calls)
        assert any("transformers" in str(call) for call in calls)
        assert any("diffusers" in str(call) for call in calls)


def test_display_owner_repositories_invalid_input():
    """Test _display_owner_repositories with invalid input."""
    with patch("builtins.print") as mock_print:
        _display_owner_repositories(6)  # Invalid choice

        calls = mock_print.call_args_list
        assert any("Invalid owner choice" in str(call) for call in calls)
        assert any(
            "Please select a number between 1 and 5" in str(call) for call in calls
        )


def test_display_owner_repositories_edge_cases():
    """Test _display_owner_repositories with edge case inputs."""
    with patch("builtins.print") as mock_print:
        # Test choice 5 (microsoft)
        _display_owner_repositories(5)
        calls = mock_print.call_args_list
        assert any("microsoft" in str(call) for call in calls)
        assert any("DeepSpeed" in str(call) for call in calls)
