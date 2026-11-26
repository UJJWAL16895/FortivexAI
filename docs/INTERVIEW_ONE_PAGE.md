# ShelfPilot · 20 places to point

Start at repo root. Line numbers are **approx**. For the three turn traces and rehearsed edits, open `docs/INTERVIEW_WHERE_IS_WHAT.md`.

| # | Interviewer asks | File → what to point at (approx) |
|---|---|---|
| 1 | What approved text can it say? | `data/knowledge/plans-and-prices.json` → Growth record, 17–29 |
| 2 | How do edited cards get trusted? | `src/rag/index.py` → `Knowledge.load`, 113–130 |
| 3 | How does LIVE find evidence? | `src/rag/index.py` → `Knowledge.retrieve`, 87–112 |
| 4 | Where is the search threshold? | `src/rag/index.py` → `SEMANTIC_THRESHOLD` / `SEMANTIC_MARGIN`, 20–21 |
| 5 | Where is the system prompt? | `src/llm/conversation.py` → `PERSONA`, 13–24 |
| 6 | Who checks claims? | `src/llm/conversation.py` → `check_line`, 81–113 |
| 7 | What is the fallback sentence? | `src/llm/claims.py` → `CHECK_SHORT_EN` / `CHECK_SHORT_HI`, 11–12 |
| 8 | When is Gemini B tried? | `src/llm/reply.py` → `ReplyPath.converse`, 69–141 |
| 9 | Who caps requests? | `src/llm/reply.py` → `RequestBudget.reserve`, 43–60 |
| 10 | Where does a turn enter? | `src/api/text_session.py` → `text_session` / `run_turns`, 35–161 |
| 11 | Where is short-term memory? | `src/memory/session.py` → `LeadSession` / `remember`, 49–58 |
| 12 | What counts as confirmation? | `src/crm/conversation.py` → `BookingSession.handle`, 71–94 |
| 13 | Who prevents double booking? | `src/crm/store.py` → `CRM.book`, 85–96 |
| 14 | Where do CRM records go? | `src/crm/store.py` → `CRM.__init__` / `save`, 32–64 |
| 15 | Why can a LIVE badge be Neutral? | `src/analytics/core.py` → `analyze_turn`, 42–55 |
| 16 | Where is Hot/Warm/Cold? | `src/analytics/core.py` → `summarize_call`, 56–89 |
| 17 | Where does the mic start? | `frontend/src/Console.jsx` → `toggleMic`, 310–383 |
| 18 | Where is audio handled? | `src/api/voice.py` → `transcribe_audio` / `speak_sentence`, 84–205 |
| 19 | Who draws a citation or receipt? | `frontend/src/CockpitPanels.jsx` → `ChatMessage`, 47–76 |
| 20 | Where do I run the checks? | `scripts/tasks.py` → `main`, 20–99 |
