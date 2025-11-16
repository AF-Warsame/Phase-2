import logging
from typing import Dict

from .fetch_repo import fetch_dataset_data, fetch_model_data, fetch_repo_data

# Import *_with_latency versions
from .metrics.score_available_dataset_and_code import score_available_dataset_and_code_with_latency
from .metrics.score_bus_factor import score_bus_factor_with_latency
from .metrics.score_code_quality import score_code_quality_with_latency
from .metrics.score_dataset_quality import score_dataset_quality_with_latency
from .metrics.score_license import score_license_with_latency
from .metrics.score_performance_claims import score_performance_claims_with_latency
from .metrics.score_ramp_up_time import score_ramp_up_time_with_latency
from .metrics.score_size import score_size_with_latency
# ✅ New import for local repo analysis
from .analyze_local_repo import analyze_hf_repo

log = logging.getLogger(__name__)


def _ensure_size_score_structure(size_scores):
    if not isinstance(size_scores, dict):
        size_scores = {
            "raspberry_pi": 0.0,
            "jetson_nano": 0.0,
            "desktop_pc": 0.0,
            "aws_server": 0.0,
        }
    for hardware in ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]:
        if hardware not in size_scores:
            size_scores[hardware] = 0.0
        size_scores[hardware] = float(size_scores[hardware])
    return size_scores


def net_score(api_data: Dict, model_id: str = None) -> Dict[str, float]:
    log.debug("net_score: input keys=%s", list(api_data.keys()))

    repo_size_bytes = (
        api_data.get("size", 0) * 1024
        if "full_name" in api_data
        else api_data.get("modelSize", 0)
    )
    license_type = (
        api_data.get("license", {}).get("spdx_id")
        if isinstance(api_data.get("license"), dict)
        else api_data.get("license")
    )
    readme = api_data.get("readme", "") or api_data.get("cardData", {}).get("content", "")
    maintainers = (
        [api_data.get("owner", {}).get("login")]
        if "owner" in api_data
        else [api_data.get("author")]
    )

    model_data = {
        "repo_size_bytes": repo_size_bytes,
        "license": license_type,
        "readme": readme,
        "maintainers": maintainers,
        "has_code": api_data.get("has_code", True),
        "has_dataset": api_data.get("has_dataset", True),
        "model_id": model_id,
        "downloads": api_data.get("downloads", 0),
        "author": api_data.get("author", ""),
        "modelSize": api_data.get("modelSize", 0),
    }

    # Add model name for performance claims scoring
    if model_id:
        # Extract model name from model_id
        model_data["name"] = model_id.split("/")[-1]
    elif "full_name" in api_data:
        model_data["name"] = api_data["full_name"]

    # Score each metric with latency
    size_scores, size_latency = score_size_with_latency(model_data)
    size_scores = _ensure_size_score_structure(size_scores)

    license_score, license_latency = score_license_with_latency(model_data)
    ramp_up_score, ramp_up_latency = score_ramp_up_time_with_latency(model_data)
    bus_factor_score, bus_factor_latency = score_bus_factor_with_latency(model_data)
    availability_score, availability_latency = score_available_dataset_and_code_with_latency(
        model_data
    )
    # Add model name to api_data for dataset quality scoring
    api_data_with_name = api_data.copy()
    if "full_name" in api_data:
        api_data_with_name["name"] = api_data["full_name"]
    elif model_id:  # This is a Hugging Face model
        # Extract model name from model_id
        api_data_with_name["name"] = model_id.split("/")[-1]
    
    # Add model_id to api_data for model-specific scoring
    api_data_with_name["model_id"] = model_id

    dataset_quality_score, dataset_quality_latency = (
        score_dataset_quality_with_latency(api_data_with_name))
    code_quality_score, code_quality_latency = (
        score_code_quality_with_latency(api_data_with_name))
    performance_claims_score, performance_claims_latency = (
        score_performance_claims_with_latency(model_data))

    # Weighted size score
    hardware_weights = {
        "raspberry_pi": 0.1,
        "jetson_nano": 0.2,
        "desktop_pc": 0.3,
        "aws_server": 0.4,
    }
    size_score_avg = sum(size_scores[hw] * weight for hw, weight in hardware_weights.items())

    # Final scores
    scores = {
        "size": size_scores,
        "size_score": size_scores,  # This will be the dictionary for output
        "size_score_latency": size_latency,

        "license": license_score,
        "license_latency": license_latency,

        "ramp_up_time": ramp_up_score,
        "ramp_up_time_latency": ramp_up_latency,

        "bus_factor": bus_factor_score,
        "bus_factor_latency": bus_factor_latency,

        "availability": availability_score,
        "availability_latency": availability_latency,
        "dataset_and_code_score": availability_score,
        "dataset_and_code_score_latency": availability_latency,

        "dataset_quality": dataset_quality_score,
        "dataset_quality_latency": dataset_quality_latency,

        "code_quality": code_quality_score,
        "code_quality_latency": code_quality_latency,

        "performance_claims": performance_claims_score,
        "performance_claims_latency": performance_claims_latency,
    }

    # NetScore weighting
    weights = {
        "size_score": 0.1,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "dataset_and_code_score": 0.1,
        "dataset_quality": 0.1,
        "code_quality": 0.15,
        "performance_claims": 0.15,
    }

    # Calculate net score using the average size score
    netscore = (size_score_avg * weights["size_score"] + 
                license_score * weights["license"] +
                ramp_up_score * weights["ramp_up_time"] +
                bus_factor_score * weights["bus_factor"] +
                availability_score * weights["dataset_and_code_score"] +
                dataset_quality_score * weights["dataset_quality"] +
                code_quality_score * weights["code_quality"] +
                performance_claims_score * weights["performance_claims"])
    scores["net_score"] = round(netscore, 3)
    scores["net_score_latency"] = (
        size_latency + license_latency + ramp_up_latency + bus_factor_latency +
        availability_latency + dataset_quality_latency + code_quality_latency +
        performance_claims_latency
    )

    log.debug("component scores=%s", scores)
    log.info("NetScore=%s", scores["net_score"])
    return scores


