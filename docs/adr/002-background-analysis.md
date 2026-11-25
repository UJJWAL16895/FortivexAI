# ADR 002 · Keep analysis off the spoken reply path

Accepted for design. The voice budget measures time until playback. Read the latest committed state, retrieve only necessary evidence and stream the reply. Queue profile extraction, scoring, sentiment and summary work keyed by call and turn. An immediate angry utterance can receive an empathetic response from its text while the dashboard label arrives later. Resolve late jobs by sequence; cap queues. Test by pausing analysis and observing uninterrupted reply audio.
