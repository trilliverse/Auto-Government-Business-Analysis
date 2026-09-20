#!/usr/bin/env python3
"""Validate a Stage 0 case and an optional Gate 0 decision."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_DECISIONS = {"approved", "request_changes", "rejected"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"缺少文件：{path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"JSON 无效：{path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"JSON 顶层必须是对象：{path}")
        return {}
    return value


def validate_case(case_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = load_json(case_dir / "case.json", errors)
    source = load_json(case_dir / "inputs" / "responsibilities.json", errors)
    if errors:
        return errors, warnings

    required_manifest = ["schema_version", "case_id", "organization", "stage", "status", "input_version", "inputs"]
    for key in required_manifest:
        require(key in manifest, f"case.json 缺少字段：{key}", errors)
    require(manifest.get("schema_version") == "0.1.0", "case.json schema_version 必须为 0.1.0", errors)
    allowed_stages = {"gate-0", "stage-1", "gate-1", "stage-2", "gate-2", "stage-3", "gate-3", "gate-4", "completed"}
    require(manifest.get("stage") in allowed_stages, "case.json stage 无效", errors)
    if manifest.get("stage") == "gate-0":
        require(manifest.get("status") == "awaiting-input-review", "Gate 0 未放行前 status 应为 awaiting-input-review", errors)
    elif manifest.get("stage") == "stage-1":
        require(manifest.get("status") == "drafting", "Stage 1 初始状态应为 drafting", errors)
    require(manifest.get("case_id") == source.get("case_id"), "case_id 在清单和输入中不一致", errors)
    require(manifest.get("input_version") == source.get("input_version"), "input_version 在清单和输入中不一致", errors)
    require(manifest.get("organization") == source.get("organization"), "organization 在清单和输入中不一致", errors)

    source_meta = source.get("source") if isinstance(source.get("source"), dict) else {}
    source_path = Path(str(source_meta.get("path", "")))
    require(source_path.is_file(), f"来源文件不存在：{source_path}", errors)
    if source_path.is_file():
        actual_hash = sha256_file(source_path)
        require(actual_hash == source_meta.get("sha256"), "来源文件 SHA-256 与提取记录不一致，Gate 0 草稿已失效", errors)

    responsibilities = source.get("responsibilities")
    require(isinstance(responsibilities, list) and bool(responsibilities), "responsibilities 必须是非空数组", errors)
    if isinstance(responsibilities, list):
        ids: list[str] = []
        sequences: list[int] = []
        for index, item in enumerate(responsibilities, start=1):
            if not isinstance(item, dict):
                errors.append(f"第 {index} 条职责不是对象")
                continue
            for key in ["responsibility_id", "sequence", "source_text", "source_locator"]:
                require(key in item and item[key] not in (None, ""), f"第 {index} 条职责缺少字段：{key}", errors)
            ids.append(str(item.get("responsibility_id")))
            sequences.append(item.get("sequence"))
        require(len(ids) == len(set(ids)), "responsibility_id 存在重复", errors)
        require(sequences == list(range(1, len(sequences) + 1)), "职责 sequence 必须从 1 连续递增", errors)

    declaration = load_json(case_dir / "inputs" / "stage-1-input-declaration.json", errors)
    if declaration:
        require(declaration.get("case_id") == source.get("case_id"), "Stage 1 输入声明 case_id 不一致", errors)
        require(declaration.get("input_version") == source.get("input_version"), "Stage 1 输入声明版本已失效", errors)
        require(declaration.get("method_guide_required") is False, "工作指引不应作为普通案件必需输入", errors)
        valid_ids = {item.get("responsibility_id") for item in responsibilities} if isinstance(responsibilities, list) else set()
        scope = declaration.get("scope") if isinstance(declaration.get("scope"), dict) else {}
        included = set(scope.get("included_responsibility_ids", []))
        excluded = set(scope.get("excluded_responsibility_ids", []))
        require(not ((included | excluded) - valid_ids), "Stage 1 输入声明包含未知职责 ID", errors)
        require(not (included & excluded), "Stage 1 输入声明有职责同时纳入和排除", errors)

    decision_path = case_dir / "reviews" / "gate-0-decision.json"
    if decision_path.exists():
        decision = load_json(decision_path, errors)
        require(decision.get("gate") == "gate-0", "审核决定 gate 必须为 gate-0", errors)
        require(decision.get("decision") in ALLOWED_DECISIONS, "审核决定必须为 approved/request_changes/rejected", errors)
        require(decision.get("reviewed_input_version") == source.get("input_version"), "审核决定绑定的输入版本已失效", errors)
        require(decision.get("reviewed_responsibilities_sha256") == source_meta.get("sha256"), "审核决定绑定的输入 SHA-256 已失效", errors)
        declaration_path = case_dir / "inputs" / "stage-1-input-declaration.json"
        if declaration_path.is_file():
            require(decision.get("input_declaration_sha256") == sha256_file(declaration_path), "审核决定绑定的 Stage 1 输入声明已失效", errors)
        for key in ["reviewer", "reviewed_at"]:
            require(bool(decision.get(key)), f"审核决定缺少字段：{key}", errors)
        if decision.get("decision") == "approved" and not errors:
            if manifest.get("stage") == "gate-0":
                warnings.append("Gate 0 决定有效且已批准；下一步可显式推进到 Stage 1。")
            else:
                require(manifest.get("gate_0_approval") == "reviews/gate-0-decision.json", "Gate 0 后续案件缺少 gate_0_approval 引用", errors)
        elif decision.get("decision") != "approved":
            warnings.append(f"Gate 0 当前决定为 {decision.get('decision')}，不得进入 Stage 1。")
    else:
        warnings.append("尚无 Gate 0 审核决定；案件应保持 awaiting-input-review。")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    errors, warnings = validate_case(case_dir)
    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")
    if errors:
        print(f"INVALID: {len(errors)} error(s)")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
