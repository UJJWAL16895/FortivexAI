# Interview guide · where is what?

Open this beside your editor. Search for the name in the third column. All line ranges are **approx**. This guide follows the code on `main` at `4f11dfe` before the interview docs. [VERIFIED] The separate booking and sentiment development branch has different behavior. In this guide **Mock** means local demo behavior and **LIVE** means Gemini is enabled for the connection.

## 1. Folder map

```text
src/api       HTTP requests, WebSocket turns and voice routes
src/llm       Gemini request, fallback, prompts and reply checks
src/rag       Loading and searching reviewed knowledge
src/memory    Recent turns, lead fields and detail read-back
src/crm       Lead and booking logic and tables
src/analytics Background scoring, summaries and saved dashboards
src/voice     Speech providers
src/core      Settings, logs and public access limits
data/knowledge Reviewed English and Hindi answer cards
frontend/src  React showcase, cockpit, voice controls and report export
tests/unit    Small checks for single parts
tests/integration Checks across backend parts
tests/e2e     Browser flows
tests/rag_eval Questions and expected sources
scripts      Setup, verify and demos
infra        Docker setup
.github/workflows Windows and Ubuntu CI
docs         Business, design and interview notes
docs/diagrams Exported drawings and screenshots
README.md    How to start the app
Makefile     Short commands for setup, verify, scan, run and demo
.env.example Safe example settings
```

## 2. Where is it?

