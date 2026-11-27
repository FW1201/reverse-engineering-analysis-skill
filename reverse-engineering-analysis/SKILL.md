---
name: reverse-engineering-analysis
description: Use when asked to click through, explore, test or "reverse engineer" an existing web app or desktop software through computer use / browser automation (optionally together with its source code) and turn what it does into a spec, SDD, TDD plan, DESIGN.md design system or rebuild plan for another agent to implement. Triggers include 逆向分析, 逆向工程, 拆解這個平台, 照這個軟體做一個, 分析功能後產出 SDD/TDD, 復刻介面設計, 截圖建立 design.md, clone this app's features, write a spec from this app. Works in Claude Code and Codex.
---

# Reverse Engineering Analysis → SDD/TDD Plan

## Overview

Black-box behavioral analysis: drive the target **through its UI like a user**, log every observation with evidence, then write a spec-driven (SDD) spec and a test-first (TDD) plan in which every requirement traces to an observation and every requirement is covered by a test task. The result is a hand-off folder a build agent can implement from without ever seeing the original.

**Core principle:** the spec describes *what the software does for a user*, proven by observations, in your own words. It never describes *how the original is coded*.

## The four rules

1. **The UI decides the spec; source code only raises hypotheses.** Every requirement is a behavior a user can see, proven by an OBS. How far you may read code depends on the **source mode**, fixed in `00-scope.md` before you start:

   | Source mode | When | Code track |
   |---|---|---|
   | `ui-only` (default) | third-party / proprietary software, or no confirmed right to read its code | OFF: no view-source, no `curl` of HTML/JS bundles, no decompiling. Allowed: network traffic, storage keys/shapes, console, accessibility labels, OS-visible metadata |
   | `authorized-source` | the user owns the code or confirms in chat they may read it (own repo, client project) | ON, after the UI pass |
   | `open-source` | public repo with a license | ON, after the UI pass; record the license in `00-scope.md`; copy no code |

   Never pick a mode above `ui-only` on your own judgment that code "looks public": served JS of a commercial site is still `ui-only`. With the code track on, every finding becomes a `CODE-nnn` hypothesis in `mechanism-notes.md` and must be **verified through the UI** (cite the OBS) before an FR relies on it as observed; what the UI cannot show (audio, timers, unload handlers, file formats) is tagged `[CODE-ONLY]`. Ids, class names, function names and code never enter `02-spec.md` in any mode.
2. **Interact with real input events.** Use the click/type/key tools. Do not script the page (`element.click()`, setting `.value`, dispatching events) — that skips focus, keyboard, default-button and validation behavior, which is exactly what you are there to observe. `evaluate_script`/`javascript_tool` is for **reading** only what a user could see or the browser exposes: storage, URL/title, rendered layout (overflow, scroll width) and computed style values for DESIGN.md — never markup, ids, class names or code. The devtools `fill` tool counts as real input; if a field ignores it, click the field and use `type_text`.
3. **Exercise the happy paths on isolated test data.** Create, edit and save for real in a sandbox (fresh browser profile, local fixture, test account). Skipping a create/edit flow because "it leaves records behind" leaves the most important requirements unobserved. Destructive or outward actions on non-isolated data (delete real data, reset all, send, publish, pay, invite, change account/security) → ask the user in chat first; if not approved, mark the requirement `[UNKNOWN]`.
4. **Defects are reported, not specified.** A bug you find (XSS, data loss, Enter cancels the form) goes into `02-spec.md` → `## Observed defects` with the corrected behavior as the requirement. Never write "reproduce for parity". Security defects are always fixed in the spec.

| Rationalization | Reality |
|---|---|
| "The source is right there, reading it is faster and exact" | In `ui-only` mode it is off-limits. In code modes it is a hypothesis generator: a spec written from code becomes a copy of their implementation (ids, CSS, quirks). UI pass first, then code, then verify. |
| "The code says max 40 chars, no need to test it" | Code can be dead, overridden or behind a flag. Type 41 chars and log the OBS — or tag `[CODE-ONLY]`. |
| "Scripting the clicks is more reliable" | It bypasses the behavior you are documenting. Use real input; slow is fine. |
| "I'll infer save/edit from what I saw elsewhere" | Inferred core flows are the #1 source of wrong specs. Do them on test data. |
| "Keeping bugs keeps the rebuild faithful" | Nobody wants their XSS cloned. Fix in spec, note in defects. |
| "User is in a hurry, one big doc is enough" | The validator gate takes seconds; untraceable specs cost the build agent hours. |
| "I'll copy the seed data / texts / logo as fixtures" | Write your own neutral fixtures. Short UI labels needed in tests are fine. |

## Workflow

1. **Scope.** Ask only what you cannot decide, in one message: which target, the **source mode** (do they own or license the code? where is it?), isolation available (test account? local copy?), where in the project folder the rebuild will live, and permission to save files the app exports/downloads into `evidence/` (exports are features too; without permission mark them `[UNKNOWN]`). Default output root: `<project>/docs/reverse-engineering/<slug>/`. Test data the app gives no way to remove: note it under "Leftovers" in `00-scope.md`.
2. **Init the workspace** (both runtimes run this from the skill directory):
   `python3 scripts/init_workspace.py <project_dir> <slug> --target "<url|app>" --kind web|native --source-mode ui-only|authorized-source|open-source [--source "<repo path or URL>"]`
   Fill `00-scope.md` (version, isolation, action policy) before touching the app.
