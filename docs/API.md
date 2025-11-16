# AI Model Catalog CLI - API Documentation

This document provides comprehensive API documentation for the AI Model Catalog CLI tool.

## Table of Contents

- [Overview](#overview)
- [Command Line Interface](#command-line-interface)
- [Python API](#python-api)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Examples](#examples)

## Overview

The AI Model Catalog CLI provides both command-line and programmatic interfaces for evaluating AI/ML models. The tool supports analysis of models from GitHub repositories and Hugging Face Hub.

## Command Line Interface

### Main Commands

#### `catalog models`
Analyze a GitHub repository containing AI/ML models.

```bash
catalog models [OPTIONS] --owner TEXT --repo TEXT
```

**Options:**
- `--owner TEXT`: GitHub repository owner (default: huggingface)
- `--repo TEXT`: GitHub repository name (default: transformers)
- `--format [text|ndjson]`: Output format (default: text)
- `--help`: Show help message

**Examples:**
```bash
# Analyze Hugging Face transformers repository
catalog models --owner huggingface --repo transformers

# Output as NDJSON for auto-grader
catalog models --owner microsoft --repo DeepSpeed --format ndjson

# Analyze with default parameters
catalog models
```

#### `catalog hf-model`
Analyze a Hugging Face Hub model.

```bash
catalog hf-model [OPTIONS] --model-id TEXT
```

**Options:**
- `--model-id TEXT`: Hugging Face model ID (default: bert-base-uncased)
- `--format [text|ndjson]`: Output format (default: text)
- `--help`: Show help message

**Examples:**
```bash
# Analyze BERT model
catalog hf-model --model-id bert-base-uncased

# Output as NDJSON for auto-grader
catalog hf-model --model-id microsoft/DialoGPT-medium --format ndjson

# Analyze with default parameters
catalog hf-model
```

#### `catalog hf-dataset`
Analyze a Hugging Face Hub dataset.

```bash
catalog hf-dataset [OPTIONS] --dataset-id TEXT
```

**Options:**
- `--dataset-id TEXT`: Hugging Face dataset ID (default: imdb)
- `--format [text|ndjson]`: Output format (default: text)
- `--help`: Show help message

**Examples:**
```bash
# Analyze IMDB dataset
catalog hf-dataset --dataset-id imdb

# Output as NDJSON for auto-grader
catalog hf-dataset --dataset-id squad --format ndjson

# Analyze with default parameters
catalog hf-dataset
```

#### `catalog interactive`
Launch interactive mode for model exploration.

```bash
catalog interactive
```

**Features:**
- Browse popular AI/ML repositories
- Search Hugging Face models
- Interactive model selection
- Real-time scoring display

#### `catalog multiple-urls`
Process multiple URLs from URL_FILE.txt for auto-grader compatibility.

```bash
catalog multiple-urls
```

**Features:**
- Reads URLs from URL_FILE.txt
- Processes Hugging Face models and datasets
- Outputs NDJSON format for each URL
- Handles URL parsing and model ID extraction
- Auto-grader compatible output format

### Auto-Grader Interface

#### `./run install`
Install dependencies for the tool.

```bash
./run install
```

**Exit Codes:**
- `0`: Success
- `1`: Failure

#### `./run test`
Run the test suite and report coverage.

```bash
./run test
```

**Output Format:**
```
X/Y test cases passed. Z% line coverage achieved.
```

**Exit Codes:**
- `0`: Success
- `1`: Failure

#### `./run URL_FILE`
Process a file containing URLs to analyze.

```bash
./run /path/to/url_file.txt
```

**URL File Format:**
- One URL per line
- Supports GitHub repositories and Hugging Face models/datasets
- Comments start with `#`
- Empty lines are ignored

**Example URL file:**
```
# GitHub repositories
https://github.com/huggingface/transformers
https://github.com/microsoft/DeepSpeed

# Hugging Face models
https://huggingface.co/bert-base-uncased
https://huggingface.co/microsoft/DialoGPT-medium

# Hugging Face datasets
https://huggingface.co/datasets/squad
```

## LLM Integration

The AI Model Catalog CLI includes LLM-enhanced analysis capabilities using Purdue GenAI Studio API (Claude-3-Sonnet) for intelligent README and metadata analysis.

### LLM Service Configuration

```python
from ai_model_catalog.llm_service import get_llm_service

# Get LLM service instance
llm_service = get_llm_service()

# Analyze README quality
analysis = llm_service.analyze_readme_quality(readme_content)
```

### Enhanced Metrics with LLM

The following metrics are enhanced with LLM analysis:

#### Ramp-up Time Score
- **Traditional**: README length measurement
- **LLM-Enhanced**: Context-aware analysis of installation instructions, examples, and documentation structure

#### Code Quality Score
- **Traditional**: Keyword matching for testing tools
- **LLM-Enhanced**: Understanding of actual tool usage and CI/CD pipeline quality

#### Dataset Quality Score
- **Traditional**: Pattern matching for dataset keywords
- **LLM-Enhanced**: Comprehensive analysis of dataset documentation and metadata

### Environment Variables

```bash
# Required for LLM features
export PURDUE_GENAI_API_KEY="your_purdue_genai_token_here"

# Optional configuration
export LLM_ENABLED="true"
export LLM_MODEL="claude-3-sonnet"
export LLM_TIMEOUT="30"
```

## Python API

### Core Functions

#### `fetch_repo_data(owner: str, repo: str) -> Dict[str, Any]`
Fetch repository data from GitHub API.

**Parameters:**
- `owner`: GitHub repository owner
- `repo`: GitHub repository name

**Returns:**
- Dictionary containing repository metadata

**Raises:**
- `GitHubAPIError`: API request failed
- `RepositoryDataError`: Data processing failed

**Example:**
```python
from ai_model_catalog.fetch_repo import fetch_repo_data

try:
    data = fetch_repo_data("huggingface", "transformers")
    print(f"Repository: {data['full_name']}")
    print(f"Stars: {data['stars']}")
except GitHubAPIError as e:
    print(f"API Error: {e}")
```

#### `fetch_hf_model(model_id: str) -> Dict[str, Any]`
Fetch model data from Hugging Face Hub.

**Parameters:**
- `model_id`: Hugging Face model identifier

**Returns:**
- Dictionary containing model metadata

**Raises:**
- `RepositoryDataError`: Data processing failed

**Example:**
```python
from ai_model_catalog.fetch_repo import fetch_hf_model

try:
    data = fetch_hf_model("bert-base-uncased")
    print(f"Model: {data['modelId']}")
    print(f"Downloads: {data['downloads']}")
except RepositoryDataError as e:
    print(f"Error: {e}")
```

#### `net_score(api_data: Dict[str, Any]) -> Dict[str, float]`
Calculate NetScore for a model.

**Parameters:**
- `api_data`: Model/repository data dictionary

**Returns:**
- Dictionary containing individual scores and NetScore

**Example:**
```python
from ai_model_catalog.score_model import net_score

data = {
    "size": 1000000,
    "license": {"spdx_id": "MIT"},
    "readme": "Comprehensive documentation...",
    "owner": {"login": "huggingface"}
}

scores = net_score(data)
print(f"NetScore: {scores['NetScore']}")
print(f"License Score: {scores['license']}")
```

### Metric Classes

#### `Metric` (Base Class)
Abstract base class for all metrics.

```python
from ai_model_catalog.metrics.base import Metric

class CustomMetric(Metric):
    def score(self, model_data: dict) -> float:
        # Implement your scoring logic
        return 0.0
```

#### Individual Metric Classes

**SizeMetric**
```python
from ai_model_catalog.metrics.score_size import SizeMetric

metric = SizeMetric()
score = metric.score({"repo_size_bytes": 1000000})
# Returns hardware compatibility object:
# {
#     "raspberry_pi": 0.20,
#     "jetson_nano": 0.40, 
#     "desktop_pc": 0.95,
#     "aws_server": 1.00
# }
```

**LicenseMetric**
```python
from ai_model_catalog.metrics.score_license import LicenseMetric

metric = LicenseMetric()
score = metric.score({"license": "MIT"})
```

**RampUpMetric**
```python
from ai_model_catalog.metrics.score_ramp_up_time import RampUpMetric

metric = RampUpMetric()
score = metric.score({"readme": "Comprehensive documentation..."})
```

**BusFactorMetric**
```python
from ai_model_catalog.metrics.score_bus_factor import BusFactorMetric

metric = BusFactorMetric()
score = metric.score({"maintainers": ["user1", "user2"]})
```

**AvailableDatasetAndCodeMetric**
```python
from ai_model_catalog.metrics.score_available_dataset_and_code import AvailableDatasetAndCodeMetric

metric = AvailableDatasetAndCodeMetric()
score = metric.score({"has_code": True, "has_dataset": True})
```

**DatasetQualityMetric**
```python
from ai_model_catalog.metrics.score_dataset_quality import DatasetQualityMetric

metric = DatasetQualityMetric()
score = metric.score({"readme": "...", "tags": ["dataset", "nlp"]})
```

**CodeQualityMetric**
```python
from ai_model_catalog.metrics.score_code_quality import CodeQualityMetric

metric = CodeQualityMetric()
score = metric.score({"readme": "Uses pytest and GitHub Actions..."})
```

**PerformanceClaimsMetric**
```python
from ai_model_catalog.metrics.score_performance_claims import PerformanceClaimsMetric

metric = PerformanceClaimsMetric()
score = metric.score({"readme": "State-of-the-art results..."})
```

### Parallel Execution

#### `run_metrics(metrics: Iterable[Metric], ctx: dict, max_workers: int = 4) -> List[MetricResult]`
Run multiple metrics in parallel.

**Parameters:**
- `metrics`: Iterable of Metric instances
- `ctx`: Context data for metrics
- `max_workers`: Maximum number of parallel workers

**Returns:**
- List of MetricResult objects

**Example:**
```python
from ai_model_catalog.metrics.runner import run_metrics
from ai_model_catalog.metrics.score_size import SizeMetric
from ai_model_catalog.metrics.score_license import LicenseMetric

metrics = [SizeMetric(), LicenseMetric()]
ctx = {"repo_size_bytes": 1000000, "license": "MIT"}

results = run_metrics(metrics, ctx, max_workers=2)
for result in results:
    print(f"{result.name}: {result.score}")
```

## Data Models

### MetricResult
Result of metric calculation.

```python
@dataclass(frozen=True)
class MetricResult:
    name: str                    # Metric name
    score: float                 # Score (0.0-1.0)
    passed: bool                 # Whether score >= 0.5
    details: Mapping[str, Any]   # Additional details
    error: Optional[str]         # Error message if failed
    elapsed_s: float             # Execution time in seconds
```

### Repository Data Structure
Standard structure for GitHub repository data.

```python
{
    "full_name": "owner/repo",
    "size": 12345,                    # Size in KB
    "license": {"spdx_id": "MIT"},    # License information
    "owner": {"login": "username"},   # Owner information
    "stars": 1000,                    # Star count
    "forks": 100,                     # Fork count
    "open_issues": 10,                # Open issues count
    "updated_at": "2024-01-01T00:00:00Z",
    "readme": "Repository README content...",
    "commits": [...],                 # Recent commits
    "contributors": [...],            # Contributors
    "issues": [...],                  # Recent issues
    "pulls": [...],                   # Recent pull requests
    "actions": [...]                  # GitHub Actions runs
}
```

### Model Data Structure
Standard structure for Hugging Face model data.

```python
{
    "modelId": "bert-base-uncased",
    "modelSize": 1000000,             # Size in bytes
    "license": "mit",                 # License string
    "author": "huggingface",          # Model author
    "readme": "Model README content...",
    "cardData": {"content": "..."},   # Model card data
    "downloads": 1000000,             # Download count
    "lastModified": "2024-01-01T00:00:00Z",
    "tags": ["pytorch", "nlp"],       # Model tags
    "pipeline_tag": "text-classification"
}
```

## Error Handling

### Exception Types

#### `GitHubAPIError`
Raised when GitHub API requests fail.

```python
from ai_model_catalog.fetch_repo import GitHubAPIError

try:
    data = fetch_repo_data("owner", "repo")
except GitHubAPIError as e:
    print(f"GitHub API error: {e}")
```

#### `RepositoryDataError`
Raised when repository data processing fails.

```python
from ai_model_catalog.fetch_repo import RepositoryDataError

try:
    data = fetch_hf_model("model-id")
except RepositoryDataError as e:
    print(f"Data processing error: {e}")
```

### Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | API rate limit exceeded |
| 3 | Invalid input |
| 4 | Network error |
| 5 | Authentication error |

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GITHUB_TOKEN` | str | None | GitHub API token |
| `LOG_FILE` | str | "catalog.log" | Log file path |
| `LOG_LEVEL` | int | 0 | Log verbosity (0-2) |
| `HF_TOKEN` | str | None | Hugging Face token |
| `MAX_WORKERS` | int | 4 | Parallel workers |
| `API_TIMEOUT` | int | 15 | API timeout (seconds) |

### Logging Levels

| Level | Description |
|-------|-------------|
| 0 | Silent (no output) |
| 1 | Informational messages |
| 2 | Debug messages (verbose) |

## Examples

### Basic Usage

```python
from ai_model_catalog.fetch_repo import fetch_repo_data, fetch_hf_model
from ai_model_catalog.score_model import net_score

# Analyze GitHub repository
repo_data = fetch_repo_data("huggingface", "transformers")
repo_scores = net_score(repo_data)
print(f"Repository NetScore: {repo_scores['NetScore']}")

# Analyze Hugging Face model
model_data = fetch_hf_model("bert-base-uncased")
model_scores = net_score(model_data)
print(f"Model NetScore: {model_scores['NetScore']}")
```

### Custom Metric

```python
from ai_model_catalog.metrics.base import Metric

class CustomMetric(Metric):
    def score(self, model_data: dict) -> float:
        # Custom scoring logic
        readme_length = len(model_data.get("readme", ""))
        return min(1.0, readme_length / 1000.0)

# Use custom metric
metric = CustomMetric()
score = metric.score({"readme": "Long documentation..."})
```

### Local Repository Analysis

```python
from pathlib import Path
from ai_model_catalog.cli import _scan_local_repo, _detect_source
from ai_model_catalog.score_model import net_score

# Analyze local repository
repo_path = Path("/path/to/repository")
local_data = _scan_local_repo(repo_path)

# Calculate NetScore for local repository
scores = net_score(local_data)
print(f"Local repository NetScore: {scores['NetScore']}")

# Detect source type (GitHub URL or local path)
source_type, info = _detect_source("https://github.com/owner/repo")
print(f"Source type: {source_type}")  # "github"
print(f"Info: {info}")  # {"owner": "owner", "repo": "repo"}

source_type, info = _detect_source("/path/to/local/repo")
print(f"Source type: {source_type}")  # "local"
print(f"Info: {info}")  # {"path": "/path/to/local/repo"}
```

**Local Repository Data Structure:**
```python
{
    "source": "local",
    "path": "/path/to/repository",
    "size_bytes": 1024000,
    "file_count": 150,
    "py_files": 25,
    "test_files": 10,
    "has_readme": True,
    "readme": "README.md",
    "license_file": "LICENSE",
    "is_git": True,
    "branch": "main",
    "last_commit": "abc123def456 1640995200",
    "contributors": [
        {"id": "user@example.com", "commits": 45},
        {"id": "developer@example.com", "commits": 23}
    ]
}
```

### Batch Processing

```python
from ai_model_catalog.fetch_repo import fetch_repo_data
from ai_model_catalog.score_model import net_score

repositories = [
    ("huggingface", "transformers"),
    ("microsoft", "DeepSpeed"),
    ("facebookresearch", "fairseq")
]

for owner, repo in repositories:
    try:
        data = fetch_repo_data(owner, repo)
        scores = net_score(data)
        print(f"{owner}/{repo}: {scores['NetScore']:.3f}")
    except Exception as e:
        print(f"Error processing {owner}/{repo}: {e}")
```

### Error Handling

```python
from ai_model_catalog.fetch_repo import fetch_repo_data, GitHubAPIError, RepositoryDataError

def analyze_repository(owner: str, repo: str) -> dict:
    try:
        data = fetch_repo_data(owner, repo)
        return {"success": True, "data": data}
    except GitHubAPIError as e:
        if "rate limit" in str(e).lower():
            return {"success": False, "error": "Rate limit exceeded", "retry_after": 3600}
        else:
            return {"success": False, "error": f"GitHub API error: {e}"}
    except RepositoryDataError as e:
        return {"success": False, "error": f"Data processing error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}
```

---

For more examples and advanced usage, see the [Examples](examples/) directory and the [README](README.md) file.
