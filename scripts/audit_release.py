"""Scan reachable Git objects, the shareable worktree, and built assets."""

import re
from collections import Counter
from pathlib import Path
from subprocess import PIPE, Popen

from dotenv import dotenv_values
from secret_scan import PATTERNS, git, prohibited

EMAIL = re.compile(rb"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(rb"(?<![\d\w])(?:\+91[ -]?)?[6-9]\d{9}(?![\d\w])")
FIXTURE_PHONES = {b"9876543210", b"8765432109", b"9123456789", b"9999999999"}


def main() -> int:
    config = dotenv_values(".env", interpolate=False) if Path(".env").is_file() else {}
    values = [
        value.encode()
        for name, value in config.items()
        if (name.endswith("_API_KEY") or name == "PUBLIC_ACCESS_CODE")
        and value
        and not value.startswith("replace_with_")
    ]

    def scan(data: bytes, count: Counter[str]) -> None:
        count["files"] += 1
        count["credentials"] += int(
            any(value in data for value in values) or any(p.search(data) for p in PATTERNS)
        )
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return
        count["email_candidates"] += sum(
            not address.lower().endswith((b".test", b".example", b".invalid"))
            for address in EMAIL.findall(data)
        )
        count["phone_candidates"] += sum(
            re.sub(rb"\D", b"", phone)[-10:] not in FIXTURE_PHONES for phone in PHONE.findall(data)
        )

    history: Counter[str] = Counter()
    with Popen(["git", "cat-file", "--batch"], stdin=PIPE, stdout=PIPE) as blobs:
        assert blobs.stdin and blobs.stdout
        for entry in git("rev-list", "--objects", "--all").splitlines():
            oid, _, name = entry.partition(b" ")
            blobs.stdin.write(oid + b"\n")
            blobs.stdin.flush()
            _, kind, size = blobs.stdout.readline().split()
            data = blobs.stdout.read(int(size))
            blobs.stdout.read(1)
            if kind == b"blob":
                history["prohibited_paths"] += int(prohibited(Path(name.decode(errors="replace"))))
                scan(data, history)
        blobs.stdin.close()

    current: Counter[str] = Counter()
    for name in git("ls-files", "-co", "--exclude-standard", "-z").split(b"\0"):
        if name:
            path = Path(name.decode())
            if path.is_file() and not path.is_symlink():
                current["prohibited_paths"] += int(prohibited(path))
                scan(path.read_bytes(), current)

    build: Counter[str] = Counter()
    for path in Path("frontend/dist").rglob("*"):
        if path.is_file():
            scan(path.read_bytes(), build)
    for scope, count in (
        ("history blobs", history),
        ("shareable worktree", current),
        ("build", build),
    ):
        print(
            f"{scope}: "
            + ", ".join(
                f"{key}={count[key]}"
                for key in (
                    "files",
                    "prohibited_paths",
                    "credentials",
                    "email_candidates",
                    "phone_candidates",
                )
            )
        )
    return int(
        not build["files"]
        or any(
            count["credentials"] or count["prohibited_paths"] for count in (history, current, build)
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
