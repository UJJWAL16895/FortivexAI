# Interview notebook · Foundation

**Why can a key list models and still fail on a sales call?** The catalog probe only establishes listing access. The OpenAI minimal generation probe returned exhausted credit. Use a bounded generation probe, monitor call-specific failures and keep a deterministic mock path.

**Why separate health from provider readiness?** The health API should tell us that the process can serve HTTP even during a provider outage. A real cloud request on every health check adds quota consumption and a dependency on network availability.

**Why test both the index and the working tree?** The commit takes its contents from the index. A developer can stage a secret and then clean the working file. The disposable-repository regression test reproduces this exact sequence without real credentials.

**Where does a model stop having authority in a booking?** In the target design it may propose a tool name and arguments. The server validates confirmation and commits a transaction. The committed receipt determines the spoken outcome.

**How would you explain the first-audio metric?** Time it from the user’s final voiced sample to playback start on the browser clock. STT, grounding, time to first text, accumulating a speakable phrase, synthesis and buffering all contribute. STEP-000 measured only time to first visible text.

The P13 gate requires 40 questions tied to the final codebase; these five cover decisions already inspectable at P0.
