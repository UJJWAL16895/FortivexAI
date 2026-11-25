# Capacity model for 1,00,000 registered users

[ASSUMED] Planning scenario: 100,000 registered buyers, 5% calling once daily, five minutes per call, a ten-hour operating window and a peak rate three times the window average. That implies 5,000 calls/day, 25,000 call-minutes/day, about 42 simultaneous calls on average during the window and **125 at peak**. Doubling call length doubles expected concurrency at the same arrival rate. These figures describe offered demand, not measured platform throughput.

Separate active connections from model request concurrency. At four generated replies per minute per active call, 125 active calls imply 500 reply requests/minute before extraction, transcription, synthesis, retries or tool continuations. Background analysis consumes quota even when removed from the spoken path. Budget it separately and shed nonessential work first.

[ASSUMED] Proposed path: keep active sockets on their gateway, persist reconnectable state in Redis, route tenant-owned commands to stateless services and use a durable queue for background jobs. Use Postgres transactions for slot arithmetic and replicas for dashboard reads. Move the vector index to managed search when corpus and query concurrency exceed local measurements. Autoscale speech workers by queue delay, admit bounded live streams and apply project-wide model limits. Pin calls to a region and route bookings to the slot’s authoritative writer.

[UNKNOWN] Actual saturation point. P12 must ramp synthetic sessions, hold load, inject provider throttling, record p50/p95 and errors, identify the first bottleneck and rerun after mitigation. Report mock and real-provider throughput separately.

## Capacity verification plan

[ASSUMED] Ramp from 10 to 125 and then 250 active sockets with realistic turn intervals. Hold each level, include disconnect/reconnect traffic and use a separate profile for slow providers. Track queue age, concurrent generation, socket reconnects, CPU and booking conflicts. Provider RPM is a candidate first bottleneck given the 500 requests/minute scenario. Compare observed saturation against quotas before choosing higher model limits, caching or a different tier.