| Question | File | Function/class and approx lines | In simple words | Mock vs LIVE |
|---|---|---|---|---|
| Where are the answer cards? | `data/knowledge/product-guide.json`, `data/knowledge/plans-and-prices.json`, `data/knowledge/faq.json`, `data/knowledge/objection-handling.json` | JSON records | Each record is one reviewed chunk. It has an ID, title, aliases and English/Hindi text. | Both |
| How are edits approved? | `data/knowledge/approval.json`, `src/rag/index.py` | `Knowledge.load` 113–130 | A card file is accepted when its SHA-256 digest matches this manifest. | Both |
| Where are chunks made? | `src/rag/index.py` | `Chunk` 59–67 | The team writes small JSON records. Automatic document splitting is NOT BUILT. | Both |
| Where are embeddings? | `src/rag/index.py`, `scripts/setup_knowledge.py` | `Knowledge.enable_embeddings` 131–140 | Optional local model makes numeric fingerprints for meaning. | Both when enabled |
| Where is search? | `src/rag/index.py` | `retrieve` 87–112, `lookup` 141–202 | LIVE ranks shared terms and can use vectors for zero term overlap. Mock uses reviewed aliases and optional vectors. | Different paths |
| Where is the threshold? | `src/rag/index.py` | `SEMANTIC_THRESHOLD`, `SEMANTIC_MARGIN` 20–21 | Minimum vector score is 0.58. Mock also uses a 0.08 lead over the runner-up in vector search. | LIVE has no margin check |
| Where is abstention? | `src/rag/index.py`, `src/llm/conversation.py` | `abstention` 35–48, `check_line` 81–113 | An abstention says a human can follow up. | Mock routes inside lookup. LIVE checks the output. |
| Where is the LIVE system and answer prompt? | `src/llm/conversation.py`, `src/llm/reply.py`, `src/llm/gemini.py` | `PERSONA` 13–24, `ReplyPath.converse` 69–142, `request_body` 23–54 | Persona and context are sent with history and buyer text. | LIVE |
| Where is the understanding prompt? | `src/llm/conversation.py`, `src/api/conversation.py` | `PERSONA`, `LiveDraft` 13–59, `live_turn` 18–83 | One Gemini response proposes `none`, `lead` or `booking`. The server then handles the action. | LIVE model picks action. Local handlers still parse details. |
| Where are sentiment and summary prompts? | `src/analytics/core.py` | `analyze_turn` 42–55, `summarize_call` 56–89 | Gemini prompts for these tasks are NOT BUILT on main. Python rules fill the fields. | Same rules |
| Where is the claim check and fallback line? | `src/llm/conversation.py`, `src/llm/claims.py` | `check_line` 81–113, `CHECK_SHORT_EN` / `CHECK_SHORT_HI` 11–12 | Match the source ID and exact sentence for a fact, or replace an unsupported claim. | Post-check in LIVE |
| Where is booking state? | `src/crm/conversation.py` | `BookingSession.handle` 10–94 | A connection remembers the contact, offered time and current reservation. | LIVE runs the handler after Gemini picks booking. Mock tries it first. |
| Where are availability and race protection? | `src/crm/store.py` | `CRM.offer` 70–84, `CRM.book` 85–96 | Offers the first free slot. SQLite gives one owner to each time. | Both |
| Where is cancel/reschedule? | `src/crm/conversation.py`, `src/crm/store.py` | `handle` 42–70, `cancel` / `move` 111–123 | Commands work for a reservation held by this connection. | Same handler |
| Where are CRM tables/identity? | `src/crm/store.py` | `normalize_contact` 16–24, `CRM.__init__` 32–45, `save` 51–64 | `leads` has contact and a JSON profile. `bookings` has a unique slot and a lead reference. | Same SQLite store |
| Where is lead scoring? | `src/analytics/core.py` | `SIGNALS` 10–20, `summarize_call` 56–89 | Four BANT fields: Budget, Authority, Need and Timeline. Each is worth 25. Hot starts at 75 and Warm at 50. | Same rules |
| Where is sentiment and escalation? | `src/analytics/core.py`, `src/analytics/worker.py` | `analyze_turn` 42–55, `summarize_call` 56–89, `Insights.work` 37–77 | Unmatched text defaults to Neutral. Any negative turn can change the report's next action. Live human handoff is NOT BUILT. | Same rules |
| Where is call reporting? | `src/analytics/store.py`, `frontend/src/reportExport.js` | `ReportStore.save` / `dashboard` 36–69, `downloadReport` | SQLite stores structured reports. The browser can export one. | Both |
| Where is memory? | `src/memory/session.py`, `src/memory/details.py` | `LeadSession.remember` / `handle` 49–137, `store_count` / `target_date` | Recent context holds four pairs. Numbers and dates can be read back. A contact can reload saved fields. | LIVE sends recent turns to Gemini |
| Where is the mic and STT? | `frontend/src/Console.jsx`, `frontend/src/voice.js`, `src/api/voice.py` | `toggleMic` 310–383, `toWav` / `transcribe` 15–55, `transcribe_audio` 84–146 | Record, convert to WAV and send audio over HTTP. | Mock returns one fixed transcript. LIVE tries configured speech providers. |
| Where are speech providers? | `src/voice/local.py`, `src/voice/gemini.py`, `src/voice/edge.py` | `recognize` / `warm` 30–42, `transcribe` / `synthesize` 28–58, `synthesize` 7–28 | Local Whisper or Gemini listens. Edge or Gemini can speak. | Cloud or local recognition is for LIVE |
| Where is audio output and language selection? | `frontend/src/voice.js`, `frontend/src/mock-speech`, `frontend/src/cockpitData.js`, `src/api/voice.py` | `createPlayback` 57–154, `receivedLanguage` 40–48, `speak_sentence` 156–205 | Uses approved clips or browser speech as needed. STT selector sends `en` or `hi`. Script detection is a heuristic. | Mock can play bundled clips. LIVE can request server speech. |
| Where are mock, LIVE switch and fallback? | `src/llm/mock.py`, `src/api/live_mode.py`, `src/llm/reply.py` | `MockLLM.stream` 6–14, `switch_mode` 74–136, `converse` 69–141 | The switch tests Gemini. LIVE tries configured A then B. Failure can return to mock. | Mock free chat is limited |
| Where are request limits? | `src/llm/reply.py`, `src/core/public.py` | `RequestBudget.reserve` 26–60, `PublicGuard.reserve` 24–47 | Local Gemini request/token limits are per process. The public demo also limits each client IP. | Public rules apply in both modes |
| Where are socket and HTTP routes? | `src/api/app.py`, `src/api/text_session.py`, `docs/API_SPEC.yaml` | `create_app` 32–122, `text_session` / `run_turns` 35–234 | HTTP handles records and health. The socket carries text turns and events. | Both |
| Where is the cockpit? | `frontend/src/main.jsx`, `frontend/src/Console.jsx`, `frontend/src/cockpit.css` | `App` 15–630, `send` 282–308 | React owns the console. CSS controls its look. | Same UI with mode badges |
| Where are badges, citations and receipts? | `frontend/src/CockpitPanels.jsx`, `frontend/src/Console.jsx`, `frontend/src/cockpitData.js` | `ChatMessage` 47–76, `Intelligence` 178–214, `bookingTime` 35–38 | The UI shows events from the server. The receipt comes from matching booking reply text. | Both |
| Where are CRM/Insights views? | `frontend/src/CockpitRecords.jsx`, `frontend/src/Console.jsx` | `CockpitRecords` 5–47, `openRecords` 484–496 | A drawer loads saved leads, bookings or reports. | Both |
| Where are config and logging? | `src/core/settings.py`, `.env.example`, `src/core/logging.py` | `Settings` 7–57, `RedactContacts.filter` / `protect_server_logs` 8–27 | Validate settings and hide common phone and email patterns in logs. | Never show secrets in either mode |
| Where are verify, CI and Docker? | `scripts/tasks.py`, `scripts/secret_scan.py`, `.github/workflows/verify.yml`, `infra/Dockerfile`, `infra/docker-compose.yml` | `main` in both scripts | The gate runs lint, types, tests, scan and frontend build. | CI uses mock/fakes |
| Where are the drawings and reports? | `docs/ARCHITECTURE.md`, `docs/diagrams/architecture.pdf`, `docs/diagrams/system.svg`, `docs/diagrams/sequence.svg`, `docs/SCALABILITY.md`, `docs/COSTS.md`, `docs/SECURITY.md` | Document sections | Point to these for design, assumptions, costs and security limits. | Both |

## 3. Follow one turn

### A. Type “What is the Growth plan price?” in LIVE

