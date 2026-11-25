import httpx
import pytest


@pytest.mark.asyncio
async def test_health_contract_is_offline_and_contains_no_credentials(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AGENT_MODE", "mock")
    from src.api.app import create_app

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "mock"}
