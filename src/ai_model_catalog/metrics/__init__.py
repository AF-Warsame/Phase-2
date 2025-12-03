from .base import Metric
from .score_available_dataset_and_code import AvailableDatasetAndCodeMetric
from .score_bus_factor import BusFactorMetric
from . import score_code_quality as _score_code_quality_module
from . import score_dataset_quality as _score_dataset_quality_module
from .score_license import LicenseMetric, score_license
from .score_performance_claims import PerformanceClaimsMetric
from .score_ramp_up_time import score_ramp_up_time
from .score_size import SizeMetric


class _ModuleFunctionProxy:
    """Expose a module-like object that is also callable."""

    def __init__(self, module, func_name: str):
        self._module = module
        self._func = getattr(module, func_name)

    def __getattr__(self, name):
        return getattr(self._module, name)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


# Preserve backwards-compatible callable exports while keeping module attributes accessible
score_code_quality = _ModuleFunctionProxy(
    _score_code_quality_module, "score_code_quality"
)
score_dataset_quality = _ModuleFunctionProxy(
    _score_dataset_quality_module, "score_dataset_quality"
)

# Use traditional metric functions that now have built-in LLM fallback
score_size = SizeMetric().score
# score_ramp_up_time is already imported above
score_bus_factor = BusFactorMetric().score
score_available_dataset_and_code = AvailableDatasetAndCodeMetric().score
score_performance_claims = PerformanceClaimsMetric().score

__all__ = [
    "score_size",
    "score_license",
    "score_ramp_up_time",
    "score_bus_factor",
    "score_available_dataset_and_code",
    "score_dataset_quality",
    "score_code_quality",
    "score_performance_claims",
]
