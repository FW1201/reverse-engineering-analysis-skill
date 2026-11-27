# 04 TDD implementation plan — demo-target-dual

Each task is one RED → GREEN → REFACTOR cycle. Do tasks in order; do not start a task before the previous one is green.
Test names should quote the acceptance criterion they prove. Paths are relative to the build location in AGENT-HANDOFF.md.

## Task list

### T-001 Project skeleton + test runner + empty notes screen
- Covers: FR-007
- RED: tests/ui/notesView.test.ts — "shows 還沒有筆記，按「新增筆記」開始 when there are no notes": render the app with an empty store; expect that text and a button named 新增筆記. Fails: no app exists.
- GREEN: Vite+TS scaffold, Vitest+jsdom config, src/main.ts mounting a notes view that renders the empty-state text.
- REFACTOR: extract render helpers (text-only node creation).
- Done when: `npm test` runs and passes.

### T-002 Title validation rules
- Covers: FR-010, FR-011, FR-012
- RED: tests/domain/note.test.ts — validateTitle("   ") returns error 標題不可空白; a 41-char input is limited to 40; " 甲 " against existing 甲 returns 已有相同標題的筆記; same title for the note itself is accepted.
- GREEN: implement validateTitle(input, notes, editingId).
- REFACTOR: keep messages in one constants module.
- Done when: all four cases pass.

### T-003 Tag parsing
- Covers: FR-013
- RED: tests/domain/note.test.ts — parseTags("a，b, A, c, d, e, f") equals [a,b,c,d,e]; parseTags(" Test , work ,, ") equals [test, work]; formatTags([test, work]) equals "test, work".
- GREEN: implement parseTags / formatTags.
- REFACTOR: none expected.
- Done when: tests pass.

### T-004 Sorting rules
- Covers: FR-003, FR-004, FR-029
- RED: tests/domain/query.test.ts — pinned 11/20 before unpinned 11/22 before 11/21 (updated sort); title sort yields 牛奶, 測試筆記, 讀書會 with pinned above; a note at 2026-11-22T15:00Z sorts above one at 2026-11-22T20:15+08:00.
- GREEN: comparator using Date.parse and Intl.Collator('zh-Hant').
- REFACTOR: single sortNotes(notes, sort) export.
- Done when: tests pass.

### T-005 Search and tag filter
- Covers: FR-005, FR-006
- RED: tests/domain/query.test.ts — query "q1" matches body "確認 Q1 預算"; "乙丙" does NOT match title 乙/body 丙; tag work + query 構式 returns only the study+work note; tagOptions returns sorted unique tags.
- GREEN: filterNotes(notes, query, tag), tagOptions(notes).
- REFACTOR: none.
- Done when: tests pass.

### T-006 Repository: first run, persistence, tolerant load
- Covers: FR-002, FR-028, FR-031
- RED: tests/store/repository.test.ts — with empty storage and a mocked sample fetch, load() returns 3 notes and writes storage; with stored empty list, load() does not fetch; with fetch rejecting, load() returns empty notes; with corrupt stored text, load() returns empty notes without throwing.
- GREEN: implement load/save with try/catch and default settings.
- REFACTOR: inject storage and fetch for testability.
- Done when: tests pass.

### T-007 Note list cards
- Covers: FR-001, FR-021
- RED: tests/ui/notesView.test.ts — card for 牛奶 shows body, chip home, a date line containing 2026/11/21, buttons 釘選/編輯/刪除; a title with angle-bracket markup and a tag with option markup render literally and the tag filter has exactly one option with the literal tag label.
- GREEN: card renderer and tag filter built with textContent only.
- REFACTOR: shared date formatter (zh-TW).
- Done when: tests pass.

### T-008 Live search, filter, empty/no-match, not persisted
- Covers: FR-005, FR-006, FR-007, FR-008
- RED: tests/ui/notesView.test.ts — typing q1 with user-event leaves one card; typing a miss shows 找不到符合的筆記; selecting work + typing 構式 leaves one card; remounting the app shows an empty search box and all notes.
- GREEN: wire input/change events to re-render; keep query in memory only.
- REFACTOR: none.
- Done when: tests pass.

### T-009 New-note dialog and create
- Covers: FR-009, FR-010, FR-014, FR-022
- RED: tests/ui/editorDialog.test.ts — clicking 新增筆記 opens modal 新增筆記 with focus in title; 儲存 with empty title shows 標題不可空白 and stays open; valid save closes, adds an unpinned card, status region shows 已新增 which is gone after advancing fake timers 3 s.
- GREEN: dialog + form submit handler + toast module.
- REFACTOR: toast timer reset on new message.
- Done when: tests pass.

