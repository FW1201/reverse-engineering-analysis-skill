# Build agent handoff — {{SLUG}}

You are implementing an original application from a behavioral specification.

## Read in this order
1. 02-spec.md — what to build (source of truth)
2. 03-design.md — how to structure it; DESIGN.md — the visual tokens and component styles to apply
3. 04-tdd-plan.md — the order of work; follow RED → GREEN → REFACTOR per task
4. 01-inventory.md + evidence/ — only when a requirement is ambiguous

## Rules
- Build in: TODO-FILL (path inside the project folder)
- Do not copy names, logos, images or long text from evidence/; use neutral placeholders.
- `[INFERRED]` requirements: implement the simplest behavior consistent with the spec and note it.
- `[DEFECT-FIX]` requirements: build the corrected behavior, not the original defect (see Observed defects in 02-spec.md).
- Styling: use DESIGN.md tokens (as CSS variables or theme config); do not hard-code colors or sizes. In `neutral` fidelity, never try to match the original's brand.
- `[CODE-ONLY]` requirements: implement from the plain-language finding in mechanism-notes.md (the CODE-nnn they cite); write the test against the behavior described there.
- Do not open the original application's source. mechanism-notes.md is the only code-derived input, and it contains no code to copy.
- `[UNKNOWN]` requirements: do not invent; leave a clearly marked stub and list it in your final report.
- A task is done only when its test was seen failing first and now passes.
- Finish by running the full test suite and reporting results per FR (see 05-traceability.md).
