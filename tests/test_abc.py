import pytest

from ai_model_catalog.metrics.base import Metric


def test_cannot_instantiate_abstract_metric():
    with pytest.raises(TypeError):
        _ = Metric()  # pylint: disable=abstract-class-instantiated
