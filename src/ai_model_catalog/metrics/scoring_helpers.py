"""Helper functions for LLM-enhanced scoring."""
from typing import Any, Dict


def combine_llm_scores(
    llm_analysis: Dict[str, Any], weights: Dict[str, float]
) -> float:
    """Combine LLM analysis scores with weights."""
    total_score = 0.0
    total_weight = 0.0

    for key, weight in weights.items():
        if key in llm_analysis and isinstance(llm_analysis[key], (int, float)):
            score = float(llm_analysis[key])
            if 0.0 <= score <= 1.0:  # Validate score range
                total_score += score * weight
                total_weight += weight

    if total_weight == 0:
        return 0.0

    return total_score / total_weight


def extract_readme_content(data: Dict[str, Any]) -> str:
    """Extract README content from data."""
    readme = data.get("readme", "")
    if not readme:
        readme = data.get("description", "")
    if not readme:
        readme = data.get("cardData", {}).get("content", "")

    return readme or ""


def extract_dataset_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract dataset-specific information."""
    return {
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
        "taskCategories": data.get("taskCategories", []),
        "downloads": data.get("downloads", 0),
        "author": data.get("author", ""),
        "license": data.get("license", ""),
    }


def validate_llm_response(response: Dict[str, Any], expected_keys: list) -> bool:
    """Validate that LLM response has expected structure."""
    if not isinstance(response, dict):
        return False

    for key in expected_keys:
        if key not in response:
            return False
        if not isinstance(response[key], (int, float)):
            return False
        if not 0.0 <= float(response[key]) <= 1.0:
            return False

    return True