1. `frontend/src/Console.jsx` → `App.send` (approx 282–308) adds the user message and sends a text frame over `/ws/text`.
2. `src/api/text_session.py` → `text_session` and `run_turns` (approx 35–161) validate the frame, check mode and quota and enter `live_turn` if still LIVE.
3. `src/api/conversation.py` → `live_turn` (approx 18–43) runs `Knowledge.retrieve` in `src/rag/index.py` (approx 87–112). It sends ranked passages, the lead profile and recent turns to `ReplyPath.converse`.
4. `src/llm/reply.py` → `converse` and `_live` (approx 69–181) call `request_body` / `stream_gemini` in `src/llm/gemini.py` (approx 23–92). They read and validate the generated JSON. A needs an available key and model. B is tried if configured and needed.
5. `src/llm/conversation.py` → `check_line` (approx 81–113) matches quoted text and the source ID or replaces an unsupported claim. `live_turn` sends checked sentences and the reply. `run_turns` submits analytics afterward.
6. `frontend/src/Console.jsx` → `App` receives events (approx 170–253). `frontend/src/CockpitPanels.jsx` → `ChatMessage` (approx 47–76) shows the source chip if there is one.

**What the user sees.** The approved Growth card says ₹2,499 per month for up to five stores, before GST. [VERIFIED] A checked LIVE answer can show that quote and source. A missing or invalid quote can produce an abstention. The first-text metric measures model output, which can come before a reviewed sentence becomes visible.

**What gets saved in the database.** Asking the price alone creates no lead or booking. Recent text stays in the connection. The analytics worker saves a structured call report at call end if there are analyzed turns.

### B. Speak a question

1. `frontend/src/Console.jsx` → `toggleMic` (approx 310–383) starts and stops the browser recorder. Browser permission is required.
2. `frontend/src/voice.js` → `toWav` and `transcribe` (approx 15–55) convert the blob to WAV and send it to `/api/voice/transcribe`. The opaque voice session links HTTP to this socket's mode.
3. `src/api/voice.py` → `transcribe_audio` (approx 84–146) validates audio and tries Gemini or local Whisper in order. Hindi local recognition uses Small. In mock mode the server returns a fixed line.
4. `frontend/src/Console.jsx` → `toggleMic` hands the transcript to `send` (approx 345–364). The socket follows the text route above or the local mock route.
5. `src/api/conversation.py` → `live_turn` (approx 39–81) emits checked sentence events. `frontend/src/voice.js` → `createPlayback` (approx 57–154) queues the audio. `src/api/voice.py` → `speak_sentence` (approx 156–205) serves cloud audio when configured. The browser can speak if it receives no server audio.

**What the user sees.** Transcript, reply and available latency stages. Missing stages show an empty value or dash.

**What gets saved in the database.** No recording is saved by this flow. CRM writes happen only for lead actions. Call analysis stores structured results.

### C. Book a demo

1. `src/api/conversation.py` → `live_turn` (approx 18–44) asks Gemini for an action. `src/crm/conversation.py` → `BookingSession.handle` (approx 19–95) runs if the action is booking. In mock mode `run_turns` calls it before knowledge search.
2. “Book a demo” without contact makes `handle` ask for a contact. Enter a fictional email or phone. `src/crm/store.py` → `normalize_contact` and `CRM.save` (approx 16–64) validate and save. `CRM.load` restores prior fields for the same contact.
3. After saving contact, send “Book a demo” again. `CRM.offer` (approx 70–84) offers the first time it finds in the next seven days at 11:00 or 15:00 IST. A custom time such as “tomorrow 5 PM” is NOT BUILT on main.
4. Send “Confirm booking”. `BookingSession.handle` calls `CRM.book` (approx 85–96). Two different contacts cannot take the same slot. A repeated confirmation for the same committed owner succeeds without inserting a second row.
5. `frontend/src/cockpitData.js` → `bookingTime` (approx 35–38) extracts the time from the booking reply. `frontend/src/CockpitPanels.jsx` → `ChatMessage` (approx 47–76) renders the receipt. `openRecords` in `frontend/src/Console.jsx` (approx 484–496) loads saved records.

**What the user sees.** Contact acknowledgement, an offered time and the receipt after commit. LIVE still relies on the model selecting the right action. Use Mock for the deterministic hero walkthrough.

**What gets saved in the database.** One lead keyed by contact and one booking keyed by time. The saved call report records whether the call was marked booked.

## 4. Rehearse an edit

Use the change in a scratch branch and revert after the check. Run commands from the repo root. Define `$py` as shown in section 6. The times below measure the scratch edit, focused checks and restoration. They are workstation timings, not model or product latency.



