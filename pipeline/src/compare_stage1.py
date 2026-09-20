#!/usr/bin/env python3
"""Compare a Stage 1 candidate against the reviewed reference and render a report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    reference = json.loads(Path(args.reference).read_text(encoding="utf-8"))
    candidate_items = candidate.get("items", [])
    reference_items = reference.get("items", [])

    matched_candidate: set[int] = set()
    rows = []
    exact_text = 0
    exact_pair = 0
    for ref in reference_items:
        eligible = [
            (index, item) for index, item in enumerate(candidate_items)
            if index not in matched_candidate and item.get("source_sequence") == ref.get("source_sequence")
        ]
        if not eligible:
            rows.append({"reference": ref, "candidate": None, "score": 0.0, "text_match": False, "category_match": False})
            continue
        index, item = max(eligible, key=lambda pair: similarity(ref["item_text"], pair[1].get("item_text", "")))
        score = similarity(ref["item_text"], item.get("item_text", ""))
        matched_candidate.add(index)
        text_match = ref["item_text"] == item.get("item_text")
        category_match = ref["category"] == item.get("category")
        exact_text += int(text_match)
        exact_pair += int(text_match and category_match)
        rows.append({"reference": ref, "candidate": item, "score": score, "text_match": text_match, "category_match": category_match})

    extras = [item for index, item in enumerate(candidate_items) if index not in matched_candidate]
    category_errors = [row for row in rows if row["candidate"] and not row["category_match"]]
    text_diffs = [row for row in rows if row["candidate"] and not row["text_match"]]
    missing = [row for row in rows if row["candidate"] is None]
    report = {
        "reference_count": len(reference_items),
        "candidate_count": len(candidate_items),
        "exact_text_matches": exact_text,
        "exact_text_and_category_matches": exact_pair,
        "category_mismatches": len(category_errors),
        "text_differences": len(text_diffs),
        "missing_reference_items": len(missing),
        "extra_candidate_items": len(extras),
        "candidate_category_counts": dict(sorted(Counter(item.get("category") for item in candidate_items).items())),
    }

    lines = [
        "# Stage 1 候选结果与人工 Gold 差异报告", "",
        "## 汇总", "",
        "```json", json.dumps(report, ensure_ascii=False, indent=2), "```", "",
        "说明：这是开发评估，不代表 Gold 是对所有未来案件都适用的业务口径。文本相似匹配只用于定位差异。", "",
        "## 差异明细", ""
    ]
    for row in rows:
        if row["text_match"] and row["category_match"]:
            continue
        ref = row["reference"]
        cand = row["candidate"]
        lines.extend([
            f"### Gold {ref['reference_item_id']}｜来源职责 {ref['source_sequence']}", "",
            f"- Gold：`{ref['item_text']}`｜{ref['category']}",
            f"- 候选：`{cand.get('item_text') if cand else '缺失'}`｜{cand.get('category') if cand else '缺失'}",
            f"- 文本相似度：{row['score']:.3f}",
            f"- 差异类型：{'文本 ' if not row['text_match'] else ''}{'分类' if not row['category_match'] else ''}", ""
        ])
    if extras:
        lines.extend(["## 候选额外事项", ""])
        for item in extras:
            lines.append(f"- 来源 {item.get('source_sequence')}：`{item.get('item_text')}`｜{item.get('category')}")
        lines.append("")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
