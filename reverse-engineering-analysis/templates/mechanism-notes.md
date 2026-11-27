# Mechanism notes (code track) — {{SLUG}}

Source mode: {{SOURCE_MODE}}. In `ui-only` mode this file stays empty apart from this header.
Each block = one hypothesis found in the source, written in plain words (no code, no identifiers to copy).
Close every block with exactly one of:
- `Verified by: OBS-nnn` — reproduced through the UI
- `Contradicted by: OBS-nnn` — the UI behaves differently (UI wins; add to Observed defects or Open questions)
- `[CODE-ONLY]` + reason — the UI cannot show it (audio, timer, unload handler, file format, server-side rule)

<!-- Example (delete when you add real blocks)
### CODE-001 Title length limit
- Location: editor form component (file:line in the original, for the analyst only)
- Finding: the title field accepts at most 40 characters
- Verify: type 41 characters into the title field and save
- Verified by: OBS-014
- Affects: FR-003
-->
