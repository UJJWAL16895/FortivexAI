# Technology decisions

[VERIFIED] P0 uses Python 3.13.2, FastAPI, Uvicorn, pydantic-settings, pytest/pytest-asyncio, HTTPX, Ruff, mypy, pre-commit and an OpenAPI validator. The exact installed Python environment is in requirements.lock. docs/API_SPEC.yaml is validated against the running application's route definition. The docs-only Mermaid CLI has its own npm lock under tools/diagrams.

[VERIFIED] P1 uses React 19.3.1, Vite 8.3.8, Node 24.11.1 and websockets 17.4. FastAPI serves the compiled UI and validates each socket message. [ASSUMED] Provider protocols will cover LLM, STT, TTS, embeddings and CRM. Local SQLite, multilingual sentence-transformers and a local vector index are the planned starting point. Pin each new dependency after an installed integration check.

[VERIFIED] See STEP-000 for actual model IDs and generation probes. [UNKNOWN] Target A/B pair, live audio merit, deployable CPU STT model and vector library compatibility with this Python build. Resolve with a minimal measured integration before committing a dependency choice.
