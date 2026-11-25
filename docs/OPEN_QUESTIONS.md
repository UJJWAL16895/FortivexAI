# Open questions

| Status | Question | Safe operating decision and closure gate |
|---|---|---|
| [UNKNOWN] | What project-level Gemini RPM, TPM, RPD and billing tier apply? | Default to mock, limit probes and capture account-specific limits before P2 live defaults. Never label a local estimate as remaining provider quota. |
| [UNKNOWN] | Which catalog pair meets short-turn quality and latency with minimal thinking? | A is provisional from STEP-000. Leave B unset until P2 evidence. |
| [UNKNOWN] | Is paid fallback usable? | STEP-000 returned exhausted credit. Keep OpenAI outside the default chain. |
| [UNKNOWN] | Can Gemini Live demonstrate lower first-audio latency on this free tier? | Compare at P5; use the pipeline for the primary design. |
| [UNKNOWN] | How well do both speech stacks handle real English and Hindi speakers? | Same audio, human-checked references and identical TTS scripts at P5. |
| [UNKNOWN] | Which local embedding/index combination installs and serves reliably on the demo machine? | P4 install and retrieval probe before pinning. |
| [UNKNOWN] | Which retention periods, consent flow, outbound rules and production SLAs apply? | Fictional inbound data and no retained audio by default; review by jurisdiction and deployment at P12. |
## Optional depth deferrals

- **Webhook adapter.** The current prototype has a concrete SQLite CRM class and no CRMAdapter contract. A safe webhook path needs an explicit delivery/outbox boundary and egress policy. Keep the demo local.
- **Additional locale.** STT route types, readback templates and voice mapping currently live in code. Adding a locale through configuration alone requires a larger interface change and bilingual test corpus. Existing fixture coverage stays in place.
- **Two-turn automatic handoff.** Current analysis is queued after replying and only publishes completed reports. An immediate handoff requires a live sequencing and CRM flag contract. The current report already suggests specialist review on negative calls. Preserve the tested asynchronous path.
- **Further Hindi tuning.** Keep the accepted 3.98-second sample and the measured cause. GPU/streaming STT remains the production design.
- **Raw analytics payloads.** Persist the validated report and ordered sentiments. Retaining verbatim buyer turns would change the data-retention boundary. Export contains derived fields.
