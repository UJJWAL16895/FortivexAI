# Contributor instructions

Use the current gate in docs/TASKS.md. Start from its acceptance criteria and test through the normal user entry point. Keep the offline path deterministic. Preserve the root Makefile and the equivalent Python commands on Windows. Update docs/API_SPEC.yaml and the contract test when public endpoints change.

Keep keys in a local ignored .env and pass only model IDs and safe diagnostic codes into reports. Do not print .env contents. Run the index-aware secret scan before committing. See docs/WORKFLOW.md for the required report, learning entry, changelog, diff review and Conventional Commit. Use phase tags only after their end-to-end demonstration runs.
