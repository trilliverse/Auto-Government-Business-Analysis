#!/usr/bin/env python3
"""Render a Stage 1 JSON draft into a human review Markdown document."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", default="stage-1/drafts/items-v1.json")
    parser.add_argument("--output", default="reviews/gate-1-stage1-review.md")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    source = json.loads((case_dir / "inputs" / "responsibilities.json").read_text(encoding="utf-8"))
    draft = json.loads((case_dir / args.draft).read_text(encoding="utf-8"))
    source_map = {item["responsibility_id"]: item for item in source["responsibilities"]}
    included = [item for item in draft["items"] if item["disposition"] == "include"]
    counts = Counter(item["category"] for item in included)
    lines = [
        "# Gate 1｜职责拆解与分类人工审核",
        "",
        f"- 案件：`{draft['case_id']}`",
        f"- 输入版本：`{draft['input_version']}`",
        f"- 输入 SHA-256：`{draft['input_sha256']}`",
        f"- 生成模式：`{draft.get('generation_mode', 'unknown')}`",
        f"- 草稿总项数：**{len(draft['items'])}**",
        f"- 拟纳入：**{len(included)}**",
        f"- 拟排除：**{len(draft['items']) - len(included)}**",
        f"- 分类统计：{dict(sorted(counts.items()))}",
        "",
        "> 本稿是开发回归基线，不代表业务人员已经完成 Gate 1 审批。实际案件需逐项复核。",
        "",
        "## 审核动作",
        "",
        "每项可选择：通过、修改、拆分、合并、改类、排除、退回。审核需确认来源、完整动作前缀、业务对象、责任边界和分类。",
        "",
    ]
    current_source = None
    for item in draft["items"]:
        if item["source_responsibility_id"] != current_source:
            current_source = item["source_responsibility_id"]
            source_item = source_map[current_source]
            lines.extend([
                f"## {current_source}｜来源职责 {source_item['sequence']}", "",
                source_item["source_text"], "",
            ])
        lines.extend([
            f"### {item['item_id']}｜{item['item_text']}", "",
            f"- 分类：**{item['category']}**",
            f"- 动作：`{item['action']}`",
            f"- 对象：{item['object']}",
            f"- 处置建议：`{item['disposition']}`",
            f"- 拆解说明：{item['derivation_note']}",
            f"- 问题：{'；'.join(item['issues']) if item['issues'] else '无'}",
            "- [ ] 来源与边界正确",
            "- [ ] 事项表达正确",
            "- [ ] 分类正确",
            "- 人工修改/意见：",
            "",
        ])
    lines.extend([
        "## Gate 1 放行条件", "",
        "所有条目均完成人工处理；拟排除项有明确理由；批准绑定本草稿版本及文件哈希；批准后冻结到 `stage-1/approved/`，不得覆盖。", ""
    ])
    output = case_dir / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
