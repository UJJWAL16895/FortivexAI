# Cost model

**As of 26 November 2026, USD.** Standard Gemini 3.5 Flash-Lite paid text input is $0.30 and output $2.50 per million tokens. Gemini 3.5 Transcribe lists approximately $0.003 per audio minute for input and $0.002 for text output under Google's token assumptions. Google lists free-tier availability for both models. Account billing and limits are unverified. [Official Gemini pricing](https://aistudio.google.com/docs/pricing)

[ASSUMED] To illustrate a paid deployment, use 800 billable input and 160 billable output tokens per connected minute. LLM = (800 × 0.30 + 160 × 2.50) / 1,000,000 = $0.00064. STT = number of input audio minutes × the input rate plus output token cost. The table uses $0.005 per connected minute as a conservative scenario, charging a full minute of transcription. TTS = synthesized units × provider rate. The table reserves **$0.015/min** as an assumed allowance, not a vendor quote. Allocated infrastructure = (compute + database + storage + egress + logs) / billable call minutes; assume **$0.010/min**. Total scenario = **$0.03064/min**. Include retries and interrupted synthesis in actual usage reports.

| Registrations [ASSUMED] | Calls/day | Connected minutes/day | Daily cost scenario |
|---:|---:|---:|---:|
| 1,000 | 50 | 250 | $7.66 |
| 10,000 | 500 | 2,500 | $76.60 |
| 100,000 | 5,000 | 25,000 | $766.00 |

The keyless local demo uses no cloud inference. Optional live testing can consume applicable free-tier allowances. The production path needs contracted speech capacity and metering. edge-tts is unofficial and demo-only. [ASSUMED] At 60% gross margin, the variable-cost-only price floor is $0.0766/min. A scenario of $0.08/min plus a platform fee would need validation against support, idle capacity, churn and willingness to pay. Production invoices and realized margins are NOT MEASURED.
