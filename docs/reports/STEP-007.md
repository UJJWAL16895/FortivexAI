# STEP-007 · Cited ShelfPilot knowledge

## Scope

Ship bilingual reference cards and answer directly from the selected card. Keep price and discount matching conservative, and retain the previous generation guard for uncited dialogue. The user accepted the earlier 3.98 s Hindi readback median. Park further latency tuning until the core workflow is complete. CPU STT and remote synthesis contributed to that wait. Production candidates are GPU or streaming STT.

## Evidence

| Retrieval configuration | Correct source on answerable prompts | Correct abstention on unsupported prompts |
|---|---:|---:|
| Reviewed topic aliases | 12/15 | 5/5 |
| Aliases and local multilingual MiniLM | 14/15 | 5/5 |

Twenty authored prompts include English, Hindi and Hinglish. The corpus contains four fictional documents with ten independently cited answer cards. There was one miss in hybrid mode for an internet connection paraphrase. This small manual set measures the supplied corpus only. There is no statistical claim or held-out accuracy estimate.

FastEmbed runs multilingual MiniLM locally. The app compares cosine scores against a 0.58 minimum and a 0.08 margin. The optional index is held in memory as one vector per answer card. Explicit prices and discounts require the reviewed topic label. A percentage supplied by the buyer must match source evidence. An abstention returns “I don't have that information, I'll have a specialist follow up” without a citation. This is a demo response, with no external message sent.

The first test failed because the retrieval module did not exist. Tests now exercise supported and unsupported pricing, an invented 40% discount, Hindi/Hinglish, modified reviewed bytes, and injection in an unapproved document. The socket regression compares the speech sentence with the cited reply. The selected card is read directly. No source content becomes a model instruction, and admission checks reviewed SHA-256 digests. A reviewer who approves malicious content can still defeat that admission boundary.

Install with setup --knowledge-model and set KNOWLEDGE_EMBEDDINGS=true. Use `python -m scripts.evaluate_knowledge --embeddings` in the venv to reproduce. Core-only and Docker demos use the reviewed alias search. [FastEmbed documentation](https://qdrant.tech/documentation/embeddings/fastembed/)
