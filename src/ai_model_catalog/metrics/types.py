from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class MetricResult:
    name: str
    score: float
    passed: bool
    details: Mapping[str, Any]
    error: Optional[str]
    elapsed_s: float
    