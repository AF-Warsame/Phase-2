"""Base class for LLM-enhanced metrics."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..llm_service import get_llm_service


class LLMEnhancedMetric(ABC):
    """Abstract base class for LLM-enhanced metrics."""

    def __init__(self):
        """Initialize the LLM-enhanced metric."""
        self.llm_service = get_llm_service()

    @abstractmethod
    def score_with_llm(self, data: Dict[str, Any]) -> float:
        """Score using LLM analysis."""
        pass

    @abstractmethod
    def score_without_llm(self, data: Dict[str, Any]) -> float:
        """Score using traditional methods (fallback)."""
        pass

    def score(self, data: Dict[str, Any]) -> float:
        """Score with LLM enhancement and fallback."""
        try:
            llm_score = self.score_with_llm(data)
            if llm_score is not None:
                return llm_score
        except (ValueError, TypeError, AttributeError, KeyError):
            pass  # Fall back to traditional method

        return self.score_without_llm(data)
