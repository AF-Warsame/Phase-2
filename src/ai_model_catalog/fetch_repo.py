"""
Repository fetching functions for AI Model Catalog
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Rate limiting variables
_last_request_time = 0
_min_request_interval = 0.1  # 100ms between requests (less aggressive)

def _rate_limit():
    """Ensure minimum time between API requests to avoid rate limiting."""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    
    if time_since_last < _min_request_interval:
        sleep_time = _min_request_interval - time_since_last
        time.sleep(sleep_time)
    
    _last_request_time = time.time()

GITHUB_API = "https://api.github.com"
HF_API = "https://huggingface.co/api"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Model-Catalog/1.0",
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# Hugging Face specific headers
HF_HEADERS = {
    "User-Agent": "AI-Model-Catalog/1.0",
    "Accept": "application/json",
}

log = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """Create a requests session with retry strategy."""
    session = requests.Session()
    retry_strategy = Retry(
        total=1,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def time_request(func, *args, **kwargs) -> Tuple[Any, int]:
    """Execute a function and return result with latency in milliseconds."""
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        latency = int((time.time() - start_time) * 1000)
        return result, latency
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        raise e


SAMPLE_ACTION_RUN = {
    "id": 1,
    "name": "CI",
    "status": "completed",
    "conclusion": "success",
    "head_commit": {"id": "abc123"},
}


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""

    pass


class RepositoryDataError(Exception):
    """Custom exception for repository data errors"""

    pass


def _make_github_request(url: str, params: Optional[Dict] = None) -> requests.Response:
    """Make a GitHub API request with proper error handling and rate limiting"""
    _rate_limit()  # Add rate limiting before each request
    session = create_session()
    try:
        log.info("GET %s", url)
        log.debug("GET %s params=%s", url, params)
        response = session.get(url, headers=HEADERS, params=params, timeout=10)

        if response.status_code == 403:
            log.warning("GitHub API 403 (rate limit?) for %s", url)
            raise GitHubAPIError("GitHub API rate limit exceeded")

        response.raise_for_status()
        log.debug(
            "OK %s status=%s len=%s", url, response.status_code, len(response.content)
        )
        return response

    except requests.ConnectionError as e:
        log.error("Network connection failed for GitHub API: %s", e)
        raise GitHubAPIError(f"Network connection failed: {e}") from e
    except requests.RequestException as e:
        log.exception("HTTP error for %s", url)
        raise GitHubAPIError(f"Failed to fetch data from {url}: {str(e)}") from e


def _extract_page_count_from_link_header(link_header: str) -> int:
    """Extract total page count from GitHub Link header"""
    if 'rel="last"' not in link_header:
        return 0

    for link in link_header.split(","):
        if 'rel="last"' in link:
            last_page_url = link.split(";")[0].strip("<> ")
            break
    else:
        return 0

    if "page=" not in last_page_url:
        return 0

    page_matches = [
        part for part in last_page_url.split("&") if part.startswith("page=")
    ]
    if not page_matches:
        return 0

    last_page_param = page_matches[-1]
    return int(last_page_param.split("=")[1])


def _get_total_count_from_link_header(url: str) -> int:
    """Get total count from GitHub API Link header without fetching all data"""
    try:
        response = _make_github_request(url, {"per_page": 1})
        link_header = response.headers.get("Link", "")

        if link_header:
            return _extract_page_count_from_link_header(link_header)

        data = response.json()
        return len(data) if isinstance(data, list) else 0

    except GitHubAPIError:
        raise
    except Exception as e:
        raise RepositoryDataError(f"Failed to get count from {url}: {str(e)}") from e


def _fetch_github_endpoint(url: str) -> List[Dict[str, Any]]:
    """Fetch data from a GitHub API endpoint"""
    try:
        response = _make_github_request(url)
        return response.json()
    except GitHubAPIError:
        raise
    except Exception as e:
        raise RepositoryDataError(f"Failed to fetch endpoint {url}: {str(e)}") from e


def _fetch_readme_content(owner: str, repo: str) -> str:
    """Fetch README content from GitHub repository"""
    readme_url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"

    try:
        log.info("Fetch README meta %s/%s", owner, repo)
        response = _make_github_request(readme_url)
        readme_data = response.json()

        if "download_url" not in readme_data:
            raise RepositoryDataError("README metadata missing download_url")

        log.debug("README download url=%s", readme_data.get("download_url"))

        download_response = requests.get(readme_data["download_url"], timeout=15)
        download_response.raise_for_status()
        return download_response.text

    except GitHubAPIError:
        raise
    except requests.RequestException as e:
        raise RepositoryDataError(f"Failed to download README content: {str(e)}") from e
    except Exception as e:
        raise RepositoryDataError(f"Failed to fetch README: {str(e)}") from e


def _fetch_repository_counts(owner: str, repo: str) -> Dict[str, int]:
    """Fetch all repository counts using Link headers"""
    base_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    log.info("Fetch counts %s/%s", owner, repo)

    endpoints = {
        "commits_count": f"{base_url}/commits",
        "contributors_count": f"{base_url}/contributors",
        "issues_count": f"{base_url}/issues",
        "pulls_count": f"{base_url}/pulls",
        "actions_count": f"{base_url}/actions/runs",
    }

    counts = {}
    for key, url in endpoints.items():
        try:
            counts[key] = _get_total_count_from_link_header(url)
        except RepositoryDataError as e:
            log.warning("Failed to get %s: %s", key, e)
            counts[key] = 0

    return counts


def _fetch_repository_samples(owner: str, repo: str) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch sample data from repository endpoints"""
    base_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    log.info("Fetch samples %s/%s", owner, repo)

    endpoints = {
        "commits_data": f"{base_url}/commits?per_page=5",
        "contributors_data": f"{base_url}/contributors?per_page=5",
        "issues_data": f"{base_url}/issues?per_page=5",
        "pulls_data": f"{base_url}/pulls?per_page=5",
        "actions_data": f"{base_url}/actions/runs?per_page=5",
    }

    samples = {}
    for key, url in endpoints.items():
        try:
            samples[key] = _fetch_github_endpoint(url)
        except RepositoryDataError as e:
            log.warning("Failed to get %s: %s", key, e)
            samples[key] = []

    return samples


