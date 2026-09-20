#!/usr/bin/env python3
"""Build a Stage 1 development baseline from the human-reviewed reference.

This is a regression fixture adapter, not the production AI decomposition path.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ACTION_PREFIXES = [
    "承担指导", "参与拟订", "贯彻执行", "督促落实", "承担编制", "承担", "参与", "承办",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def infer_action(text: str) -> str:
    for prefix in ACTION_PREFIXES:
        if text.startswith(prefix):
            return prefix
    match = re.match(r"^[\u4e00-\u9fff]{2,6}", text)
    return match.group(0) if match else "待人工确认"


def infer_object(text: str, action: str) -> str:
    value = text[len(action):].strip() if text.startswith(action) else text.strip()
    return value or "待人工确认"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--reference", required=True)
    parser.add_argument("--output", default="stage-1/drafts/items-v1.json")
    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    source = json.loads((case_dir / "inputs" / "responsibilities.json").read_text(encoding="utf-8"))
    decision = json.loads((case_dir / "reviews" / "gate-0-decision.json").read_text(encoding="utf-8"))
    reference = json.loads(Path(args.reference).resolve().read_text(encoding="utf-8"))
    if manifest.get("stage") != "stage-1" or manifest.get("status") != "drafting":
        raise ValueError("案件必须已通过 Gate 0 并处于 stage-1/drafting")
    if decision.get("decision") != "approved":
        raise ValueError("Gate 0 未批准")
    if decision.get("reviewed_input_version") != source.get("input_version"):
        raise ValueError("Gate 0 批准的输入版本已失效")
    if decision.get("reviewed_responsibilities_sha256") != source.get("source", {}).get("sha256"):
        raise ValueError("Gate 0 批准的输入哈希已失效")

    source_by_text = {item["source_text"].rstrip("；。"): item for item in source["responsibilities"]}
    items = []
    unmatched = []
    for ref in reference["items"]:
        normalized = ref["source_responsibility_text"].rstrip("；。")
        source_item = source_by_text.get(normalized)
        if source_item is None:
            unmatched.append(ref["source_responsibility_text"])
            continue
        action = infer_action(ref["item_text"])
        items.append({
            "item_id": f"I{len(items)+1:03d}",
            "source_responsibility_id": source_item["responsibility_id"],
            "source_sequence": source_item["sequence"],
            "item_sequence": ref["item_sequence"],
            "item_text": ref["item_text"],
            "action": action,
            "object": infer_object(ref["item_text"], action),
            "category": ref["category"],
            "derivation_note": "开发基线：由人工核验结果映射，用于回归测试；生产执行必须由拆解 Skill 生成独立草稿。",
            "issues": [],
            "disposition": "include",
            "status": "draft"
        })
    if unmatched:
        raise ValueError("参考集职责无法映射原始职责：" + "；".join(sorted(set(unmatched))))

    # The source-only fallback responsibility remains auditable but is proposed for exclusion.
    represented = {item["source_responsibility_id"] for item in items}
    for responsibility in source["responsibilities"]:
        if responsibility["responsibility_id"] not in represented:
            text = responsibility["source_text"]
            stripped = re.sub(r"^（[^）]+）", "", text).rstrip("；。")
            action = infer_action(stripped)
            items.append({
                "item_id": f"I{len(items)+1:03d}",
                "source_responsibility_id": responsibility["responsibility_id"],
                "source_sequence": responsibility["sequence"],
                "item_sequence": 1,
                "item_text": stripped,
                "action": action,
                "object": infer_object(stripped, action),
                "category": "负责",
                "derivation_note": "原始职责完整性占位；黄金人工成果未纳入正式事项。",
                "issues": ["开发基线按黄金人工结果建议从正式清单排除；实际案件须由业务人员确认。"],
                "disposition": "exclude-proposed",
                "status": "draft"
            })

    items.sort(key=lambda item: (item["source_sequence"], item["item_sequence"]))
    for index, item in enumerate(items, start=1):
        item["item_id"] = f"I{index:03d}"
    draft = {
        "schema_version": "0.1.0",
        "case_id": manifest["case_id"],
        "input_version": source["input_version"],
        "input_sha256": source["source"]["sha256"],
        "skill": {"name": "responsibility-decomposition", "version": "0.1.0-baseline-adapter"},
        "status": "awaiting-review",
        "generated_at": utc_now(),
        "generation_mode": "human-reviewed-reference-baseline",
        "items": items
    }
    output_path = case_dir / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "total_items": len(items),
        "included_items": sum(i["disposition"] == "include" for i in items),
        "exclude_proposed": sum(i["disposition"] == "exclude-proposed" for i in items)
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
