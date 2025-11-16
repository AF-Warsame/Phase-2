from typing import Any, Dict

import typer

from .score_model import net_score
def _as_int(v: Any, default: int = 0) -> int:
    """Convert value to int with default fallback."""
    try:
        if isinstance(v, bool):
            return 0
        return int(v)
    except (ValueError, TypeError):
        return default
def _as_bool(v: Any) -> bool:
    """Convert value to bool, treating empty/false strings as False."""
    return bool(v) and str(v).strip().lower() not in {
        "",
        "false",
        "0",
        "none",
        "null",
    }
def _extract_license_name(license_info: Any) -> str:
    if isinstance(license_info, dict):
        return license_info.get("spdx_id") or "None"
    return license_info or "None"
def _format_repository_data(
    data: Dict[str, Any], owner: str, repo: str
) -> Dict[str, Any]:
    """Extract and format repository data for display."""
    return {
        "full_name": data.get("full_name") or f"{owner}/{repo}",
        "stars": data.get("stargazers_count")
        or data.get("stargazers")
        or data.get("stars")
        or 0,
        "forks": data.get("forks_count") or data.get("forks") or 0,
        "language": data.get("language") or data.get("primary_language") or "N/A",
        "updated": data.get("pushed_at")
        or data.get("updated_at")
        or data.get("lastModified")
        or "N/A",
        "open_issues": data.get("open_issues_count") or data.get("open_issues") or 0,
        "size": data.get("size", 0),
        "license_name": _extract_license_name(data.get("license", {})),
        "description": data.get("description") or "No description available",
        "default_branch": data.get("default_branch", "main"),
        "readme": data.get("readme", ""),
    }
def _format_count_info(data: Dict[str, Any], key: str, display_name: str) -> str:
    count = data.get(f"{key}_count", 0)
    sample_data = data.get(key, [])

    if count == 0:
        sample_count = len(sample_data)
        return f"Recent {display_name}: {sample_count} (showing first 30)"
    return f"Total {display_name}: {count:,}"
def _get_repository_counts_info(data: Dict[str, Any]) -> Dict[str, str]:
    return {
        "commits": _format_count_info(data, "commits", "commits"),
        "contributors": _format_count_info(data, "contributors", "contributors"),
        "issues": _format_count_info(data, "issues", "issues"),
        "pulls": _format_count_info(data, "pulls", "pull requests"),
        "actions": _format_count_info(data, "actions", "actions runs"),
    }
def _display_repository_info(
    formatted_data: Dict[str, Any], counts_info: Dict[str, str]
) -> None:
    typer.echo(f"Repo: {formatted_data['full_name']} ⭐ {formatted_data['stars']}")

    typer.echo(f"Description: {formatted_data['description']}")
    typer.echo(f"Default branch: {formatted_data['default_branch']}")
    typer.echo(f"Language: {formatted_data['language']}")
    typer.echo(f"Updated: {formatted_data['updated']}")
    typer.echo(f"Stars: {formatted_data['stars']:,}")
    typer.echo(f"Forks: {formatted_data['forks']:,}")
    typer.echo(f"Open issues: {formatted_data['open_issues']}")
    typer.echo(f"Size: {formatted_data['size']:,} KB")
    typer.echo(f"License: {formatted_data['license_name']}")
    typer.echo(counts_info["commits"])
    typer.echo(counts_info["contributors"])
    typer.echo(counts_info["issues"])
    typer.echo(counts_info["pulls"])
    typer.echo(counts_info["actions"])
    typer.echo(f"README length: {len(formatted_data['readme'])} characters")
def _format_model_data(data: Dict[str, Any], model_id: str) -> Dict[str, Any]:
    return {
        "model_name": data.get("modelId", model_id),
        "author": data.get("author", "Unknown"),
        "description": data.get("description", ""),
        "model_size": data.get("modelSize", 0),
        "downloads": data.get("downloads", 0),
        "last_modified": data.get("lastModified", "Unknown"),
        "readme": data.get("readme", ""),
        "license_name": _extract_license_name(data.get("license")),
        "tags": data.get("tags") or [],
        "task": data.get("pipeline_tag"),
    }
def _display_model_info(formatted_data: Dict[str, Any]) -> None:
    typer.echo(f"Model: {formatted_data['model_name']}")
    typer.echo(f"Author: {formatted_data['author']}")
    typer.echo(
        f"Description: {formatted_data['description'] or 'No description available'}"
    )
    typer.echo(f"Model Size: {formatted_data['model_size']:,} bytes")
    typer.echo(f"License: {formatted_data['license_name']}")
    typer.echo(f"Downloads: {formatted_data['downloads']:,}")
    typer.echo(f"Last Modified: {formatted_data['last_modified']}")
    typer.echo(f"README length: {len(formatted_data['readme'])} characters")

    if isinstance(formatted_data["tags"], list) and formatted_data["tags"]:
        typer.echo(f"Tags: {', '.join(formatted_data['tags'])}")
    if formatted_data["task"]:
        typer.echo(f"Task: {formatted_data['task']}")
def _pick_repo_for_owner(owner: str, repo_input: str) -> str:
    """
    Given an owner and a user input (either a repo name or a selection number),
    return the actual repo name.

    Assumes you have a predefined list of repos per owner (same as in interactive_main).
    """
    owner_repos = {
        "huggingface": [
            "transformers",
            "diffusers",
            "accelerate",
            "datasets",
            "trl",
        ],
        "openai": [
            "openai-cookbook",
            "whisper",
            "gym",
            "baselines",
            "microscope",
        ],
        "facebookresearch": [
            "fairseq",
            "llama",
            "detectron2",
            "pytorch3d",
            "esm",
        ],
        "google-research": [
            "bert",
            "t5x",
            "vision_transformer",
            "biggan",
            "scenic",
        ],
        "microsoft": [
            "DeepSpeed",
            "LoRA",
            "onnxruntime",
            "lightgbm",
            "NCCL",
        ],
    }

    repos = owner_repos.get(owner, [])

    # If input is a digit, convert to repo by index (1-based)
    if repo_input.isdigit():
        idx = int(repo_input) - 1
        if 0 <= idx < len(repos):
            return repos[idx]

    # Otherwise, check if repo_input matches any repo exactly
    if repo_input in repos:
        return repo_input

    # Fallback to default if no match
    return "transformers"
def _display_scores(data: Dict[str, Any]) -> None:
    scores = net_score(data)
    typer.echo("\nNetScore Breakdown:")
    for key, value in scores.items():
        if key == "size" and isinstance(value, dict):
            # Display size scores as hardware mappings
            typer.echo(f"{key}:")
            for hardware, score in value.items():
                typer.echo(f"  {hardware}: {score:.3f}")
        else:
            typer.echo(f"{key}: {value:.3f}")
