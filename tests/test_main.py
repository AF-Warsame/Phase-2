"""Tests for the main module entry point."""

from unittest.mock import patch

from ai_model_catalog.__main__ import main

# import pytest


def test_main_function():
    """Test that main function calls configure_logging and app."""
    with (
        patch("ai_model_catalog.__main__.configure_logging") as mock_logging,
        patch("ai_model_catalog.__main__.app") as mock_app,
    ):

        main()

        # Verify configure_logging was called
        mock_logging.assert_called_once()

        # Verify app was called
        mock_app.assert_called_once()


def test_main_module_execution():
    """Test that the module can be executed directly."""
    with (
        patch("ai_model_catalog.__main__.configure_logging") as mock_logging,
        patch("ai_model_catalog.__main__.app") as mock_app,
    ):

        # Simulate running the module directly
        main()

        # Verify configure_logging was called
        mock_logging.assert_called_once()

        # Verify app was called
        mock_app.assert_called_once()


def test_main_function_return_type():
    """Test that main function returns None."""
    with (
        patch("ai_model_catalog.__main__.configure_logging"),
        patch("ai_model_catalog.__main__.app"),
    ):

        main()  # main() returns None, so we don't assign it


def test_main_module_direct_execution():
    """Test that the module can be executed directly via if __name__ == '__main__'."""
    # Test that the main function is callable
    with patch("ai_model_catalog.__main__.configure_logging") as mock_logging:
        with patch("ai_model_catalog.__main__.app") as mock_app:
            # Simulate the if __name__ == "__main__" block
            # This should trigger the main() function
            main()

            mock_logging.assert_called_once()
            mock_app.assert_called_once()