| # | Request and exact edit | Expected and observed |
|---|---|---|
| 1 | `data/knowledge/plans-and-prices.json` (approx 27–28): `₹2,499` → `₹2,699` in both languages. Refresh the approved digest. | **TESTED on 2026-11-26 · 0.66 s.** Cited Growth price changed from ₹2,499 to ₹2,699. |
| 2 | `data/knowledge/faq.json` (approx 1): insert the record below after the outer `[`. Refresh the approved digest. | **TESTED on 2026-11-26 · 0.45 s.** Returned `A printable setup guide is available.` |
| 3 | `src/llm/claims.py` (approx 11): `I’ll check with our team and can offer a human follow-up.` → `I’ll check with a specialist and offer a human follow-up.` | **TESTED on 2026-11-26 · 0.26 s.** Unsupported 40% claim returned the edited line and `blocked=True`. |
| 4 | `src/rag/index.py` (approx 20): `SEMANTIC_THRESHOLD = 0.58` → `SEMANTIC_THRESHOLD = 0.72`. | **TESTED on 2026-11-26 · 0.53 s.** A fixed vector with score 0.60 went from one retrieved passage to zero. Shared-word matches are unaffected. |
| 5 | `src/llm/conversation.py` (approx 14): `friendly retail inventory sales assistant` → `patient retail inventory sales assistant`. `frontend/src/Console.jsx` (approx 12): `Hi, I’m the ShelfPilot demo agent.` → `Hello from ShelfPilot.` | **TESTED on 2026-11-26 · 1.58 s.** Persona contained `patient retail` and the Vite build contained `Hello from ShelfPilot.` |
| 6 | `src/analytics/core.py` (approx 80): `score >= 75` → `score >= 100`. | **TESTED on 2026-11-26 · 0.28 s.** Three signals printed `75 Warm`. |
| 7 | `src/crm/store.py` (approx 80): `for hour in (11, 15):` → `for hour in (12, 15):`. | **TESTED on 2026-11-26 · 0.33 s.** Empty database printed `First slot: 12:00 IST`. Slot duration is NOT BUILT. |
| 8 | `src/memory/session.py` (approx 44): add `city: str \| None = None` after `company`. `frontend/src/CockpitRecords.jsx` (approx 14): insert `{item.city && <p>City: {item.city}</p>}` after company. SQLite stores a JSON profile and the API forwards it. | **TESTED on 2026-11-26 · 8.30 s.** Seeded SQLite through CRM, got `GET /api/crm: city=Pune` and saw `City: Pune` in Chrome's CRM drawer. Capturing city from speech is outside this drill. |
| 9 | `frontend/src/cockpitData.js` (approx 7): `'How much does Growth cost?',` → `'How much does Growth cost?', 'Can I import a CSV?',`. | **TESTED on 2026-11-26 · 0.93 s.** Build contained `Can I import a CSV?`. |
| 10 | `src/llm/reply.py` (approx 86–89): move the unchanged `("Gemini B", settings.gemini_fallback_model, settings.gemini_fallback_thinking),` tuple ahead of A in `converse`. | **TESTED on 2026-11-26 · 0.47 s.** First event was `Gemini B fixture-b`. No provider call. |
| 11 | `src/core/settings.py` (approx 22): in `gemini_daily` change `Field(default=60` → `Field(default=2`. | **TESTED on 2026-11-26 · 0.47 s.** Third request: `429 (local); used=2 cap=2`. |
| 12 | `src/core/settings.py` (approx 26): change the `voice_tts` default `"edge"` → `"browser"`. | **TESTED on 2026-11-26 · 0.35 s.** Settings printed `Default TTS: browser`. Speech quality was NOT MEASURED. A new language also requires API choices, browser controls, detection rules, answer cards, a voice mapping and tests. |
| 13 | `src/api/app.py` (approx 106): insert the route below before the health decorator. Regenerate `docs/API_SPEC.yaml`. | **TESTED on 2026-11-26 · 4.18 s.** Contract check: `1 passed in 1.74s`. |
| 14 | `tests/unit/test_analysis.py` (approx 4): insert the test below after the import. | **TESTED on 2026-11-26 · 0.74 s.** Targeted pytest: `1 passed in 0.13s`. |
| 15 | `src/analytics/core.py` (approx 64): `elif "Negative" in sentiment:` → `elif sentiment[-3:] == ["Negative"] * 3:`. | **TESTED on 2026-11-26 · 0.26 s.** Two negatives gave `Ask the buyer about budget.` Three gave `Ask a specialist to review the concern before following up.` This is a report recommendation. LIVE handoff is NOT BUILT. |

### Verification commands

For 1–2, choose the file and question to match the drill. Review changes before updating the manifest. Restart the app to reload the card and rebuild any enabled vectors. A permanent price edit also needs changes to tests that assert the old price.

```json
{"id":"print-guide","title":"FAQ","kind":"faq","aliases":["printed setup guide"],"en":"A printable setup guide is available.","hi":"छापने योग्य सेटअप गाइड उपलब्ध है।"},
```

```powershell
$card = 'plans-and-prices.json' # use 'faq.json' for drill 2
$q = 'What is the Growth plan price?' # or 'Where is the printed setup guide?'
$env:PYTHONIOENCODING = 'utf-8'
& $py -c "import hashlib,json,sys; from pathlib import Path; p=Path('data/knowledge'); m=p/'approval.json'; d=json.loads(m.read_text()); n=sys.argv[1]; d[n]=hashlib.sha256((p/n).read_text(encoding='utf-8').encode()).hexdigest(); m.write_text(json.dumps(d,indent=2)+chr(10))" $card
& $py -c "import sys; from src.rag.index import Knowledge; a=Knowledge.load().lookup(sys.argv[1]); assert a and a.chunk; print(a.text)" $q
```

**3–4.** Use the claim and vector examples below. Run the vector on both versions.

