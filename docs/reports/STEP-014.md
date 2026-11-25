# STEP-014 · Final operational evidence

The mock text load test ran client and one Uvicorn server on the Windows Ryzen 7 5800H. It replayed five cited requests per connection from 10 through 500 concurrent sessions, with no cloud calls. The table and throughput knee are in SCALABILITY.md. Voice fleet load is NOT MEASURED. The local speech timing in STEP-006 supplies a separate CPU-stage observation.

## Quiz

1. **Does 100,000 registrations mean 100,000 sockets?** No. The planning scenario results in about 125 peak sockets.
2. **What leveled off in the mock run?** Completed turns per second, even as p95 increased.
3. **What replaces SQLite at scale?** A Postgres primary for writes and read replicas for reports.
4. **What replaces local CPU speech?** Warm GPU workers or managed streaming STT.
5. **What funds the paid scenario?** An explicit usage rate and a platform fee, subject to pilot validation.

## Scratch live-coding verification

[VERIFIED] On the isolated codex/interview-rehearsal clone, scripts/rehearse.py reported PASS and restored each edit. The ten checks printed memory/session.py:24 and :51, analytics/core.py:78 and :8, crm/store.py:79, knowledge/faq.json:12 plus the approval hash, core/settings.py:26, api/app.py:81, llm/reply.py:26 and rag/index.py:19. These line numbers refer to the scratch base. Git reported no diff after restoration and pytest returned 41 passed in 7.30s. Each edit had a focused check. The full suite ran after restoring all changes. The language exercise changed an alias, not an entire language, and the sentiment exercise checked the schema, not the classifier.
