#!/usr/bin/env python3
"""Merge verified direct evidence into a copy of the Stage 2 baseline for pilot review."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--baseline", default="stage-2/drafts/assessments-baseline-v1.json")
    parser.add_argument("--evidence", default="stage-2/drafts/verified-evidence-pilot.json")
    args = parser.parse_args()
    case = Path(args.case_dir).resolve()
    baseline = json.loads((case / args.baseline).read_text(encoding="utf-8"))
    evidence = json.loads((case / args.evidence).read_text(encoding="utf-8"))
    refs = {item["item_id"]: item["evidence_refs"] for item in evidence["items"]}
    merged_count = 0
    for assessment in baseline["assessments"]:
        if assessment["item_id"] in refs:
            assessment["evidence_refs"] = refs[assessment["item_id"]]
            assessment["human_additions"].append("已补入试点直接证据；数字化状态和完整流程仍沿用人工Gold，需在独立分析中复核。")
            merged_count += 1
    baseline["generation_mode"] = "human-reviewed-reference-plus-verified-evidence-pilot"
    baseline["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    output = case / "stage-2/drafts/assessments-pilot-v1.json"
    output.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "merged_items": merged_count}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