```powershell
@'
from src.llm.conversation import SpokenLine, check_line
r = check_line(SpokenLine(text="40% discount", kind="fact"), ())
assert r.blocked and "check with a specialist" in r.text
print(r.text)
'@ | & $py -
@'
from src.rag.index import Chunk, Knowledge
class V:
    def tolist(self): return [0.6, 0.8]
class E:
    def embed(self, texts): return iter([V()])
c = Chunk(id="label", title="T", kind="faq", aliases=[], en="alpha", hi="alpha")
k = Knowledge([(c, "test")])
k.embedder = E()
k.vectors = [[1., 0.]]
print(len(k.retrieve("omega")))
'@ | & $py -
```

**5–9.** Run the matching check. For the frontend build, use the label for your edit.

```powershell
& $py -c "from src.llm.conversation import PERSONA; assert 'patient retail' in PERSONA"
& $py -c "from src.analytics.core import TurnAnalysis,summarize_call; r=summarize_call([TurnAnalysis(sentiment='Neutral',signals=['budget','authority','need'])],booked=False); print(r.score,r.rating)"
@'
from pathlib import Path
from tempfile import TemporaryDirectory
from src.crm.store import CRM
with TemporaryDirectory() as box:
    print(CRM(Path(box) / "crm.db").offer())
'@ | & $py -
@'
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from src.api.app import create_app
from src.memory.session import LeadProfile
with TemporaryDirectory() as box:
    os.environ["CRM_PATH"] = str(Path(box) / "crm.db")
    app = create_app()
    app.state.crm.save("scratch@example.test", LeadProfile(city="Pune").model_dump(exclude_none=True))
    with TestClient(app) as client:
        assert client.get("/api/crm").json()["leads"][0]["city"] == "Pune"
        print("GET /api/crm: city=Pune")
'@ | & $py -
npm.cmd --prefix frontend run build
$assets = Join-Path 'frontend' 'dist/assets'
rg -l -F 'Hello from ShelfPilot.' $assets
rg -l -F 'City: ' $assets
rg -l -F 'Can I import a CSV?' $assets
```

For 8, the fixture above checks SQLite and the API. For the Chrome check, keep a temporary database for both the seed and the server. Use the following in the scratch branch after the build. Open `/console` and click **View demo CRM**. The fixture row should say `City: Pune`.

```powershell
$env:CRM_PATH = Join-Path ([IO.Path]::GetTempPath()) ("shelfpilot-city-" + [guid]::NewGuid() + '.sqlite3')
& $py -c "import os; from pathlib import Path; from src.crm.store import CRM; CRM(Path(os.environ['CRM_PATH'])).save('browser@example.test', {'city': 'Pune'})"
& $py scripts/tasks.py run --port 8011
# After stopping this scratch server:
Remove-Item Env:CRM_PATH
```

**10–12.** Run only the matching block. Disable overrides when checking defaults.

```powershell
@'
import asyncio
from contextlib import aclosing
from src.core.settings import Settings
from src.llm.reply import ReplyPath
async def first():
    settings = Settings(_env_file=None, gemini_model="fixture-a", gemini_fallback_model="fixture-b")
    async with aclosing(ReplyPath(settings).converse("hello", (), {}, ())) as events:
        event = await anext(events)
        print(event["provider"], event["model"])
asyncio.run(first())
'@ | & $py -
@'
from src.core.settings import Settings
from src.llm.gemini import ProviderError
from src.llm.reply import ReplyPath
budget = ReplyPath(Settings(_env_file=None)).budget
budget.reserve(1)
budget.reserve(1)
try:
    budget.reserve(1)
except ProviderError as error:
    assert error.local and error.status == 429
    print(budget.usage())
else:
    raise AssertionError("Expected the local cap to reject request three.")
'@ | & $py -
& $py -c "from src.core.settings import Settings; print('Default TTS:', Settings(_env_file=None).voice_tts)"
```

**13–14.** Insert the route inside `create_app` and the test at module level.

```python
    @app.get("/api/lead-count")
    async def lead_count() -> dict[str, int]:
        records = await crm_view()
        return {"count": len(records["leads"])}
```

```python
def test_angry_badge():
    assert analyze_turn("I am angry.").sentiment == "Negative"
```

```powershell
@'
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import yaml
from src.api.app import create_app
with TemporaryDirectory() as box:
    os.environ["CRM_PATH"] = str(Path(box) / "crm.db")
    Path("docs/API_SPEC.yaml").write_text(
        yaml.safe_dump(create_app().openapi(), sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
'@ | & $py -
& $py -m pytest -q tests/integration/test_contract.py
& $py -m pytest -q tests/unit/test_analysis.py::test_angry_badge
```

**15.** Compare the report after two and three negative turns.

```powershell
@'
from src.analytics.core import analyze_turn, summarize_call
m = analyze_turn("I am angry.")
for count in (2, 3):
    print(summarize_call([m] * count, booked=False).next_action)
'@ | & $py -
```

[VERIFIED] Scratch changes were restored. Recipe 2 first failed because the edit touched nested JSON arrays. Inserting only at the outer bracket fixed the rehearsal.

## 5. Something broke

