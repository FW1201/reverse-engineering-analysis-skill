#!/usr/bin/env python3
"""Append one observation to observations.jsonl with the next OBS id.

Usage:
    python3 scripts/log_observation.py <workspace_dir> \
        --screen SCR-01 --action click --target "＋ 新增筆記" \
        --result "modal dialog 'New note' opened, title field focused" \
        [--evidence evidence/screens/OBS-004.png ...] [--risk safe|reversible|destructive] [--note "..."]

    python3 scripts/log_observation.py <workspace_dir> --peek
        -> prints the id the NEXT log call will get (e.g. OBS-004), without logging.

Typical loop: log with --shot -> it prints "OBS-004 evidence/screens/OBS-004.png" -> save the
screenshot to exactly that path. (--peek only prints the next id.)
Evidence is optional per observation (e.g. a pure storage read can cite nothing).
Using the script instead of hand-editing keeps ids unique and the JSON valid.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

ACTIONS = ["observe", "click", "type", "key", "scroll", "navigate", "hover",
           "drag", "network", "storage", "console", "resize", "reload", "other"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--peek", action="store_true", help="print the next id and exit")
    ap.add_argument("--screen", help="SCR-xx id of the screen the action happened on")
    ap.add_argument("--action", choices=ACTIONS)
    ap.add_argument("--target", default="", help="element label/role/selector acted on")
    ap.add_argument("--input", default="", help="text typed or value chosen (never real secrets)")
    ap.add_argument("--result", help="what visibly/observably changed")
    ap.add_argument("--evidence", nargs="*", default=[], help="paths relative to workspace")
    ap.add_argument("--shot", action="store_true",
                    help="also attach evidence/screens/<id>.png and print that path; save the screenshot there next")
    ap.add_argument("--risk", choices=["safe", "reversible", "destructive"], default="safe")
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    ws = pathlib.Path(a.workspace).expanduser().resolve()
    log = ws / "observations.jsonl"
    if not log.exists():
        print(f"no observations.jsonl in {ws}; run init_workspace.py first", file=sys.stderr)
        return 2

    n = sum(1 for line in log.read_text(encoding="utf-8").splitlines() if line.strip())
    oid = f"OBS-{n + 1:03d}"
    if a.peek:
        print(oid)
        return 0
    missing = [f for f in ("screen", "action", "result") if not getattr(a, f)]
    if missing:
        print("required: " + ", ".join("--" + m for m in missing), file=sys.stderr)
        return 2
    if a.shot:
        a.evidence = [f"evidence/screens/{oid}.png"] + a.evidence
    rec = {
        "id": oid,
        "ts": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "screen": a.screen,
        "action": a.action,
        "target": a.target,
        "input": a.input,
        "result": a.result,
        "evidence": a.evidence,
        "risk": a.risk,
        "note": a.note,
    }
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(oid, *(a.evidence[:1] if a.shot else []))
    return 0


if __name__ == "__main__":
    sys.exit(main())
