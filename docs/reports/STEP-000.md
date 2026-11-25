# STEP-000 · Provider verification before P0 approval

## Objective and plan

Select a free-tier-eligible Gemini Flash model using this project's authenticated catalog and exercise the three LLM capabilities the sales workflow needs. Use only fictional input. Check the optional OpenAI fallback with a minimal completion.

## Results · 26 November 2026

| Check | Observed output | Interpretation |
|---|---|---|
| Gemini model listing | HTTP 200 | [VERIFIED] The model IDs and methods from the listing are reproduced below. |
| Hinglish structured extraction, gemini-3.5-flash-lite | HTTP 200, 6794 ms, exact object match | [VERIFIED] The caller had three stores, expressed a price objection, and asked about availability. The supplied product chunk was STOCK-07. |
| Same request, gemini-3.8-flash | HTTP 503 UNAVAILABLE, 1724 ms | [VERIFIED] This individual request failed. Long-run availability is unknown. |
| Hindi text streaming, gemini-3.5-flash-lite | HTTP 200, 2 text events, 1566 ms to first text, 1567 ms total | [VERIFIED] Returned “आपके पास कुल कितने स्टोर हैं?” Times include network and request setup. |
| Availability tool selection, gemini-3.5-flash-lite | HTTP 200, exact_name_and_args True | [VERIFIED] Selected check_availability with date 2026-12-02 and timezone Asia/Kolkata. The probe only declared the tool. |
| OpenAI model listing and minimal generation | HTTP 200 on listing, HTTP 429 credit_balance_exhausted on gpt-4o-mini | [VERIFIED] The configured fallback credential can list models. The attempted completion requires available credit. |

The extraction response matched this object exactly.

~~~json
{"stores":3,"objection":"price","source":"STOCK-07","intent":"check_availability"}
~~~

## Decision, limitations and sources

[VERIFIED] Select gemini-3.5-flash-lite via GEMINI_MODEL for the live text pipeline. Google lists standard input and output as free in the free tier. The planned cache is local to the application. [Official pricing](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite)

[UNKNOWN] This project's active billing tier, remaining quota, and actual billed amount. Google measures limits per project across multiple dimensions. Exact active limits belong in the rate-limiter configuration after account-level verification. [Official rate limits](https://aistudio.google.com/docs/rate-limits)

[UNKNOWN] Voice loop latency, accented speech accuracy, production retrieval quality, sustained availability and live audio performance. Each probe used one synthetic input. The source ID was supplied in the prompt. The retrieval system, tool executor, and microphone are later implementation gates.

## Proposed repository deliverables and gates

This is the pre-build inventory for approval. Filenames below describe planned artifacts.

| Gate | Files and acceptance evidence |
|---|---|
| P0 foundation | Root README.md, CLAUDE.md, CHANGELOG.md, Makefile, .env.example and .gitignore. Write docs/PRD.md, USER_STORIES.md, NON_FUNCTIONAL.md, ARCHITECTURE.md, TECH_STACK.md, DATA_MODEL.md, API_SPEC.yaml, TASKS.md, ASSUMPTIONS.md, OPEN_QUESTIONS.md, RISKS.md, DEFINITION_OF_DONE.md, TESTING_STRATEGY.md and WORKFLOW.md under docs. Record one decision per file in docs/adr/. ARCHITECTURE.md contains Mermaid system, per-turn sequence and data-flow diagrams plus responsibilities, technologies, failures and scaling per component. Validate the diagrams and the initial API contract. Wire secret scanning, dependency pins, pre-commit and GitHub Actions. Verify make on Windows. |
| P1–P4 text pipeline | React/Vite frontend and Python packages under src/api, core, llm, memory, rag and db. Add a deterministic offline text demo, provider resilience, persistent memory, and cited retrieval over bilingual data/knowledge/. Capture evaluation results and test weak matches. |
| P5–P9 voice and business workflow | src/voice, tools, crm and analytics under src. Measure STT and TTS, streaming and barge-in, test code-switching, transactional booking, CRM idempotency, scoring, escalation and post-call insights. |
| P10–P11 hero demo and reliability | tests/unit, integration, e2e, rag_eval and latency under tests. Demonstrate and record the end-to-end flow, including persisted business outcomes. Verify graceful degradation, redaction, health, metrics and UI. |
| P12 operations and business case | scripts/ for setup, verify, seed, demo and load_test. infra/Dockerfile and infra/docker-compose.yml. Complete docs/SCALABILITY.md, SECURITY.md, COSTS.md, BUSINESS_CASE.md and DEPLOYMENT.md using measured results, explicit capacity assumptions and dated official sources. |
| P13 interview readiness | docs/DIRECTORY_GUIDE.md, LIVE_CODING_CHEATSHEET.md, DEMO_SCRIPT.md and INTERVIEW_QA.md. Rehearse the fallback demo, 60-second pitch and code-specific exercises. |
| Every approved build step | Acceptance test first, then implementation, real verification output, diff review, docs/reports/STEP-XXX.md, docs/LEARNING_LOG.md and docs/CONCEPTS/ as concepts arise, TASKS and CHANGELOG updates, then a Conventional Commit. |

