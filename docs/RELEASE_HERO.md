# Hero acceptance walkthrough

Start with the README setup and run commands. For an automated browser run install the pinned browser utilities with npm ci --prefix tools/diagrams, use a fresh CRM_PATH and run node tests/e2e/hero_browser.mjs URL CHROME_PATH with CHECK_HERO_INSIGHTS=1. The browser checks a real citation, a stored appointment, returning identity and the Insights draft. The command requires a local Chromium-based browser.

1. Ask “How much does Growth cost?” Say “The answer is a reviewed card, and the transcript shows its source.”
2. Ask for a 40% discount. Say “I want the agent to abstain when the corpus cannot support the offer.”
3. Type “My name is Asha.” and then “My email is hero@example.test.” Use fictional data.
4. Say or type “Book a demo.” Read the offered IST time. Type “Confirm booking.” Repeat once. Open View demo CRM and point out the unique receipt.
5. End conversation. Open View insights. Show the saved-call denominator and the draft. Refresh the browser or restart the local API to show the SQLite results.
6. For live voice, use the microphone for the price question and the two booking verbs. Allow mic access, record, speak, stop and wait for the playback panel. Keep text ready if speech fails.
