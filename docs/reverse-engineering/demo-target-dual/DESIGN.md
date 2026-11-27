---
version: alpha
name: "demo-target-dual rebuild"
description: "Plain, compact note-taking UI: white page, light grey rounded cards, one blue primary button, red for destructive actions, native form controls, optional dark theme."
colors:
  primary: "#2563EB"
  on-primary: "#FFFFFF"
  secondary: "#DBEAFE"
  on-secondary: "#1E3A8A"
  background: "#FFFFFF"
  surface: "#F4F4F5"
  on-surface: "#111111"
  on-surface-muted: "#666666"
  outline: "#CCCCCC"
  divider: "#DDDDDD"
  control-border: "#767676"
  error: "#DC2626"
  on-error: "#FFFFFF"
  scrim: "#0000001A"
  toast: "#111111"
  on-toast: "#FFFFFF"
  focus-ring: "#005FCC"
  background-dark: "#111111"
  surface-dark: "#222222"
  on-surface-dark: "#EEEEEE"
  on-surface-muted-dark: "#AAAAAA"
typography:
  h1:
    fontFamily: system-ui
    fontSize: 18px
    fontWeight: 700
    lineHeight: normal
  h2:
    fontFamily: system-ui
    fontSize: 24px
    fontWeight: 700
    lineHeight: normal
  h3-dialog:
    fontFamily: system-ui
    fontSize: 18.72px
    fontWeight: 700
    lineHeight: normal
  title-md:
    fontFamily: system-ui
    fontSize: 16px
    fontWeight: 700
    lineHeight: normal
  body-md:
    fontFamily: system-ui
    fontSize: 16px
    fontWeight: 400
    lineHeight: normal
  body-sm:
    fontFamily: system-ui
    fontSize: 12px
    fontWeight: 400
    lineHeight: normal
  label-md:
    fontFamily: Arial
    fontSize: 13.33px
    fontWeight: 400
    lineHeight: normal
  label-sm:
    fontFamily: system-ui
    fontSize: 11px
    fontWeight: 400
    lineHeight: normal
rounded:
  sm: 6px
  md: 8px
  lg: 10px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  btn-y: 6px
  btn-x: 10px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 6px 10px
    typography: "{typography.label-md}"
  button-neutral:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.sm}"
    padding: 6px 10px
    typography: "{typography.label-md}"
  button-danger:
    backgroundColor: "{colors.error}"
    textColor: "{colors.on-error}"
    rounded: "{rounded.sm}"
    padding: 6px 10px
    typography: "{typography.label-md}"
  note-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 10px 12px
  tag-chip:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.on-secondary}"
    rounded: "{rounded.lg}"
    padding: 1px 6px
    typography: "{typography.label-sm}"
  dialog:
    backgroundColor: "{colors.background}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 16px
  toast:
    backgroundColor: "{colors.toast}"
    textColor: "{colors.on-toast}"
    rounded: "{rounded.sm}"
    padding: 8px 14px
---
## Overview
A deliberately plain utility look. One narrow centred column of light grey cards on a white page, a thin header with the app name and two navigation buttons, and native browser form controls. Colour is used sparingly: blue only for the single "new note" / "save" action and for tag chips, red only for destructive actions and validation errors. A dark theme swaps the page and card greys but keeps every size, radius and spacing. There is no motion besides the browser's own.

## Colors
- `background` — page and dialog surface (light). `background-dark` in dark theme.
- `surface` — note cards and neutral buttons (navigation, pin, edit, delete, cancel). `surface-dark` in dark theme.
- `on-surface` / `on-surface-muted` — main text / timestamp meta line (5.22:1 on cards). Dark: `on-surface-dark` / `on-surface-muted-dark` (6.85:1).
- `outline` — 1px border of neutral buttons (kept in dark theme). `divider` — header bottom rule. `control-border` — native search/select/text field border.
- `primary` / `on-primary` — the one action per screen: "＋ new note" in the list, "save" in the editor (5.17:1).
- `secondary` / `on-secondary` — tag chips (8.49:1), unchanged in dark theme.
- `error` / `on-error` — destructive buttons (confirm delete, clear all data; 4.83:1) and inline validation text on white (4.83:1).
- `scrim` — 10% black behind modal dialogs. `toast` / `on-toast` — status message box. `focus-ring` — browser default focus outline (no custom focus styling).

## Typography
System UI sans for content (`system-ui`, 16px base, line-height `normal`). Headings: app name 18/700, settings heading 24/700, dialog heading 18.72/700, card titles 16/700. Meta line 12px, tag chips 11px. Buttons do not inherit the page font: they render in the browser's default control font (Arial-like sans) at 13.33px — recorded exactly; a rebuild may set buttons to `system-ui` at the same 13.33px size without visible change in layout.

