import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDES = ("INTERVIEW_WHERE_IS_WHAT.md", "INTERVIEW_ONE_PAGE.md")
REPO_PATH = re.compile(
    r"(?<![\w./\\-])"
    r"(?:(?:src|frontend|tests|scripts|docs|data|infra|tools|\.github)"
    r"(?:[/\\][\w.-]+)+"
    r"|\.env\.example|\.gitignore|Makefile|[\w-]+\.(?:md|lock|toml))"
    r"(?![\w.-])"
)
GENERATED_PREFIXES = ("frontend/dist/", "data/runtime/")


def test_interview_guides_reference_existing_repo_paths():
    missing = []
    for name in GUIDES:
        guide = ROOT / "docs" / name
        for number, line in enumerate(guide.read_text(encoding="utf-8-sig").splitlines(), 1):
            for match in REPO_PATH.finditer(line):
                path = match.group().replace("\\", "/")
                if not path.startswith(GENERATED_PREFIXES) and not (ROOT / path).exists():
                    missing.append(f"{name}:{number}: {path}")
    assert not missing, "\n".join(missing)
