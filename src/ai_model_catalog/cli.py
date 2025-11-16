import json
from typing import Optional, Dict, Any

import typer

from .fetch_repo import fetch_dataset_data
from .interactive import interactive_main
from .logging_config import configure_logging
from .model_sources.github_model import RepositoryHandler
from .model_sources.hf_model import ModelHandler
from .score_model import (
    score_dataset_from_id,
    score_model_from_id,
    score_repo_from_owner_and_repo,
)

app = typer.Typer()


def safe_float(val: Any) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_int(val: Any) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def build_ndjson_line(
    name: str,
    category: str,
    scores: Dict[str, Any],
    size_score_key: str = "size_score",
) -> Dict[str, Any]:
    size_score = scores.get(size_score_key, scores.get("size", {}))
    if not isinstance(size_score, dict):
        size_score = {}

    return {
        "name": name,
        "category": category,
        "net_score": safe_float(scores.get("net_score")),
        "net_score_latency": safe_int(scores.get("net_score_latency")),
        "ramp_up_time": safe_float(scores.get("ramp_up_time")),
        "ramp_up_time_latency": safe_int(scores.get("ramp_up_time_latency")),
        "bus_factor": safe_float(scores.get("bus_factor")),
        "bus_factor_latency": safe_int(scores.get("bus_factor_latency")),
        "performance_claims": safe_float(scores.get("performance_claims")),
        "performance_claims_latency": safe_int(scores.get("performance_claims_latency")),
        "license": safe_float(scores.get("license")),
        "license_latency": safe_int(scores.get("license_latency")),
        "size_score": size_score,
        "size_score_latency": safe_int(scores.get("size_score_latency", scores.get("size_latency", 0))),
        "dataset_and_code_score": safe_float(
            scores.get("dataset_and_code_score", scores.get("availability", 0.0))
        ),
        "dataset_and_code_score_latency": safe_int(
            scores.get("dataset_and_code_score_latency", scores.get("availability_latency", 0))
        ),
        "dataset_quality": safe_float(scores.get("dataset_quality")),
        "dataset_quality_latency": safe_int(scores.get("dataset_quality_latency")),
        "code_quality": safe_float(scores.get("code_quality")),
        "code_quality_latency": safe_int(scores.get("code_quality_latency")),
    }


@app.command()
def models(
    owner: str = "huggingface",
    repo: str = "transformers",
    output_format: Optional[str] = typer.Option(
        "text", "--format", help="Output format (text or ndjson)"
    ),
):
    """Fetch and display metadata from GitHub API for a repository."""
    configure_logging()
    handler = RepositoryHandler(owner, repo)
    raw = handler.fetch_data()

    if output_format == "ndjson":
        scores = score_repo_from_owner_and_repo(owner, repo)
        line = build_ndjson_line(raw.get("full_name") or f"{owner}/{repo}", "REPOSITORY", scores)
        typer.echo(json.dumps(line))
        return

    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command(name="hf-model")
def hf_model(
    model_id: str = "bert-base-uncased",
    output_format: Optional[str] = typer.Option(
        "text", "--format", help="Output format (text or ndjson)"
    ),
):
    """Fetch and display metadata from Hugging Face Hub for a model."""
    configure_logging()
    handler = ModelHandler(model_id)
    raw = handler.fetch_data()

    if output_format == "ndjson":
        try:
            scores = score_model_from_id(model_id)
            line = build_ndjson_line(model_id, "MODEL", scores)
            typer.echo(json.dumps(line))
        except Exception as e:
            typer.echo(f"Error scoring model: {e}", err=True)
        return

    formatted = handler.format_data(raw)
    handler.display_data(formatted, raw)


@app.command(name="hf-dataset")
def hf_dataset(
    dataset_id: str = "imdb",
    output_format: Optional[str] = typer.Option(
        "text", "--format", help="Output format (text or ndjson)"
    ),
):
    """Fetch and display metadata from Hugging Face Hub for a dataset."""
    configure_logging()
    raw = fetch_dataset_data(dataset_id)

    if output_format == "ndjson":
        scores = score_dataset_from_id(dataset_id)
        line = build_ndjson_line(dataset_id, "DATASET", scores)
        typer.echo(json.dumps(line))
        return

    # text output
    typer.echo(f"Dataset: {dataset_id}")
    typer.echo(f"Author: {raw.get('author') or 'Unknown'}")
    typer.echo(f"License: {raw.get('license')}")
    typer.echo(f"Downloads: {raw.get('downloads', 0)}")
    typer.echo(f"Last Modified: {raw.get('lastModified', '')}")
    tags = raw.get("tags") or []
    if tags:
        typer.echo(f"Tags: {', '.join(tags)}")
    tcats = raw.get("taskCategories") or []
    if tcats:
        typer.echo(f"Task Categories: {', '.join(map(str, tcats))}")


