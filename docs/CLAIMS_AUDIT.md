# Claims audit

26 November 2026. Release gates and command output are in [STEP-019](reports/STEP-019.md). Prior reports preserve measurements from their own checkpoints.

| Claim | Evidence | Status |
|---|---|---|
| The README starts a keyless browser app and a terminal hero on Windows. | Clean remote clone, setup, verify and demo commands. GitHub Actions also exercises setup, verify and CLI demo. | [VERIFIED] |
| The demo retrieves a reviewed price and citation, confirms a booking, saves one CRM lead and creates insights. | tests/integration/test_hero.py, test_restart.py, browser hero and CLI smoke. | [VERIFIED] for fictional data |
| The dashboard survives a local process restart on persistent storage. | tests/integration/test_restart.py. Two reports, one booking, 50% booked. | [VERIFIED] Local SQLite, not an ephemeral host. |
| Booking changes require explicit confirmation and a contested move retains the original time. | tests/unit/test_booking_changes.py. Changes operate in the booking session. | [VERIFIED] |
| English, Hindi and Roman Hinglish can switch in one session. | tests/integration/test_languages.py and docs/MULTILINGUAL_DEMO.md. | [VERIFIED] for fixture inputs. Production language detection and dialect accuracy are NOT MEASURED. |
| Hindi first audio hit a 3.98 s median on the confirmation path. | STEP-006, three warmed scripted Chrome turns for that language. | [VERIFIED] Physical microphones and live fleet percentiles are NOT MEASURED. |
| The optional local semantic search retrieved 14/15 expected sources and abstained on 5/5 unsupported questions. | STEP-007 and authored evaluation set. Alias route retrieved 12/15. | [VERIFIED] Held-out retrieval accuracy is NOT MEASURED. |
| The demo text server returned p95 66.4 ms at 125 clients. | SCALABILITY.md and STEP-014, loopback cited mock traffic, 625 turns. | [VERIFIED] This test excludes live inference and speech. |
| 100,000 registered buyers imply 125 peak sockets and $766/day. | SCALABILITY.md and COSTS.md, stated demand and usage formulas. | [ASSUMED] Planning scenario only. |
| Gemini published text and transcription prices and free-tier availability. | COSTS.md cites the official pricing page, checked 26 November 2026. Actual account entitlement and costs depend on settings and use. | [VERIFIED] listed rates. Account invoices NOT MEASURED. |
| A sales team might save $646.80/month before fixed costs. | BUSINESS_CASE.md calculates $800 modeled labor savings minus $153.20 scenario variable cost. | [ASSUMED] Pilot savings and conversion NOT MEASURED. |
| Reviewed sentences, log filtering and public access gates enforce specific boundaries. | SECURITY.md, claims and reliability tests, PublicGuard tests. | [VERIFIED] Prototype tests. Universal injection resistance, production identity, retention, audited consent and tenant isolation remain open. |
| The site avoids live quota for the scripted sample. | Local fixture and Chrome with external requests blocked, STEP-015. | [VERIFIED] Fictional sample sentiment and score are illustrative. |
| Lighthouse scored 98 performance and 100 accessibility. | STEP-015, one run at the showcase checkpoint. | [VERIFIED] historical measurement. |
| Public preview defaults to mock and skips the local STT weights. | Settings test and local non-root Docker smoke, STEP-018. | [VERIFIED] locally. Hosted account, proxy and behavior [UNKNOWN]. |
| Interview recipes were rehearsed on a scratch branch. | [STEP-014](reports/STEP-014.md), ten focused edits and restored full-suite verification. | [VERIFIED] Scope includes locale alias and schema-label smoke only. |
| Voice input uses bounded HTTP upload and the reply path uses streaming WebSocket events. | Voice routes and Console, current architecture diagrams and code map. | [VERIFIED] Continuous audio streaming, automatic endpointing and full barge-in remain open. |

## Secrets and contact data

The release script scans reachable Git blobs, tracked and non-ignored files, and the compiled client. It checks common key patterns and exact active API-key values without printing them. The scan also reviewed email and Indian mobile-number candidates. Known synthetic domains and fixture numbers were separated during review. The remaining candidates were reserved example.com addresses in tests and two decimal SVG coordinates. There were no API key or prohibited-path hits in the audited scopes. This pattern review cannot establish that arbitrary free text is free of personal data. Ignored local runtime stores, private downloads, Git author metadata and unrelated system files are outside this check. The local .env is ignored and untracked. The image build uses explicit COPY instructions and a restricted build context.
