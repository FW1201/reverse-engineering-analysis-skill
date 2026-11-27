# Building DESIGN.md from the UI

Output: `<ws>/DESIGN.md` in Google design.md alpha format (YAML tokens + Overview / Colors / Typography / Layout / Components / Do's and Don'ts), plus a `## Provenance` section. Lint: `npx -y @google/design.md lint DESIGN.md` (optional, needs Node; may require the user's approval to run). `validate_artifacts.py` is the required gate.

## Fidelity follows the source mode

| Source mode | Fidelity | Tokens you write |
|---|---|---|
| `ui-only` | `neutral` | Keep **structure**: spacing scale, type scale (sizes/weights/line-heights), radius, elevation steps, density, layout grid, component anatomy and states. Replace **identity**: brand/accent hues become an original palette with the same roles and contrast; fonts become a freely licensed family of the same class (e.g. geometric sans → Inter / Noto Sans TC); no logo, illustration, icon set or imagery. Record the original only as a role description ("saturated blue primary, dark navy background"). |
| `authorized-source` / `open-source` | `exact` | Measured values as-is (hex, font families, px). Logos/images only if the user owns them; reference them by path, never embed. |

## Web: measure rendered values (read-only)

Use [scripts/design_tally.js](../scripts/design_tally.js) — it returns **value frequencies only** (no selectors, class names or markup), consistent with rule 1. Paste its function into `evaluate_script` (chrome-devtools) / `javascript_tool` (Claude browser pane) / `cua_repl`; the snippet returns an object, so `filePath` saves real JSON.

1. **Viewport first:** `emulate` a desktop viewport (1440x900) before measuring; the browser may still be at a narrow size from earlier steps. Repeat at 375x812 for the responsive notes.
2. **Page tally** per main screen → `evidence/design/<SCR-id>-computed.json`, logged as an OBS (`--action other --target "computed styles"`). It captures colors, fonts (incl. line-height `normal`), gradients, radii, shadows, padding, gap, borders, opacity, transitions.
3. **Component states:** for each component in the inventory, measure one instance with the single-element function (pass its snapshot `uid`), then hover / Tab-focus / press with real input, **wait ~300 ms** for transitions, measure again → `evidence/design/<SCR-id>-components.json`.
4. **Themes:** if the app has a dark mode, switch it with the UI and re-run the tally; name dark tokens with a `-dark` suffix (`background-dark`, `on-surface-dark`).
5. Visual bugs you see (invisible hover label, failing contrast, focus ring missing) go to **Observed defects** like any other defect, with the fixed token in DESIGN.md.

## Native apps / no DOM: measure pixels

- `python3 scripts/sample_colors.py evidence/screens/OBS-012.png --top 12` → dominant colors (background, surface, text, accent). Default 5-bit buckets separate near-whites like #F4F4F5 vs #FFFFFF; `--bits 6` for finer, `--bits 4` for a coarse overview.
- `--at x,y ...` → exact color of a button, link or badge you can see in the screenshot.
- `--contrast "#FG" "#BG"` → WCAG ratio; put failures in Observed defects. Pass the two hex values literally (zsh does not word-split a variable).
- Sizes: measure in the screenshot (zoom tool) and divide by the device scale factor (Retina = 2).
- Fonts: system apps usually use the platform font (SF Pro / PingFang TC on macOS); say "system UI font" unless the About box or bundle lists a custom font.

## From tallies to tokens

| Tally | Token | Rule of thumb |
|---|---|---|
| most frequent large-area background | `colors.background` | |
| card/dialog backgrounds | `colors.surface` | |
| most frequent text color | `colors.on-surface`; lighter one → `on-surface-muted` | |
| color on primary buttons / active nav | `colors.primary` | primary = the main action, not decoration |
| destructive button / error text | `colors.error` | |
| font sizes | `typography.h1…label-sm` | map largest → h1, body text → body-md; keep weights and line-heights |
| radii | `rounded.sm/md/lg/full` | cluster near values (6/8px → md) |
| paddings + gaps | `spacing.xs…xl` | look for the base unit (4 or 8) and a scale |
| shadows | describe in `## Elevation` | |

## Required sections in the markdown body
`## Overview` (look-and-feel in 3–5 sentences, original wording) · `## Colors` (role of each token) · `## Typography` · `## Layout` (grid, max width, breakpoints seen at narrow width, density) · `## Components` (one bullet per component in 01-inventory: anatomy, sizes, states default/hover/focus/disabled/error) · `## Do's and Don'ts` · `## Provenance` (fidelity, evidence OBS ids per section, what was neutralized).
