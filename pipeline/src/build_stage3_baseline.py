#!/usr/bin/env python3
"""Build conservative reviewable swimlane logic drafts from Stage 2 baseline text."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SYSTEM_WORDS = ("系统", "平台", "数据库", "项目库")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def split_sentences(text: str) -> list[str]:
    flow = text.split("待确认", 1)[0]
    flow = re.sub(r"^流程(?:线索)?：", "", flow.strip())
    return [part.strip() for part in re.split(r"[。；\n]+", flow) if part.strip()]


def choose_lane(sentence: str) -> str:
    if any(key in sentence for key in ("养护技术服务处", "本处室")): return "L3"
    if any(key in sentence for key in ("厅公路管理处", "省级", "省厅", "上级", "厅级")): return "L2"
    return "L1"


def short_label(sentence: str) -> str:
    value = re.sub(r"^(市县|基层|申请企业|填报单位|省级相关单位|养护技术服务处|本处室)[^，,]{0,16}[，,]?", "", sentence)
    value = value.strip(" ，,")
    return value[:24] + ("…" if len(value) > 24 else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--stage2", help="Approved Stage 2 artifact; defaults to case manifest pointer")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    if manifest.get("stage") != "gate-2" or manifest.get("status") != "approved":
        raise ValueError("只有 Gate 2 已批准案件可以生成 Stage 3 草稿")
    stage2_relative = args.stage2 or manifest.get("stage_2_approved_artifact")
    if not stage2_relative:
        raise ValueError("case.json 缺少 stage_2_approved_artifact")
    stage2_path = case_dir / stage2_relative
    stage2 = json.loads(stage2_path.read_text(encoding="utf-8"))
    approved = json.loads((case_dir / manifest["stage_1_approved_artifact"]).read_text(encoding="utf-8"))
    item_map = {i["item_id"]: i for i in approved["items"]}
    models = []
    row = 2
    for assessment in stage2["assessments"]:
        if assessment["digital_status"] != "有":
            row += 1
            continue
        item = item_map[assessment["item_id"]]
        lanes = [
            {"lane_id": "L1", "name": "发起/办理单位"},
            {"lane_id": "L2", "name": "省级主责部门"},
            {"lane_id": "L3", "name": "养护技术服务处（具体节点待核验）"}
        ]
        nodes = [{"node_id": "N1", "lane_id": "L1", "type": "start", "label": "开始", "evidence_status": "inferred"}]
        for sentence in split_sentences(assessment["process_narrative"]):
            nodes.append({
                "node_id": f"N{len(nodes)+1}", "lane_id": choose_lane(sentence), "type": "activity",
                "label": short_label(sentence), "evidence_status": "human"
            })
        nodes.append({"node_id": f"N{len(nodes)+1}", "lane_id": "L2", "type": "result", "label": "形成业务结果", "evidence_status": "unresolved"})
        nodes.append({"node_id": f"N{len(nodes)+1}", "lane_id": "L2", "type": "end", "label": "结束", "evidence_status": "inferred"})
        edges = [{"edge_id": f"E{i}", "source": nodes[i-1]["node_id"], "target": nodes[i]["node_id"], "label": ""} for i in range(1, len(nodes))]
        models.append({
            "item_id": assessment["item_id"], "item_text": item["item_text"],
            "page_name": f"行{row}-{item['item_text'][:18]}", "lanes": lanes,
            "nodes": nodes, "edges": edges,
            "system_notes": [s["name"] for s in assessment["systems"]],
            "unresolved_questions": assessment["unresolved_questions"], "status": "draft"
        })
        row += 1
    result = {
        "schema_version": "0.1.0", "case_id": manifest["case_id"],
        "stage_2_draft_sha256": sha256(stage2_path),
        "stage_2_artifact_path": stage2_relative.replace("\\", "/"),
        "generation_mode": "conservative-baseline-from-human-reviewed-narrative",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "models": models
    }
    output = case_dir / "stage-3" / "drafts" / "swimlane-models-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "model_count": len(models)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
