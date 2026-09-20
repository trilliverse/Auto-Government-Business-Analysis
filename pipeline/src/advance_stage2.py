#!/usr/bin/env python3
"""Advance a Gate 1 approved case into Stage 2 evidence indexing."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    manifest_path = case_dir / "case.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("stage") != "gate-1" or manifest.get("status") != "approved":
        raise ValueError("案件必须处于 gate-1/approved")
    artifact_path = case_dir / manifest["stage_1_approved_artifact"]
    decision = json.loads((case_dir / manifest["stage_1_approval"]).read_text(encoding="utf-8"))
    artifact_hash = sha256(artifact_path)
    if decision.get("reviewed_draft_sha256") != artifact_hash:
        raise ValueError("Stage 1 批准产物与 Gate 1 决定哈希不一致")
    (case_dir / "stage-2" / "index").mkdir(parents=True, exist_ok=True)
    (case_dir / "stage-2" / "drafts").mkdir(parents=True, exist_ok=True)
    (case_dir / "stage-2" / "approved").mkdir(parents=True, exist_ok=True)
    manifest["stage"] = "stage-2"
    manifest["status"] = "indexing"
    manifest["stage_1_approved_sha256"] = artifact_hash
    manifest["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"stage": "stage-2", "status": "indexing", "stage_1_approved_sha256": artifact_hash}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