## Next gate

Approval to start P0. The proposed demo company sells inventory software to Indian retailers. The demo follows a bilingual inbound lead through qualification, a cited answer, an objection, a booked demo, CRM update and follow-up.

## Authenticated Gemini catalog

[VERIFIED] The table below contains the name and supportedGenerationMethods fields from a fresh authenticated models.list response. Other response fields are omitted. [API reference](https://aistudio.google.com/api-reference/models)

| Model resource | Advertised methods |
|---|---|
| models/gemini-2.5-flash | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-2.5-pro | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-2.5-flash-preview-tts | countTokens, generateContent |
| models/gemini-2.5-pro-preview-tts | countTokens, generateContent, batchGenerateContent |
| models/gemma-4-26b-a4b-it | generateContent, countTokens |
| models/gemma-4-31b-it | generateContent, countTokens |
| models/gemini-flash-latest | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-flash-lite-latest | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-pro-latest | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-2.5-flash-lite | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-2.5-flash-image | generateContent, countTokens, batchGenerateContent |
| models/gemini-3-flash-preview | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.1-pro-preview | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.1-pro-preview-customtools | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.1-flash-lite-preview | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.1-flash-lite | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3-pro-image-preview | generateContent, countTokens, batchGenerateContent |
| models/gemini-3-pro-image | generateContent, countTokens, batchGenerateContent |
| models/nano-banana-pro-preview | generateContent, countTokens, batchGenerateContent |
| models/gemini-3.1-flash-image-preview | generateContent, countTokens, batchGenerateContent |
| models/gemini-3.1-flash-image | generateContent, countTokens, batchGenerateContent |
| models/gemini-3.1-flash-lite-image | generateContent, countTokens, batchGenerateContent |
| models/gemini-nano-banana-2.1 | generateContent, countTokens, batchGenerateContent |
| models/gemini-3.5-flash | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.5-flash-lite | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-omni-flash-preview | generateContent, countTokens |
| models/gemini-omni-1.1-flash | generateContent, countTokens |
| models/gemini-omni-1.2-flash | generateContent, countTokens |
| models/gemini-3.5-transcribe | generateContent, countTokens |
| models/gemini-3.6-flash | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.7-flash | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-3.8-flash | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-4-argon | generateContent, countTokens, batchGenerateContent |
| models/gemini-4-carbon | generateContent, countTokens, batchGenerateContent |
| models/gemini-4-hydrogen | generateContent, countTokens, batchGenerateContent |
| models/gemini-4-neon | generateContent, countTokens, batchGenerateContent |
| models/lyria-3-clip-preview | generateContent, countTokens |
| models/lyria-3-pro-preview | generateContent, countTokens |
| models/lyria-3.5 | generateContent, countTokens |
| models/gemini-3.1-flash-tts-preview | generateContent, countTokens, batchGenerateContent |
| models/gemini-3.8-flash-tts | generateContent, countTokens, batchGenerateContent |
| models/gemini-3.8-flash-lite-tts | generateContent, countTokens, batchGenerateContent |
| models/gemini-robotics-er-2-preview | generateContent, countTokens, createCachedContent, batchGenerateContent |
| models/gemini-2.5-computer-use-preview-10-2025 | generateContent, countTokens |
| models/antigravity-preview-05-2026 | generateContent, countTokens |
| models/antigravity-preview-09-2026 | generateContent, countTokens |
| models/antigravity-preview-latest | generateContent, countTokens |
| models/deep-research-max-preview-04-2026 | generateContent, countTokens |
| models/deep-research-preview-04-2026 | generateContent, countTokens |
| models/gemini-embedding-001 | embedContent, countTextTokens, countTokens, asyncBatchEmbedContent |
| models/gemini-embedding-2-preview | embedContent, countTextTokens, countTokens, asyncBatchEmbedContent |
| models/gemini-embedding-2 | embedContent, countTextTokens, countTokens, asyncBatchEmbedContent |
| models/aqa | generateAnswer |
| models/gemini-3.5-transcribe-live | bidiGenerateContent |
| models/gemini-2.5-flash-native-audio-latest | countTokens, bidiGenerateContent |
| models/gemini-2.5-flash-native-audio-preview-09-2025 | countTokens, bidiGenerateContent |
| models/gemini-2.5-flash-native-audio-preview-12-2025 | countTokens, bidiGenerateContent |
| models/gemini-3.1-flash-live-preview | bidiGenerateContent |
| models/gemini-3.8-live | bidiGenerateContent |
| models/gemini-3.8-live-extended-thinking | bidiGenerateContent |
| models/genie-4 | bidiGenerateContent |
| models/gemini-robotics-er-2-streaming-preview | bidiGenerateContent |
| models/gemini-3.5-live-translate-preview | bidiGenerateContent |
| models/lyria-realtime-exp | bidiGenerateMusic |
| models/gemini-decision-1 | createDecision |
