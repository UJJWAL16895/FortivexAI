# Non-functional targets

[ASSUMED] Initial warm-path target on the demo laptop is **p50 ≤ 2.0 s, p95 ≤ 3.5 s** from the final voiced microphone sample to first audible synthesized audio. Include endpoint silence, network and playback buffering. Report cold starts, errors, interruptions and provider fallbacks separately. A text event is insufficient evidence for this target.

| Stage | Provisional p50 allocation |
|---|---:|
| Endpoint detection | 250 ms |
| STT final result | 400 ms |
| Retrieval and reply preparation | 100 ms |
| LLM request to first text | 750 ms |
| Accumulate first speakable phrase | 150 ms |
| TTS request to first playable bytes | 250 ms |
| Transport, decode and playback | 100 ms |

[VERIFIED] The single P0 preflight sample took 1566 ms to first text. [UNKNOWN] Feasibility of the proposed budget. P2 benchmarks first text, P5 instruments actual playback. Store timestamps with a monotonic clock on each host. Measure the overall interval on the browser clock; compare stage durations without subtracting timestamps from different clocks.

Design targets include deterministic keyless verification, bounded retries and queues, tenant-scoped state, safe cancellation, idempotent writes, and responsive audio despite slow analytics. No external account should be necessary for the mock demo.
