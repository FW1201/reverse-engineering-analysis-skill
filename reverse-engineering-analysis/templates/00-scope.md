# 00 Scope & rules of engagement — {{SLUG}}

- Target: {{TARGET}}  (kind: {{KIND}})
- Version / build observed: TODO-FILL (About page, footer, response headers, app menu)
- Source mode: {{SOURCE_MODE}}   (ui-only | authorized-source | open-source)
- Source location: {{SOURCE}}
- Authorization / license: {{AUTH}}
- Analysis date: {{DATE}}
- Analyst runtime: TODO-FILL (Claude Code / Codex) + tools used

## Purpose
Black-box behavioral analysis so a build agent can implement an original app with equivalent features.
We describe *behavior*, never copy code, assets, brand names, logos, copy text verbatim beyond short UI labels needed for tests.

## Environment
- Account used: TODO-FILL (test account / guest / local fixture — never the user's real account unless they said so)
- Data isolation: TODO-FILL (fresh browser profile, sandbox workspace, local copy)

## Action policy
| Class | Examples | Rule |
|---|---|---|
| safe | open, hover, read, navigate, search, open/close dialogs | do freely, log it |
| reversible | create/edit test data, toggle settings | do on test data, restore afterwards, log it |
| destructive / outward | delete real data, reset-all, send, publish, pay, invite, change account/security | STOP — ask the user in chat first; record as [UNKNOWN] if not approved |

## In scope
- TODO-FILL

## Out of scope
- TODO-FILL

## Leftovers (test data the app could not remove)
- None