| Symptom and exact clue | First check | Where to point | What to do |
|---|---|---|---|
| LIVE falls back. `Live quota reached, using mock` or `Gemini returned a quota limit (HTTP 429).` | See provider trace and local cap. | `src/api/live_mode.py` → `provider_reason`, `src/llm/reply.py` → `RequestBudget.reserve` | Use Mock for the demo. Check configured models and provider quota privately before retrying LIVE. |
| A known answer becomes `I’ll check with our team and can offer a human follow-up.` | Check the approved record, then look at the retrieved passage and model's output classification in an offline test. | `src/rag/index.py` → `Knowledge.retrieve`, `src/llm/conversation.py` → `check_line` | If search missed, fix the reviewed card or ranking. If the quote was wrong, fix and test the prompt or output handling. |
| A reply states an unsupported fact. Possible UI clue: `No source: abstained` on a citation-free knowledge-style reply. | Check the exact sentence and whether it actually has a source ID. | `frontend/src/CockpitPanels.jsx` → `ChatMessage`, `src/llm/conversation.py` → `check_line` | Replay with a fake provider and assert that the sentence is blocked. No raw production prompt log exists to consult. |
| The model says it booked something with no row. | Open Bookings or GET `/api/crm`. Check whether a server-generated booking reply was emitted. | `src/api/conversation.py` → `live_turn`, `src/crm/store.py` → `CRM.book` | Treat the stored row as proof. Reproduce with a fake before changing claim handling. |
| `There is no pending demo time. Say book a demo first.` | On the same socket, check both contact and offered slot. | `src/crm/conversation.py` → `BookingSession.handle` | Save contact, ask “Book a demo” again, then use the confirm chip. A spoken custom time does not set the slot on main. |
| Wrong `Neutral` or `Analysis unavailable` | Distinguish completed local rules from no result. The worker can log `A demo analysis job was skipped.` | `src/analytics/core.py` → `analyze_turn`, `src/analytics/worker.py` → `Insights.work`, `frontend/src/CockpitPanels.jsx` → `ChatMessage` | Reproduce the exact text with `analyze_turn`. Queue or turn results can also be missing. |
| `Microphone unavailable. Check browser permission or type your message.` | Check site permission, secure origin or localhost, and input device. | `frontend/src/Console.jsx` → `toggleMic` | Reconnect or type. For STT `Transcription unavailable. Type your message to continue.`, inspect `transcribe_audio` in `src/api/voice.py` and model setup. |
| `Speech playback failed. Read the reply in the transcript.` | Check the speech request and the browser voice. HTTP 204 means browser fallback. | `frontend/src/voice.js` → `createPlayback`, `src/api/voice.py` → `speak_sentence` | Use browser speech or text. Check latency stages separately. |
| Port is taken or the wrong server replies. | Check the listener and `/health`. | `scripts/tasks.py` → `main`, `src/api/app.py` → `health` | Run on another port via `--port 8011`. If replacing a server you own, stop it from its terminal. The OS bind error varies. |
| Search is empty after editing cards. `Local embeddings unavailable. Using reviewed keyword retrieval.` may also show. | Check the edited file's digest and schema. | `src/rag/index.py` → `Knowledge.load`, `src/api/app.py` → `lifespan` | Update the reviewed digest, restart and run the knowledge evaluation. The digest rejection itself is silent. |
| Tests failed after a change. `FAILED` identifies the first assertion. | Run the specific test before full verify. | `tests/integration/test_contract.py` → `test_published_contract_matches_live_routes`, `scripts/tasks.py` → `main` | For route changes, update the checked-in contract. Run `verify` again. |
| Old UI or `Build the console with scripts/tasks.py setup first.` | Check the process/port and rebuild the bundle. | `src/api/app.py` → `console`, `frontend/src/main.jsx` → `Page` | Build with npm, restart if needed, then hard reload with Ctrl+Shift+R at `/console`. |

**Offline reproductions on 2026-11-26 [VERIFIED].** Feeding the booking handler “book a demo”, a fictional contact, “tomorrow 5 PM” and “Confirm booking” ended with `There is no pending demo time. Say book a demo first.` and zero booking rows. Both “i dont want to buy” and “ok i change my mind and i am too happy to buy with the 10 percent discount” returned `Neutral` from the local analyzer. In a fake LIVE draft, two unsupported claims with no evidence produced two identical replacement sentences. That reproduces the duplicate mechanism. The original trigger text for the reported duplicate was unavailable.

## 6. Settings and Windows commands

Code defaults come from `Settings` in `src/core/settings.py` (approx 7–57). The safe setup sample is `.env.example`. Put any real credentials in the ignored local environment file. An empty default below means “unset.” Provider caps below are application settings.

