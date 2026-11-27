#!/usr/bin/env python3
"""Create the analysis workspace for one target inside the PROJECT folder.

Usage:
    python3 scripts/init_workspace.py <project_dir> <target-slug> --target "<url or app name>" [--kind web|native] [--source-mode ui-only|authorized-source|open-source --source <path|url> --auth "<who/license>"]

Creates  <project_dir>/docs/reverse-engineering/<slug>/  with the template files
and an empty observation log. Never overwrites existing files.
Standard library only, so it runs the same under Claude Code and Codex.
"""
import argparse
import datetime as dt
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("slug")
    ap.add_argument("--target", required=True, help="URL or app name being analyzed")
    ap.add_argument("--kind", choices=["web", "native"], default="web")
    ap.add_argument("--source-mode", choices=["ui-only", "authorized-source", "open-source"], default="ui-only",
                    help="ui-only unless the user owns/authorized the code or it is open source")
    ap.add_argument("--source", default="", help="repo path or URL (code modes only)")
    ap.add_argument("--auth", default="", help="who authorized reading the code, or the license")
    a = ap.parse_args()
    if a.source_mode != "ui-only" and not a.source:
        print("--source is required for authorized-source / open-source", file=sys.stderr)
        return 2

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,48}", a.slug):
        print("slug must be lowercase letters, digits, hyphens", file=sys.stderr)
        return 2

    root = pathlib.Path(a.project_dir).expanduser().resolve() / "docs" / "reverse-engineering" / a.slug
    (root / "evidence" / "screens").mkdir(parents=True, exist_ok=True)
    (root / "evidence" / "network").mkdir(parents=True, exist_ok=True)
    (root / "evidence" / "snapshots").mkdir(parents=True, exist_ok=True)
    (root / "evidence" / "design").mkdir(parents=True, exist_ok=True)

    today = dt.date.today().isoformat()
    created, kept = [], []
    for tpl in sorted(TEMPLATES.glob("*.md")):
        dest = root / tpl.name
        if tpl.name == "mechanism-notes.md" and a.source_mode == "ui-only":
            continue
        if dest.exists():
            kept.append(dest.name)
            continue
        text = tpl.read_text(encoding="utf-8")
        text = (text.replace("{{TARGET}}", a.target)
                    .replace("{{SLUG}}", a.slug)
                    .replace("{{KIND}}", a.kind)
                    .replace("{{DATE}}", today)
                    .replace("{{SOURCE_MODE}}", a.source_mode)
                    .replace("{{FIDELITY}}", "neutral" if a.source_mode == "ui-only" else "exact")
                    .replace("{{SOURCE}}", a.source or "n/a (ui-only)")
                    .replace("{{AUTH}}", a.auth or ("n/a (ui-only)" if a.source_mode == "ui-only" else "TODO-FILL")))
        dest.write_text(text, encoding="utf-8")
        created.append(dest.name)

    log = root / "observations.jsonl"
    if not log.exists():
        log.write_text("", encoding="utf-8")
        created.append(log.name)

    stale = [n for n in kept if n == "AGENT-HANDOFF.md"
             and "DESIGN.md" not in (root / n).read_text(encoding="utf-8")]
    print(f"workspace: {root}")
    if stale:
        print("note: existing AGENT-HANDOFF.md predates the DESIGN.md step; compare with templates/AGENT-HANDOFF.md")
    if created:
        print("created:", ", ".join(created))
    if kept:
        print("kept existing:", ", ".join(kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())
