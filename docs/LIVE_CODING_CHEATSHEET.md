# Live coding · Executable P0 recipes

**Trace failed startup.** Open Settings.validate_live_config in src/core/settings.py. Run `.venv/Scripts/python.exe -m pytest tests/unit/test_settings.py -q` on Windows. Ask which combinations require a live key and model. Inspect sanitized validation messages only.

**Change the health endpoint.** Edit create_app and Health in src/api/app.py. Change the expected response in tests/integration/test_health.py. Regenerate docs/API_SPEC.yaml from create_app().openapi() with yaml.safe_dump and run tests/integration/test_contract.py. The contract must reflect precisely the schema served to clients.

**Debug a verification failure.** In scripts/tasks.py follow main in execution order. Run the failing check independently, then both Windows and Make verify commands. For a secret-scan failure inspect your own changes privately, correct both working and staged content, and rerun. Never paste suspect lines into chat or reports.

Recipes for provider swaps, languages, scoring, RAG, booking, CRM fields, tool registration and latency investigation are acceptance deliverables when those modules exist.
