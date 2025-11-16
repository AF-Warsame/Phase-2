"""Additional tests for analyze_local_repo.py to improve coverage."""

import os
import tempfile
from unittest.mock import patch
from git.exc import GitCommandError, InvalidGitRepositoryError

from ai_model_catalog.analyze_local_repo import (
    clone_or_get_repo,
    analyze_repo_contents,
    get_git_metadata,
    analyze_hf_repo,
    cleanup_cloned_repo,
)


class TestAnalyzeLocalRepoCoverage:
    """Test cases to improve coverage for analyze_local_repo.py."""

    def test_clone_or_get_repo_git_error(self):
        """Test clone_or_get_repo when GitCommandError occurs."""
        with patch("ai_model_catalog.analyze_local_repo.Repo") as mock_repo:
            mock_repo.clone_from.side_effect = GitCommandError("clone", "Git error")
            result = clone_or_get_repo("test/model")
            assert result is None

    def test_analyze_repo_contents_missing_files(self):
        """Test analyze_repo_contents when files are missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty directory
            result = analyze_repo_contents(temp_dir)
            expected = {
                "README.md": False,
                "config.json": False,
                "model_index.json": False,
                "pytorch_model.bin": False,
                "tokenizer.json": False,
                "tokenizer_config.json": False,
            }
            assert result == expected

    def test_get_git_metadata_exception(self):
        """Test get_git_metadata when exception occurs."""
        with patch("ai_model_catalog.analyze_local_repo.Repo") as mock_repo:
            mock_repo.side_effect = InvalidGitRepositoryError("Not a git repo")
            result = get_git_metadata("fake_path")
            assert result == {
                "contributor_count": None,
                "last_commit_time": None,
            }

    def test_analyze_hf_repo_clone_failure(self):
        """Test analyze_hf_repo when clone fails."""
        with patch(
            "ai_model_catalog.analyze_local_repo.clone_or_get_repo"
        ) as mock_clone:
            mock_clone.return_value = None
            result = analyze_hf_repo("test/model")
            assert result == {}

    def test_cleanup_cloned_repo_directory_exists(self):
        """Test cleanup_cloned_repo when directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test directory
            test_dir = os.path.join(temp_dir, "test_model")
            os.makedirs(test_dir)

            with patch("ai_model_catalog.analyze_local_repo.os.path.join") as mock_join:
                mock_join.return_value = test_dir
                cleanup_cloned_repo("test/model", temp_dir)
                # Directory should be deleted
                assert not os.path.exists(test_dir)

    def test_cleanup_cloned_repo_directory_not_exists(self):
        """Test cleanup_cloned_repo when directory doesn't exist."""
        with patch("ai_model_catalog.analyze_local_repo.os.path.isdir") as mock_isdir:
            mock_isdir.return_value = False
            # Should not raise exception
            cleanup_cloned_repo("test/model")

    def test_analyze_repo_contents_with_files(self):
        """Test analyze_repo_contents with various files present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the specific files that the function looks for
            files_to_create = [
                "README.md",
                "config.json",
                "model_index.json",
                "pytorch_model.bin",
                "tokenizer.json",
                "tokenizer_config.json",
            ]

            for file_path in files_to_create:
                full_path = os.path.join(temp_dir, file_path)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write("test content")

            result = analyze_repo_contents(temp_dir)
            expected = {
                "README.md": True,
                "config.json": True,
                "model_index.json": True,
                "pytorch_model.bin": True,
                "tokenizer.json": True,
                "tokenizer_config.json": True,
            }
            assert result == expected
