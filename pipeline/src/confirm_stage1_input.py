#!/usr/bin/env python3
"""Confirm Stage 1 source authority, scope, and project-specific rules."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--source-type", required=True, choices=["formal-three-determinations", "official-adjustment", "working-sheet-copy", "other"])
    parser.add_argument("--authority-status", required=True, choices=["verified", "not-verified", "conflicting"])
    parser.add_argument("--effective-date")
    parser.add_argument("--source-notes", required=True)
    parser.add_argument("--scope-mode", required=True, choices=["all", "include-list", "exclude-list"])
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--scope-notes", required=True)
    parser.add_argument("--special-rule", action="append", default=[])
    parser.add_argument("--confirmed-by", required=True)
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    source = json.loads((case_dir / "inputs/responsibilities.json").read_text(encoding="utf-8"))
    valid_ids = {item["responsibility_id"] for item in source["responsibilities"]}
    include, exclude = set(args.include), set(args.exclude)
    unknown = (include | exclude) - valid_ids
    if unknown: raise ValueError("未知职责 ID：" + ",".join(sorted(unknown)))
    if include & exclude: raise ValueError("同一职责不能同时纳入和排除")
    if args.scope_mode == "all" and (include or exclude): raise ValueError("scope-mode=all 时不得提供 include/exclude")
    if args.scope_mode == "include-list" and not include: raise ValueError("include-list 至少需要一个 --include")
    if args.scope_mode == "exclude-list" and not exclude: raise ValueError("exclude-list 至少需要一个 --exclude")
    declaration = {
        "schema_version": "0.1.0", "case_id": source["case_id"], "input_version": source["input_version"],
        "responsibility_source": {"source_type": args.source_type, "authority_status": args.authority_status, "effective_date": args.effective_date, "notes": args.source_notes},
        "scope": {"mode": args.scope_mode, "included_responsibility_ids": sorted(include), "excluded_responsibility_ids": sorted(exclude), "notes": args.scope_notes},
        "special_rules": args.special_rule, "method_guide_required": False,
        "status": "confirmed", "confirmed_by": args.confirmed_by,
        "confirmed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    }
    path = case_dir / "inputs/stage-1-input-declaration.json"
    path.write_text(json.dumps(declaration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