def score_model_from_id(model_id: str) -> Dict[str, float]:
    api_data = fetch_model_data(model_id)
    local_data = analyze_hf_repo(model_id)

    # Apply local-only analysis:
    contributor_count = local_data.get("contributor_count", 1)
    readme_exists = local_data.get("files_present", {}).get("README.md", True)

    # Patch the API data with local repo insights
    api_data["readme"] = api_data.get("readme") if readme_exists else ""
    api_data["cardData"] = api_data.get("cardData") or {}
    api_data["cardData"]["content"] = api_data["cardData"].get("content") if readme_exists else ""
    api_data["owner"] = {"login": f"local_user_{i}"} if (i := contributor_count) else {"login": "unknown"}
    
    # Add model name for scoring functions to access
    model_name = model_id.split("/")[-1]
    api_data["name"] = model_name
    api_data["modelId"] = model_id

    # Calculate all scores
    scores = net_score(api_data, model_id)
    
    # Use the actual scoring functions from score_* files
    # The scores from net_score() should be within expected ranges

    def safe_score(val):
        try:
            return min(max(float(val), 0.0), 1.0)
        except (ValueError, TypeError):
            return 0.0

    def safe_latency(val):
        try:
            return max(int(float(val)), 0)
        except (ValueError, TypeError):
            return 0

    def safe_size(val):
        try:
            if isinstance(val, dict):
                return {k: min(max(float(v), 0.0), 1.0) for k, v in val.items()}
            return min(max(float(val), 0.0), 1.0)
        except (ValueError, TypeError):
            return {"raspberry_pi": 0.0, "jetson_nano": 0.0, "desktop_pc": 0.0, "aws_server": 0.0}

    return {
        "net_score": safe_score(scores.get("net_score", 0.0)),
        "net_score_latency": safe_latency(scores.get("net_score_latency", 0)),
        "ramp_up_time": safe_score(scores.get("ramp_up_time", 0.0)),
        "ramp_up_time_latency": safe_latency(scores.get("ramp_up_time_latency", 0)),
        "bus_factor": safe_score(scores.get("bus_factor", 0.0)),
        "bus_factor_latency": safe_latency(scores.get("bus_factor_latency", 0)),
        "performance_claims": safe_score(scores.get("performance_claims", 0.0)),
        "performance_claims_latency": safe_latency(scores.get("performance_claims_latency", 0)),
        "license": safe_score(scores.get("license", 0.0)),
        "license_latency": safe_latency(scores.get("license_latency", 0)),
        "size_score": safe_size(scores.get("size_score", {})),
        "size_score_latency": safe_latency(scores.get("size_score_latency", 0)),
        "dataset_and_code_score": safe_score(scores.get("dataset_and_code_score", 0.0)),
        "dataset_and_code_score_latency": safe_latency(scores.get("dataset_and_code_score_latency", 0)),
        "dataset_quality": safe_score(scores.get("dataset_quality", 0.0)),
        "dataset_quality_latency": safe_latency(scores.get("dataset_quality_latency", 0)),
        "code_quality": safe_score(scores.get("code_quality", 0.0)),
        "code_quality_latency": safe_latency(scores.get("code_quality_latency", 0)),
    }




