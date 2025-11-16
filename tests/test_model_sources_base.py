"""Tests for the base model sources module."""

from abc import ABC

from ai_model_catalog.model_sources.base import BaseHandler

# import pytest


class ConcreteHandler(BaseHandler):
    """Concrete implementation for testing."""

    def fetch_data(self):
        return {"test": "data"}

    def format_data(self, data):
        return {"formatted": data}

    def display_data(self, formatted_data, raw_data):
        print(f"Displaying: {formatted_data}")


def test_base_handler_is_abstract():
    """Test that BaseHandler is abstract and cannot be instantiated."""
    # Test that BaseHandler is abstract by checking its ABC status
    assert BaseHandler.__abstractmethods__ != set()
    assert hasattr(BaseHandler, "__abstractmethods__")


def test_concrete_handler_can_be_instantiated():
    """Test that concrete implementations can be instantiated."""
    handler = ConcreteHandler()
    assert isinstance(handler, BaseHandler)
    assert isinstance(handler, ABC)


def test_concrete_handler_methods():
    """Test that concrete handler methods work correctly."""
    handler = ConcreteHandler()

    # Test fetch_data
    data = handler.fetch_data()
    assert data == {"test": "data"}

    # Test format_data
    formatted = handler.format_data(data)
    assert formatted == {"formatted": {"test": "data"}}

    # Test display_data (should not raise exception)
    handler.display_data(formatted, data)


def test_base_handler_abstract_methods():
    """Test that BaseHandler has the required abstract methods."""
    # Check that the abstract methods exist
    assert hasattr(BaseHandler, "fetch_data")
    assert hasattr(BaseHandler, "format_data")
    assert hasattr(BaseHandler, "display_data")

    # Check that they are abstract
    assert getattr(BaseHandler.fetch_data, "__isabstractmethod__", False)
    assert getattr(BaseHandler.format_data, "__isabstractmethod__", False)
    assert getattr(BaseHandler.display_data, "__isabstractmethod__", False)
