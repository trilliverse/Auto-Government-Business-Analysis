#!/usr/bin/env python3
"""Validate Stage 2 assessments against the approved Stage 1 artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

STATUSES = {"有", "无", "待确认", "不纳入本次梳理范畴"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def validate(case_dir: Path, draft_path: Path) -> tuple[list[str], dict]:
    errors = []
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    approved_path = case_dir / manifest["stage_1_approved_artifact"]
    approved = json.loads(approved_path.read_text(encoding="utf-8"))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    current_hash = sha256(approved_path)
    if draft.get("case_id") != manifest.get("case_id"): errors.append("case_id 不匹配")
    if draft.get("stage_1_artifact_sha256") != current_hash: errors.append("上游 Stage 1 哈希已失效")
    expected_ids = [i["item_id"] for i in approved["items"] if i["disposition"] == "include" and i["status"] != "rejected"]
    assessments = draft.get("assessments", [])
    actual_ids = [a.get("item_id") for a in assessments]
    if actual_ids != expected_ids: errors.append("assessment item_id 必须完整且保持 Stage 1 顺序")
    for index, item in enumerate(assessments, start=1):
        if item.get("digital_status") not in STATUSES: errors.append(f"第 {index} 项数字化状态无效")
        for field in ["process_narrative", "unresolved_questions", "systems", "evidence_refs", "inference_notes", "human_additions", "status"]:
            if field not in item: errors.append(f"第 {index} 项缺少 {field}")
        if item.get("digital_status") == "待确认" and not item.get("unresolved_questions"):
            errors.append(f"第 {index} 项为待确认但没有 unresolved_questions")
        if item.get("digital_status") == "无":
            has_direct = any(ref.get("strength") == "direct" for ref in item.get("evidence_refs", []))
            has_human = bool(item.get("human_additions"))
            if not (has_direct or has_human):
                errors.append(f"第 {index} 项判无但没有正面直接证据或人工意见")
        for ref in item.get("evidence_refs", []):
            if not all(ref.get(key) for key in ["evidence_id", "document_id", "locator", "quote", "supports", "strength"]):
                errors.append(f"第 {index} 项存在不完整证据引用")
            if ref.get("strength") == "direct" and not ref.get("document_sha256"):
                errors.append(f"第 {index} 项直接证据缺少 document_sha256")
        # A baseline or human addition may have no structured direct evidence;
        # it must be explicitly labeled rather than silently presented as proof.
        if not item.get("evidence_refs") and not item.get("human_additions") and item.get("digital_status") != "待确认":
            errors.append(f"第 {index} 项无直接证据且未标明人工来源")
    report = {
        "assessment_count": len(assessments),
        "digital_status_counts": dict(sorted(Counter(a.get("digital_status") for a in assessments).items())),
        "items_with_unresolved": sum(bool(a.get("unresolved_questions")) for a in assessments),
        "items_with_structured_evidence": sum(bool(a.get("evidence_refs")) for a in assessments),
        "items_with_human_additions": sum(bool(a.get("human_additions")) for a in assessments)
    }
    return errors, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", default="stage-2/drafts/assessments-baseline-v1.json")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    errors, report = validate(case_dir, case_dir / args.draft)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    for error in errors: print("ERROR:", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
