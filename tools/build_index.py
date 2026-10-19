#!/usr/bin/env python3
"""Build (or validate) the Applix showcase index.

Usage:
  python3 tools/build_index.py            # regenerate showcase.json
  python3 tools/build_index.py --check    # exit 1 if showcase.json is out of date

Repository layout:

  showcase.json            <- the index the Applix app downloads
  <slug>/app.html         <- the app
  <slug>/showcase.json    <- metadata (name, description, author, added, resources)
  <slug>/resources/<name> <- optional bundled files

The index is what the app reads:

  {
    "base_url": "https://raw.githubusercontent.com/Konprostart/Applix-showcase/main",
    "apps": [
      {
        "slug": "todo",
        "name": "Todo List",
        "description": "...",
        "author": "Konprostart",
        "bridges": ["load", "save"],
        "resourceCount": 0,
        "resourceSize": 0
      }
    ]
  }

The "bridges" list is derived from the app source itself (every iappyx./applix.
call), so it can never drift away from what the app actually uses.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "showcase.json"
BASE_URL = "https://raw.githubusercontent.com/Konprostart/Applix-showcase/main"

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
BRIDGE_RE = re.compile(r"(?:window\s*\.\s*)?(?:iappyx|applix)\s*\.\s*([A-Za-z_$][\w$]*)")
SKIP_DIRS = {".git", ".github", "tools", "assets"}


def derive_bridges(app_html: str) -> list[str]:
    """Every bridge symbol the app calls, in source order, de-duplicated."""
    found: list[str] = []
    for match in BRIDGE_RE.finditer(app_html):
        name = match.group(1)
        if name not in found:
            found.append(name)
    return sorted(found)


def collect() -> tuple[list[dict], list[str]]:
    apps: list[dict] = []
    problems: list[str] = []
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP_DIRS):
        app_html = folder / "app.html"
        meta_file = folder / "showcase.json"
        if not app_html.exists():
            continue
        slug = folder.name
        if not SLUG_RE.match(slug):
            problems.append(f"{slug}: slug must match {SLUG_RE.pattern}")
        if not meta_file.exists():
            problems.append(f"{slug}: missing showcase.json")
            continue
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{slug}: invalid showcase.json ({exc})")
            continue
        for field in ("name", "description", "author"):
            if not str(meta.get(field, "")).strip():
                problems.append(f"{slug}: showcase.json is missing '{field}'")
        resources = meta.get("resources") or []
        resource_dir = folder / "resources"
        for res in resources:
            res_name = str(res.get("name", ""))
            if not res_name:
                problems.append(f"{slug}: resource entry without a name")
                continue
            if not (resource_dir / res_name).exists():
                problems.append(f"{slug}: declared resource '{res_name}' is not in resources/")
        apps.append({
            "slug": slug,
            "name": str(meta.get("name", slug)),
            "description": str(meta.get("description", "")),
            "author": str(meta.get("author", "")),
            "bridges": derive_bridges(app_html.read_text(encoding="utf-8", errors="replace")),
            "resourceCount": len(resources),
            "resourceSize": sum(int(res.get("size", 0)) for res in resources),
        })
    apps.sort(key=lambda a: (a["name"].lower(), a["slug"]))
    return apps, problems


def build_index() -> str:
    apps, problems = collect()
    if problems:
        print("ERROR: showcase entries are invalid:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        raise SystemExit(1)
    return json.dumps({"base_url": BASE_URL, "apps": apps}, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    check = "--check" in sys.argv[1:]
    expected = build_index()
    current = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    if not check:
        if current != expected:
            INDEX.write_text(expected, encoding="utf-8")
            print(f"updated {INDEX.relative_to(ROOT)}")
        else:
            print("showcase.json is up to date")
        return 0
    if current != expected:
        print("ERROR: showcase.json is out of date - run: python3 tools/build_index.py", file=sys.stderr)
        return 1
    print("showcase.json is up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
