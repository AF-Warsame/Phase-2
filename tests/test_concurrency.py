import time
from unittest.mock import Mock

from ai_model_catalog.metrics.runner import run_metrics


def make_metric(score_value, sleep_time=0):
    m = Mock()

    def score(ctx):  # accept ctx argument
        mult = float(ctx.get("mult", 1.0))
        if sleep_time > 0:
            time.sleep(sleep_time)
        return score_value * mult

    m.score = score
    m.__class__.__name__ = "MockMetric"
    return m


def test_run_metrics_with_single_worker_runs_serially():
    metrics = [make_metric(0.5, 0.2), make_metric(0.5, 0.2)]
    start = time.perf_counter()
    run_metrics(metrics, ctx={"mult": 1.0}, max_workers=1)
    duration = time.perf_counter() - start
    assert duration >= 0.4


def test_run_metrics_with_multiple_workers_runs_concurrently():
    metrics = [make_metric(0.5, 0.2), make_metric(0.5, 0.2)]
    start = time.perf_counter()
    run_metrics(metrics, ctx={"mult": 1.0}, max_workers=2)
    duration = time.perf_counter() - start
    assert duration < 0.4


def test_run_metrics_max_workers_minimum_one():
    metric = make_metric(0.7)
    results = run_metrics([metric], ctx={"mult": 1.0}, max_workers=0)
    assert len(results) == 1
    assert results[0].score == 0.7
