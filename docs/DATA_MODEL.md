# Data model

[ASSUMED] Proposed logical schema for the hero demo. P0 has no persistent tables. Record actual migration IDs here as the storage gates land.

| Entity and key | Stored fields | Invariant |
|---|---|---|
| Tenant, Lead (tenant_id, lead_id) | Name, company, verified contact lookup, preferred language, need, timeline, budget and objections | Tenant-scoped unique normalized contact; update an existing lead on repeat |
| Call (call_id) | Tenant, lead, start/end, consent state, outcome | End once, assign post-call work once |
| Turn (call_id, seq) | Speaker, language, redacted transcript, provider, timing, evidence IDs | Sequence is unique per call; preserve interrupted turns |
| ProfileUpdate (call_id, seq) | Validated extraction, BANT evidence, sentiment and version | Apply by version; reprocessing cannot overwrite a newer value |
| DocumentChunk (chunk_id, version) | Source, locale, passage, embedding model and offsets | Citation resolves to the ingested text version |
| Slot (resource_id, start_utc) | Start/end instants and resource | Server generates canonical slots; store display timezone separately |
| Booking (booking_id) | Lead, slot, status, request key and timestamps | Unique active booking per slot; unique request key and request fingerprint |
| Outbox / Job (job_id) | Event type, aggregate version, attempt, lease, next retry | Write business change and event atomically; consumer deduplicates |
| Summary (call_id) | Evidence-based notes, next action, email draft and aggregate inputs | One published summary per call revision |

At confirmation, validate timezone, selected slot, request fingerprint and ownership. Within one transaction claim the slot, write the appointment and lead update, and append the CRM event. A conflict triggers fresh availability. Rescheduling must claim the new slot before releasing the old in the same transaction. Production migration requires a Postgres constraint, concurrent integration tests, backfill verification and an explicit rollback point.
