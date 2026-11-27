# Reverse Engineering Analysis (REA) Skill

Drive a web or desktop app through computer use, log every observation with evidence, and produce an **SDD spec, a TDD plan and a DESIGN.md design system** that a build agent can implement without ever seeing the original. Works in **Claude Code** and **Codex**.

## Two tracks: UI leads, code assists

| | UI track (computer use) | Code track |
|---|---|---|
| Answers | what it does; what users see | why; hidden rules and edge cases |
| Output | observations (OBS) → requirements (FR) | findings (CODE) → hypotheses |
| Allowed when | always | only `authorized-source` / `open-source` |
| Feeds the spec? | yes | only after UI verification, or tagged `[CODE-ONLY]` |

Source mode is fixed in `00-scope.md` before analysis starts:
- `ui-only` (default) — third-party/proprietary software. No source, no bundles, no decompiling.
- `authorized-source` — you own the code or are authorized to read it.
- `open-source` — public repo; the license is recorded and no code is copied.

## Outputs (`docs/reverse-engineering/<slug>/`)
| File | Contents |
|---|---|
| `00-scope.md` | Target, source mode, isolation, action policy |
| `observations.jsonl` + `evidence/` | Log of every action (OBS) + screenshots / network / design measurements |
| `01-inventory.md` | Screens SCR, components CMP, flows FLW, entities ENT, APIs, rules RUL |
| `02-spec.md` | SDD: FR + Given/When/Then, observed defects (fixed in the spec), open questions |
| `mechanism-notes.md` | Code-track findings (code modes only) |
| `DESIGN.md` | Google design.md alpha format: tokens + components + states; third-party = neutral (no brand copying), own system = exact |
| `03-design.md` | Architecture for the rebuild |
| `04-tdd-plan.md` | RED → GREEN → REFACTOR tasks |
| `05-traceability.md` | FR → OBS → T matrix (generated) |
| `AGENT-HANDOFF.md` | Entry point for the build agent |

## Install

```bash
git clone https://github.com/FW1201/reverse-engineering-analysis-skill.git
```
```bash
cd reverse-engineering-analysis-skill && bash install.sh
```

The installer first checks your environment and walks you through any missing setup. It installs only after every required check passes.

| Check | Level | If missing |
|---|---|---|
| Python 3.9+ | required | prints the install command |
| Claude Code or Codex | required (at least one) | prints the install link |
| Node 20.19+, Chrome | needed for web targets | prints the install command |
| chrome-devtools MCP (each runtime) | needed for web targets | prints `claude mcp add …` / `codex mcp add …` and offers to run it |
| Claude desktop app / Codex Computer Use | needed for native app targets | explains how to enable it |
| Skill script self-test | required | stops the install |

Options: `--check` checks only and changes nothing · `--mode copy` copies instead of linking · `--yes` takes the defaults without prompting · `--uninstall` removes the skill.
Install locations: `~/.agents/skills` (if present, else `~/.codex/skills` or `~/.claude/skills`); other runtimes get a symlink, so the skill is never installed twice.

## Usage
1. Ask: "Use reverse-engineering-analysis on https://… and write the SDD/TDD plan." (If it's your own code, add the source location.)
2. Check that the validator prints `READY FOR HANDOFF`.
3. Start the build agent: `Read docs/reverse-engineering/<slug>/AGENT-HANDOFF.md and implement the app task by task.`

## Layout
| Path | What |
|---|---|
| `reverse-engineering-analysis/` | The skill (SKILL.md, scripts/, templates/, references/) |
| `install.sh` | Environment check + guided setup + install |
| `docs/reverse-engineering/<slug>/` | Analysis output for each target |
| `fixtures/demo-target/` + `tests/` | Local demo app and answer key for regression tests |

## Regression test
```bash
cd fixtures/demo-target && python3 -m http.server 8765 --bind 127.0.0.1
```
Run the skill against `http://127.0.0.1:8765/` (UI-only, or authorized-source with the source in `fixtures/demo-target/`), then compare its output with `tests/demo-target-ground-truth.md`.

## Test record
| Run | Result |
|---|---|
| Baseline, no skill | Read the source with curl, spec copied DOM ids/CSS, clicks scripted with JS, planned to reproduce XSS, skipped create/edit, one monolithic doc |
| UI-only (third-party web app) | Real input only; 43 OBS / 26 FR / 19 T; 11 defects turned into corrected requirements |
| Dual track (demo app, authorized-source) | All 9 answer-key behaviors found; the code track added duplicate-title check, silent 5-tag cap, full-width-comma splitting and the timestamp sort bug |
| DESIGN.md (neutral + exact) | Neutral kept structure, swapped the brand palette and fixed two contrast failures; exact recorded tokens as-is; 5 visual defects found |
