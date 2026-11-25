# Technology decisions

[VERIFIED] P0 uses Python 3.13.2, FastAPI, Uvicorn, pydantic-settings, pytest/pytest-asyncio, HTTPX, Ruff, mypy, pre-commit and an OpenAPI validator. The exact installed Python environment is in requirements.lock. docs/API_SPEC.yaml is validated against the running application's route definition. The docs-only Mermaid CLI has its own npm lock under tools/diagrams.

[ASSUMED] React/Vite will deliver the demo console at P1. Provider protocols will cover LLM, STT, TTS, embeddings and CRM. Keep provider credentials on the server. Local SQLite, multilingual sentence-transformers and a local vector index are the planned starting point. Pin each new dependency after installation and a test through its normal entry point.

[VERIFIED] See STEP-000 for actual model IDs and generation probes. [UNKNOWN] Target A/B pair, live audio merit, deployable CPU STT model and vector library compatibility with this Python build. Resolve with a minimal measured integration before committing a dependency choice.
