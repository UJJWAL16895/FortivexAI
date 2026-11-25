import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "secret_scan.py"


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".env\n")
    (tmp_path / ".env").write_text("OPENAI_API_KEY=local-only-test-value\n")
    return tmp_path


def scan(root):
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=root, capture_output=True)


def test_ignored_local_credentials_are_allowed(repo):
    assert scan(repo).returncode == 0


def test_staged_leak_remains_visible_after_worktree_cleanup(repo):
    value = "sk-" + "a" * 42
    file = repo / "example.txt"
    file.write_text(value)
    git(repo, "add", "example.txt")
    file.write_text("clean")
    result = scan(repo)
    assert result.returncode == 1
    assert value.encode() not in result.stdout + result.stderr


def test_untracked_file_cannot_copy_local_key(repo):
    (repo / "notes.txt").write_text("local-only-test-value")
    assert scan(repo).returncode == 1


def test_forced_add_of_env_is_rejected(repo):
    git(repo, "add", "-f", ".env")
    assert scan(repo).returncode == 1
