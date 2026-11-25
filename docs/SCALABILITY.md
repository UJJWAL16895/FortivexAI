# Scaling to 100,000 registered buyers

[ASSUMED] 5% place one call per day, each call runs five minutes, the operating window is 10 hours, and peak arrivals are 3× average. At 100,000 registrations this is 5,000 calls and 25,000 connected minutes/day. Average concurrency is 25,000 / 600 = 41.7. Design for 125 peak sockets under this scenario. At four model replies per connected minute, peak text quota demand could be 500 requests/minute before retries and routing overhead.

[VERIFIED] One Windows Ryzen 7 5800H ran both the mock WebSocket server and load generator on loopback. Five cited Growth turns per connection.

| Sessions | Turns | Errors | Turns/s | p95 ms |
|---:|---:|---:|---:|---:|
| 10 | 50 | 0 | 586.7 | 11.1 |
| 50 | 250 | 0 | 1318.1 | 34.1 |
| 125 | 625 | 0 | 1178.7 | 66.4 |
| 250 | 1250 | 0 | 1157.3 | 210.5 |
| 500 | 2500 | 0 | 1360.3 | 387.3 |

Throughput leveled off around 50 concurrent clients while latency increased. The test includes receiving the profile event, excludes cloud calls, and does not isolate client CPU, server CPU, or database wait. Exact saturation was not established. In the measured Hindi voice readback, the median STT stage was 2.10 s and playback began at 3.98 s after Stop. Fleet voice throughput was NOT MEASURED. [Voice evidence](reports/STEP-006.md)

## Production design [ASSUMED]

- A WebSocket gateway owns each active connection. Keep session affinity during the socket lifetime. Move reconnectable memory into tenant-scoped Redis with TTL; stateless API workers can resume on any instance.
- Send durable analysis jobs to a bounded queue with retries and unique call IDs. Use Postgres primary transactions for slot uniqueness, CRM and reports. Route dashboard reads to replicas with explicit lag bounds. Move reviewed card vectors to a managed tenant-filtered index.
- Replace local CPU Whisper per request with a warm GPU STT pool or managed streaming STT. Turn endpoint detection should send partial audio before the speaker stops. Pool TTS streams and precompute common approved phrases. Cap outstanding frames and apply admission/backpressure on queue lag.
- Separate project/provider budgets by model. Cache approved repeated content, escalate only difficult requests, and open a circuit when quota is exhausted. Preserve deterministic product facts during generation outages.
- Start in one region near the demo users. At multi-region scale keep bookings on one authoritative writer per tenant and replicate read models. Fail closed on a slot write when the authoritative region is unavailable. Measure reconnect, mixed live traffic, queue age, quota exhaustion and booking conflicts before committing to capacity.
