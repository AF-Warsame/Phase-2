import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter
from typing import Iterable, List, TextIO

from .base import Metric
from .types import MetricResult

log = logging.getLogger(__name__)


def run_metrics(
    metrics: Iterable[Metric], ctx, max_workers: int = 4
) -> List[MetricResult]:
    """Run a set of Metric objects concurrently and return MetricResult rows."""
    max_workers = max(1, max_workers)
    results: List[MetricResult] = []

    def _run_one(m: Metric) -> MetricResult:
        t0 = perf_counter()
        name = m.__class__.__name__.replace("Metric", "").lower()
        try:
            s = float(m.score(ctx))
            s = max(0.0, min(1.0, s))  # clamp to [0, 1]
            res = MetricResult(
                name=name,
                score=s,
                passed=(s >= 0.5),
                details={},
                error=None,
                elapsed_s=perf_counter() - t0,
            )
            log.debug(
                "metric %s score=%.3f passed=%s elapsed=%.4fs",
                name,
                res.score,
                res.passed,
                res.elapsed_s,
            )
            return res

        except Exception as e:  # pylint: disable=broad-exception-caught
            res = MetricResult(
                name=name,
                score=0.0,
                passed=False,
                details={},
                error=str(e),
                elapsed_s=perf_counter() - t0,
            )
            # include traceback at LOG_LEVEL=2
            log.exception("metric %s crashed after %.4fs: %s", name, res.elapsed_s, e)
            return res

    log.debug(
        "run_metrics: starting %d metrics with max_workers=%d",
        len(list(metrics)) if hasattr(metrics, "__len__") else -1,
        max_workers,
    )

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(_run_one, m): m for m in metrics}
        for fut in as_completed(futs):
            results.append(fut.result())

    log.debug("run_metrics: finished %d results", len(results))
    return results


def print_ndjson(results: List[MetricResult], stream: TextIO) -> None:
    for r in results:
        line = {
            "name": r.name,
            "score": r.score,
            "passed": r.passed,
            "latency_ms": round(r.elapsed_s * 1000, 2),
            "error": r.error,
            **(dict(r.details) if r.details else {}),
        }
        stream.write(json.dumps(line) + "\n")
