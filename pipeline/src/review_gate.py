#!/usr/bin/env python3
"""Record a Gate 0 human decision or advance an approved case to Stage 1."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from validate_case import validate_case


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_decision(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir).resolve()
    manifest_path = case_dir / "case.json"
    source_path = case_dir / "inputs" / "responsibilities.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if manifest.get("stage") != "gate-0":
        raise ValueError("只有处于 gate-0 的案件可以记录 Gate 0 决定")
    declaration_path = case_dir / "inputs" / "stage-1-input-declaration.json"
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    if declaration.get("status") != "confirmed":
        raise ValueError("Stage 1 输入声明尚未由人工确认，不得记录 Gate 0 决定")
    if declaration.get("input_version") != source.get("input_version"):
        raise ValueError("Stage 1 输入声明版本已失效")
    decision = {
        "gate": "gate-0",
        "decision": args.decision,
        "reviewed_input_version": source["input_version"],
        "reviewed_responsibilities_sha256": source["source"]["sha256"],
        "reviewer": args.reviewer,
        "reviewed_at": utc_now(),
        "comments": args.comments or "",
        "input_declaration": "inputs/stage-1-input-declaration.json",
        "input_declaration_sha256": sha256(declaration_path),
        "input_declaration_confirmed_at": declaration.get("confirmed_at"),
    }
    decision_path = case_dir / "reviews" / "gate-0-decision.json"
    write_json(decision_path, decision)
    errors, warnings = validate_case(case_dir)
    if errors:
        decision_path.unlink(missing_ok=True)
        raise ValueError("审核决定未通过校验：" + "；".join(errors))
    print(json.dumps({"decision_path": str(decision_path), "decision": args.decision, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0


def advance(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir).resolve()
    manifest_path = case_dir / "case.json"
    errors, _ = validate_case(case_dir)
    if errors:
        raise ValueError("案件校验失败：" + "；".join(errors))
    decision_path = case_dir / "reviews" / "gate-0-decision.json"
    if not decision_path.exists():
        raise ValueError("尚无 Gate 0 决定，不得进入 Stage 1")
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    if decision.get("decision") != "approved":
        raise ValueError(f"Gate 0 决定为 {decision.get('decision')}，不得进入 Stage 1")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["stage"] = "stage-1"
    manifest["status"] = "drafting"
    manifest["updated_at"] = utc_now()
    manifest["gate_0_approval"] = "reviews/gate-0-decision.json"
    write_json(manifest_path, manifest)
    print(json.dumps({"case_dir": str(case_dir), "stage": "stage-1", "status": "drafting"}, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    decide = sub.add_parser("decide")
    decide.add_argument("case_dir")
    decide.add_argument("--decision", required=True, choices=["approved", "request_changes", "rejected"])
    decide.add_argument("--reviewer", required=True)
    decide.add_argument("--comments")
    advance_parser = sub.add_parser("advance")
    advance_parser.add_argument("case_dir")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        raise SystemExit(record_decision(args) if args.command == "decide" else advance(args))
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
