# 02 Specification (SDD) — demo-target-dual

Spec-driven: this file is the source of truth for the build agent. One block per requirement.
Status tags: cited OBS ids = observed; `[INFERRED]` = deduced, not directly seen; `[UNKNOWN]` = could not test; `[DEFECT-FIX]` = corrected behavior for a DEF row; `[CODE-ONLY]` = known from a CODE-nnn the UI cannot show.

UI language is Traditional Chinese (Taiwan). Short UI labels quoted below are the test-visible strings; the rebuild must use its own app name (not the original's).

## Product summary
A single-user, browser-only note keeper. Users write short notes with a title, free-text body and up to five tags, pin important ones, find them by live search and tag filter, and choose between "most recently updated" and "title" ordering. Everything is kept in the browser and survives reloads; a reset brings back a small set of sample notes. A settings screen offers a dark theme, the sort order and the reset.

## Functional requirements

### FR-001 Note list shows each note as a card
- Source: FLW-01, OBS-001, OBS-019, OBS-032
- Description: The notes screen lists every note as a card with its title, body, tag chips and the last-updated date-time in Taiwan locale format, plus three actions: pin toggle, 編輯, 刪除. A note without body/tags shows only title and the date line.
- Acceptance criteria:
  - Given a note titled 牛奶 with body 低脂 2 瓶, tag home, updated 2026-11-21 18:30 (UTC+8)
  - When the notes screen is shown
  - Then a card shows 牛奶, 低脂 2 瓶, a chip home and a date line containing 2026/11/21, and has buttons labelled 釘選 (pin), 編輯 and 刪除

### FR-002 Sample notes on first run only
- Source: FLW-01, OBS-003, OBS-004, OBS-042, CODE-006
- Description: When the app has never stored data, it loads three sample notes (one pinned) and saves them. Once any data has been stored — even an empty list — reloading never brings the samples back (only reset does, FR-027).
- Acceptance criteria:
  - Given a browser with no stored data for the app
  - When the app opens
  - Then three sample notes are listed and stored
  - Given the user deleted every note
  - When the page is reloaded
  - Then the list is still empty

### FR-003 Default order: pinned first, then most recently updated
- Source: RUL-01, OBS-001
- Description: With sort 最近更新 (default) pinned notes come first; inside each group the most recently updated note is on top.
- Acceptance criteria:
  - Given a pinned note updated 11/20 and unpinned notes updated 11/22 and 11/21
  - When the list is shown with the default sort
  - Then the order is the pinned note, then the 11/22 note, then the 11/21 note

### FR-004 Title sort with Traditional Chinese collation
- Source: RUL-02, OBS-008, OBS-026, OBS-027, CODE-008
- Description: With sort 標題 A→Z the pinned-first rule still applies; inside each group notes are ordered by title using Traditional Chinese locale collation (Han titles by stroke order; in the original, Latin titles followed Han titles).
- Acceptance criteria:
  - Given unpinned notes 讀書會, 牛奶 and 測試筆記 and sort set to 標題 A→Z
  - When the list is shown
  - Then the order is 牛奶, 測試筆記, 讀書會, and any pinned note is listed above them

### FR-005 Live search over title and body
- Source: FLW-02, OBS-010, OBS-047, CODE-007, DEF-04
- Description: Typing in the search box (placeholder 搜尋標題或內容) filters the list on every keystroke. The query is trimmed and matched case-insensitively as a substring of the title or of the body — separately; text spanning the end of the title and the start of the body must not match (fix of DEF-04).
- Acceptance criteria:
  - Given a note whose body contains "Q1"
  - When the user types q1
  - Then only that note is listed
  - Given a note titled 乙 with body 丙
  - When the user searches 乙丙
  - Then the note is not listed

### FR-006 Tag filter
- Source: FLW-02, OBS-013, OBS-014, OBS-031
- Description: The tag filter offers 全部標籤 plus every tag currently used by any note, alphabetically, each once. Choosing a tag shows only notes carrying it; it combines with search (both must match). Tags no longer used disappear from the options.
- Acceptance criteria:
  - Given notes tagged work, study+work and home
  - When the user picks work and types 構式
  - Then only the note tagged study+work whose body contains 構式 is listed
  - Given the only note tagged test is deleted
  - When the filter is opened
  - Then test is no longer an option

### FR-007 Empty and no-match states
- Source: RUL-07, OBS-011, OBS-041
- Description: With no notes at all the list area shows 還沒有筆記，按「新增筆記」開始. When notes exist but search/filter exclude all, it shows 找不到符合的筆記. The 新增 button stays available in both.
- Acceptance criteria:
  - Given there are no notes
  - When the notes screen is shown
  - Then the text 還沒有筆記，按「新增筆記」開始 is shown
  - Given notes exist
  - When the search matches none
  - Then the text 找不到符合的筆記 is shown

### FR-008 Search and filter are not remembered
- Source: OBS-012
- Description: After a reload the search box is empty and the filter is 全部標籤.
- Acceptance criteria:
  - Given the user typed a query that hides some notes
  - When the page is reloaded
  - Then the search box is empty and all notes are listed

### FR-009 New-note dialog
- Source: FLW-03, OBS-015
- Description: 「＋ 新增筆記」 opens a modal dialog titled 新增筆記 with empty fields 標題（必填，最多 40 字）, 內容 (multi-line) and 標籤（逗號分隔）, and buttons 取消 and 儲存. Focus starts in the title field.
- Acceptance criteria:
  - Given the notes screen
  - When the user presses 新增筆記
  - Then a modal dialog titled 新增筆記 opens with three empty fields and keyboard focus in the title field

### FR-010 Title is required
- Source: RUL-03, OBS-016, OBS-017
- Description: Saving with an empty or whitespace-only title shows the inline error 標題不可空白 and keeps the dialog open; nothing is saved.
- Acceptance criteria:
  - Given the editor with a title of three spaces
  - When the user presses 儲存
  - Then the error 標題不可空白 is shown, the dialog stays open and no note is added

### FR-011 Title limited to 40 characters
- Source: RUL-03, OBS-018
- Description: The title field accepts at most 40 characters; further typing is ignored. Leading/trailing spaces are removed on save.
- Acceptance criteria:
  - Given an empty title field
  - When the user types 41 characters
  - Then the field contains only the first 40

### FR-012 Titles must be unique
- Source: RUL-04, OBS-045, OBS-048, CODE-001
- Description: Saving a title (after trimming) identical to another note's title shows 已有相同標題的筆記 and keeps the dialog open. Saving a note with its own unchanged title is allowed.
- Acceptance criteria:
  - Given a note titled 甲 exists
  - When the user creates a note titled " 甲 " and presses 儲存
  - Then the error 已有相同標題的筆記 is shown and nothing is saved
  - Given the user edits 甲 without changes
  - When the user presses 儲存
  - Then the note is saved without error

### FR-013 Tag input normalization
- Source: RUL-05, OBS-019, OBS-043, CODE-002
- Description: The tag field is split on ASCII or full-width commas; each part is trimmed and lowercased; empty parts are dropped; duplicates removed; at most five tags are kept (the first five unique ones). When the edit dialog opens, tags are shown joined by ", ".
- Acceptance criteria:
  - Given the tag field contains "a，b, A, c, d, e, f"
  - When the note is saved
  - Then its tags are exactly a, b, c, d, e
  - Given the tag field contains " Test , work ,, "
  - When the note is saved
  - Then its tags are test and work

### FR-014 Creating a note
- Source: FLW-03, OBS-019, OBS-020
- Description: A valid save closes the dialog, adds an unpinned note stamped with the current time, shows the confirmation 已新增 and places the note according to the current sort.
- Acceptance criteria:
  - Given a valid title in the new-note dialog
  - When the user presses 儲存
  - Then the dialog closes, 已新增 is announced, and a new unpinned card with that title and the current date-time appears

### FR-015 Editing a note
- Source: FLW-04, OBS-021, OBS-026, OBS-048
- Description: 編輯 opens the same dialog titled 編輯筆記 prefilled with the note. Saving updates title/body/tags, sets the timestamp to now, re-sorts the list and announces 已更新.
- Acceptance criteria:
  - Given a note titled ABC
  - When the user opens 編輯, changes the title to 測試筆記 and presses 儲存
  - Then the card shows 測試筆記 with the current date-time and 已更新 is announced

### FR-016 Cancel and Escape discard changes
- Source: FLW-04, OBS-022, OBS-023
- Description: 取消 or the Escape key closes the editor without saving.
- Acceptance criteria:
  - Given the edit dialog with a modified title
  - When the user presses 取消 (or Escape)
  - Then the dialog closes and the note is unchanged

### FR-017 Enter in a single-line field saves
- Source: [DEFECT-FIX] DEF-01, OBS-024, OBS-025, CODE-005
- Description: Pressing Enter in the title or tag field behaves like 儲存 (including validation). Enter in the multi-line body inserts a new line.
- Acceptance criteria:
  - Given the edit dialog with the title changed to 測試筆記
  - When the user presses Enter in the title field
  - Then the note is saved with title 測試筆記 and 已更新 is announced
  - Given the editor with an empty title
  - When the user presses Enter in the title field
  - Then the error 標題不可空白 is shown and the dialog stays open

### FR-018 Validation message lifecycle
- Source: OBS-018, OBS-021, CODE-013
- Description: The inline error is cleared whenever the dialog is opened. (Original keeps an error visible while the user corrects the field — see Open questions.)
- Acceptance criteria:
  - Given a previous save attempt showed 標題不可空白
  - When the dialog is closed and opened again
  - Then no error text is shown

### FR-019 Pin and unpin
- Source: FLW-05, OBS-027, OBS-028, CODE-014
- Description: The pin button toggles the note's pinned state. Pinned notes show a filled pin labelled 取消釘選; unpinned show a pin labelled 釘選. Pinning moves the note into the pinned group immediately and does not change its timestamp. The state persists.
- Acceptance criteria:
  - Given an unpinned note
  - When the user presses its 釘選 button
  - Then the note moves to the top group, its button is labelled 取消釘選, and its date line is unchanged

### FR-020 Delete with in-app confirmation
- Source: FLW-06, OBS-029, OBS-030, OBS-031
- Description: 刪除 opens an in-app modal 確定刪除「title」？此動作無法復原。 with 取消 (focused by default) and 確定刪除. Cancel keeps the note; confirming removes it and announces 已刪除.
- Acceptance criteria:
  - Given a note titled 測試筆記
  - When the user presses 刪除
  - Then a modal asks 確定刪除「測試筆記」？此動作無法復原。 with focus on 取消
  - When the user presses 確定刪除
  - Then the note disappears and 已刪除 is announced

### FR-021 User text is always shown as plain text
- Source: [DEFECT-FIX] DEF-02, OBS-019, OBS-032, OBS-046, CODE-004
- Description: Titles, bodies and tags containing markup characters are displayed literally everywhere — cards, tag chips and the tag filter options. No user text may ever be interpreted as markup.
- Acceptance criteria:
  - Given a note with title containing angle-bracket markup and a tag containing option markup
  - When the list and the tag filter are shown
  - Then the card shows the text literally and the tag filter contains exactly one option whose label is the literal tag text (no extra or blank options)

### FR-022 Confirmation messages
- Source: RUL-08, OBS-019, OBS-044, CODE-003
- Description: 已新增, 已更新 and 已刪除 are shown in a polite status region (screen readers announce them) and disappear after about two seconds.
- Acceptance criteria:
  - Given the user just saved a new note
  - When 3 seconds pass
  - Then the 已新增 message is no longer visible

### FR-023 Two views with URL fragment
- Source: FLW-09, OBS-005, OBS-035, OBS-036
- Description: Header buttons 筆記 and 設定 switch between the notes and settings views and set the URL fragment to notes / settings. Opening the app with the settings fragment shows settings; any other or unknown fragment shows notes and replaces the fragment with notes.
- Acceptance criteria:
  - Given the app is opened at the settings fragment
  - When the page loads
  - Then the settings view is shown
  - Given the app is opened with an unknown fragment
  - When the page loads
  - Then the notes view is shown and the fragment becomes notes

### FR-024 View follows browser history
- Source: [DEFECT-FIX] DEF-03, OBS-037, CODE-012
- Description: Browser Back/Forward and manual fragment edits switch the view to match the URL.
- Acceptance criteria:
  - Given the user went from 設定 to 筆記
  - When the user presses the browser Back button
  - Then the settings view is shown and the URL fragment is settings

### FR-025 Dark mode
- Source: FLW-07, OBS-006, OBS-009
- Description: The 深色模式 checkbox switches the whole app (including dialogs) to a dark theme immediately; the choice survives reloads.
- Acceptance criteria:
  - Given dark mode is off
  - When the user ticks 深色模式 and reloads
  - Then the app is dark and the checkbox is ticked

### FR-026 Sort setting
- Source: FLW-07, OBS-007, OBS-008, OBS-009
- Description: The 排序 select offers 最近更新 (default) and 標題 A→Z; the choice applies to the list and survives reloads.
- Acceptance criteria:
  - Given sort is 最近更新
  - When the user picks 標題 A→Z and reloads
  - Then the list is title-ordered and the select shows 標題 A→Z

### FR-027 Reset all data
- Source: FLW-08, OBS-038, OBS-039, OBS-040, CODE-006
- Description: 清除所有資料 asks for confirmation 清除所有資料並還原範例？. Declining changes nothing; accepting deletes all notes and settings and restores the sample notes with default settings (light theme, 最近更新).
- Acceptance criteria:
  - Given 4 notes and dark mode on
  - When the user presses 清除所有資料 and declines
  - Then the 4 notes remain
  - When the user presses it again and accepts
  - Then exactly the 3 sample notes are listed, dark mode is off and sort is 最近更新

### FR-028 Persistence
- Source: OBS-004, OBS-009, OBS-020, OBS-042
- Description: Every create, edit, pin, delete and settings change is saved immediately in the browser and is present after reload. No server is required beyond serving the app and the sample data.
- Acceptance criteria:
  - Given the user created, pinned and edited notes
  - When the page is reloaded
  - Then the list shows the same notes in the same states

### FR-029 Recent-first order uses real time
- Source: [DEFECT-FIX] DEF-05, OBS-001, CODE-009
- Description: The 最近更新 order compares actual moments in time, regardless of the time zone the timestamp was recorded in.
- Acceptance criteria:
  - Given a sample note updated 2026-11-22 20:15 at UTC+8 and a note saved at 2026-11-22 15:00 UTC
  - When the list is sorted by 最近更新
  - Then the note saved at 15:00 UTC (later in real time) is listed first

### FR-030 Current view exposed to assistive technology
- Source: [CODE-ONLY] CODE-010
- Description: The header button of the visible view is marked as the current page for screen readers; the other is not.
- Acceptance criteria:
  - Given the settings view is shown
  - When the accessibility tree is inspected
  - Then 設定 is marked current and 筆記 is not

### FR-031 Graceful load failure
- Source: [CODE-ONLY] CODE-011
- Description: If the sample data cannot be loaded on first run, or the stored data cannot be read, the app still renders the notes view with the empty state instead of a blank area. (The original has no handling; corrected here.)
- Acceptance criteria:
  - Given the sample data request fails on first run
  - When the app opens
  - Then the notes view shows 還沒有筆記，按「新增筆記」開始 and 新增筆記 works

## Non-functional requirements
- Persistence: browser-local only; survives reload (OBS-004, OBS-009). Storage mechanism is a design choice; the original used browser local storage under one key (API-02).
- Responsive: usable in a single column at 500 px wide with no horizontal scrolling (OBS-033); target 360 px too.
- Locale: zh-Hant UI, dates in zh-TW locale format with AM/PM prefix (上午/下午) (OBS-001).
- Visual: apply DESIGN.md tokens (fidelity exact) in both themes; text contrast ≥ 4.5:1 in both themes (OBS-058).
- Accessibility: search and tag filter have accessible names 搜尋 / 標籤篩選; pin buttons have names 釘選 / 取消釘選; dialogs are modal with focus moved inside; status messages are polite live announcements (OBS-015, OBS-019, OBS-029).
- Reliability: no console errors during normal use (OBS-034).

## Observed defects
| ID | Defect seen in the original | Evidence | Required behavior in rebuild (FR) |
|---|---|---|---|
| DEF-01 | Pressing Enter in the editor closes it and discards the changes | OBS-024, OBS-025, CODE-005 | FR-017 |
| DEF-02 | Tag text is injected as markup into the tag filter (security: HTML/script injection) | OBS-046, CODE-004 | FR-021 |
| DEF-03 | Browser Back/Forward or manual fragment change updates the URL but not the view | OBS-037, CODE-012 | FR-024 |
| DEF-04 | Search matches text spanning title end and body start | OBS-047, CODE-007 | FR-005 |
| DEF-05 | Recent-first order compares timestamps textually across time zones (code-only) | CODE-009 | FR-029 |
| DEF-06 | Failed sample load or unreadable stored data leaves the list blank (code-only) | CODE-011 | FR-031 |
| DEF-07 | Dark theme leaves native search/select/checkbox white and keeps light borders | OBS-054, OBS-055 | FR-025; DESIGN.md → Do's (theme native controls) |
| DEF-08 | Status message box has no visible edge in dark theme (same #111 as the page, 1:1) | OBS-056, OBS-058 | FR-022; DESIGN.md → Components (toast) |
| DEF-09 | The current navigation item is not visually distinguished (only announced to assistive tech) | OBS-050 | FR-030; DESIGN.md → Components (header navigation) |

## Open questions
- Tags beyond five are dropped silently (OBS-043). Rebuild keeps the 5-tag limit (FR-013); whether to warn the user is a product decision — default: no message, matching the original.
- Saving an unchanged note bumps its timestamp and moves it to the top (OBS-048). Kept as-is (FR-015); confirm with the product owner.
- The inline error stays visible while the user fixes the field (OBS-018). Rebuild may clear it on input; not required.
- Ordering of Latin vs Han titles under title sort depends on the platform's Traditional Chinese collation (OBS-019); tests should assert only Han-to-Han order (FR-004).
- Whether the app warns before leaving with an unsaved dialog: [UNKNOWN] — not tested (reload auto-accepts leave prompts); the source shows no such warning.
- Body text is stored untrimmed (source); no visible effect observed.
