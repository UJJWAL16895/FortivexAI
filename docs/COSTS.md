# Cost model

Use the same workload assumptions as SCALABILITY.md. Meter audio minutes, provider input, output and thinking tokens, TTS units, storage, egress and worker time independently. Count retries and analytics. With per-million token prices, estimated LLM cost per minute is (input tokens × input price + billable output tokens × output price) / 1,000,000. Add STT cost, TTS cost and allocated infrastructure per minute. If thinking tokens already appear in billable output, count them once.

| Registered buyers | Scenario calls/day | Scenario minutes/day | Daily variable cost at measured blended rate c per minute |
|---:|---:|---:|---:|
| 1,000 | 50 | 250 | 250 × c |
| 10,000 | 500 | 2,500 | 2,500 × c |
| 100,000 | 5,000 | 25,000 | 25,000 × c |

[ASSUMED] Each row uses 5% daily callers and five-minute calls. For a target gross margin m, the usage-price floor is fully allocated cost per minute / (1 − m). Include idle capacity, support and payment costs before proposing a customer price.

[VERIFIED] STEP-000 records the provider’s published free-tier eligibility for the probed primary text model. [UNKNOWN] Actual project billing, free-tier capacity, observed token mix, licensed TTS economics and paid production margin. P12 must date and source provider rates and replace c with measured scenarios. Do not project free demo usage into production capacity. [Official Gemini pricing](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite)

| Cost category | P1 local demo | Production scenario input |
|---|---|---|
| Reply and analysis | Deterministic mock runs in-process | Billable tokens per turn, turns per minute, retries, cached share |
| STT and TTS | Outside P1 | Audio and synthesis units per minute, including interrupted responses |
| Infrastructure | Local machine runs API and UI | Active stream-hours, fixed idle capacity, metrics, egress and storage |

[ASSUMED] Model the low and high cases using half and twice the observed retry and cloud speech rates. Include software support as a separate fixed line item before pricing the pilot. This worksheet tracks usage; the paid rates and invoice reconciliation belong to P12.
