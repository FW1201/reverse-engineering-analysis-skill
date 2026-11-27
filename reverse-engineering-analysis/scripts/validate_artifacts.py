#!/usr/bin/env python3
"""Gate check before handing the plan to a build agent.

Usage:
    python3 scripts/validate_artifacts.py <workspace_dir> [--write-matrix]

Checks
  observations.jsonl  valid JSON lines, unique OBS ids, evidence files exist
  01-inventory.md     defines SCR-/FLW-/ENT- ids (API-/RUL- optional)
  02-spec.md          every '### FR-xxx' block has Given/When/Then acceptance
                      criteria and either cites existing OBS ids or is tagged
                      [INFERRED] / [UNKNOWN] / [DEFECT-FIX]; a 'Open questions' section exists
  04-tdd-plan.md      every '### T-xxx' block names a failing test first (RED)
                      and covers >=1 FR; every in-scope FR is covered by a task
  00-scope.md         declares Source mode; ui-only => no CODE blocks
  mechanism-notes.md  each CODE-xxx is Verified by / Contradicted by an OBS or [CODE-ONLY]
  DESIGN.md           design.md alpha tokens + sections; Provenance cites OBS; ui-only => neutral
  02-spec.md          no code blocks / selectors / code identifiers (leak check)
  all docs            no leftover template placeholders ({{ }}, TBD, TODO-FILL)

--write-matrix writes 05-traceability.md (FR -> OBS -> T).
Exit code 0 = ready for handoff, 1 = problems listed.
"""
import argparse
import json
import pathlib
import re
import sys

ID = {
    "OBS": re.compile(r"\bOBS-\d{3}\b"),
    "FR": re.compile(r"\bFR-\d{3}\b"),
    "T": re.compile(r"\bT-\d{3}\b"),
    "CODE": re.compile(r"\bCODE-\d{3}\b"),
}
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}|\bTODO-FILL\b|\bTBD\b")


