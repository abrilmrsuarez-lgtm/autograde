from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from src.autograde.cli import check_repository


# ─── Git helpers ──────────────────────────────────────────────────────────────

def git(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


def init_repo(path: Path) -> None:
    git(path, "init", "-b", "main")
    git(path, "config", "user.email", "test@test.com")
    git(path, "config", "user.name", "Test User")


def commit_file(path: Path, filename: str, content: str, message: str) -> None:
    (path / filename).write_text(content, encoding="utf-8")
    git(path, "add", filename)
    git(path, "commit", "-m", message)


def empty_commit(path: Path, message: str) -> None:
    git(path, "commit", "--allow-empty", "-m", message)


def create_branch(path: Path, name: str) -> None:
    git(path, "checkout", "-b", name)
    git(path, "checkout", "main")


# ─── is_git_repository ────────────────────────────────────────────────────────

def test_is_git_repository_true(tmp_path: Path):
    init_repo(tmp_path)
    empty_commit(tmp_path, "init")
    result = check_repository(str(tmp_path))
    assert result["is_git_repository"] is True


def test_is_git_repository_false(tmp_path: Path):
    # tmp_path exists but is NOT a git repo
    result = check_repository(str(tmp_path))
    assert result["is_git_repository"] is False


def test_non_git_repo_all_false(tmp_path: Path):
    result = check_repository(str(tmp_path))
    assert result == {
        "is_git_repository": False,
        "has_main_branch": False,
        "has_feature_branch": False,
        "file1_exists_in_main": False,
    }


# ─── has_main_branch ──────────────────────────────────────────────────────────

def test_has_main_branch_true(tmp_path: Path):
    init_repo(tmp_path)
    empty_commit(tmp_path, "init")
    result = check_repository(str(tmp_path))
    assert result["has_main_branch"] is True


# ─── has_feature_branch ───────────────────────────────────────────────────────

def test_has_feature_branch_true(tmp_path: Path):
    init_repo(tmp_path)
    empty_commit(tmp_path, "init")
    create_branch(tmp_path, "feature")
    result = check_repository(str(tmp_path))
    assert result["has_feature_branch"] is True


def test_has_feature_branch_false_when_not_created(tmp_path: Path):
    init_repo(tmp_path)
    empty_commit(tmp_path, "init")
    result = check_repository(str(tmp_path))
    assert result["has_feature_branch"] is False


# ─── file1_exists_in_main ─────────────────────────────────────────────────────

def test_file1_exists_in_main_true(tmp_path: Path):
    init_repo(tmp_path)
    commit_file(tmp_path, "file1.txt", "hello", "Add file1.txt")
    result = check_repository(str(tmp_path))
    assert result["file1_exists_in_main"] is True


def test_file1_exists_in_main_false_when_absent(tmp_path: Path):
    init_repo(tmp_path)
    empty_commit(tmp_path, "init")
    result = check_repository(str(tmp_path))
    assert result["file1_exists_in_main"] is False


def test_file1_only_on_feature_not_counted(tmp_path: Path):
    """file1.txt committed only on feature should NOT satisfy the main check."""
    init_repo(tmp_path)
    empty_commit(tmp_path, "init")
    git(tmp_path, "checkout", "-b", "feature")
    commit_file(tmp_path, "file1.txt", "hello", "Add file1.txt on feature")
    git(tmp_path, "checkout", "main")
    result = check_repository(str(tmp_path))
    assert result["file1_exists_in_main"] is False


# ─── Full passing scenario ────────────────────────────────────────────────────

def test_all_conditions_pass(tmp_path: Path):
    init_repo(tmp_path)
    commit_file(tmp_path, "file1.txt", "hello", "Add file1.txt")
    create_branch(tmp_path, "feature")
    result = check_repository(str(tmp_path))
    assert result == {
        "is_git_repository": True,
        "has_main_branch": True,
        "has_feature_branch": True,
        "file1_exists_in_main": True,
    }


# ─── Partial scenarios (matching the provided spec exactly) ──────────────────

def test_valid_repo_all_conditions(tmp_path: Path):
    init_repo(tmp_path)
    commit_file(tmp_path, "file1.txt", "hello", "Add file1.txt")
    create_branch(tmp_path, "feature")
    results = check_repository(str(tmp_path))
    assert results["is_git_repository"]
    assert results["has_main_branch"]
    assert results["has_feature_branch"]
    assert results["file1_exists_in_main"]


def test_missing_feature_branch(tmp_path: Path):
    init_repo(tmp_path)
    commit_file(tmp_path, "file1.txt", "hello", "Add file1.txt")
    results = check_repository(str(tmp_path))
    assert results["is_git_repository"]
    assert results["has_main_branch"]
    assert not results["has_feature_branch"]
    assert results["file1_exists_in_main"]


def test_missing_file1(tmp_path: Path):
    init_repo(tmp_path)
    empty_commit(tmp_path, "Initial commit")
    create_branch(tmp_path, "feature")
    results = check_repository(str(tmp_path))
    assert results["is_git_repository"]
    assert results["has_main_branch"]
    assert results["has_feature_branch"]
    assert not results["file1_exists_in_main"]