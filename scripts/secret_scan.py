"""Check the Git index and non-ignored working tree without printing matched data."""

import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

PATTERNS = (
    re.compile(rb"AIza[\w-]{35}"),
    re.compile(rb"sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    re.compile(
        rb"(?im)^\s*(?:GEMINI_API_KEY|OPENAI_API_KEY)\s*=\s*"
        rb"(?!replace_with_)[\"']?[a-zA-Z0-9_-]{12,}"
    ),
)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def prohibited(path: Path) -> bool:
    parts = path.parts
    return (
        (path.name.startswith(".env.") or path.name == ".env")
        and path.name != ".env.example"
        or path.suffix.lower() in {".key", ".pem"}
        or path.as_posix().startswith("data/recordings/")
        or any(re.search(r"\.(?:db|sqlite3?)(?:-.*)?$", part, re.I) for part in parts)
    )


def main() -> int:
    os.chdir(os.fsdecode(git("rev-parse", "--show-toplevel").rstrip(b"\r\n")))
    config = dotenv_values(".env", interpolate=False) if Path(".env").is_file() else {}
    values = [
        v.encode()
        for k, v in config.items()
        if k.endswith("_API_KEY") and v and not v.startswith("replace_with_")
    ]

    def unsafe(data: bytes) -> bool:
        return any(v in data for v in values) or any(pattern.search(data) for pattern in PATTERNS)

    # Read index blobs by object ID: unstaged edits cannot hide a staged credential.
    entries = git("ls-files", "--stage", "-z").split(b"\0")
    failures = 0
    for entry in filter(None, entries):
        meta, name = entry.split(b"\t", 1)
        mode, oid, _stage = meta.split()
        path = Path(os.fsdecode(name))
        if prohibited(path) or (
            mode != b"160000" and unsafe(git("cat-file", "blob", oid.decode()))
        ):
            failures += 1

    paths = git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    for raw in filter(None, paths.split(b"\0")):
        path = Path(os.fsdecode(raw))
        if prohibited(path) or (
            not path.is_symlink() and path.is_file() and unsafe(path.read_bytes())
        ):
            failures += 1
    if failures:
        print(f"Secret scan blocked {failures} index/worktree findings (contents suppressed).")
        return 1
    print("Secret scan: clean (Git index and non-ignored working tree).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
