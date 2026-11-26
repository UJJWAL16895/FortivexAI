# Live coding on a scratch branch

Showcase edits: change the hero heading in frontend/src/Showcase.jsx, add a feature to its features array or change --accent in frontend/src/styles.css. Run the production build and the showcase browser check. See UI_GUIDE.md.

[VERIFIED] Run scripts/rehearse.py from a clean scratch clone on branch codex/interview-rehearsal. The script records lines, runs focused checks and restores the edited files.

| Recipe | Anchor | Rehearsed change |
|---|---|---|
| Language variant | src/memory/session.py:24 | Add a Roman confirmation alias. |
| Qualification | src/analytics/core.py:78 | Raise the Hot threshold and check Warm. |
| Booking | src/crm/store.py:79 | Move the first slot to noon. |
| Knowledge doc | data/knowledge/faq.json:12 and approval.json | Add an alias and recompute its digest. |
| CRM field | src/memory/session.py:51 | Add a role and test persistence. |
| Sentiment | src/analytics/core.py:8 | Add a validated Concerned label. |
| Provider | src/core/settings.py:26 | Select browser TTS in settings. |
| Endpoint | src/api/app.py:81 | Serve and call GET /ping. |
| Latency | src/llm/reply.py:26 | Shorten the deadline and test fallback. |
| RAG miss | src/rag/index.py:19 | Inspect the threshold and check abstention. |

The locale rehearsal exercises a language variant only. A production locale also needs STT and TTS support, localized answers and voice fixtures.

Evidence: [STEP-014 scratch run](reports/STEP-014.md). It ran ten focused checks, restored edits and passed the full suite on the restored branch. The knowledge rehearsal adjusted an alias and approval hash in an existing file. The sentiment rehearsal proved schema acceptance of a new label. To test a new classification rule or a full new locale, extend fixture coverage before shipping.

| Cockpit recipe | What to edit |
|---|---|
| Add a new live card | In CockpitPanels.jsx → Intelligence, add an IntelligenceGroup fed by an existing event field. Use a pending state for absent data. |
| Change the accent color | In styles.css, edit the shared accent and glow tokens. Verify focus and text contrast on both routes. |
| Add a quick-scenario chip | In cockpitData.js, add a message to scenarios. Check the label, what send submits and how it reads at mobile width. |
| Change lead-score colors | In cockpit.css, edit rating rules for Hot, Warm and Cold. Leave the score and rating from the saved report intact. |