### T-010 Edit, cancel, Escape, Enter saves, error lifecycle
- Covers: FR-015, FR-016, FR-017, FR-018
- RED: tests/ui/editorDialog.test.ts — 編輯 opens 編輯筆記 prefilled (tags "test, work"); 取消 and Escape leave the note unchanged; changing the title and pressing Enter in the title field saves and shows 已更新; Enter with empty title shows 標題不可空白; reopening the dialog shows no error; saving updates the date line.
- GREEN: prefill logic; cancel button type=button; submit on Enter.
- REFACTOR: share create/edit save path.
- Done when: tests pass.

### T-011 Pin toggle
- Covers: FR-019
- RED: tests/ui/notesView.test.ts — pressing 釘選 moves the note to the top group, button name becomes 取消釘選, date line unchanged; state persisted to storage.
- GREEN: togglePin mutation without touching updatedAt.
- REFACTOR: none.
- Done when: tests pass.

### T-012 Delete with in-app confirmation
- Covers: FR-020
- RED: tests/ui/confirmDialog.test.ts — 刪除 opens modal 確定刪除「測試筆記」？此動作無法復原。 with focus on 取消; 取消 keeps the note; 確定刪除 removes it and shows 已刪除; deleting the last tagged note removes its tag option.
- GREEN: confirm dialog module + delete mutation.
- REFACTOR: none.
- Done when: tests pass.

### T-013 Router: fragments, deep link, history
- Covers: FR-023, FR-024, FR-030
- RED: tests/ui/router.test.ts — loading with #settings shows settings; unknown fragment shows notes and fragment becomes #notes; after nav 設定 → 筆記, dispatching history back (hashchange) shows settings; the visible view's header button has aria-current="page", the other none.
- GREEN: router listening to hashchange.
- REFACTOR: none.
- Done when: tests pass.

### T-014 Settings: dark mode, sort, persistence
- Covers: FR-025, FR-026
- RED: tests/ui/settingsView.test.ts — ticking 深色模式 applies the dark theme class/attribute at once and survives remount; choosing 標題 A→Z re-orders the list and survives remount.
- GREEN: settings view + persistence.
- REFACTOR: theme via CSS custom properties.
- Done when: tests pass.

### T-015 Reset all
- Covers: FR-027
- RED: tests/ui/settingsView.test.ts — with window.confirm mocked false nothing changes; mocked true restores the 3 sample notes, dark off, sort 最近更新; confirm text is 清除所有資料並還原範例？.
- GREEN: reset handler clearing storage and reloading state from samples.
- REFACTOR: none.
- Done when: tests pass.

### T-016 E2E happy paths and responsive check
- Covers: FR-001, FR-014, FR-015, FR-019, FR-020, FR-024, FR-025, FR-027, FR-028
- RED: e2e/flows.spec.ts (Playwright) — first run lists 3 samples; create → edit with Enter → pin → reload persists → delete; Back button follows views; dark mode survives reload; reset restores samples; at 360 px width document scrollWidth equals viewport width.
- GREEN: fix whatever the E2E run exposes.
- REFACTOR: shared page helpers.
- Done when: `npx playwright test` passes.

### T-017 Design tokens, dark theme and visual states from DESIGN.md
- Covers: FR-025, FR-022, FR-030
- RED: (1) `tests/design/tokens.test.ts` parses the YAML front matter of `docs/reverse-engineering/demo-target-dual/DESIGN.md` and fails unless `src/ui/tokens.css` defines a variable for every color, rounded, spacing and typography token with the same value; (2) `e2e/visual.spec.ts` (Playwright + axe-core) fails unless notes, editor, confirm and settings have zero color-contrast violations in light and dark theme, the search field's computed background is dark when dark theme is on (DEF-07), the toast's border/background differs from the dark page background (DEF-08), and the current navigation button differs visually from the other one (DEF-09).
- GREEN: write `tokens.css`; dark theme block reassigns only the `-dark` tokens and sets color scheme dark; toast uses `surface-dark` + `outline` border in dark theme; current nav item gets the `primary` text colour and underline.
- REFACTOR: collapse the three button variants into one base rule plus modifiers.
- Done when: both tests pass in both themes.
