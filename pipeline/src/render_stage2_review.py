#!/usr/bin/env python3
"""Render Stage 2 assessments as a Gate 2 human-review document."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", default="stage-2/drafts/assessments-baseline-v1.json")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    approved = json.loads((case_dir / manifest["stage_1_approved_artifact"]).read_text(encoding="utf-8"))
    item_map = {i["item_id"]: i for i in approved["items"]}
    draft = json.loads((case_dir / args.draft).read_text(encoding="utf-8"))
    counts = Counter(a["digital_status"] for a in draft["assessments"])
    lines = [
        "# Gate 2｜数字化支撑、流程和证据人工审核", "",
        f"- 案件：`{draft['case_id']}`",
        f"- Stage 1 哈希：`{draft['stage_1_artifact_sha256']}`",
        f"- 生成模式：`{draft.get('generation_mode', 'unknown')}`",
        f"- 事项数：**{len(draft['assessments'])}**",
        f"- 状态分布：{dict(sorted(counts.items()))}", "",
        "> 当前开发基线来自人工核验工作簿。其中叙述性“流程依据”被记录为 inference_notes，不冒充为已经拆分到文档ID、页码和短引文的直接证据。", ""
    ]
    for assessment in draft["assessments"]:
        item = item_map[assessment["item_id"]]
        lines.extend([
            f"## {assessment['item_id']}｜{item['item_text']}", "",
            f"- 数字化状态：**{assessment['digital_status']}**",
            f"- 系统：{'；'.join(s['name'] for s in assessment['systems']) or '无'}",
            f"- 结构化直接证据数：{len(assessment['evidence_refs'])}",
            f"- 人工来源说明：{'；'.join(assessment['human_additions']) or '无'}", "",
            "### 流程与待确认问题", "", assessment["process_narrative"] or "（空）", "",
            "### 待确认清单", ""
        ])
        lines.extend([f"- {value}" for value in assessment["unresolved_questions"]] or ["- 无"])
        lines.extend(["", "### 依据分层", ""])
        lines.extend([f"- 推导/历史叙述：{value}" for value in assessment["inference_notes"]] or ["- 无"])
        lines.extend([
            "", "### 人工审核", "",
            "- [ ] 数字化状态正确",
            "- [ ] 业务范围与事项一致",
            "- [ ] 主体与处室责任未扩大",
            "- [ ] 系统名称及编号来源明确",
            "- [ ] 直接证据、推导和人工补充区分正确",
            "- [ ] 待确认问题完整",
            "- 修改意见：", ""
        ])
    output = case_dir / "reviews" / "gate-2-stage2-review.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
