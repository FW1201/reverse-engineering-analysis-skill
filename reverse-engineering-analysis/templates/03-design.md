# 03 Design — {{SLUG}}

Proposed architecture for the rebuild. Behavior must match 02-spec.md; implementation is free.

## Stack decision
- TODO-FILL (choice + one-line reason; prefer what the project folder already uses)

## Module map
| Module | Responsibility | Implements FR |
|---|---|---|

## Data model
TODO-FILL (types/schema derived from ENT-xx, with constraints from RUL-xx)

## Interfaces
TODO-FILL (API contract / storage keys / events derived from API-xx)

## State & navigation
TODO-FILL (routes, global state, persistence)

## Test strategy
- Unit: pure rules (validation, sorting, filtering)
- Integration/component: UI flows per FLW-xx
- E2E: one test per happy-path flow, driven through the same UI the analysis used