def score_repo_from_owner_and_repo(owner: str, repo: str) -> Dict[str, float]:
    log.info("Scoring repository %s/%s", owner, repo)
    api_data = fetch_repo_data(owner=owner, repo=repo)
    return net_score(api_data, f"{owner}/{repo}")


def score_dataset_from_id(dataset_id: str) -> Dict[str, float]:
    api_data = fetch_dataset_data(dataset_id)
    model_data = {
        "repo_size_bytes": 0,
        "license": api_data.get("license"),
        "readme": api_data.get("readme", ""),
        "maintainers": [api_data.get("author")],
        "has_code": False,
        "has_dataset": True,
    }

    size_scores = {
        "raspberry_pi": 0.5,
        "jetson_nano": 0.5,
        "desktop_pc": 0.5,
        "aws_server": 0.5,
    }

    size_score_avg = 0.5
    size_latency = 0  # Default latency for static dataset scores

    license_score, license_latency = score_license_with_latency(model_data)
    ramp_up_score, ramp_up_latency = score_ramp_up_time_with_latency(model_data["readme"])
    bus_factor_score, bus_factor_latency = score_bus_factor_with_latency(model_data["maintainers"])
    availability_score, availability_latency = score_available_dataset_and_code_with_latency(
        model_data["has_code"], model_data["has_dataset"]
    )
    dataset_quality_score, dataset_quality_latency = (
        score_dataset_quality_with_latency(api_data))
    performance_claims_score, performance_claims_latency = (
        score_performance_claims_with_latency(model_data))

    scores = {
        "size": size_scores,
        "size_score": size_scores,  # Use the dictionary, not the average
        "size_score_latency": size_latency,

        "license": license_score,
        "license_latency": license_latency,

        "ramp_up_time": ramp_up_score,
        "ramp_up_time_latency": ramp_up_latency,

        "bus_factor": bus_factor_score,
        "bus_factor_latency": bus_factor_latency,

        "availability": availability_score,
        "availability_latency": availability_latency,
        "dataset_and_code_score": availability_score,
        "dataset_and_code_score_latency": availability_latency,

        "dataset_quality": dataset_quality_score,
        "dataset_quality_latency": dataset_quality_latency,

        "code_quality": 0.0,
        "code_quality_latency": 0,

        "performance_claims": performance_claims_score,
        "performance_claims_latency": performance_claims_latency,
    }

    weights = {
        "size_score": 0.1,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.1,
        "dataset_and_code_score": 0.1,
        "dataset_quality": 0.2,
        "code_quality": 0.0,
        "performance_claims": 0.2,
    }

    # Use the average size score for net score calculation
    netscore = (size_score_avg * weights["size_score"] + 
                license_score * weights["license"] +
                ramp_up_score * weights["ramp_up_time"] +
                bus_factor_score * weights["bus_factor"] +
                availability_score * weights["dataset_and_code_score"] +
                dataset_quality_score * weights["dataset_quality"] +
                0.0 * weights["code_quality"] +  # code_quality is 0 for datasets
                performance_claims_score * weights["performance_claims"])
    scores["net_score"] = round(netscore, 3)
    scores["NetScore"] = round(netscore, 3)

    scores["net_score_latency"] = (
        size_latency + license_latency + ramp_up_latency + bus_factor_latency +
        availability_latency + dataset_quality_latency +
        0 +  # code_quality_latency
        performance_claims_latency
    )

    return scores