"""
Autograde: A Python CLI tool to evaluate Git repositories.

This package provides functionality to check if a repository meets specific criteria:
- Is a valid Git repository
- Has a main branch
- Has a feature branch on the remote
- Has file1.txt on the main branch
"""

import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


__version__ = "0.1.0"


class RepositoryValidator:
    """Validates a Git repository against specified criteria."""

    def __init__(self, repo_url: str):
        """
        Initialize the validator with a repository URL.

        Args:
            repo_url: The URL of the Git repository to validate.
        """
        self.repo_url = repo_url
        self.temp_dir = None

    def _run_git_command(self, *args, cwd=None):
        """
        Execute a git command and return the output.

        Args:
            *args: Git command arguments.
            cwd: Working directory for the command.

        Returns:
            Command output as string, or None if command fails.
        """
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None

    def _is_valid_git_repository(self):
        """
        Check if the URL points to a valid Git repository.

        Returns:
            True if valid, False otherwise.
        """
        try:
            # Verify the URL format
            parsed = urlparse(self.repo_url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # Try to list remote refs to verify it's a valid git repo
            result = subprocess.run(
                ["git", "ls-remote", "--heads", self.repo_url],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _main_branch_exists(self):
        """
        Check if the main branch exists on the remote.

        Returns:
            True if main branch exists, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", self.repo_url, "main"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and result.stdout.strip()
        except Exception:
            return False

    def _feature_branch_exists(self):
        """
        Check if the feature branch exists on the remote.

        Returns:
            True if feature branch exists, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", self.repo_url, "feature"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and result.stdout.strip()
        except Exception:
            return False

    def _file1_exists_on_main(self):
        """
        Check if file1.txt exists on the main branch.

        Returns:
            True if file1.txt exists on main, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "cat-file", "-e", f"refs/heads/main:file1.txt"],
                cwd=self.temp_dir,
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                # Try with origin/main if local doesn't work
                result = subprocess.run(
                    ["git", "cat-file", "-e", f"refs/remotes/origin/main:file1.txt"],
                    cwd=self.temp_dir,
                    capture_output=True,
                    timeout=10,
                )
            return result.returncode == 0
        except Exception:
            return False

    def validate(self):
        """
        Validate the repository against all criteria.

        Returns:
            A dictionary with validation results for each criterion.
        """
        results = {
            "is_valid_repository": self._is_valid_git_repository(),
            "main_branch_exists": self._main_branch_exists(),
            "feature_branch_exists": self._feature_branch_exists(),
            "file1_on_main": False,
        }

        # Only try to check for file1.txt if it's a valid repo
        if results["is_valid_repository"]:
            import tempfile
            import shutil

            self.temp_dir = tempfile.mkdtemp()
            try:
                # Clone the repository to check for file1.txt
                clone_result = subprocess.run(
                    ["git", "clone", "--quiet", "--depth=1", self.repo_url, self.temp_dir],
                    capture_output=True,
                    timeout=30,
                )
                if clone_result.returncode == 0:
                    results["file1_on_main"] = self._file1_exists_on_main()
            except Exception:
                pass
            finally:
                # Cleanup
                if self.temp_dir and Path(self.temp_dir).exists():
                    shutil.rmtree(self.temp_dir, ignore_errors=True)

        return results

    def get_summary(self):
        """
        Get a validation summary for the repository.

        Returns:
            A dictionary with the validation results and overall status.
        """
        results = self.validate()
        all_passed = all(results.values())

        return {
            "repository_url": self.repo_url,
            "is_valid_repository": results["is_valid_repository"],
            "main_branch_exists": results["main_branch_exists"],
            "feature_branch_exists": results["feature_branch_exists"],
            "file1_on_main": results["file1_on_main"],
            "all_checks_passed": all_passed,
        }
