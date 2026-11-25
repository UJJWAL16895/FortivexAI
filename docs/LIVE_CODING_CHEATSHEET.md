# Live coding on a scratch branch

[VERIFIED] Run scripts/rehearse.py from a clean scratch clone on branch codex/interview-rehearsal. The script records lines, runs focused checks and restores the edited files.

| Recipe | Anchor | Rehearsed change |
|---|---|---|
| Language variant | src/memory/session.py:24 | Add a Roman confirmation alias. |
| Qualification | src/analytics/core.py:78 | Raise the Hot threshold and check Warm. |
| Booking | src/crm/store.py:79 | Move the first slot to noon. |
| Knowledge doc | data/knowledge/faq.json:12 and approval.json | Add an alias and recompute its digest. |
| CRM field | src/memory/session.py:51 | Add a role and test persistence. |
| Sentiment | src/analytics/core.py:8 | Add a validated Concerned label. |
| Provider | src/core/settings.py:26 | Select browser TTS in settings. |
| Endpoint | src/api/app.py:81 | Serve and call GET /ping. |
| Latency | src/llm/reply.py:26 | Shorten the deadline and test fallback. |
| RAG miss | src/rag/index.py:19 | Inspect the threshold and check abstention. |

The locale rehearsal exercises a language variant only. A production locale also needs STT and TTS support, localized answers and voice fixtures.