def blocks(text: str, prefix: str):
    """Yield (id, body) for each '### <prefix>-nnn' heading block."""
    pat = re.compile(rf"^###\s+({prefix}-\d{{3}})\b.*$", re.M)
    hits = list(pat.finditer(text))
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        nxt = re.search(r"^##\s", text[m.end():end], re.M)  # stop at next H2
        if nxt:
            end = m.end() + nxt.start()
        yield m.group(1), text[m.start():end]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--write-matrix", action="store_true")
    a = ap.parse_args()
    ws = pathlib.Path(a.workspace).expanduser().resolve()
    errs, warns = [], []

    def read(name):
        p = ws / name
        if not p.exists():
            errs.append(f"missing {name}")
            return ""
        return p.read_text(encoding="utf-8")

    # --- observations
    obs = {}
    log = ws / "observations.jsonl"
    if not log.exists():
        errs.append("missing observations.jsonl")
    else:
        for n, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError as e:
                errs.append(f"observations.jsonl line {n}: invalid JSON ({e})")
                continue
            oid = r.get("id", "")
            if oid in obs:
                errs.append(f"duplicate {oid}")
            obs[oid] = r
            for ev in r.get("evidence", []):
                if not (ws / ev).exists():
                    errs.append(f"{oid}: evidence file not found: {ev}")
        if len(obs) < 10:
            warns.append(f"only {len(obs)} observations; coverage is probably thin")
        if obs and not any(r.get("evidence") for r in obs.values()):
            errs.append("no observation has evidence attached (screenshots/snapshots/network dumps)")

    # --- inventory
    inv = read("01-inventory.md")
    for p in ("SCR", "FLW", "ENT"):
        if inv and not re.search(rf"\b{p}-\d{{2}}\b", inv):
            errs.append(f"01-inventory.md defines no {p}-xx ids")

    # --- source mode + code track
    scope = (ws / "00-scope.md").read_text(encoding="utf-8") if (ws / "00-scope.md").exists() else ""
    mm = re.search(r"Source mode:\s*(ui-only|authorized-source|open-source)\b", scope)
    mode = mm.group(1) if mm else None
    if scope and not mode:
        errs.append("00-scope.md: missing 'Source mode: ui-only|authorized-source|open-source'")
    codes, affects = {}, {}
    mech_p = ws / "mechanism-notes.md"
    mech = re.sub(r"<!--.*?-->", "", mech_p.read_text(encoding="utf-8"), flags=re.S) if mech_p.exists() else ""
    for cid, body in blocks(mech, "CODE"):
        ver = re.search(r"Verified by:\s*(OBS-\d{3})", body)
        con = re.search(r"Contradicted by:\s*(OBS-\d{3})", body)
        only = "[CODE-ONLY]" in body
        state = "verified" if ver else "contradicted" if con else "code-only" if only else None
        if state is None:
            errs.append(f"{cid}: close with 'Verified by: OBS-nnn', 'Contradicted by: OBS-nnn' or [CODE-ONLY]")
        for m in (ver, con):
            if m and m.group(1) not in obs:
                errs.append(f"{cid}: cites unknown {m.group(1)}")
        if re.search(r"```|=>|\bfunction\s*\(|getElementById|querySelector", body):
            errs.append(f"{cid}: contains code; describe the finding in plain words")
        codes[cid] = state
        affects[cid] = set(ID["FR"].findall("".join(re.findall(r"Affects:.*", body))))
    if mode == "ui-only" and codes:
        errs.append(f"source mode is ui-only but mechanism-notes.md has {len(codes)} CODE block(s); "
                    "reading code needs authorized-source/open-source")
    if mode == "open-source" and re.search(r"Authorization / license:\s*(TODO-FILL|n/a)", scope):
        errs.append("00-scope.md: open-source mode needs the license recorded")

    # --- spec
    spec = read("02-spec.md")
    frs, spec_cites = {}, {}
    for fid, body in blocks(spec, "FR"):
        if fid in frs:
            errs.append(f"duplicate {fid} in 02-spec.md")
        tag = next((x for x in ("[UNKNOWN]", "[INFERRED]", "[CODE-ONLY]", "[DEFECT-FIX]") if x in body), None)
        tagged = tag is not None
        out_scope = "[OUT-OF-SCOPE]" in body
        cites = set(ID["OBS"].findall(body))
        for c in set(ID["CODE"].findall(body)):
            if c not in codes:
                errs.append(f"{fid}: cites undefined {c}")
            elif codes[c] == "code-only" and tag not in ("[CODE-ONLY]", "[DEFECT-FIX]") and not cites:
                errs.append(f"{fid}: relies on code-only {c}; tag the FR [CODE-ONLY] (or [DEFECT-FIX] if it fixes a defect)")
        missing = sorted(c for c in cites if c not in obs)
        if missing:
            errs.append(f"{fid}: cites unknown observations {', '.join(missing)}")
        if not cites and not tagged and not out_scope:
            errs.append(f"{fid}: no OBS evidence and not tagged [INFERRED]/[UNKNOWN]/[CODE-ONLY]/[DEFECT-FIX]")
        if not out_scope and not all(re.search(rf"\b{k}\b", body, re.I) for k in ("Given", "When", "Then")):
            errs.append(f"{fid}: acceptance criteria must use Given / When / Then")
        frs[fid] = {"obs": sorted(cites), "out": out_scope, "tagged": tagged, "tag": tag}
        spec_cites[fid] = set(ID["CODE"].findall(body))
    if spec and not frs:
        errs.append("02-spec.md has no '### FR-xxx' requirement blocks")
    if spec and not re.search(r"^##\s+.*(Open questions|未決問題)", spec, re.M | re.I):
        errs.append("02-spec.md needs an '## Open questions' section (write 'None' if truly none)")

    # --- tdd plan
    plan = read("04-tdd-plan.md")
    covered = {}
    tasks = list(blocks(plan, "T"))
    if plan and not tasks:
        errs.append("04-tdd-plan.md has no '### T-xxx' task blocks")
    for tid, body in tasks:
        refs = set(ID["FR"].findall(body))
        if not refs:
            errs.append(f"{tid}: covers no FR")
        for f in refs:
            if f not in frs:
                errs.append(f"{tid}: references undefined {f}")
            covered.setdefault(f, []).append(tid)
        if not re.search(r"\bRED\b", body):
            errs.append(f"{tid}: must state the failing test first (RED)")
        if not re.search(r"\bGREEN\b", body):
            errs.append(f"{tid}: must state the minimal implementation step (GREEN)")
    for f, meta in frs.items():
        if not meta["out"] and f not in covered:
            errs.append(f"{f}: not covered by any T-xxx task")

    # --- placeholders
    for name in ("00-scope.md", "01-inventory.md", "02-spec.md", "03-design.md", "04-tdd-plan.md", "AGENT-HANDOFF.md", "DESIGN.md"):
        p = ws / name
        if not p.exists():
            if name not in ("01-inventory.md", "02-spec.md", "04-tdd-plan.md", "DESIGN.md"):
                errs.append(f"missing {name}")
            continue
        for m in PLACEHOLDER.finditer(p.read_text(encoding="utf-8")):
            errs.append(f"{name}: leftover placeholder '{m.group(0)}'")
            break

    # --- Affects consistency
    for cid, frset in affects.items():
        for f in sorted(frset):
            if f not in frs:
                errs.append(f"{cid}: Affects undefined {f}")
            elif cid not in spec_cites.get(f, set()):
                warns.append(f"{cid} says it affects {f}, but {f} does not cite {cid}")

    # --- DESIGN.md (visual design system, Google design.md alpha)
    dp = ws / "DESIGN.md"
    if not dp.exists():
        errs.append("missing DESIGN.md (see references/design-extraction.md)")
    else:
        d = dp.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n(.*)$", d, re.S)
        if not fm:
            errs.append("DESIGN.md: needs YAML front matter between --- lines")
        else:
            y, body = fm.groups()
            if not re.search(r"^version:\s*alpha\s*$", y, re.M):
                errs.append("DESIGN.md: front matter needs 'version: alpha'")
            for sect, keys in (("colors", ("primary", "background", "on-surface")),
                               ("typography", ("h1", "body-md")),
                               ("rounded", ("sm", "md", "lg")),
                               ("spacing", ("sm", "md", "lg"))):
                m = re.search(rf"^{sect}:\n((?:[ \t]+.*\n?)+)", y, re.M)
                if not m:
                    errs.append(f"DESIGN.md: front matter missing '{sect}'")
                    continue
                for k in keys:
                    if not re.search(rf"^[ \t]+{re.escape(k)}:", m.group(1), re.M):
                        errs.append(f"DESIGN.md: {sect}.{k} missing")
            for hx in re.findall(r"#[0-9A-Fa-f]{3,8}\b", y):
                if len(hx) not in (4, 7, 9):
                    errs.append(f"DESIGN.md: bad hex {hx}")
            for sect in ("Overview", "Colors", "Typography", "Layout", "Components", "Do's and Don'ts", "Provenance"):
                if not re.search(rf"^##\s+{re.escape(sect)}\s*$", body, re.M):
                    errs.append(f"DESIGN.md: missing '## {sect}' section")
            prov = body.split("## Provenance", 1)[-1]
            fid = re.search(r"Fidelity:\s*(neutral|exact)", prov)
            if not fid:
                errs.append("DESIGN.md: Provenance needs 'Fidelity: neutral|exact'")
            elif mode == "ui-only" and fid.group(1) != "neutral":
                errs.append("DESIGN.md: ui-only mode requires Fidelity: neutral (do not copy a third-party brand)")
            dobs = set(ID["OBS"].findall(prov))
            if not dobs:
                errs.append("DESIGN.md: Provenance must cite the OBS evidence the tokens come from")
            for o in sorted(dobs - set(obs)):
                errs.append(f"DESIGN.md: cites unknown {o}")
            if mode == "ui-only" and not re.search(r"Neutralized:\s*\S", prov):
                errs.append("DESIGN.md: ui-only mode must list what was neutralized")
            for cmp_id, name in re.findall(r"^\|\s*(CMP-\d{2})\s*\|\s*([^|]+?)\s*\|", inv, re.M):
                comp_sec = body.split("## Components", 1)[-1].split("\n## ", 1)[0]
                if cmp_id not in comp_sec and name.lower() not in comp_sec.lower():
                    warns.append(f"DESIGN.md: component {cmp_id} ({name}) from 01-inventory.md has no entry under ## Components")
            if plan and not re.search(r"DESIGN\.md|design token|tokens?\b", plan, re.I):
                errs.append("04-tdd-plan.md: no task applies/tests the DESIGN.md tokens (add a styling task with a RED test)")
            if re.search(r"data:image|base64,", d):
                errs.append("DESIGN.md: embedded image data; reference files or describe instead")

    # --- implementation leakage into the spec
    LEAK = re.compile(r"`[#.][A-Za-z][\w-]*`|getElementById|querySelector|addEventListener|localStorage\.|"
                      r"\buse(State|Effect)\b|=>|\bfunction\s*\(|\bclassName\b")
    for n, line in enumerate(spec.splitlines(), 1):
        if line.strip().startswith("```"):
            errs.append(f"02-spec.md:{n}: code block in spec; specs describe behavior only")
            break
    for n, line in enumerate(spec.splitlines(), 1):
        m = LEAK.search(line)
        if m:
            errs.append(f"02-spec.md:{n}: implementation detail '{m.group(0)}' in spec")

    # --- stats
    inferred = sum(1 for m in frs.values() if m["tag"] in ("[INFERRED]", "[UNKNOWN]", "[CODE-ONLY]"))
    if frs and inferred / len(frs) > 0.3:
        warns.append(f"{inferred}/{len(frs)} FRs are [INFERRED]/[UNKNOWN]/[CODE-ONLY]; explore more before handoff")

    if a.write_matrix and frs:
        rows = ["# 05 Traceability matrix (generated by validate_artifacts.py)", "",
                "| FR | Evidence | Tasks | Status |", "|---|---|---|---|"]
        for f in sorted(frs):
            m = frs[f]
            status = ("out-of-scope" if m["out"] else
                      (m["tag"].strip("[]").lower() if m["tag"] else "observed"))
            rows.append(f"| {f} | {', '.join(m['obs']) or '—'} | {', '.join(covered.get(f, [])) or '—'} | {status} |")
        (ws / "05-traceability.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(f"mode: {mode}  observations: {len(obs)}  requirements: {len(frs)}  tasks: {len(tasks)}"
          + (f"  code: {sum(v == 'verified' for v in codes.values())} verified / "
             f"{sum(v == 'code-only' for v in codes.values())} code-only / "
             f"{sum(v == 'contradicted' for v in codes.values())} contradicted" if codes else ""))
    for w in warns:
        print("WARN ", w)
    for e in errs:
        print("ERROR", e)
    print("READY FOR HANDOFF" if not errs else f"NOT READY: {len(errs)} problem(s)")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
