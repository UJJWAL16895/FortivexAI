# STEP-003 · P2 streaming Gemini and fallback

## Objective and plan

Exercise the real Gemini stream using the configured local key, choose two models, stream text and speakable sentences through the existing socket, and demonstrate failover in the browser. Replace the deprecated Starlette test transport and keep the offline quickstart runnable.

## Real benchmark · 26 November 2026

| Catalog model | Setting sent | Completion | First visible text, completed turns | Decision and quick quality |
|---|---|---:|---|---|
| gemini-3.5-flash-lite | thinkingLevel=minimal | 10/10 | Median 3919 ms, range 638–6361 ms | **A.** Understandable replies across all three prompt groups. One volunteered an unsupported discount and another claimed real-time sync. |
| gemini-3.1-flash-lite | thinkingLevel=minimal | 2/10, eight 503-class failures | Median 4640 ms, range 1368–7912 ms | **B, provisional.** Two usable replies, one Hindi and one Hinglish. Prefer its observed response times over 3.6 among the available backups. |
| gemini-3.6-flash | thinkingLevel=minimal | 2/10, eight 503-class failures | Median 8484 ms, range 7215–9753 ms | Slower in the two completed samples. Both replies were in English. |

[VERIFIED] The benchmark uses POST v1beta/models/{model}:streamGenerateContent with alt=sse, maxOutputTokens=192, no tools, provider-default sampling and x-goog-api-key header. Google documents minimal as the lowest supported setting for these three. Three groups contain four English, three Hindi and three Hinglish synthetic prompts. A and 3.1 were interleaved. 3.6 ran a separate pass on the same prompts. First text timing includes request setup and excludes hidden thoughts. The adapter maps transport and parse failures to 503, so this summary cannot attribute every 503-class result to Google. One separate 2.5 Flash-Lite eligibility probe with thinkingBudget=0 returned 404. [Thinking settings](https://aistudio.google.com/docs/thinking) · [Pricing](https://aistudio.google.com/docs/pricing)

The shipped prompt remains short and explicitly says that prices, discounts, features and booking availability are unknown. A three-prompt A recheck after this change gave 1146, 1042 and 1937 ms. The pricing response stated that current details were unavailable and the demo response stated that calendar access was unavailable. This small recheck cannot establish groundedness. P4 adds verifiable product evidence and abstention. The initial request instructed the model to use at most two short sentences, match caller language, ask one relevant question and avoid invented prices, features or confirmed appointments. Reproduce the current prompt with `python -m scripts.benchmark_replies` from the root in the venv.

## Implementation and verification

- [VERIFIED] A and B stream incremental text. SentenceBuffer emits ready segments and preserves split decimals and final fragments. A midstream interruption terminates the turn to avoid duplicating displayed or spoken text.
- [VERIFIED] Chrome showed `LIVE Gemini A active` on a real reply. The opt-in failure control showed `MOCK Gemini A failed (503) > Gemini B failed (503) > mock active`. MockTransport tests separately exercise a real adapter HTTP 503, successful B fallback and interruption after partial A output.
- [VERIFIED] Offline verification reported `19 passed`, clean Ruff and mypy, a clean secret scan and a built frontend. The pinned httpx2 transport removed the Starlette deprecation warning and CI treats a recurrence as an error.
- [ASSUMED] The app defaults to 8 requests/minute, 60 per rolling 24 hours and 12,000 estimated input tokens/minute. These are conservative local policy settings. The quota indicator distinguishes a local limit and upstream throttling. The cache holds only predefined synthetic prompts for five minutes. An upstream 429 temporarily limits both slots because account-level quota details are unknown. [Official quota dimensions](https://aistudio.google.com/docs/rate-limits)

## Limits and next gate

[UNKNOWN] Active project quota and billed amount, model availability over time, and first-audio latency. Successful-only latency samples for B and 3.6 are especially sparse. Pinning the chosen backup does not guarantee service availability. On this sample A already exceeded the warm first-audio budget at the median first-text step. Both known failures and rate limits must preserve the mock demo. OpenAI stays disabled. Next implement and verify the thin mic-to-playback loop, then publish demo-voice-thin before P3.
