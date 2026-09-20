#!/usr/bin/env python3
"""Map the reviewed Stage 2 reference to the immutable approved Stage 1 IDs."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def unresolved_parts(narrative: str) -> list[str]:
    if "待确认" not in narrative: return []
    tail = narrative.split("待确认", 1)[1].lstrip("：: \n")
    return [part.strip() for part in tail.replace("\n", "；").split("；") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--reference", required=True)
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    approved_path = case_dir / manifest["stage_1_approved_artifact"]
    approved = json.loads(approved_path.read_text(encoding="utf-8"))
    reference = json.loads(Path(args.reference).resolve().read_text(encoding="utf-8"))
    approved_by_pair = {(i["item_text"], i["category"]): i for i in approved["items"] if i["disposition"] == "include"}
    assessments = []
    for ref in reference["items"]:
        item = approved_by_pair.get((ref["item_text"], ref["category"]))
        if item is None: raise ValueError("Stage 2 Gold 无法映射批准事项：" + ref["item_text"])
        systems = [{"name": value, "number": None, "support_strength": "strong", "source_type": "human"} for value in ref["systems"]]
        assessments.append({
            "item_id": item["item_id"], "digital_status": ref["digital_status"],
            "process_narrative": ref["process_narrative"],
            "unresolved_questions": unresolved_parts(ref["process_narrative"]),
            "systems": systems, "evidence_refs": [],
            "inference_notes": [ref["evidence_narrative"]] if ref["evidence_narrative"] else [],
            "human_additions": ["开发基线由人工核验工作簿映射；不得冒充为文档直接证据。"],
            "status": "draft"
        })
    draft = {
        "schema_version": "0.1.0", "case_id": manifest["case_id"],
        "stage_1_artifact_sha256": sha256(approved_path),
        "generation_mode": "human-reviewed-reference-baseline",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "document_catalog": [], "assessments": assessments
    }
    output = case_dir / "stage-2" / "drafts" / "assessments-baseline-v1.json"
    output.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "assessment_count": len(assessments)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
