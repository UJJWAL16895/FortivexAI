# Morning report · 26 November 2026

Submit the [FORTIVEX repository](https://github.com/UJJWAL16895/FortivexAI) at **final-submission**. Use `git rev-parse 'final-submission^{commit}'` to copy its exact commit ID into a form. The locally exercised application snapshot was `c28f478`. Release audit notes and claim corrections follow that snapshot. The rollback for the complete pre-showcase demo is **demo-final**.

## What changed

- SQLite retains analyzed calls, sentiments, BANT and summaries. The restart fixture checked the booking-rate denominator.
- The English, Hindi and Hinglish fixtures now cover mid-call changes, quantities, dates and phone normalization. Slow replies, disconnects, failed transcription, repeated confirmation and selected log redaction have regression coverage.
- The product landing page and offline scripted sample sit alongside the working console. Booking can be cancelled or moved within the original session. Saved call summaries export as Markdown.
- The public Docker preset defaults to mock. Intentional live needs a code and has process-local request caps. The deployment account steps remain yours.
- The interview kit includes architecture exports, the live-coding map, 40 questions, rehearsal evidence and a step-by-step demo script. [Checklist](docs/SUBMISSION_CHECKLIST.md) · [Audit](docs/CLAIMS_AUDIT.md) · [Demo script](docs/DEMO_SCRIPT.md)

The webhook adapter, config-only new locale, automatic two-turn handoff and additional Hindi tuning were deferred. The first three need broader contracts or language coverage. Hindi remains at the previously accepted measured checkpoint. No demo-depth tag was created. [Open questions](docs/OPEN_QUESTIONS.md)

## Ten-minute morning checklist

1. Open PowerShell in the repo. Run the commands below. Setup is needed once and initial dependency download time varies.
2. Visit [the local home page](http://127.0.0.1:8000), click **Watch a sample call**, and play the local fixture.
3. Open [Console](http://127.0.0.1:8000/console). Ask **How much does Growth cost?** Expect a price and a citation. Ask **Can I get 40% off?** Expect an offer to have a specialist follow up.
4. Type **My name is Asha.** and **My email is morning@example.test**. Ask **Book a demo**, then type **Confirm booking**. Check the IST time and one receipt in **View demo CRM**.
5. Click **End conversation** and **View insights**. Open the saved call, show the BANT reasons and download the Markdown report.
6. Check your own mic once in Chrome on localhost. Record a short backup video that only shows fictional data. Rehearse the pitch and use the architecture PDF for the walkthrough.

```powershell
git fetch --tags origin
git rev-parse 'final-submission^{commit}'
& .\.venv\Scripts\python.exe scripts/tasks.py verify
& .\.venv\Scripts\python.exe scripts/tasks.py demo --port 0
& .\.venv\Scripts\python.exe scripts/tasks.py run
```

For a new clone run the README setup first. For the mic test, use live mode with your existing ignored local settings if you want real speech recognition. Mock records and uses a fixture transcript. Stop the server with Ctrl+C.

## What an interviewer is most likely to notice

1. **Voice timing and mic permissions.** This is push-to-talk. Hindi readback was 3.98 s median over three warmed synthetic turns. Physical mic and fleet latency are unmeasured. Switch to text if needed.
2. **A narrow approved corpus.** Unsupported offers get a specialist follow-up offer. No actual handoff or email is sent.
3. **A synthetic operator workspace.** Contacts act as recall keys without identity verification. Keep real data out of the demo.
4. **Hosting limits.** A free host can sleep or lose its ephemeral SQLite file. Local Docker with its named volume demonstrates durability. Public quotas reset with the server.
5. **Commercial numbers.** Scale and cost are labeled scenarios. Real adoption and margins are unmeasured.

Only you can test the physical microphone, record a backup, authorize the hosting account, submit the form and revoke provider credentials when finished. If you deploy, keep the public preview in mock and follow [the host checklist](docs/DEPLOY_STEPS.md). The final audit supplies the verified rollback matrix.

For rollback, stop the server and run this in a clean checkout. Existing uncommitted work should be saved first. Keep the checkout’s database separate from the one you plan to use on stage.

```powershell
git fetch --tags origin
git switch --detach demo-final
& .\.venv\Scripts\python.exe scripts/tasks.py setup
& .\.venv\Scripts\python.exe scripts/tasks.py verify
& .\.venv\Scripts\python.exe scripts/tasks.py run
```
