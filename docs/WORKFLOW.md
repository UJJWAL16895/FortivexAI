# Step workflow

Read the current report and task gate. Publish a short plan with observable acceptance criteria. Capture one failing test for the new behavior. Implement the smallest integrated change, then exercise the user-facing entry point. Compare the diff with the plan and check scope, secrets, failure behavior and previously supported paths.

Record objective, plan, decisions, actual commands and output, limitations, assumptions, risks and next step in docs/reports/STEP-XXX.md. Record a plain-language lesson, relevant files and exercise in LEARNING_LOG.md. Update TASKS.md and CHANGELOG.md, run the staged scan before committing, then create the Conventional Commit. Attach release tags only at the designated verified demo gates.

Use [VERIFIED] for a measured outcome or read source, [ASSUMED] for proposed values and [UNKNOWN] for an open question. Put assumptions and unresolved questions in their registers. Avoid putting prompt content, contacts, recordings or secrets into reports.

Before tagging or closing a phase, prove the README quickstart from a clean checkout, update SUBMISSION_CHECKLIST.md and record evidence for the numbered PRD criteria. Include five questions with answers for the phase. Explain advanced mechanisms in plain language when they enter the code.
