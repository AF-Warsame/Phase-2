import os
import shutil
import logging
from typing import Dict, Optional
from git import Repo, GitCommandError
import requests

log = logging.getLogger(__name__)

HF_GIT_BASE = "https://huggingface.co"


def clone_or_get_repo(model_id: str, base_dir: str = "cloned_models") -> Optional[str]:
    """
    Clone the HF model repo (if not already cloned).
    """
    repo_path = os.path.join(base_dir, model_id.replace("/", "_"))
    hf_repo_url = f"{HF_GIT_BASE}/{model_id}.git"

    if os.path.isdir(repo_path):
        log.info(f"Using cached repo at {repo_path}")
        return repo_path

    os.makedirs(base_dir, exist_ok=True)
    try:
        log.info(f"Cloning {hf_repo_url} → {repo_path}")
        Repo.clone_from(hf_repo_url, repo_path)
        return repo_path
    except GitCommandError as e:
        log.error(f"Failed to clone repo: {e}")
        return None


def analyze_repo_contents(repo_path: str) -> Dict[str, bool]:
    """
    Check for presence of key model files.
    """
    required_files = [
        "README.md",
        "config.json",
        "model_index.json",
        "pytorch_model.bin",
        "tokenizer.json",
        "tokenizer_config.json",
    ]
    result = {}
    for fname in required_files:
        fpath = os.path.join(repo_path, fname)
        result[fname] = os.path.isfile(fpath)

    return result


def get_git_metadata(repo_path: str) -> Dict[str, Optional[str]]:
    """
    Get contributor count and last commit timestamp.
    """
    try:
        repo = Repo(repo_path)
        contributors = {commit.author.email for commit in repo.iter_commits()}
        last_commit = next(repo.iter_commits())
        return {
            "contributor_count": len(contributors),
            "last_commit_time": last_commit.committed_datetime.isoformat(),
        }
    except Exception as e:
        log.error(f"Error analyzing git repo: {e}")
        return {
            "contributor_count": None,
            "last_commit_time": None,
        }


def analyze_hf_repo(model_id: str) -> Dict[str, any]:
    """
    Main function to clone and analyze a Hugging Face model repo.
    Returns a dictionary with all useful metrics.
    """
    repo_path = clone_or_get_repo(model_id)
    if not repo_path:
        return {}

    files_present = analyze_repo_contents(repo_path)
    git_data = get_git_metadata(repo_path)

    return {
        "model_id": model_id,
        "files_present": files_present,
        **git_data,
    }


def cleanup_cloned_repo(model_id: str, base_dir: str = "cloned_models") -> None:
    """
    Remove cloned repo directory.
    """
    repo_path = os.path.join(base_dir, model_id.replace("/", "_"))
    if os.path.isdir(repo_path):
        shutil.rmtree(repo_path)
        log.info(f"Deleted {repo_path}")