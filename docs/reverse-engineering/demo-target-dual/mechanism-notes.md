# Mechanism notes (code track) — demo-target-dual

Source mode: authorized-source. Code track run after the UI pass (OBS-001–OBS-042); verification OBS-043–OBS-048.
Each block = one hypothesis found in the source, written in plain words (no code, no identifiers to copy).
Close every block with exactly one of:
- `Verified by: OBS-nnn` — reproduced through the UI
- `Contradicted by: OBS-nnn` — the UI behaves differently (UI wins; add to Observed defects or Open questions)
- `[CODE-ONLY]` + reason — the UI cannot show it (audio, timer, unload handler, file format, server-side rule)

### CODE-001 Duplicate titles are rejected
- Location: single HTML file, save handler of the editor (around line 87)
- Finding: saving is refused with the message "已有相同標題的筆記" when another note already has exactly the same (trimmed) title; the note being edited is excluded from the comparison. Not seen in the UI pass.
- Verify: create a note whose title equals an existing one (with surrounding spaces); then edit that existing note and save unchanged
- Verified by: OBS-045
- Also: OBS-048 (own title is not a conflict)
- Affects: FR-012

### CODE-002 Tag parsing rules
- Location: save handler (around line 88)
- Finding: tags split on ASCII and full-width commas, are trimmed and lowercased, empties dropped, duplicates removed, and only the first five unique tags kept — extra tags are dropped silently.
- Verify: save tags "a，b, A, c, d, e, f"
- Verified by: OBS-043
- Affects: FR-013

### CODE-003 Toast hides after about two seconds
- Location: toast helper (line 64)
- Finding: confirmation messages are shown for about 2 seconds, then hidden; a new message restarts the timer.
- Verify: save a note and look again after 3 seconds
- Verified by: OBS-044
- Affects: FR-022

### CODE-004 Tag text is inserted into the filter dropdown as markup
- Location: list rendering, tag filter options (line 74)
- Finding: note titles, bodies and tag chips are escaped, but the tag filter options are built from raw tag text, so markup in a tag becomes real elements (HTML injection / script injection vector).
- Verify: save a tag containing closing and opening option markup and open the filter
- Verified by: OBS-046
- Affects: FR-021, DEF-02

### CODE-005 Enter in the editor triggers the cancel button
- Location: editor form markup (lines 46–54)
- Finding: the editor is a dialog form whose first button is Cancel; pressing Enter in a single-line field activates that first button, so the dialog closes and nothing is saved.
- Verify: change a title and press Enter
- Verified by: OBS-024
- Also: OBS-025 (reproduced with typed keys)
- Affects: FR-017, DEF-01

### CODE-006 Sample data only when nothing is stored; reset deletes and reloads
- Location: load routine (lines 65–68) and reset handler (line 103)
- Finding: sample notes are fetched only when no stored document exists; an empty notes list is still "existing data". Reset removes the stored document and reloads the page, which re-fetches the samples and restores default settings.
- Verify: delete all notes and reload; run reset
- Verified by: OBS-042
- Also: OBS-040
- Affects: FR-002, FR-027

### CODE-007 Search runs over title and body glued together
- Location: list filter (line 75)
- Finding: the query is matched against the title immediately followed by the body, so text spanning the end of the title and the start of the body matches.
- Verify: note titled 乙 with body 丙, search "乙丙"
- Verified by: OBS-047
- Affects: FR-005, DEF-04

### CODE-008 Title sort uses Traditional Chinese collation
- Location: list sort (line 76)
- Finding: title order follows locale-aware comparison for Traditional Chinese (stroke-based for Han characters), always after the pinned-first rule.
- Verify: switch sort to title and compare 牛奶 / 測試筆記 / 讀書會 order
- Verified by: OBS-026
- Affects: FR-004

### CODE-009 Recent-first sort compares timestamps as text
- Location: list sort (line 76)
- Finding: the "most recently updated" order compares stored timestamp strings character by character. Sample notes carry a +08:00 offset while new saves are stored in UTC, so a note saved later in real time can sort below a sample note on the same day (e.g. UTC 15:00 vs local 20:15 = UTC 12:15).
- Verify: would need saving a note at a specific clock time relative to the sample timestamps
- [CODE-ONLY] the clock cannot be controlled through the UI; demonstrating it requires waiting for a particular wall-clock time or altering stored data by script
- Affects: FR-029, DEF-05

### CODE-010 Active navigation item marked for assistive technology
- Location: view switcher (line 99)
- Finding: the header button of the visible view is flagged as the current page for screen readers; the other is not.
- Verify: inspect the accessibility tree after switching views
- [CODE-ONLY] the devtools accessibility snapshot (also verbose) does not expose this state, and reading markup attributes is outside the allowed read-only checks
- Affects: FR-030

### CODE-011 No handling of a failed sample fetch or corrupt stored data
- Location: load routine (lines 65–68)
- Finding: if the sample file cannot be fetched or the stored document is not valid JSON, loading throws and the list is never rendered (blank area, no message).
- Verify: stop the server before first run, or corrupt the stored document
- [CODE-ONLY] would require breaking the user's server or writing to storage by script, both outside the run's rules
- Affects: FR-031

### CODE-012 View is chosen only at page load
- Location: startup line (104) and view switcher (99)
- Finding: the fragment is read once at load (#settings opens settings, anything else opens notes); later fragment changes (Back/Forward, typing in the address bar) are not listened to.
- Verify: click 筆記 after 設定, press browser Back
- Verified by: OBS-037
- Also: OBS-035, OBS-036
- Affects: FR-023, FR-024, DEF-03

### CODE-013 Editor error is cleared only when the dialog opens
- Location: open-editor routine (line 84)
- Finding: the inline error is reset each time the dialog opens, but not while the user edits the field.
- Verify: trigger the empty-title error, then type a title
- Verified by: OBS-018
- Affects: FR-018

### CODE-014 Pinning does not touch the timestamp
- Location: list click handler (line 95)
- Finding: toggling pin flips only the pinned flag; the updated time stays the same.
- Verify: pin a note and compare its timestamp
- Verified by: OBS-027
- Affects: FR-019
