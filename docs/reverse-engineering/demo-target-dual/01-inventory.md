# 01 Inventory — demo-target-dual

Every row cites the observations (OBS-xxx) that show it.

## Screens (SCR)
| ID | Name / route | Purpose | Key elements | Evidence |
|---|---|---|---|---|
| SCR-01 | Notes list, fragment `#notes` (default) | browse, search, filter notes | header (app name, nav 筆記 / 設定), search box, tag filter, 新增 button, note cards (pin, 編輯, 刪除, title, body, tag chips, timestamp), empty-state text, status toast | OBS-001, OBS-010, OBS-011, OBS-041 |
| SCR-02 | Settings, fragment `#settings` | preferences and reset | heading 設定, 深色模式 checkbox, 排序 select (最近更新 / 標題 A→Z), red 清除所有資料 button | OBS-005, OBS-006, OBS-038 |
| SCR-03 | Note editor (modal dialog) | create / edit a note | heading 新增筆記 or 編輯筆記, fields 標題 (max 40), 內容 (multiline), 標籤 (comma list), inline error line, 取消, 儲存 | OBS-015, OBS-016, OBS-021 |
| SCR-04 | Delete confirmation (in-app modal) | confirm destructive delete | message 確定刪除「title」？此動作無法復原。, 取消 (focused), 確定刪除 | OBS-029 |

## Flows (FLW)
| ID | Flow | Steps (SCR → SCR) | Happy path result | Error/edge paths seen | Evidence |
|---|---|---|---|---|---|
| FLW-01 | First run / load | open app → SCR-01 | sample notes fetched once and stored | reload with data present: no fetch; empty list stays empty | OBS-001, OBS-003, OBS-004, OBS-042 |
| FLW-02 | Search & filter | SCR-01 | live, case-insensitive, AND with tag | no match message; query not persisted; title+body glued match | OBS-010–OBS-014, OBS-047 |
| FLW-03 | Create note | SCR-01 → SCR-03 → SCR-01 | toast 已新增, card added | empty / whitespace title, 41 chars, duplicate title, tag normalization, markup | OBS-015–OBS-020, OBS-032, OBS-043, OBS-045 |
| FLW-04 | Edit note | SCR-01 → SCR-03 → SCR-01 | toast 已更新, timestamp bumped | cancel, Escape, Enter discards (defect), save unchanged bumps time | OBS-021–OBS-026, OBS-048 |
| FLW-05 | Pin / unpin | SCR-01 | note moves to/from pinned group | timestamp unchanged | OBS-027, OBS-028 |
| FLW-06 | Delete note | SCR-01 → SCR-04 → SCR-01 | toast 已刪除, card gone | cancel keeps note; last note → empty state | OBS-029–OBS-031, OBS-041 |
| FLW-07 | Settings | SCR-01 → SCR-02 | dark mode instant, sort changes list, both persist | — | OBS-005–OBS-009 |
| FLW-08 | Reset all | SCR-02 → browser confirm → SCR-02 | samples + default settings restored | dismiss keeps data | OBS-038–OBS-040, OBS-049 |
| FLW-09 | Navigation | header nav / URL fragment | view + fragment switch | unknown fragment → notes; Back / manual fragment change ignored (defect) | OBS-005, OBS-035–OBS-037 |

## Data entities (ENT)
| ID | Entity | Fields (type, constraint) | Where stored (server / localStorage / file) | Evidence |
|---|---|---|---|---|
| ENT-01 | Note | id (string, generated), title (string, trimmed, 1–40 chars, unique), body (string, may be empty, untrimmed), tags (0–5 lowercase unique strings), pinned (bool, default false), updatedAt (timestamp) | browser local storage, one JSON document | OBS-002, OBS-020, OBS-043 |
| ENT-02 | Settings | dark (bool, default false), sort ('updated' default or 'title') | same document as notes | OBS-002, OBS-006, OBS-040 |
| ENT-03 | Sample data | 3 notes (one pinned, tags home/study/work) | served JSON file, fetched on first run and after reset | OBS-003, OBS-040 |

## Interfaces (API) — network calls, IPC, files, URL schemes
| ID | Method + path | Request | Response shape | When called | Evidence |
|---|---|---|---|---|---|
| API-01 | GET /api/notes.json (relative to app) | none | object with notes array (Note shape) | first run (no stored data) and after reset | OBS-003, OBS-040 |
| API-02 | local storage key `pocketnote.v1` | — | object with notes and settings | written after every change | OBS-002, OBS-020 |
| API-03 | URL fragment `#notes` / `#settings` | — | selects the view on load | on nav click and page load | OBS-005, OBS-035, OBS-036 |

## Rules & states (RUL) — validation, sorting, limits, empty/error/loading states
| ID | Rule | How it was confirmed | Evidence |
|---|---|---|---|
| RUL-01 | Pinned notes first; then newest update first (default) | seed order | OBS-001 |
| RUL-02 | Title sort uses Traditional Chinese collation (牛 < 測 < 讀; Latin after Han); applies inside pinned group too | sort switched to 標題 A→Z | OBS-008, OBS-026, OBS-027 |
| RUL-03 | Title required after trimming; max 40 chars (extra keystrokes ignored) | empty, spaces, 41 chars | OBS-016–OBS-018 |
| RUL-04 | Title must be unique (trimmed exact match, own note excluded) | duplicate create, unchanged edit | OBS-045, OBS-048 |
| RUL-05 | Tags: split on , or ，; trim; lowercase; drop empty; dedupe; keep first 5 | tag inputs | OBS-019, OBS-043 |
| RUL-06 | Search: trimmed, case-insensitive substring of title/body; AND with tag | typing | OBS-010, OBS-014 |
| RUL-07 | Empty states: 還沒有筆記… when no notes; 找不到符合的筆記 when filters exclude all | delete all, search miss | OBS-011, OBS-041 |
| RUL-08 | Toasts 已新增 / 已更新 / 已刪除 in a polite live region, hide after ~2 s | after actions | OBS-019, OBS-044 |
| RUL-09 | Pinning does not change the timestamp; saving (even unchanged) sets it to now | pin, save | OBS-027, OBS-048 |

## Coverage checklist
- [x] every nav item / menu / tab opened
- [x] every form: submitted empty, invalid, boundary (max length), valid
- [x] every list: empty state, filter/search/sort combos, many items (only up to 4 notes; no paging seen)
- [x] persistence: reload / restart keeps what?
- [x] network/storage captured (web) or files/prefs inspected (native)
- [x] keyboard shortcuts (Enter, Escape), responsive/narrow width, dark mode (if present)
- [ ] errors: offline, server error, permission denied — not safely testable without scripting; code-only (CODE-011)
