# Directory guide

| Path | Start here when… |
|---|---|
| src/core/settings.py | Changing startup validation, credential handling or configured mode |
| src/api/app.py | Extending FastAPI routes or the Health response |
| src/api/text_session.py and src/llm/mock.py | Tracing a validated text turn and changing the deterministic replies |
| frontend/src/main.jsx and styles.css | Tracing connection state, transcript rendering and responsive console styling |
| scripts/demo.py | Running the same WebSocket protocol from a three-turn script |
| docs/API_SPEC.yaml | Checking the published HTTP contract against runtime |
| scripts/tasks.py and Makefile | Following what setup, verify, run and scan execute on Windows or Linux |
| scripts/secret_scan.py | Reviewing how staged and working content are scanned |
| tests/unit and tests/integration | Understanding failure cases, ASGI liveness and contract drift |
| tools/diagrams | Rebuilding Mermaid figures with the locked documentation tool |
| infra | Inspecting container build context, launch settings and health checks |
| docs/adr, docs/reports and docs/CONCEPTS | Comparing a decision, its measured result and a teaching example |

Setup creates the feature and evaluation directories reserved for later gates. Planned ownership: src/voice for audio lifecycle, llm for chat adapters, rag for evidence retrieval, memory for session state, tools for validated actions, crm for integrations, analytics for analysis/insights, db for persistence. data/knowledge holds approved fictional material. tests/e2e, rag_eval and latency hold independent evaluations as corresponding features land.
