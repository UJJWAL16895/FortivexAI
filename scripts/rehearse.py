"""Run temporary live-coding edits in a clean scratch clone, then restore files."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable


def recipe(label, filename, before, after, check, *extra):
    path = Path(filename)
    original = path.read_text(encoding="utf-8")
    if before not in original:
        raise RuntimeError(label + ": anchor missing")
    line = original[: original.index(before)].count("\n") + 1
    copies = [(path, original)]
    try:
        path.write_text(original.replace(before, after, 1), encoding="utf-8")
        if extra:
            manifest = Path(extra[0])
            contents = manifest.read_text(encoding="utf-8")
            copies.append((manifest, contents))
            approval = json.loads(contents)
            approval[path.name] = hashlib.sha256(
                path.read_text(encoding="utf-8").encode()
            ).hexdigest()
            manifest.write_text(json.dumps(approval), encoding="utf-8")
        subprocess.run([PYTHON, "-c", check], check=True)
        print(f"{label} | {filename}:{line} | PASS (restored)", flush=True)
    finally:
        for target, content in copies:
            target.write_text(content, encoding="utf-8", newline="\n")


def main():
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    if branch != "codex/interview-rehearsal":
        raise SystemExit("Use the clean codex/interview-rehearsal scratch branch")
    recipe(
        "Language",
        "src/memory/session.py",
        '"sahi hai",',
        '"sahi hai",\n    "aama",',
        "from src.memory.session import LeadSession; s=LeadSession(); s.handle('three stores'); s.handle('aama'); assert s.profile.store_count==3",
    )
    recipe(
        "Qualification criteria",
        "src/analytics/core.py",
        "score >= 75",
        "score >= 100",
        "from src.analytics.core import *; assert summarize_call([analyze_turn('I am the owner. We need it tomorrow.')],booked=False).rating=='Warm'",
    )
    recipe(
        "Booking rule",
        "src/crm/store.py",
        "for hour in (11, 15):",
        "for hour in (12, 15):",
        "from tempfile import TemporaryDirectory; from pathlib import Path; from src.crm.store import CRM; t=TemporaryDirectory(); assert 'T12:' in CRM(Path(t.name)/'test.db').offer()",
    )
    recipe(
        "Knowledge doc",
        "data/knowledge/faq.json",
        '"csv upload"',
        '"csv upload", "inventory sheet transfer"',
        "from src.rag.index import Knowledge; assert Knowledge.load().lookup('inventory sheet transfer').chunk.id=='import'",
        "data/knowledge/approval.json",
    )
    recipe(
        "CRM field",
        "src/memory/session.py",
        "company: str | None = None",
        "company: str | None = None\n    role: str | None = None",
        "from tempfile import TemporaryDirectory; from pathlib import Path; from src.crm.store import CRM; from src.memory.session import LeadProfile; t=TemporaryDirectory(); c=CRM(Path(t.name)/'test.db'); c.save('x@example.test',LeadProfile(role='owner').model_dump()); assert c.load('x@example.test')['role']=='owner'",
    )
    recipe(
        "Sentiment label",
        "src/analytics/core.py",
        'Literal["Positive", "Neutral", "Negative"]',
        'Literal["Positive", "Neutral", "Negative", "Concerned"]',
        "from src.analytics.core import TurnAnalysis; assert TurnAnalysis(sentiment='Concerned',signals=[]).sentiment=='Concerned'",
    )
    recipe(
        "Swap provider",
        "src/core/settings.py",
        '= "edge"',
        '= "browser"',
        "from src.core.settings import Settings; assert Settings(_env_file=None).voice_tts=='browser'",
    )
    recipe(
        "Endpoint",
        "src/api/app.py",
        '    @app.get("/health"',
        '    @app.get("/ping")\n    async def ping() -> dict[str, bool]:\n        return {"ready": True}\n\n    @app.get("/health"',
        "from fastapi.testclient import TestClient; from src.api.app import create_app; assert TestClient(create_app()).get('/ping').json()=={'ready':True}",
    )
    recipe(
        "Latency spike",
        "src/llm/reply.py",
        "REPLY_TIMEOUT = 9.0",
        "REPLY_TIMEOUT = 0.05",
        "import pytest; raise SystemExit(pytest.main(['tests/integration/test_reliability.py','-q','-k','slow_provider']))",
    )
    recipe(
        "RAG miss",
        "src/rag/index.py",
        "SEMANTIC_THRESHOLD = 0.58",
        "SEMANTIC_THRESHOLD = 0.64",
        "from src.rag.index import Knowledge; assert Knowledge.load().lookup('40% annual discount').chunk is None",
    )


if __name__ == "__main__":
    main()
