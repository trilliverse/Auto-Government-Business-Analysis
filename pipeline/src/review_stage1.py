#!/usr/bin/env python3
"""Record Gate 1 decisions and freeze an approved Stage 1 draft immutably."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from validate_stage1 import validate


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def decide(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir).resolve()
    draft_path = case_dir / args.draft
    errors, report = validate(case_dir, draft_path, None)
    if errors:
        raise ValueError("Stage 1 草稿校验失败：" + "；".join(errors))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if draft.get("status") != "awaiting-review":
        raise ValueError("只有 awaiting-review 草稿可以记录 Gate 1 决定")
    decision = {
        "gate": "gate-1",
        "decision": args.decision,
        "draft_path": args.draft.replace("\\", "/"),
        "reviewed_draft_sha256": sha256(draft_path),
        "input_version": draft["input_version"],
        "input_sha256": draft["input_sha256"],
        "reviewer": args.reviewer,
        "reviewed_at": now(),
        "comments": args.comments or "",
        "summary": report,
    }
    output = case_dir / "reviews" / "gate-1-decision.json"
    write_json(output, decision)
    print(json.dumps({"decision": args.decision, "decision_path": str(output), "draft_sha256": decision["reviewed_draft_sha256"]}, ensure_ascii=False, indent=2))
    return 0


def freeze(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir).resolve()
    manifest_path = case_dir / "case.json"
    decision_path = case_dir / "reviews" / "gate-1-decision.json"
    if not decision_path.exists():
        raise ValueError("尚无 Gate 1 决定")
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    if decision.get("decision") != "approved":
        raise ValueError(f"Gate 1 决定为 {decision.get('decision')}，不得冻结")
    draft_path = case_dir / decision["draft_path"]
    if sha256(draft_path) != decision.get("reviewed_draft_sha256"):
        raise ValueError("草稿在审核后已变化，Gate 1 决定失效")
    errors, report = validate(case_dir, draft_path, None)
    if errors:
        raise ValueError("Stage 1 草稿校验失败：" + "；".join(errors))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    if draft["input_version"] != decision.get("input_version") or draft["input_sha256"] != decision.get("input_sha256"):
        raise ValueError("Gate 1 决定绑定的输入已失效")

    approved_dir = case_dir / "stage-1" / "approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    approved_path = approved_dir / f"items-{decision['reviewed_draft_sha256'][:12]}.json"
    if approved_path.exists():
        if sha256(approved_path) != decision["reviewed_draft_sha256"]:
            raise ValueError("不可变批准路径已存在不同内容")
    else:
        shutil.copyfile(draft_path, approved_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["stage"] = "gate-1"
    manifest["status"] = "approved"
    manifest["stage_1_approval"] = "reviews/gate-1-decision.json"
    manifest["stage_1_approved_artifact"] = approved_path.relative_to(case_dir).as_posix()
    manifest["updated_at"] = now()
    write_json(manifest_path, manifest)
    print(json.dumps({"approved_artifact": str(approved_path), "sha256": sha256(approved_path), "summary": report}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("decide")
    d.add_argument("case_dir")
    d.add_argument("--draft", default="stage-1/drafts/items-v1.json")
    d.add_argument("--decision", choices=["approved", "request_changes", "rejected"], required=True)
    d.add_argument("--reviewer", required=True)
    d.add_argument("--comments")
    f = sub.add_parser("freeze")
    f.add_argument("case_dir")
    args = parser.parse_args()
    try:
        return decide(args) if args.command == "decide" else freeze(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
