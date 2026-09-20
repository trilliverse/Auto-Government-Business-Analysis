#!/usr/bin/env python3
"""Validate swimlane logic before Draw.io rendering."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SYSTEM_WORDS = ("系统", "平台", "数据库", "项目库")
TYPES = {"start", "activity", "decision", "result", "end", "placeholder"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", default="stage-3/drafts/swimlane-models-v1.json")
    parser.add_argument("--stage2", help="Approved Stage 2 artifact; defaults to draft pointer or case manifest")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    draft = json.loads((case_dir / args.draft).read_text(encoding="utf-8"))
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    stage2_relative = args.stage2 or draft.get("stage_2_artifact_path") or manifest.get("stage_2_approved_artifact")
    if not stage2_relative:
        raise ValueError("无法确定 Stage 2 上游产物")
    stage2_path = case_dir / stage2_relative
    errors = []
    if draft.get("stage_2_draft_sha256") != sha256(stage2_path): errors.append("Stage 2 上游草稿哈希已失效")
    page_names = []
    for model in draft.get("models", []):
        page_names.append(model.get("page_name"))
        lanes = model.get("lanes", [])
        lane_ids = {lane.get("lane_id") for lane in lanes}
        for lane in lanes:
            if any(word in lane.get("name", "") for word in SYSTEM_WORDS): errors.append(f"{model['item_id']} 将系统画成泳道：{lane['name']}")
        nodes = model.get("nodes", [])
        node_ids = {node.get("node_id") for node in nodes}
        if sum(node.get("type") == "start" for node in nodes) != 1: errors.append(f"{model['item_id']} 必须恰有一个开始节点")
        if sum(node.get("type") == "end" for node in nodes) != 1: errors.append(f"{model['item_id']} 必须恰有一个结束节点")
        if not any(node.get("type") == "result" for node in nodes): errors.append(f"{model['item_id']} 缺少结果节点")
        for node in nodes:
            if node.get("lane_id") not in lane_ids: errors.append(f"{model['item_id']} 节点泳道无效：{node.get('node_id')}")
            if node.get("type") not in TYPES: errors.append(f"{model['item_id']} 节点类型无效")
            if len(node.get("label", "")) > 30: errors.append(f"{model['item_id']} 节点文字过长：{node.get('node_id')}")
        outgoing = {node_id: [] for node_id in node_ids}
        incoming = {node_id: [] for node_id in node_ids}
        for edge in model.get("edges", []):
            if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
                errors.append(f"{model['item_id']} 边引用不存在节点：{edge.get('edge_id')}")
                continue
            outgoing[edge["source"]].append(edge)
            incoming[edge["target"]].append(edge)
        for node in nodes:
            if node["type"] == "decision":
                labels = {edge.get("label") for edge in outgoing[node["node_id"]]}
                if len(outgoing[node["node_id"]]) < 2 or not ({"是", "否"} <= labels or {"通过", "不通过"} <= labels):
                    errors.append(f"{model['item_id']} 判断节点分支不完整：{node['node_id']}")
            if node["type"] != "start" and not incoming[node["node_id"]]: errors.append(f"{model['item_id']} 节点不可达：{node['node_id']}")
        # graph reachability
        start = next((n["node_id"] for n in nodes if n["type"] == "start"), None)
        seen, stack = set(), [start] if start else []
        while stack:
            current = stack.pop()
            if current in seen: continue
            seen.add(current)
            stack.extend(edge["target"] for edge in outgoing.get(current, []))
        if seen != node_ids: errors.append(f"{model['item_id']} 存在无法从开始到达的节点")
    if len(page_names) != len(set(page_names)): errors.append("Draw.io 页签名重复")
    report = {"valid": not errors, "model_count": len(draft.get("models", [])), "page_count": len(page_names), "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