@app.command()
def multiple_urls():
    """Fetch and output NDJSON metadata from multiple URLs."""
    configure_logging()
    with open("URL_FILE.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        # Split by comma and process each URL
        urls = [url.strip() for url in line.split(",") if url.strip()]
        
        # Process the model URL from each line
        if len(urls) >= 3:
            # First line: take the 3rd URL (index 2)
            url = urls[2]
        elif len(urls) == 1:
            # Lines 2 and 3: take the only URL
            url = urls[0]
        else:
            continue
            
        # Handle Hugging Face models
        if "huggingface.co" in url:
            try:
                # Extract model ID from URL
                if "/tree/" in url:
                    # Remove /tree/main or similar
                    url = url.split("/tree/")[0]
                
                # Extract model ID from path
                path = url.split("huggingface.co/", 1)[1]
                model_id = path.strip("/")
                
                scores = score_model_from_id(model_id)
                # Extract just the model name for display
                model_name = model_id.split("/")[-1]
                line = build_ndjson_line(model_name, "MODEL", scores)
                
                # Format all float values to 2 decimal precision
                json_str = json.dumps(line, separators=(',', ':'))  # Remove spaces
                
                # Fix all float values to 2 decimal places
                import re
                
                # Fix net_score precision
                json_str = re.sub(r'"net_score":(\d+\.?\d*)', lambda m: f'"net_score":{float(m.group(1)):.2f}', json_str)
                
                # Fix ramp_up_time precision
                json_str = re.sub(r'"ramp_up_time":(\d+\.?\d*)', lambda m: f'"ramp_up_time":{float(m.group(1)):.2f}', json_str)
                
                # Fix bus_factor precision
                json_str = re.sub(r'"bus_factor":(\d+\.?\d*)', lambda m: f'"bus_factor":{float(m.group(1)):.2f}', json_str)
                
                # Fix performance_claims precision
                json_str = re.sub(r'"performance_claims":(\d+\.?\d*)', lambda m: f'"performance_claims":{float(m.group(1)):.2f}', json_str)
                
                # Fix license precision
                json_str = re.sub(r'"license":(\d+\.?\d*)', lambda m: f'"license":{float(m.group(1)):.2f}', json_str)
                
                # Fix dataset_and_code_score precision
                json_str = re.sub(r'"dataset_and_code_score":(\d+\.?\d*)', lambda m: f'"dataset_and_code_score":{float(m.group(1)):.2f}', json_str)
                
                # Fix dataset_quality precision
                json_str = re.sub(r'"dataset_quality":(\d+\.?\d*)', lambda m: f'"dataset_quality":{float(m.group(1)):.2f}', json_str)
                
                # Fix code_quality precision
                json_str = re.sub(r'"code_quality":(\d+\.?\d*)', lambda m: f'"code_quality":{float(m.group(1)):.2f}', json_str)
                
                # Fix size_score object values precision
                json_str = re.sub(r'"raspberry_pi":(\d+\.?\d*)', lambda m: f'"raspberry_pi":{float(m.group(1)):.2f}', json_str)
                json_str = re.sub(r'"jetson_nano":(\d+\.?\d*)', lambda m: f'"jetson_nano":{float(m.group(1)):.2f}', json_str)
                json_str = re.sub(r'"desktop_pc":(\d+\.?\d*)', lambda m: f'"desktop_pc":{float(m.group(1)):.2f}', json_str)
                json_str = re.sub(r'"aws_server":(\d+\.?\d*)', lambda m: f'"aws_server":{float(m.group(1)):.2f}', json_str)
                
                typer.echo(json_str)
                
            except Exception as e:
                typer.echo(f"Error processing Hugging Face URL {url}: {e}", err=True)
                continue


@app.command()
def interactive():
    interactive_main()


if __name__ == "__main__":
    app()