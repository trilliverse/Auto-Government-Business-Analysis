#!/usr/bin/env python3
"""Validate Stage 1 items and optionally compare included items with a reference."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

CATEGORIES = {"督导", "组织", "负责", "参与", "待确认"}
DISPOSITIONS = {"include", "exclude-proposed"}
STATUSES = {"draft", "reviewed", "approved", "rejected"}
REQUIRED_ITEM_FIELDS = {
    "item_id", "source_responsibility_id", "source_sequence", "item_sequence", "item_text",
    "action", "object", "category", "derivation_note", "issues", "disposition", "status"
}


def validate(case_dir: Path, draft_path: Path, reference_path: Path | None) -> tuple[list[str], dict]:
    errors: list[str] = []
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    source = json.loads((case_dir / "inputs" / "responsibilities.json").read_text(encoding="utf-8"))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if manifest.get("stage") != "stage-1": errors.append("案件不在 stage-1")
    if draft.get("case_id") != manifest.get("case_id"): errors.append("draft case_id 不匹配")
    if draft.get("input_version") != source.get("input_version"): errors.append("draft input_version 已失效")
    if draft.get("input_sha256") != source.get("source", {}).get("sha256"): errors.append("draft input_sha256 已失效")
    if draft.get("status") not in {"draft", "awaiting-review", "approved"}: errors.append("draft status 无效")

    source_map = {item["responsibility_id"]: item for item in source["responsibilities"]}
    items = draft.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items 必须是非空数组")
        items = []
    ids = []
    sequence_by_source = defaultdict(list)
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"第 {index} 项不是对象")
            continue
        missing = REQUIRED_ITEM_FIELDS - set(item)
        if missing: errors.append(f"第 {index} 项缺字段：{','.join(sorted(missing))}")
        ids.append(item.get("item_id"))
        source_id = item.get("source_responsibility_id")
        if source_id not in source_map:
            errors.append(f"第 {index} 项来源职责不存在：{source_id}")
        else:
            if item.get("source_sequence") != source_map[source_id]["sequence"]:
                errors.append(f"第 {index} 项 source_sequence 与来源不一致")
        sequence_by_source[source_id].append(item.get("item_sequence"))
        if item.get("category") not in CATEGORIES: errors.append(f"第 {index} 项 category 无效")
        if item.get("disposition") not in DISPOSITIONS: errors.append(f"第 {index} 项 disposition 无效")
        if item.get("status") not in STATUSES: errors.append(f"第 {index} 项 status 无效")
        if not isinstance(item.get("issues"), list): errors.append(f"第 {index} 项 issues 必须是数组")
        for field in ["item_text", "action", "object"]:
            if not isinstance(item.get(field), str) or not item.get(field).strip(): errors.append(f"第 {index} 项 {field} 为空")
    if len(ids) != len(set(ids)): errors.append("item_id 重复")
    for source_id, values in sequence_by_source.items():
        if values != list(range(1, len(values) + 1)):
            errors.append(f"{source_id} 的 item_sequence 必须从 1 连续递增")
    missing_sources = set(source_map) - set(sequence_by_source)
    if missing_sources: errors.append("以下原始职责没有任何事项或排除占位：" + ",".join(sorted(missing_sources)))

    included = [item for item in items if item.get("disposition") == "include"]
    report = {
        "total_items": len(items),
        "included_items": len(included),
        "exclude_proposed": len(items) - len(included),
        "category_counts": dict(sorted(Counter(item.get("category") for item in included).items()))
    }
    if reference_path:
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        actual_pairs = [(item["item_text"], item["category"]) for item in included]
        expected_pairs = [(item["item_text"], item["category"]) for item in reference["items"]]
        report["reference_item_count"] = len(expected_pairs)
        report["exact_reference_match"] = actual_pairs == expected_pairs
        if actual_pairs != expected_pairs:
            errors.append("纳入事项与黄金参考集的文本/分类/顺序不完全一致")
    return errors, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", default="stage-1/drafts/items-v1.json")
    parser.add_argument("--reference")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    draft_path = case_dir / args.draft
    reference_path = Path(args.reference).resolve() if args.reference else None
    try:
        errors, report = validate(case_dir, draft_path, reference_path)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    for error in errors: print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