3. **Pick tools** from [references/tool-adapters.md](references/tool-adapters.md) — chrome-devtools MCP works in both Claude Code and Codex for web; `mcp__computer-use__*` (Claude Code) or `cua_repl` (Codex) for native apps.
4. **Explore breadth-first, then depth.** Map every screen/menu first (SCR), then each flow (FLW) with: empty, invalid, boundary, valid, cancel, reload-persistence. Use the coverage checklist in `01-inventory.md`. For web, capture network + storage after each state-changing action.
5. **Log every action** as you go — one line per action, never assign ids yourself. With `--shot` the script prints `OBS-nnn evidence/screens/OBS-nnn.png`; save the screenshot to exactly that path right after. Without `--shot` the line has no screenshot (storage reads, native `confirm()` dialogs — quote the dialog text in `--result`).
   `python3 scripts/log_observation.py <ws> --shot --screen SCR-02 --action click --target "儲存" --result "error '標題不可空白' shown, dialog stays open" --risk safe`
6. **Code track** (only `authorized-source` / `open-source`, only after steps 4–5 cover every screen). Read the code with targeted questions the UI pass left open: Open questions, `[INFERRED]` items, validation limits, storage/persistence, timers, error paths, export formats, permission checks. For each finding add a `### CODE-nnn` block to `mechanism-notes.md` (location, finding in plain words, `Verify:` the UI action that would show it). Then go back to the UI, do that action, log the OBS and fill `Verified by: OBS-nnn` (an OBS from the UI pass that already shows it counts) — or `[CODE-ONLY]` with the reason it cannot be shown, or `Contradicted by: OBS-nnn` when the UI disagrees (the UI wins; the gap goes to Observed defects or Open questions).
7. **Design system** — build `DESIGN.md` from the screenshots and measured styles, following [references/design-extraction.md](references/design-extraction.md): web → emulate a desktop viewport, then `scripts/design_tally.js` (read-only) per main screen and per component state, saved to `evidence/design/`; native → `python3 scripts/sample_colors.py <png>` for palette, point colors and contrast. Fidelity follows the source mode: `ui-only` → `neutral` (keep spacing/type scale/radius/layout/component anatomy; replace brand hues, fonts, logos, imagery with original equivalents of the same role); code modes → `exact`. Every component in `01-inventory.md` gets an entry with its states.
8. **Write the documents** in order (templates already in the workspace):
   - `01-inventory.md` — SCR / FLW / ENT / API / RUL tables, each row citing OBS ids.
   - `02-spec.md` — one `### FR-nnn` block per behavior: source OBS ids (or `[INFERRED]` deduced / `[UNKNOWN]` untested / `[DEFECT-FIX]` new behavior that fixes a DEF row / `[CODE-ONLY]` known from a CODE-nnn the UI cannot show; FRs may also cite CODE ids), Given/When/Then acceptance criteria phrased in user-visible terms; then NFRs, `## Observed defects`, `## Open questions`.
   - `03-design.md` — an original architecture for the rebuild (stack chosen for the project folder, not copied from the target).
   - `04-tdd-plan.md` — ordered `### T-nnn` tasks, each with `Covers: FR-…`, `RED:` (exact failing test), `GREEN:` (minimal code), `REFACTOR:`, `Done when:`.
   - `AGENT-HANDOFF.md` — build location and rules for the implementing agent.
   - `DESIGN.md` — finished in step 7; `03-design.md` references its tokens instead of repeating values.
9. **Gate:** `python3 scripts/validate_artifacts.py <ws> --write-matrix` must print `READY FOR HANDOFF`. Fix every ERROR; explore more if it warns that >30% of FRs are inferred.
10. **Report** to the user: workspace path, source mode, counts (OBS / FR / T / CODE verified vs code-only), DESIGN.md fidelity, defects found, open questions, anything skipped for safety, and the one-line prompt to start the build agent:
   `Read docs/reverse-engineering/<slug>/AGENT-HANDOFF.md and implement the app task by task.`

## Writing good requirements

| Weak (implementation-coupled) | Strong (behavioral, testable) |
|---|---|
| `#f-err` shows text when `#f-save` clicked | Given the editor is open with an empty title, When the user presses Save, Then an inline error "標題不可空白" appears and the dialog stays open |
| Store in `localStorage['pocketnote.v1']` | Notes and settings survive a page reload (storage mechanism is a design choice; original used browser local storage — OBS-031) |
| Sorted by `b.updatedAt.localeCompare(a.updatedAt)` | Pinned notes appear first; within each group the most recently edited note is on top |

Storage keys, API paths and payload shapes observed on the network belong in `01-inventory.md` (API/ENT) as evidence; the spec states the behavior they support.

## Common mistakes

- One giant markdown file → the validator cannot trace anything; use the workspace files.
- Screenshots kept only in chat → save files under `evidence/`; a build agent cannot see your context.
- Acceptance criteria that test internals (`state.notes.length === 4`) → test what a user sees.
- Forgetting reload/restart persistence and empty/error states → they are requirements too.
- Writing outputs outside the project folder → everything goes under `<project>/docs/reverse-engineering/<slug>/`.
