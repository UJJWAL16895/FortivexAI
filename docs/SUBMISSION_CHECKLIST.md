# Submission checklist

Update this page every phase. A candidate release must run from a fresh checkout and its documentation must describe the actual behavior. Future items remain visible to the evaluator.

| Evaluation item | Status and evidence |
|---|---|
| Repository link and access | [VERIFIED] Public source repository. Record the checkpoint and fresh-checkout commands for each release. [FortivexAI](https://github.com/UJJWAL16895/FortivexAI) |
| Source code | [VERIFIED] React console, FastAPI, mock provider, runnable verification and pinned dependencies. See the directory guide. |
| Architecture diagram | [VERIFIED] Current system, sequence and data flow are in ARCHITECTURE.md. SVG exports and a one-page PDF are in docs/diagrams. |
| Working demo | [VERIFIED] Cited price, explicit IST booking and persisted demo CRM by text and browser voice. End the conversation and open Insights for the recent call report. STEP-007 through STEP-010 hold the evidence. |
| Business problem and feasibility | [ASSUMED] Initial segment, pilot design and ROI model documented in BUSINESS_CASE.md. |
| Scalability to 1,00,000 users | [ASSUMED] Workload math and migration plan in SCALABILITY.md. [VERIFIED] Loopback mock load tested through 500 clients. |
| Security and data handling | [VERIFIED] Local same-origin browser check, bounded input and staged secrets gate. Planned production controls and open questions in SECURITY.md. |
| Costs and deployment | [ASSUMED] Workload economics in COSTS.md. Reproducible demo deployment in DEPLOYMENT.md. Production rates and capacity remain open. |
| Interview preparation | [VERIFIED] Interview guide, 40 project questions, live-coding rehearsals, code map and phase quizzes. |
| Showcase | Browser checks, responsive screenshots and Lighthouse evidence are recorded in STEP-015. The previous baseline is demo-final. |
| Public preview | [VERIFIED] Local Docker startup and mock default. The evaluator gate and caps have automated coverage. [UNKNOWN] Hosted TLS and persistence until deployment. See DEPLOY_STEPS.md and STEP-018. |

## Release tags

| Tag | When to use it |
|---|---|
| final-submission | Complete submission candidate with audited documents, showcase and verified console. |
| demo-ui | Restore the verified showcase and baseline console before optional additions. |
| demo-final | Use the hardened baseline if showcase or later changes cause a problem. |
| pre-ui | Rollback checkpoint taken before starting the showcase branch. Same commit as demo-final. |
| demo-voice-booking-crm | Earlier synthetic voice booking and CRM checkpoint. Later main fixed its Ubuntu race fixture. |
| demo-text-hero | Earlier text-only RAG, booking and CRM exhibit. |
| demo-voice-fast | Earlier measured latency and checked speech checkpoint. |
| demo-voice-thin | Earlier minimal browser voice round trip. |
| demo-p1-text | Earliest keyless text fallback. |

Use the keyless run from README first. Check the latest audit, physical microphone status and account-side tasks in MORNING_REPORT.md. Optional depth deferrals are in OPEN_QUESTIONS.md.

## Console cockpit

Use pre-console-ui to restore the earlier console, or use demo-cockpit after the cockpit release gates pass. The accepted submission checkpoint remains available as final-submission. See STEP-020 for the browser checks, Lighthouse, screenshots and backend data limits.

## Live-mode checkpoint

See STEP-021 for the switch checks, screenshots and real smoke evidence. pre-live-toggle and demo-cockpit preserve the earlier cockpit. demo-live-toggle is the release tag for the verified switch.

## Cockpit polish checkpoint

See STEP-022 for source labels, live analysis, grounded elaboration and layout evidence. pre-polish points to the previous live-toggle checkpoint. demo-polish is the tagged release once the verification gates pass.
