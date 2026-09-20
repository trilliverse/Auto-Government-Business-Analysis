#!/usr/bin/env python3
"""Render Stage 2A document catalog and evidence candidates for human review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    index = json.loads((case_dir / "stage-2/index/document-index.json").read_text(encoding="utf-8"))
    candidates = json.loads((case_dir / "stage-2/index/evidence-candidates.json").read_text(encoding="utf-8"))
    lines = [
        "# Stage 2A｜文档目录与证据候选人工审核", "",
        f"- 文档数：**{len(index['documents'])}**",
        f"- 文本块数：**{len(index['chunks'])}**",
        f"- 事项数：**{candidates['statistics']['item_count']}**",
        f"- 有候选事项：**{candidates['statistics']['items_with_candidates']}**",
        f"- 候选总数：**{candidates['statistics']['candidate_count']}**", "",
        "> 候选仅由关键词和定位信息生成，不证明系统实际支撑事项，也不证明目标处室拥有操作或审批权限。", "",
        "## 文档目录", ""
    ]
    for doc in index["documents"]:
        lines.extend([
            f"### {doc['document_id']}｜{doc['filename']}", "",
            f"- SHA-256：`{doc['sha256']}`",
            f"- 媒体类型：`{doc['media_type']}`",
            f"- 提取状态：`{doc['extraction_status']}`；文本块：{doc['chunk_count']}",
            f"- 范围说明：{doc['scope_note']}",
            f"- 路径：`{doc['path']}`", ""
        ])
    lines.extend(["## 逐事项证据候选", ""])
    for item in candidates["items"]:
        lines.extend([f"### {item['item_id']}｜{item['item_text']}", "", f"检索词：{'、'.join(item['query_terms']) or '无'}", ""])
        if not item["candidates"]:
            lines.extend(["- 无候选。需要补充资料或人工检索。", ""])
            continue
        for candidate in item["candidates"]:
            lines.extend([
                f"#### {candidate['candidate_id']}｜{candidate['filename']}｜{candidate['locator']}", "",
                f"- 材料角色：`{candidate.get('evidence_role', 'unknown')}`；匹配词：{'、'.join(candidate['matched_terms'])}；分数：{candidate['score']}",
                f"- 摘录：{candidate['quote']}",
                "- [ ] 保留为证据候选",
                "- [ ] 仅作背景线索",
                "- [ ] 删除错配候选",
                "- 审核意见：", ""
            ])
    output = case_dir / "reviews" / "stage-2a-evidence-candidates-review.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
