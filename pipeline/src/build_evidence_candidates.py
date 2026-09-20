#!/usr/bin/env python3
"""Rank locator-preserving document chunks as review-only evidence candidates."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

STOP = {"国省干线公路", "公路", "事务性工作", "承担", "参与", "指导", "相关", "方面", "全省", "国家", "江西省", "工作"}
DOMAIN_TERMS = [
    "风险隐患排查整治", "技术状况监测", "交通流量调查", "信用体系建设", "养护作业安全生产",
    "路网运行监测", "养护市场管理", "养护工程项目", "绩效考核", "应急体系建设", "应急保通",
    "资质审批", "发展纲要", "规章制度", "统计", "备案", "计划", "造价", "养护管理",
]


def terms(text: str) -> list[str]:
    found = [term for term in DOMAIN_TERMS if term in text]
    # Add meaningful 2-6 character segments split on punctuation and function words.
    for segment in re.split(r"[，、；。及和与/（）\s]+", text):
        segment = re.sub(r"^(贯彻执行|参与拟订|督促落实|承担编制|承担指导|承担|参与|承办)", "", segment)
        segment = re.sub(r"(等)?事务性工作$", "", segment)
        if 2 <= len(segment) <= 12 and segment not in STOP:
            found.append(segment)
    return list(dict.fromkeys(found))


def item_scope_tags(text: str) -> list[str]:
    tags = []
    if "国省干线" in text: tags.extend(["普通国省干线", "普通干线"])
    if "交通流量" in text: tags.append("交通流量")
    if "应急" in text: tags.append("应急")
    if "养护" in text: tags.append("养护")
    return list(dict.fromkeys(tags))


def score(item_terms: list[str], text: str) -> tuple[int, list[str]]:
    hits = [term for term in item_terms if term in text and term not in STOP]
    # Specific business actions must outweigh broad parent objects. Otherwise a
    # “计划” item is incorrectly ranked behind any row merely mentioning the
    # broad phrase “养护工程项目”.
    broad = {"养护工程项目", "养护管理", "统计"}
    value = sum(3 if term in broad else max(8, min(len(term) * 2, 20)) for term in hits)
    return value, hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    artifact = json.loads((case_dir / manifest["stage_1_approved_artifact"]).read_text(encoding="utf-8"))
    index = json.loads((case_dir / "stage-2" / "index" / "document-index.json").read_text(encoding="utf-8"))
    documents = {d["document_id"]: d for d in index["documents"]}
    result_items = []
    for item in artifact["items"]:
        if item["disposition"] != "include" or item["status"] == "rejected": continue
        item_terms = terms(item["item_text"])
        item_scopes = item_scope_tags(item["item_text"])
        ranked = []
        for chunk in index["chunks"]:
            value, hits = score(item_terms, chunk["text"])
            if value:
                document = documents[chunk["document_id"]]
                scope_hits = [tag for tag in item_scopes if tag in document.get("scope_tags", []) or tag in chunk["text"]]
                scope_conflict = "国省干线" in item["item_text"] and any(tag in (document.get("scope_tags") or []) for tag in ("高速公路", "农村公路")) and not scope_hits
                type_bonus = {"requirements": 4, "operation-manual": 4, "preliminary-design": 3, "high-level-design": 2, "detailed-design": 2, "database-design": 0, "feasibility-study": -1, "test-material": -2}.get(document.get("document_type"), 0)
                adjusted = value + 4 * len(scope_hits) + type_bonus - (20 if scope_conflict else 0)
                ranked.append((adjusted, chunk, hits, scope_hits, scope_conflict))
        role_priority = {"process-source": 0, "business-context": 1, "responsibility-source": 2, "reference-method": 3}
        ranked.sort(key=lambda row: (role_priority.get(row[1].get("evidence_role"), 9), -row[0], row[1]["document_id"], row[1]["chunk_id"]))
        candidates = []
        for value, chunk, hits, scope_hits, scope_conflict in ranked[:args.top]:
            document = documents[chunk["document_id"]]
            candidates.append({
                "candidate_id": f"{item['item_id']}-{len(candidates)+1}",
                "document_id": chunk["document_id"], "filename": document["filename"],
                "system_number": document.get("system_number"), "system_name": document.get("system_name"),
                "document_type": document.get("document_type"), "document_scope_tags": document.get("scope_tags", []),
                "chunk_id": chunk["chunk_id"], "locator": chunk["locator"],
                "evidence_role": chunk.get("evidence_role", "business-context"),
                "score": value, "matched_terms": hits, "scope_matches": scope_hits, "scope_conflict": scope_conflict,
                "quote": chunk["text"][:500], "review_status": "unreviewed",
                "warning": "关键词候选，不构成数字化判断或流程直接证据"
            })
        result_items.append({"item_id": item["item_id"], "item_text": item["item_text"], "query_terms": item_terms, "scope_tags": item_scopes, "candidates": candidates})
    result = {
        "schema_version": "0.1.0", "case_id": manifest["case_id"],
        "stage_1_artifact_sha256": manifest["stage_1_approved_sha256"],
        "index_path": "stage-2/index/document-index.json", "items": result_items,
        "statistics": {
            "item_count": len(result_items), "items_with_candidates": sum(bool(i["candidates"]) for i in result_items),
            "candidate_count": sum(len(i["candidates"]) for i in result_items),
            "documents_used": len({c["document_id"] for i in result_items for c in i["candidates"]})
        }
    }
    output = case_dir / "stage-2" / "index" / "evidence-candidates.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["statistics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