## Layout
- Header: full width, 58px tall, 12x16 padding, app name left, navigation buttons right with a 4px gap, 1px `divider` bottom rule.
- Main: centred column, max width 720px, 16px padding; at 1280px wide it sits with equal side margins, at 375px it fills the width (same padding, no breakpoint-specific rules).
- Notes view: toolbar stacked vertically (search field, tag select, new-note button; 8px gap; 12px below), then the card list (8px between cards).
- Card anatomy: action row (pin, edit, delete; 4px gaps) above the title, body line, then chips + timestamp meta line.
- Dialog: 300px content width (max viewport - 38px), centred, 16px padding, 10px radius, no shadow; fields full width; actions right-aligned.
- Spacing scale: 4 / 6 / 8 / 10 / 12 / 16. Density is compact (33px buttons, 35px fields). No horizontal scrolling at 375px.

## Components
- **Header navigation buttons** (notes / settings) — `button-neutral`, 33px tall; the current page is announced to assistive tech but looks identical to the other button (rebuild: also mark it visually, e.g. `primary` text or a 2px underline).
- **Search field / tag select / sort select** — native controls, full width, 35px tall, 6px padding, 16px text, `control-border` (search 2px inset, selects 1px). Focus: browser focus ring.
- **New-note button** — `button-primary`, 33px tall. Hover: unchanged (no hover style). Focus-visible: browser ring. No disabled state seen.
- **Neutral buttons** (pin icon, edit, delete, cancel, nav) — `button-neutral`, 1px `outline` border; hover unchanged; pressed default.
- **Note card** — `note-card`, 8px radius, no border or shadow; pinned and unpinned cards look the same apart from the pin icon (📌 vs 📍).
- **Tag chip** — `tag-chip`, 15px tall, 4px right margin.
- **Meta line** — `body-sm` in `on-surface-muted`, "· date time" after the chips.
- **Empty / no-match message** — `body-md` text in place of the list.
- **Editor dialog** — `dialog` + `scrim`; heading `h3-dialog`; labelled title (35px), body textarea (90px), tags field; inline error line `body-sm` in `error` with 16px height reserved so the layout does not jump; actions: cancel (`button-neutral`) and save (`button-primary`).
- **Delete confirm dialog** — `dialog`, 336px wide; message `body-md`; cancel (`button-neutral`, receives focus on open) and confirm (`button-danger`).
- **Settings** — `h2` heading, native 13px checkbox for dark theme, labelled sort select, `button-danger` "clear all data".
- **Toast** — `toast`, fixed bottom-centre 16px above the edge, `body-md` white text, 6px radius, polite live region, hidden after ~2 s.
- **Dark theme** — swap `background`/`surface`/`on-surface`/`on-surface-muted` for their `-dark` tokens; primary, chips and error unchanged.

## Do's and Don'ts
- Do keep exactly one `primary` button per view and use `error` only for destructive actions and validation text.
- Do keep cards borderless and flat; separation comes from the grey fill and 8px gaps.
- Do theme native controls in dark mode (set the page color scheme so search, select and checkbox turn dark) — the original leaves them white.
- Do give the toast a visible edge in dark theme (e.g. `surface-dark` fill with `outline` border) — the original's #111 box on the #111 page has a 1:1 edge.
- Do show the current navigation item visually, not only to screen readers.
- Don't add shadows, gradients or animation; this design has none.
- Don't change sizes between themes.

## Provenance
- Fidelity: exact
- Evidence: Colors: OBS-050, OBS-055, OBS-058 (light/dark tallies, pixel palette, contrast), OBS-052, OBS-053, OBS-054; Typography: OBS-050, OBS-052, OBS-054; Layout: OBS-050, OBS-052, OBS-057, OBS-033; Components and states: OBS-051 (hover/focus), OBS-052 (editor + error), OBS-053 (delete confirm), OBS-054 (settings, dark switch), OBS-056 (toast, pin); earlier screens OBS-001, OBS-006, OBS-009, OBS-016, OBS-029. Raw values: evidence/design/SCR-01-computed-light.json, SCR-01-components-light.json, SCR-01-computed-dark.json, SCR-02-computed-dark.json, SCR-03-components-light.json, palette-sample.txt.
- Neutralized: nothing in the tokens (exact mode; authorized source, owner approved). The app name in the header is not a token — the rebuild picks its own name per AGENT-HANDOFF.md. Values were measured from the rendered UI, not copied from the source stylesheet.
