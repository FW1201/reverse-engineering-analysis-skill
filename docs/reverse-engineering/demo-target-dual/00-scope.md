# 00 Scope & rules of engagement — demo-target-dual

- Target: http://127.0.0.1:8765/  (kind: web)
- Version / build observed: no version string in the UI, page title or response headers; single-page note app served locally, observed 2026-11-27
- Source mode: authorized-source   (ui-only | authorized-source | open-source)
- Source location: fixtures/demo-target/
- Authorization / license: owner (user) in chat
- Analysis date: 2026-11-27
- Analyst runtime: Claude Code (Opus) + chrome-devtools MCP (isolated browser context `rea-demo-dual`), python3 skill scripts

## Purpose
Black-box behavioral analysis so a build agent can implement an original app with equivalent features.
We describe *behavior*, never copy code, assets, brand names, logos, copy text verbatim beyond short UI labels needed for tests.

## Environment
- Account used: none (app has no accounts); local fixture served on 127.0.0.1
- Data isolation: fresh isolated browser context; all data is browser-local test data. The user approved destructive actions inside this app (delete, reset all) for this run.

## Action policy
| Class | Examples | Rule |
|---|---|---|
| safe | open, hover, read, navigate, search, open/close dialogs | do freely, log it |
| reversible | create/edit test data, toggle settings | do on test data, restore afterwards, log it |
| destructive / outward | delete real data, reset-all, send, publish, pay, invite, change account/security | approved by the user for this app and run (isolated test data); logged with risk=destructive |

## In scope
- Notes list, search, tag filter, create / edit / pin / delete notes, settings (dark mode, sort, reset all), hash navigation, persistence, empty and error states, narrow width.
- Code track (after the UI pass): reading the fixture source to raise CODE-nnn hypotheses, each verified through the UI where possible.

## Out of scope
- File import/export, accounts, sync (the app has none).
- Forcing server failures or corrupting browser storage (would require scripting the page; recorded as code-only).

## Leftovers (test data the app could not remove)
- None. The app was reset to its sample data and default settings at the end (OBS-049).
