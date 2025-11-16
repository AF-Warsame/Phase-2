import abc
from typing import Any, Dict


class BaseHandler(abc.ABC):
    """Abstract base class for all handlers."""

    @abc.abstractmethod
    def fetch_data(self) -> Dict[str, Any]:
        """Fetch data from source."""
        pass

    @abc.abstractmethod
    def format_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw data for display."""
        pass

    @abc.abstractmethod
    def display_data(
        self, formatted_data: Dict[str, Any], raw_data: Dict[str, Any]
    ) -> None:
        """Display formatted data to the user."""
        pass
