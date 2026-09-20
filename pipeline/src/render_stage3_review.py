#!/usr/bin/env python3
"""Render swimlane logic models for Gate 3 review before drawing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", default="stage-3/drafts/swimlane-models-v1.json")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    draft = json.loads((case_dir / args.draft).read_text(encoding="utf-8"))
    lines = [
        "# Gate 3｜泳道图逻辑模型人工审核", "",
        f"- Stage 2 草稿哈希：`{draft['stage_2_draft_sha256']}`",
        f"- 模型数量：**{len(draft['models'])}**", "",
        "> 先审核业务逻辑，再渲染 Draw.io。当前保守基线不会凭空补充判断和退回分支；缺失分支保留为待确认问题。", ""
    ]
    for model in draft["models"]:
        lane_map = {lane["lane_id"]: lane["name"] for lane in model["lanes"]}
        lines.extend([f"## {model['page_name']}", "", f"业务事项：**{model['item_text']}**", "", "### 泳道", ""])
        lines.extend([f"- `{lane['lane_id']}` {lane['name']}" for lane in model["lanes"]])
        lines.extend(["", "### 节点", ""])
        for node in model["nodes"]:
            lines.append(f"- `{node['node_id']}` [{node['type']}] {lane_map[node['lane_id']]}：{node['label']}（{node['evidence_status']}）")
        lines.extend(["", "### 连线", ""])
        lines.extend([f"- `{edge['source']} → {edge['target']}` {edge['label']}" for edge in model["edges"]])
        lines.extend(["", "### 系统支撑备注（不是泳道）", ""])
        lines.extend([f"- {value}" for value in model["system_notes"]] or ["- 无"])
        lines.extend(["", "### 待确认问题", ""])
        lines.extend([f"- {value}" for value in model["unresolved_questions"]] or ["- 无"])
        lines.extend([
            "", "### 审核", "",
            "- [ ] 泳道均为业务主体",
            "- [ ] 主体分工正确",
            "- [ ] 节点顺序正确",
            "- [ ] 判断和退回路径完整或已明确待确认",
            "- [ ] 最终成果正确",
            "- [ ] 系统只作为节点说明或备注",
            "- 修改意见：", ""
        ])
    output = case_dir / "reviews" / "gate-3-swimlane-logic-review.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
