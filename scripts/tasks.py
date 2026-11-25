"""Cross-platform commands. Run from the repository root with Python 3.13."""

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".venv"
PYTHON = ENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
NPM = "npm.cmd" if os.name == "nt" else "npm"


def run(*args: str | Path) -> None:
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=["setup", "verify", "run", "scan", "demo"])
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.task == "setup":
        if sys.version_info[:2] != (3, 13):
            parser.error("Use Python 3.13 for the verified dependency lock.")
        if not PYTHON.exists():
            venv.EnvBuilder(with_pip=True).create(ENV)
        run(PYTHON, "-m", "pip", "install", "-r", "requirements.lock")
        run(PYTHON, "-m", "pre_commit", "install")
        run(NPM, "--prefix", "frontend", "ci", "--no-audit", "--no-fund")
        run(NPM, "--prefix", "frontend", "run", "build")
        for directory in (
            "src/voice",
            "src/llm",
            "src/rag",
            "src/memory",
            "src/tools",
            "src/crm",
            "src/analytics",
            "src/db",
            "data/knowledge",
            "tests/e2e",
            "tests/rag_eval",
            "tests/latency",
        ):
            (ROOT / directory).mkdir(parents=True, exist_ok=True)
        return
    if not PYTHON.exists():
        parser.error("Run scripts/tasks.py setup first with Python 3.13.")
    if args.task == "scan":
        run(PYTHON, "scripts/secret_scan.py")
    elif args.task == "demo":
        run(PYTHON, "-m", "scripts.demo", "--port", str(args.port))
    elif args.task == "run":
        if not (ROOT / "frontend/dist/index.html").is_file():
            parser.error("Build the console with scripts/tasks.py setup first.")
        run(
            PYTHON,
            "-m",
            "uvicorn",
            "src.api.app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
            "--ws",
            "websockets-sansio",
            "--ws-max-size",
            "16384",
            "--no-access-log",
        )
    else:
        run(PYTHON, "scripts/secret_scan.py")
        run(PYTHON, "-m", "pip", "check")
        run(PYTHON, "-m", "ruff", "check", ".")
        run(PYTHON, "-m", "ruff", "format", "--check", ".")
        run(PYTHON, "-m", "mypy")
        run(PYTHON, "-m", "pytest", "-q")
        run(NPM, "--prefix", "frontend", "run", "build")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
