# Tool adapters: Claude Code ↔ Codex

The workflow uses seven primitive operations. Pick the first available row per runtime.
Load deferred tools in ONE search call (Claude Code: `ToolSearch`; Codex: tools are listed at start).

| Primitive | Purpose |
|---|---|
| OPEN | start the target (URL or app) in an isolated surface |
| LOOK | structured state: accessibility tree / DOM snapshot (preferred over pixels) |
| SHOT | screenshot saved to `evidence/screens/OBS-xxx.png` |
| ACT | click / type / key / scroll / select |
| NET | list network requests + fetch bodies (web only) |
| STORE | read localStorage / cookies names / IndexedDB (web) or prefs/files (native) |
| CONSOLE | console errors/warnings |

## Web targets

Choose the browser surface by isolation: a fresh/automation profile beats the user's daily browser
(no logged-in accounts, no real data at risk).

### chrome-devtools MCP (works in BOTH runtimes — default)
Claude Code tool names `mcp__plugin_chrome-devtools-mcp_chrome-devtools__*`; Codex lists the same tools from the `chrome-devtools-mcp` plugin.

| Primitive | Tool |
|---|---|
| OPEN | `new_page {url}` / `navigate_page` |
| LOOK | `take_snapshot` (a11y tree with `uid`s used by ACT) |
| SHOT | `take_screenshot {filePath: "<ws>/evidence/screens/OBS-xxx.png"}` |
| ACT | `click {uid}`, `fill {uid, value}`, `fill_form`, `press_key`, `hover`, `handle_dialog {action}` |
| NET | `list_network_requests`, `get_network_request {reqid}` → save JSON under `evidence/network/` |
| STORE | `evaluate_script` with `() => JSON.stringify(Object.fromEntries(Object.entries(localStorage)))` |
| CONSOLE | `list_console_messages` |

Native `confirm()/alert()` dialogs block the page: answer with `handle_dialog` — `dismiss` unless the action was approved.

Known quirks (observed in testing):
- `fill` may not update framework-controlled inputs (value looks set, app ignores it). Fallback: `click` the field, then `type_text`.
- `Meta+A`/`Control+A` via `press_key` may not select all. To replace a value: reload to a clean state, or click the field and press `Backspace` repeatedly.
- `navigate_page` reload auto-accepts `beforeunload`; whether the app warns on leave stays `[UNKNOWN]` unless tested with a real click on a link.
- "No page found" mid-run: `list_pages`, then `select_page` or `new_page` in the same isolated context (storage survives).
- `resize_page` may stop at ~500px wide; for phone widths use `emulate` with a viewport (e.g. 375x812, mobile).
- Native `confirm()`/`alert()` cannot be screenshotted: log the dialog text from the `handle_dialog` result without `--shot`.
- Waiting for animations (spins, toasts): `wait_for {text}` beats fixed sleeps.
- Testing URL/CSV/file imports without external data: feed a `data:` URL, e.g. `data:text/csv;charset=utf-8,%E5%A7%93%E5%90%8D%0A...`, or serve a fixture you wrote from `evidence/fixtures/` with `python3 -m http.server`. Never upload the user's real files.

### Claude Code alternatives
- Built-in browser pane `mcp__Claude_Browser__*`: `navigate`, `read_page` (LOOK), `computer {action:"screenshot"}` (SHOT; save via the screenshot result is not a file — prefer chrome-devtools when files are needed), `find` + `computer left_click {ref}` (ACT), `read_network_requests` (NET), `javascript_tool` (STORE), `read_console_messages`.
  Allowed for localhost / local files; for remote sites prefer Claude in Chrome.
- Claude in Chrome `mcp__claude-in-chrome__*`: the user's real Chrome — use only when the target needs the user's own sign-in, and treat everything there as the user's data. `tabs_create_mcp`, `navigate`, `read_page`, `computer`, `read_network_requests`, `javascript_tool`, `gif_creator` (record a flow as evidence).

### Codex alternatives
- `cua_repl` `js` tool (unified computer use). First call exactly one entry point, then follow the docs it returns:
  `let tab = await cua.createBrowserTab("iab", url, { visible: true });` (in-app browser), or `"chrome"` with a `sessionName`.
  Emit `::browser-complete{title="..."}` when leaving the browser activity, per its instructions.

### Shell fallback (both runtimes, no MCP)
`npx -y playwright@1.49.1 screenshot --full-page <url> evidence/screens/OBS-xxx.png` for SHOT, and
`curl -s <url>` for static assets/API probes (NET). No clicking — use only to supplement.

## Native desktop targets (macOS)

### Claude Code — `mcp__computer-use__*`
Load all at once: `ToolSearch {query: "computer-use", max_results: 30}`.
1. `request_access {apps:[...]}` — user approves; browsers get read tier, terminals/IDEs click tier.
2. OPEN `open_application`; LOOK `app_ax_find` / `app_list_windows`; SHOT `app_screenshot`;
   ACT `app_click`, `app_type`, `app_key`, `app_scroll`, `app_menu` (menu bar = great feature inventory); `app_batch` for predictable sequences.
3. Prefer `app_*` (background control). Full-screen control only if an `app_*` call says it is needed.
Screenshots come back as images, not files: save evidence by describing the frame in the OBS `result` and, when a file is needed, `screencapture -l <windowid> evidence/screens/OBS-xxx.png` via shell.

### Codex — `cua_repl`
`let app = await cua.getApp("App Name");` then use the returned API docs (UI state, click, type, screenshot).
`await cua.getState()` gives the inventory of apps/browsers when the name is unknown.

### Static inspection that is still black-box (both runtimes, shell)
Allowed because it reads only what the app exposes to any user:
- `plutil -p "/Applications/X.app/Contents/Info.plist"` — bundle id, version, URL schemes, document types
- `defaults read <bundle-id>` — preference keys (names reveal settings)
- `ls ~/Library/Application\ Support/<App>` — storage format (sqlite/json); `sqlite3 file .schema` for schema only
Not allowed: decompiling, disassembling, patching, bypassing licensing/DRM, extracting bundled assets for reuse.