| Name | Meaning | Code default | Safe example |
|---|---|---|---|
| `AGENT_MODE` | Starting session mode | `mock` | `mock` |
| `GEMINI_API_KEY` | Gemini credential | unset | leave blank in Mock |
| `OPENAI_API_KEY` | Optional credential setting. No OpenAI reply adapter is wired on main. | unset | leave blank |
| `GEMINI_MODEL` | First LIVE text model | empty | `gemini-3.5-flash-lite` from the sample |
| `GEMINI_FALLBACK_MODEL` | Second LIVE text model | empty | `gemini-3.1-flash-lite` from the sample |
| `OPENAI_MODEL` | Optional model setting, unused in current reply path | empty | leave blank |
| `GEMINI_THINKING` | First model thinking setting | `minimal` | `minimal` |
| `GEMINI_FALLBACK_THINKING` | Second model thinking setting | `minimal` | `minimal` |
| `GEMINI_RPM` | Local Gemini requests per minute | `8` | `8` |
| `GEMINI_DAILY` | Local Gemini requests per rolling day | `60` | `20` |
| `GEMINI_TPM` | Local Gemini estimated tokens per minute | `12000` | `12000` |
| `ALLOW_FALLBACK_DEMO` | Enable the simulated fallback button | `false` | `true` for a local demo |
| `GEMINI_STT_MODEL` | Gemini speech-to-text model | `gemini-3.5-transcribe` | same |
| `GEMINI_TTS_MODEL` | Gemini text-to-speech model | `gemini-3.8-flash-tts` | same |
| `VOICE_TTS` | Server speech engine or browser speech | `edge` | `browser` |
| `VOICE_STT` | Preferred speech recognizer | `gemini` | `local` after installing models |
| `WHISPER_EN_MODEL` | Local English recognizer size | `small` | `base` |
| `KNOWLEDGE_EMBEDDINGS` | Optional vector search | `false` | `false` |
| `CRM_PATH` | SQLite file, created by the app | `data/runtime/crm.sqlite3` | `scratch.sqlite3` |
| `PUBLIC_DEMO` | Enable public guard | `false` | `false` locally |
| `PUBLIC_LIVE_ENABLED` | Permit LIVE in a public deployment | `false` | `false` |
| `PUBLIC_ACCESS_CODE` | Secret for public unlock | unset | leave blank locally |
| `PUBLIC_REQUESTS_PER_MINUTE` | Local per-IP public request ceiling | `20` | `20` |
| `PUBLIC_DAILY_REQUEST_CAP` | Local per-IP public daily cap | `250` | `100` |

LIVE model access depends on the authenticated catalog. The examples are project settings, and current access was NOT MEASURED in this docs task.

```powershell
py -3.13 scripts/tasks.py setup
# Optional first-time downloads
py -3.13 scripts/tasks.py setup --voice-models --knowledge-model
$py = Join-Path '.venv' 'Scripts/python.exe'
$env:AGENT_MODE = 'mock'
& $py scripts/tasks.py run --port 8000
# Open http://127.0.0.1:8000/console in your browser.
# In another shell at the repo root, set $py again before running these:
& $py scripts/tasks.py scan
& $py scripts/tasks.py verify
& $py -m pytest -q tests/unit/test_knowledge.py
& $py -m pytest -q tests/integration/test_conversation_v2.py
& $py -m scripts.evaluate_knowledge
& $py scripts/tasks.py demo --port 0
npm.cmd --prefix frontend run build
Get-NetTCPConnection -LocalPort 8000 -State Listen
Invoke-RestMethod http://127.0.0.1:8000/health
```

If Make is available, the equivalents are `make setup`, `make setup VOICE_MODELS=1 KNOWLEDGE_MODEL=1`, `make scan`, `make verify`, `make run PORT=8000` and `make demo PORT=0`. To use the local LIVE setup, configure the Gemini names and key locally, then remove the `AGENT_MODE` process override and use the cockpit switch. The scripted hero always forces Mock and uses a temporary database.

## 7. Why this choice?

- **FastAPI.** In simple words, one server routes text, audio and records. A socket ties a conversation to one worker. In production, route each active socket consistently and share the data it needs.
- **SQLite.** One file stores prototype records and enforces unique bookings. Writes share the same file. For more concurrent writers, use Postgres and keep the unique constraint.
- **Local embeddings.** The fingerprints help match meaning across wording and languages without a hosted embedding request. The model adds RAM and startup work. At scale, put retrieval behind a service and measure misses on real questions.
- **Whisper Small.** It can recognize Hindi on the machine after the model has been downloaded. CPU time can slow a voice turn. A production path could use streaming STT or GPU capacity and measure that outcome.
- **edge-tts.** It provides voice without a paid prototype speech account. It is an unofficial demo-only dependency and can fail. Use a supported speech service and keep browser fallback.
- **Gemini A → B → mock.** Two configured models give the app a second attempt, and mock keeps a demo available offline. The models can still share a quota problem. Use explicit production quotas, retries and deadlines.
- **Mock mode.** It makes the demo repeatable and keeps tests inexpensive. It uses local rules and approved examples with limited free conversation. Production verification still needs real provider smoke tests.
- **Server-side booking.** The server owns the contact and the slot. SQLite decides who gets the time. Production would add a clearly modeled state machine and link it to a real calendar.
- **Post-generation guardrail.** The checker can refuse an unsupported quote before it reaches playback. This adds a wait and can miss claims or reject useful text. Expand accepted evidence carefully and test both mistakes.
- **No Vercel serverless backend.** This app expects a FastAPI process that accepts persistent WebSocket connections. Deploy that process to a WebSocket-capable HTTPS host. The hosted frontend can be separated later.

## 8. Quiz

