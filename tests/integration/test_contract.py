from pathlib import Path

import yaml
from openapi_spec_validator import validate

from src.api.app import create_app


def test_published_contract_matches_live_routes(monkeypatch, tmp_path):
    contract = Path(__file__).resolve().parents[2] / "docs" / "API_SPEC.yaml"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    spec = yaml.safe_load(contract.read_text(encoding="utf-8"))
    validate(spec)
    assert spec == create_app().openapi()
