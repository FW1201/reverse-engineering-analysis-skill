# 03 Design — demo-target-dual

Proposed architecture for the rebuild. Behavior must match 02-spec.md; implementation is free.

## Stack decision
- Vite + TypeScript, no UI framework (the app is two small views; the project folder has no existing app stack).
- Unit/component tests: Vitest + jsdom + @testing-library/dom + @testing-library/user-event (real keyboard/click semantics, needed for Enter/Escape behavior).
- E2E: Playwright against `vite preview`, one spec per flow.
- Styling: one `src/ui/tokens.css` holding every DESIGN.md token as a CSS variable named after it (`--color-primary` = `colors.primary`, `--rounded-md` = `rounded.md`, `--space-lg` = `spacing.lg`, …); fidelity is `exact`, so values are the measured ones. Dark theme = a `[data-theme=dark]` block that only reassigns the `-dark` color tokens and sets the page color scheme to dark. Components never hard-code colors or sizes.
- Rendering: build DOM nodes with text content only (never assemble markup from user strings) — this is how FR-021 is guaranteed.

## Module map
| Module | Responsibility | Implements FR |
|---|---|---|
| src/domain/note.ts | Note/Settings types, title validation (trim, required, max 40, unique), tag parsing | FR-010, FR-011, FR-012, FR-013 |
| src/domain/query.ts | search (title or body separately), tag filter, sorting (pinned first; recent by real time; title with zh-Hant collation), tag option list | FR-003, FR-004, FR-005, FR-006, FR-029 |
| src/store/repository.ts | load/save document, first-run sample fetch, reset, tolerant of fetch/parse errors | FR-002, FR-027, FR-028, FR-031 |
| src/store/state.ts | in-memory app state, mutations (create/update/togglePin/delete/settings) that persist after each change | FR-014, FR-015, FR-019, FR-020, FR-025, FR-026 |
| src/ui/router.ts | fragment ↔ view, listens to history changes, unknown → notes, current-page marking | FR-023, FR-024, FR-030 |
| src/ui/notesView.ts | toolbar, list cards, empty states | FR-001, FR-006, FR-007, FR-008 |
| src/ui/editorDialog.ts | modal create/edit form, validation display, Enter = save, Escape/取消 = discard | FR-009, FR-015, FR-016, FR-017, FR-018 |
| src/ui/confirmDialog.ts | in-app delete confirmation, focus on 取消 | FR-020 |
| src/ui/settingsView.ts | dark mode, sort, reset (browser confirm) | FR-025, FR-026, FR-027 |
| src/ui/toast.ts | polite status message, auto-hide 2 s | FR-022 |
| public/sample-notes.json | neutral sample data written for the rebuild (3 notes, one pinned) | FR-002 |

## Visual system (DESIGN.md)
| UI module | DESIGN.md components / tokens it uses |
|---|---|
| src/ui/notesView.ts | Header navigation buttons, search field / tag select, `button-primary`, `note-card`, `tag-chip`, meta line, empty message |
| src/ui/editorDialog.ts | `dialog`, `scrim`, `h3-dialog`, inline error (`error`, `body-sm`), `button-neutral`, `button-primary` |
| src/ui/confirmDialog.ts | `dialog`, `button-neutral`, `button-danger` |
| src/ui/settingsView.ts | `h2`, native checkbox / select, `button-danger`, dark-theme tokens |
| src/ui/toast.ts | `toast` (with a visible edge in dark theme) |
| src/ui/router.ts | current-page marker shown visually (DESIGN.md → Do's) |
Token coverage and the dark-theme fixes (DEF-07, DEF-08, DEF-09) are tested in T-017.

## Data model
- Note: id (string, unique; e.g. random UUID), title (1–40 chars, trimmed, unique), body (string), tags (string[] ≤ 5, lowercase, unique, non-empty), pinned (boolean), updatedAt (ISO-8601 string; always compared via parsed epoch milliseconds).
- Settings: dark (boolean, default false), sort ('updated' | 'title', default 'updated').
- Document: { version: 1, notes: Note[], settings: Settings }.

## Interfaces
- Storage: one JSON document in localStorage under a rebuild-specific key (e.g. `notes-app.v1`). Missing key ⇒ first run. Unparseable ⇒ treat as empty, keep app usable (FR-031).
- Sample data: GET `sample-notes.json` relative to the app base, only on first run and after reset; on failure start with an empty list.
- Routes: `#notes` (default), `#settings`; `hashchange`/`popstate` re-render.

## State & navigation
- Single state object; every mutation → save → re-render. Search query and tag filter live only in memory (FR-008).
- Sort comparator: pinned desc, then (sort === 'title' ? Intl.Collator('zh-Hant') on title : Date.parse(updatedAt) desc).
- Editor uses a `<dialog>` with a `<form>` whose submit (Enter or 儲存) runs validation; the cancel button is type="button" so it is never the default.

## Test strategy
- Unit: pure rules (validation, sorting, filtering)
- Integration/component: UI flows per FLW-xx
- E2E: one test per happy-path flow, driven through the same UI the analysis used
