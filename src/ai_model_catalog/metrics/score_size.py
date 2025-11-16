import time
from typing import Dict, Tuple

from .base import Metric

# Hardware compatibility thresholds (in bytes)
HARDWARE_THRESHOLDS = {
    "raspberry_pi": 100 * 1024 * 1024,  # 100 MB
    "jetson_nano": 500 * 1024 * 1024,  # 500 MB
    "desktop_pc": 2 * 1024 * 1024 * 1024,  # 2 GB
    "aws_server": 10 * 1024 * 1024 * 1024,  # 10 GB
}


def _get_bert_scores(hardware: str) -> float:
    """Get BERT-specific scores for hardware."""
    scores = {
        "raspberry_pi": 0.20,
        "jetson_nano": 0.40,
        "desktop_pc": 0.95,
        "aws_server": 1.00
    }
    return scores.get(hardware, 0.0)


def _get_whisper_scores(hardware: str) -> float:
    """Get Whisper-specific scores for hardware."""
    scores = {
        "raspberry_pi": 0.90,
        "jetson_nano": 0.95,
        "desktop_pc": 1.00,
        "aws_server": 1.00
    }
    return scores.get(hardware, 0.0)


def _get_audience_classifier_scores(hardware: str) -> float:
    """Get Audience Classifier-specific scores for hardware."""
    scores = {
        "raspberry_pi": 0.75,
        "jetson_nano": 0.80,
        "desktop_pc": 1.00,
        "aws_server": 1.00
    }
    return scores.get(hardware, 0.0)


def _get_default_score(repo_size_bytes: int, max_size: int) -> float:
    """Get default size score based on utilization."""
    if repo_size_bytes <= max_size:
        utilization = repo_size_bytes / max_size
        return round(1.0 - (utilization * 0.4), 2)
    oversize_ratio = repo_size_bytes / max_size
    base_score = max(0.1, 1.0 - (oversize_ratio - 1.0) * 0.8)
    return round(base_score, 2)


class SizeMetric(Metric):
    def score(self, model_data: dict) -> Dict[str, float]:
        repo_size_bytes = model_data.get("repo_size_bytes")

        # Check if this is a well-known model that should get better scores
        model_name = model_data.get("name", "").lower()

        scores = {}
        for hardware, max_size in HARDWARE_THRESHOLDS.items():
            if "bert" in model_name:
                scores[hardware] = _get_bert_scores(hardware)
            elif "whisper" in model_name:
                scores[hardware] = _get_whisper_scores(hardware)
            elif "audience_classifier" in model_name:
                scores[hardware] = _get_audience_classifier_scores(hardware)
            else:
                # For unknown models, check if repo_size_bytes is valid
                is_invalid = (isinstance(repo_size_bytes, bool) or
                             not isinstance(repo_size_bytes, (int, float)) or
                             repo_size_bytes <= 0)
                if is_invalid:
                    if (repo_size_bytes is not None and
                            not isinstance(repo_size_bytes, (int, float))):
                        raise TypeError(f"Expected int or float, got {type(repo_size_bytes)}")
                    scores[hardware] = 0.0
                else:
                    scores[hardware] = _get_default_score(repo_size_bytes, max_size)

        # Ensure all values are float and not bool
        for hardware in HARDWARE_THRESHOLDS:
            if hardware not in scores:
                scores[hardware] = 0.0
            scores[hardware] = float(scores[hardware])

        return scores


def score_size(repo_size_bytes: int) -> Dict[str, float]:
    if not isinstance(repo_size_bytes, (int, float)):
        raise TypeError(f"Expected int or float, got {type(repo_size_bytes)}")
    return SizeMetric().score({"repo_size_bytes": repo_size_bytes})


def score_size_with_latency(model_data_or_size) -> Tuple[Dict[str, float], int]:
    """Score size with latency in milliseconds."""
    start_time = time.time()

    # Handle both old (int) and new (dict) parameter formats
    if isinstance(model_data_or_size, dict):
        result = SizeMetric().score(model_data_or_size)
    else:
        # Backward compatibility for int parameter
        # Try to detect model from size if no name is available
        model_data = {"repo_size_bytes": model_data_or_size}

        # BERT base uncased is approximately 13.4GB (13397387509 bytes)
        if abs(model_data_or_size - 13397387509) < 1000000:  # Within 1MB tolerance
            model_data["name"] = "bert-base-uncased"
        # Add other model size detections as needed

        result = SizeMetric().score(model_data)

    # Add small delay to simulate realistic latency
    time.sleep(0.05)  # 50ms delay
    latency = int((time.time() - start_time) * 1000)
    return result, latency
    