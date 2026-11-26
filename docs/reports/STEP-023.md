# STEP-023 · Model-first LIVE conversation

The old gate was run_turns in src/api/text_session.py, which called small_talk from src/llm/claims.py and could answer without invoking Gemini. Unmatched text reached ReplyPath.stream, which approved only exact phrases and substituted a specialist response for other output. Both paths were removed from LIVE.

## Verification

- [VERIFIED] Fake-provider regression sends all eleven requested inputs through retrieval and Gemini. The fixture raises if legacy lookup, lead, or booking phrase handlers are called to route ordinary conversation. It checks the previous question on no and yes, and validates the profile and passage payload.
- [VERIFIED] Unsupported offer and price claims are removed sentence by sentence. The Hindi Growth price keeps the reviewed citation. Existing content-digest tests still exclude modified and unapproved documents.
- [VERIFIED] The provider adapter requests JSON and validates it before sending text or speech. A valid conversation line survives alongside a blocked claim. The fallback tests verify that partial JSON never reaches the buyer.
- [VERIFIED] The bounded real run used at most eight provider requests, including one transport diagnostic. An isolated request returned HTTP 200 and a completed structured stream. The socket attempts below did not produce a usable live reply. No additional quota was spent after the ceiling.

| Real input | Observed output | Time to reply |
|---|---|---:|
| hii, first attempt | Live quota reached, using mock | 5521.04 ms |
| hii, second attempt | Live model unavailable, switching to mock. Gemini A failed with application code 502 and Gemini B with 503. | 3281.36 ms |
| hello how are you | No real reply captured after the session switched to mock. Covered by the fake-provider regression. | — |
| no | No real reply captured after the session switched to mock. Covered with the previous question in fake-provider history. | — |
| How much does Growth cost? | Live quota reached, using mock. Gemini A returned HTTP 429. | 255.28 ms |

The text numbers above measure failed turns and include fallback processing. The incremental latency of a successful always-model reply is unmeasured (n=0 successful live socket replies). Historical timings describe a different prompt and route, so subtracting them would give a misleading estimate. The UI still records per-turn first provider text. Checked sentences are released after the complete structured response validates.

The claim check combines model-provided sentence categories with a conservative check of generated wording and exact evidence matching. It is a prototype and its ability to catch arbitrarily phrased or multilingual misclassified assertions is not established. Business actions run only after the model responds, and existing input/confirmation checks still authorize writes.