def _extract_actions_runs(actions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract workflow runs from actions data"""
    if isinstance(actions_data, dict):
        return actions_data.get("workflow_runs", [])
    return []


def _format_actions_data(actions_runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format actions runs data for output"""
    return [
        {
            "id": run.get("id"),
            "name": run.get("name"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "commit": run.get("head_commit", {}).get("id"),
        }
        for run in actions_runs
    ]


def _fetch_github_api_data(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch all required data from GitHub API endpoints"""
    repo_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    repo_response = _make_github_request(repo_url)
    repo_data = repo_response.json()

    readme_text = _fetch_readme_content(owner, repo)
    counts = _fetch_repository_counts(owner, repo)
    samples = _fetch_repository_samples(owner, repo)

    actions_runs = _extract_actions_runs(samples["actions_data"])

    return {
        "repo_data": repo_data,
        "readme_text": readme_text,
        "commits_data": samples["commits_data"],
        "contributors_data": samples["contributors_data"],
        "issues_data": samples["issues_data"],
        "pulls_data": samples["pulls_data"],
        "actions_runs": actions_runs,
        **counts,
    }


def _format_repo_api_data(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the fetched GitHub data into the expected API structure"""
    repo_data = github_data["repo_data"]
    actions_runs = github_data["actions_runs"]

    return {
        "full_name": repo_data.get("full_name"),
        "size": repo_data.get("size"),
        "license": repo_data.get("license"),
        "owner": repo_data.get("owner"),
        "stars": repo_data.get("stargazers_count"),
        "forks": repo_data.get("forks_count"),
        "open_issues": repo_data.get("open_issues_count"),
        "updated_at": repo_data.get("updated_at"),
        "readme": github_data["readme_text"],
        "commits": github_data["commits_data"],
        "contributors": github_data["contributors_data"],
        "issues": github_data["issues_data"],
        "pulls": github_data["pulls_data"],
        "actions": _format_actions_data(actions_runs),
        "modelSize": repo_data.get("size"),
        "cardData": {"content": github_data["readme_text"]},
        "commits_count": github_data.get("commits_count", 0),
        "contributors_count": github_data.get("contributors_count", 0),
        "issues_count": github_data.get("issues_count", 0),
        "pulls_count": github_data.get("pulls_count", 0),
        "actions_count": github_data.get("actions_count", 0),
    }


def fetch_repo_data(
    owner: str = "huggingface", repo: str = "transformers"
) -> Dict[str, Any]:
    """Fetch all required GitHub metadata for scoring functions"""
    try:
        github_data = _fetch_github_api_data(owner, repo)
        return _format_repo_api_data(github_data)
    except (GitHubAPIError, RepositoryDataError) as e:
        log.error("Failed to fetch repository data for %s/%s: %s", owner, repo, e)
        raise
    except Exception as e:
        log.error(
            "Unexpected error fetching repository data for %s/%s: %s", owner, repo, e
        )
        raise RepositoryDataError(f"Unexpected error: {e}") from e


def _calculate_model_size(model_data: Dict[str, Any]) -> int:
    """Calculate model size from available fields"""
    if "usedStorage" in model_data and model_data["usedStorage"]:
        return model_data["usedStorage"]

    if "safetensors" in model_data and model_data["safetensors"]:
        return sum(
            file_info.get("size", 0)
            for file_info in model_data["safetensors"]
            if isinstance(file_info, dict)
        )

    if "siblings" in model_data and model_data["siblings"]:
        return sum(
            file_info.get("size", 0)
            for file_info in model_data["siblings"]
            if isinstance(file_info, dict)
        )

    return 100 * 1024 * 1024


def _fetch_hf_readme(model_id: str) -> str:
    """Fetch README content from Hugging Face model"""
    try:
        readme_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
        response = requests.get(readme_url, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RepositoryDataError(
            f"Failed to fetch README from Hugging Face: {e}"
        ) from e


def fetch_model_data(model_id: str) -> Dict[str, Any]:
    """
    Fetch Hugging Face Hub model metadata and shape it for ModelHandler usage.
    """
    model_url = f"{HF_API}/models/{model_id}"

    # Add authentication header if token is available
    headers = HF_HEADERS.copy()
    hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN") or os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    session = create_session()
    try:
        _rate_limit()  # Add rate limiting before HF API request
        response = session.get(model_url, headers=headers, timeout=10)
        response.raise_for_status()
        model_data = response.json()
    except requests.ConnectionError as e:
        log.error("Network connection failed for Hugging Face API: %s", e)
        # Return minimal data instead of raising
        return {
            "modelSize": 0,
            "license": "unknown",
            "author": "unknown",
            "readme": f"# {model_id}\n\nNetwork unavailable - could not fetch model data.",
            "cardData": {},
            "downloads": 0,
            "lastModified": "",
        }
    except requests.RequestException as e:
        log.error(
            "Failed to fetch model data from Hugging Face for %s: %s", model_id, e
        )
        # Return minimal data instead of raising
        return {
            "modelSize": 0,
            "license": "unknown",
            "author": "unknown",
            "readme": f"# {model_id}\n\nAPI request failed - could not fetch model data.",
            "cardData": {},
            "downloads": 0,
            "lastModified": "",
        }

    license_type = model_data.get("license", "unknown")

    card_data = model_data.get("cardData", {})
    readme_text = card_data.get("content", "") if card_data else ""

    if not readme_text:
        try:
            readme_text = _fetch_hf_readme(model_id)
        except RepositoryDataError:
            readme_text = (
                f"# {model_id}\n\nThis is a Hugging Face model.\n\n"
                f"For more information, visit: https://huggingface.co/{model_id}"
            )

    model_size = _calculate_model_size(model_data)

    return {
        "modelSize": model_size,
        "license": license_type,
        "author": model_data.get("author"),
        "readme": readme_text,
        "cardData": card_data,
        "downloads": model_data.get("downloads", 0),
        "likes": model_data.get("likes", 0),
        "lastModified": model_data.get("lastModified", ""),
        "tags": model_data.get("tags", []),
    }


def fetch_hf_model(model_id: str) -> Dict[str, Any]:
    """Fetch Hugging Face Hub model metadata and shape it for net_score()"""
    model_url = f"{HF_API}/models/{model_id}"

    session = create_session()
    try:
        _rate_limit()  # Add rate limiting before HF API request
        response = session.get(model_url, headers=HF_HEADERS, timeout=10)
        response.raise_for_status()
        model_data = response.json()
    except requests.ConnectionError as e:
        log.error("Network connection failed for Hugging Face API: %s", e)
        raise RepositoryDataError(f"Network connection failed: {e}") from e
    except requests.RequestException as e:
        raise RepositoryDataError(
            f"Failed to fetch model data from Hugging Face: {e}"
        ) from e

    license_type = model_data.get("license", "unknown")

    card_data = model_data.get("cardData", {})
    readme_text = card_data.get("content", "") if card_data else ""

    if not readme_text:
        try:
            readme_text = _fetch_hf_readme(model_id)
        except RepositoryDataError:
            readme_text = (
                f"# {model_id}\n\nThis is a Hugging Face model.\n\n"
                f"For more information, visit: https://huggingface.co/{model_id}"
            )

    model_size = _calculate_model_size(model_data)

    return {
        "modelSize": model_size,
        "license": license_type,
        "author": model_data.get("author"),
        "readme": readme_text,
        "cardData": model_data.get("cardData", {}),
        "downloads": model_data.get("downloads", 0),
        "likes": model_data.get("likes", 0),
        "lastModified": model_data.get("lastModified", ""),
        "tags": model_data.get("tags", []),
    }


def fetch_dataset_data(dataset_id: str) -> Dict[str, Any]:
    """
    Fetch Hugging Face Hub dataset metadata for CLI usage.
    """
    dataset_url = f"{HF_API}/datasets/{dataset_id}"

    # Add authentication header if token is available
    headers = {}
    hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN") or os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    try:
        _rate_limit()  # Add rate limiting before HF API request
        response = requests.get(dataset_url, headers=headers, timeout=15)
        response.raise_for_status()
        ds_data = response.json()
    except requests.RequestException as e:
        log.error(
            "Failed to fetch dataset data from Hugging Face for %s: %s", dataset_id, e
        )
        raise RepositoryDataError(
            f"Failed to fetch dataset data from Hugging Face: {e}"
        ) from e

    license_type = ds_data.get("license", "unknown")

    card_data = ds_data.get("cardData", {})
    readme_text = card_data.get("content", "") if card_data else ""

    if not readme_text:
        try:
            readme_text = _fetch_hf_readme(dataset_id)
        except RepositoryDataError:
            readme_text = (
                f"# {dataset_id}\n\nThis is a Hugging Face dataset.\n\n"
                f"For more information, visit: https://huggingface.co/datasets/{dataset_id}"
            )

    return {
        "license": license_type,
        "author": ds_data.get("author"),
        "readme": readme_text,
        "cardData": card_data,
        "downloads": ds_data.get("downloads", 0),
        "lastModified": ds_data.get("lastModified", ""),
        "tags": ds_data.get("tags", []),
        "taskCategories": ds_data.get("task_categories", []),
        "taskIds": ds_data.get("task_ids", []),
        "description": ds_data.get("description", ""),
    }