Cover the right column. Find each answer in the editor. The approximate locations are in section 2.

| Question | Point here |
|---|---|
| 1. Where is Growth's approved price? | `data/knowledge/plans-and-prices.json` → Growth pricing record |
| 2. Who verifies a card digest? | `src/rag/index.py` → `Knowledge.load` |
| 3. What is a chunk? | `src/rag/index.py` → `Chunk` |
| 4. Who builds vectors? | `src/rag/index.py` → `Knowledge.enable_embeddings` |
| 5. Where is LIVE retrieval? | `src/rag/index.py` → `Knowledge.retrieve` |
| 6. Where is Mock lookup? | `src/rag/index.py` → `Knowledge.lookup` |
| 7. Where is the LIVE persona? | `src/llm/conversation.py` → `PERSONA` |
| 8. Where is the action schema? | `src/llm/conversation.py` → `LiveDraft` |
| 9. Where is the claim verifier? | `src/llm/conversation.py` → `check_line` |
| 10. Where is the replacement sentence? | `src/llm/claims.py` → `CHECK_SHORT_EN` |
| 11. Where is the Gemini payload? | `src/llm/gemini.py` → `request_body` |
| 12. Where is backup order? | `src/llm/reply.py` → `ReplyPath.converse` |
| 13. Who rejects over-budget calls? | `src/llm/reply.py` → `RequestBudget.reserve` |
| 14. Where does LIVE switch mode? | `src/api/live_mode.py` → `switch_mode` |
| 15. Where is the socket entry? | `src/api/text_session.py` → `text_session` |
| 16. Where is the selected action run? | `src/api/conversation.py` → `live_turn` |
| 17. Where is recent history kept? | `src/memory/session.py` → `LeadSession.remember` |
| 18. Where is a target date parsed? | `src/memory/details.py` → `target_date` |
| 19. Where is booking pending state? | `src/crm/conversation.py` → `BookingSession` |
| 20. Where is the slot chosen? | `src/crm/store.py` → `CRM.offer` |
| 21. Where is uniqueness enforced? | `src/crm/store.py` → `CRM.__init__` / `CRM.book` |
| 22. Where is a lead updated? | `src/crm/store.py` → `CRM.save` |
| 23. Where is Neutral chosen? | `src/analytics/core.py` → `analyze_turn` |
| 24. Where is Hot chosen? | `src/analytics/core.py` → `summarize_call` |
| 25. Where is the report queued? | `src/analytics/worker.py` → `Insights.submit` |
| 26. Where are dashboard totals? | `src/analytics/store.py` → `ReportStore.dashboard` |
| 27. Where does recording start? | `frontend/src/Console.jsx` → `toggleMic` |
| 28. Where does STT select a provider? | `src/api/voice.py` → `transcribe_audio` |
| 29. Where are receipts and citations drawn? | `frontend/src/CockpitPanels.jsx` → `ChatMessage` |
| 30. Where do log filters attach? | `src/core/logging.py` → `protect_server_logs` |

### Ten edit drills with answers

| Interviewer asks | Answer |
|---|---|
| 1. Make Growth cost ₹2,699. | Recipe 1. Edit both language fields, approve the file and query the card. |
| 2. Add a printable setup FAQ. | Recipe 2. Add a bilingual card and test its new alias. |
| 3. Make the assistant say “check with a specialist.” | Recipe 3. Change the LIVE replacement constant and test a blocked claim. |
| 4. Stop weak semantic matches at 0.60. | Recipe 4. Raise the threshold to 0.72 and verify one passage becomes zero. |
| 5. Start with a different greeting. | Recipe 5. Edit `initialMessage`. For model tone, edit `PERSONA` too. |
| 6. Call a 75-point lead Warm. | Recipe 6. Make the Hot boundary 100 and check the same 75-point fixture. |
| 7. Move the 11:00 slot to noon. | Recipe 7. Change the hour tuple and query the first empty slot. |
| 8. Add city to CRM. | Recipe 8. Add the profile field, seed it, and render it in the CRM row. |
| 9. Add a clickable CSV question. | Recipe 9. Edit `scenarios.Ask` and build. |
| 10. Try B first or cap Gemini at two calls. | Recipes 10–11. Reorder the tuples or lower the cap and check the first event or third request. |

## Things I would admit are NOT built

- Automatic ingestion of arbitrary documents and a hosted vector database.
- A real CRM or calendar integration on main. SQLite CRM, basic cancellation and rescheduling on the current connection are built.
- Natural-language booking time selection, an affirmative “yes” that commits a slot, and a separate receipt ID. The console explicitly says `Receipt ID unavailable in this console`.
- Gemini sentiment, confidence scores, a Gemini summary prompt and an in-call human handoff on main. The local rules can mark unsupported phrasings Neutral. A post-call recommendation can flag a concern for review.
- Full user accounts, role-based permissions and tenant isolation. There is an optional public access-code gate.
- Streaming mic audio and automatic endpointing in the main speech loop. It uploads a WAV when recording stops. LIVE does not show unreviewed text while waiting for structured output.
- Guaranteed detection of every unsupported claim or false booking claim. The verifier checks model classifications and selected output patterns. A booking row is the way to confirm a reservation.
