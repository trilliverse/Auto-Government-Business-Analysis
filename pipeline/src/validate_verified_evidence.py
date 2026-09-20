#!/usr/bin/env python3
"""Validate evidence document hashes, locators, and quotes against the current index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--evidence", default="stage-2/drafts/verified-evidence-pilot.json")
    args = parser.parse_args()
    case = Path(args.case_dir).resolve()
    index = json.loads((case / "stage-2/index/document-index.json").read_text(encoding="utf-8"))
    evidence = json.loads((case / args.evidence).read_text(encoding="utf-8"))
    docs = {d["document_id"]: d for d in index["documents"]}
    chunks = {(c["document_id"], c["locator"]): c for c in index["chunks"]}
    errors = []
    count = 0
    for item in evidence["items"]:
        for ref in item["evidence_refs"]:
            count += 1
            doc = docs.get(ref["document_id"])
            if not doc: errors.append(f"{ref['evidence_id']} 文档不存在"); continue
            if doc["sha256"] != ref["document_sha256"]: errors.append(f"{ref['evidence_id']} 文档哈希失效")
            chunk = chunks.get((ref["document_id"], ref["locator"]))
            if not chunk: errors.append(f"{ref['evidence_id']} 定位不存在"); continue
            # Quotes may be privacy-redacted substrings, so require every
            # nontrivial quote segment to occur in the indexed text.
            segments = [s.strip() for s in ref["quote"].replace("", "\n").splitlines() if len(s.strip()) >= 8]
            if segments and not all(segment in chunk["text"] for segment in segments):
                errors.append(f"{ref['evidence_id']} 引文与定位文本不一致")
            if not ref.get("supports"): errors.append(f"{ref['evidence_id']} 未声明支持字段")
    result = {"valid": not errors, "item_count": len(evidence["items"]), "evidence_count": count, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__": raise SystemExit(main())
