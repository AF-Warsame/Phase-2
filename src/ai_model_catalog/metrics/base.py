from abc import ABC, abstractmethod


class Metric(ABC):
    @abstractmethod
    def score(self, model_data: dict) -> float:
        """Calculate normalized score [0, 1]"""
        pass
