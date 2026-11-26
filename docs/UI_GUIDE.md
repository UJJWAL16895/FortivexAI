# Showcase guide

Open / for the overview and /console for the working console. The route entry in frontend/src/main.jsx loads either page separately. Showcase.jsx contains the hero, section list, worked example, architecture controls and scenario values. Console.jsx connects the microphone and WebSocket. The cockpit panel and record components render their data.

- Change the hero text in Showcase.jsx inside the section with id home.
- Add or edit a feature in the features list at the top of Showcase.jsx.
- Change the accent at --accent and --glow in styles.css. Check contrast against the background.
- Change wave timing in the signal animation. IntersectionObserver highlights the flow and reveals cards. Reduced motion disables the waveform animation and parallax.
- The sample array contains the local script. Its claims and numbers are illustrative. Keep real observations synced with SCALABILITY.md and COSTS.md.

## Quiz

1. **Where is the real console?** At /console.
2. **Does the local script spend quota?** It plays locally from the array.
3. **Where does the wave in the console get its signal?** A Web Audio analyser reads the active mic stream.
4. **How does reduced motion work?** The CSS media query stops animation and JavaScript skips parallax and typing.
5. **Where do scenario costs come from?** COSTS.md, including its assumptions.

## Live Call Cockpit

| Panel | File and purpose |
|---|---|
| Shell | Console.jsx renders the navigation, connection badge, timers, presenter switch, mobile tabs and reset. Its existing WebSocket handler supplies the data. |
| Call controls | CockpitPanels.jsx → CallPanel. The analyser in Console.jsx supplies the real mic signal. The stage is derived from mic, pending, playback and error state. Edit the stage colors and animations in cockpit.css. |
| Conversation | CockpitPanels.jsx → Conversation and ChatMessage. The existing delta event streams approved text. The source drawer shows the exact approved excerpt that the backend returned with the citation. |
| Intelligence | CockpitPanels.jsx → Intelligence. Add a named IntelligenceGroup and pass it the real data it needs. If the field is missing, render a dash or a message. |
| Records | CockpitRecords.jsx loads when first opened. It renders the existing CRM and Insights snapshots as cards. |

The shared palette is in styles.css. The layout, stage colors, labels and controls are in cockpit.css and CockpitPanels.jsx. Scenario and guided-message wording is in cockpitData.js. Opening the guide leaves the conversation untouched until you click a suggested message. Smaller screens offer conversation, call and intelligence tabs. The record buttons open their drawers directly from any mobile tab.

Sentiment and BANT come from the latest **saved** report after a call ends. The current protocol supplies neither live analysis events nor a report ID that would associate that snapshot with a socket on a shared server. The existing booking reply supplies the time and timezone but no separate receipt ID. The cockpit shows the date/time and labels the missing ID. Roman Hinglish has no reliable protocol label. The transcript labels mixed script and explicit microphone hints where available.

Icons are small inline SVG paths in cockpitIcons.jsx. They add no dependency, network reference or accessible name to decorative icons.

## One-click LIVE and MOCK

Console.jsx renders the segmented buttons and the status ribbon. It sends one mode request on the open socket. It disables the mic during the check and adds a divider only after the server confirms a mode change. The ribbon shows the probe round-trip, latest Gemini first text and the server's rolling counter. CSS in cockpit.css defines mode colors and honors reduced motion. Screenshots and real smoke results are in STEP-021.
