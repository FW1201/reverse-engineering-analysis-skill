# 01 Inventory — {{SLUG}}

Every row cites the observations (OBS-xxx) that show it.

## Screens (SCR)
| ID | Name / route | Purpose | Key elements | Evidence |
|---|---|---|---|---|
| SCR-01 | TODO-FILL | | | OBS-001 |

## Components (CMP) — reusable UI pieces; each gets an entry in DESIGN.md `## Components`
| ID | Component | Where used (SCR) | Variants / states seen | Evidence |
|---|---|---|---|---|
| CMP-01 | TODO-FILL | | | |

## Flows (FLW)
| ID | Flow | Steps (SCR → SCR) | Happy path result | Error/edge paths seen | Evidence |
|---|---|---|---|---|---|
| FLW-01 | TODO-FILL | | | | |

## Data entities (ENT)
| ID | Entity | Fields (type, constraint) | Where stored (server / localStorage / file) | Evidence |
|---|---|---|---|---|
| ENT-01 | TODO-FILL | | | |

## Interfaces (API) — network calls, IPC, files, URL schemes
| ID | Method + path | Request | Response shape | When called | Evidence |
|---|---|---|---|---|---|

## Rules & states (RUL) — validation, sorting, limits, empty/error/loading states
| ID | Rule | How it was confirmed | Evidence |
|---|---|---|---|

## Coverage checklist
- [ ] every nav item / menu / tab opened
- [ ] every form: submitted empty, invalid, boundary (max length), valid
- [ ] every list: empty state, filter/search/sort combos, many items
- [ ] persistence: reload / restart keeps what?
- [ ] network/storage captured (web) or files/prefs inspected (native)
- [ ] keyboard shortcuts, responsive/narrow width, dark mode (if present)
- [ ] design: tally per main screen, component states (hover/focus/disabled/error), both themes
- [ ] errors: offline, server error, permission denied (if safely testable)
