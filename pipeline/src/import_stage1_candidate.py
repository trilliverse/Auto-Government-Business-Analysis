#!/usr/bin/env python3
"""Normalize a model-produced {items:[...]} response into a Stage 1 draft envelope."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="stage-1/drafts/model-candidate-v1.json")
    parser.add_argument("--model-label", default="independent-subagent")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    source = json.loads((case_dir / "inputs" / "responsibilities.json").read_text(encoding="utf-8"))
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    items = raw.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("模型输出必须包含非空 items 数组")
    normalized = []
    for index, item in enumerate(items, start=1):
        normalized.append({
            "item_id": f"M{index:03d}",
            "source_responsibility_id": item["source_responsibility_id"],
            "source_sequence": item["source_sequence"],
            "item_sequence": item["item_sequence"],
            "item_text": item["item_text"],
            "action": item["action"],
            "object": item["object"],
            "category": item["category"],
            "derivation_note": f"由 {args.model_label} 仅依据原始职责和 Skill 规则生成。",
            "issues": item.get("issues", []),
            "disposition": item.get("disposition", "include"),
            "status": "draft"
        })
    envelope = {
        "schema_version": "0.1.0",
        "case_id": manifest["case_id"],
        "input_version": source["input_version"],
        "input_sha256": source["source"]["sha256"],
        "skill": {"name": "responsibility-decomposition", "version": "0.1.0"},
        "status": "awaiting-review",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "generation_mode": args.model_label,
        "items": normalized
    }
    output = case_dir / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
