# STEP-021 · One-click LIVE and MOCK

Base checkpoint is pre-live-toggle. The browser requests mode on the socket and the server confirms it after readiness. The socket owns lead, history and mode. An ephemeral voice handle connects existing HTTP audio requests to the same state. Public mode uses the existing evaluator gate and per-IP frame limit.

## Evidence

| Check | Observed result |
|---|---|
| Integration | [VERIFIED] Six new integration tests exercise activation, missing key, invalid credential rejection, missing Whisper, independent socket and voice modes, quota reversion and the public access gate. The fixture checks that responses omit its key. |
| Chrome with synthetic provider | [VERIFIED] MOCK → CHECKING → WARMING → LIVE → MOCK. Dividers, selected buttons, fallback toast and presenter mode at 390 px passed. Screenshots use a fake-provider server. Any timing in those screenshots is fixture timing. |
| One real readiness request | [VERIFIED] gemini-3.5-flash-lite, 1796.84 ms round trip, 1 / 60 local rolling calls. The request used `generateContent`, prompt “Reply OK.”, max output 8, no system prompt and the configured minimal thinking level. [Gemini API reference](https://ai.google.dev/api/generate-content) |
| One real text turn | [VERIFIED] Gemini first text 1278.46 ms. The existing policy guard supplied the visible wording. Local rolling counter reached 2 / 60. |
| One real voice turn | [VERIFIED] Chrome injected a synthetic microphone clip. Local faster-whisper small took 1802 ms. Bundled speech took 6 ms to first byte and playback began 1843 ms after Stop. The confirmed-store question took the local path with no Gemini first-text measurement, so the local counter stayed 2 / 60. |
| Credential scan | [VERIFIED] The release scanner compares exact server API-key values and common credential patterns against the compiled browser files without printing matches. |

The counter is the process budget, including provider attempts and readiness probes in a rolling 24-hour window. It does not represent the provider's project-wide remaining quota. The real run measured a synthetic audio fixture on this laptop. The host and physical mic were not tested.

## Screenshots

[Mock](../diagrams/ui/live-toggle-mock.png) · [Checking](../diagrams/ui/live-toggle-checking.png) · [Warming](../diagrams/ui/live-toggle-warming.png) · [Live](../diagrams/ui/live-toggle-live.png) · [Failure toast](../diagrams/ui/live-toggle-failure.png) · [390 px presenter](../diagrams/ui/live-toggle-mobile.png)
