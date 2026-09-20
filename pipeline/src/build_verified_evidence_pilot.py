#!/usr/bin/env python3
"""Build a deterministic pilot evidence set from manually verified indexed chunks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Pilot locators are selected after reading indexed text for three representative
# items. This file intentionally does not infer roles beyond the quoted leaves.
SELECTION = {
    "I005": [
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2633", ["systems", "process_narrative"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2544", ["digital_status", "process_narrative"]),
    ],
    "I011": [
        ("JXJTDCXTV2_6_需求分析_需求定义说明书.docx", "paragraph:621", ["digital_status", "process_narrative", "systems"]),
        ("JXJTDCXTV2_6_需求分析_需求定义说明书.docx", "paragraph:626", ["process_narrative"]),
    ],
    "I006": [
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2635", ["digital_status", "process_narrative", "systems"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2650", ["process_narrative"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2651", ["process_narrative"]),
    ],
    "I007": [
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2743", ["digital_status", "process_narrative", "systems"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2745", ["process_narrative"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2747", ["process_narrative"]),
    ],
    "I008": [
        ("江西省公路养护综合监管系统升级改造采购项目-需求规格说明书v1.1(1).pdf", "page:66", ["digital_status", "process_narrative", "systems"]),
        ("江西省公路养护综合监管系统升级改造采购项目-需求规格说明书v1.1(1).pdf", "page:110", ["process_narrative"]),
        ("江西省公路养护综合监管系统升级改造采购项目-需求规格说明书v1.1(1).pdf", "page:111", ["process_narrative"]),
    ],
    "I009": [
        ("IE-JXLWII-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-需求分析说明书-V1.0.pdf", "page:92", ["digital_status", "process_narrative", "systems"]),
        ("IE-JXLWII-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-需求分析说明书-V1.0.pdf", "page:98", ["process_narrative"]),
    ],
    "I010": [
        ("江西省公路养护综合监管系统升级改造采购项目-需求规格说明书v1.1(1).pdf", "page:98", ["digital_status", "process_narrative", "systems"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2524", ["process_narrative"]),
    ],
    "I012": [
        ("江西省交通运输统计分析监测和投资计划管理信息系统工程可行性研究报告.pdf", "page:43", ["digital_status", "process_narrative", "systems"]),
        ("江西省交通运输统计分析监测和投资计划管理信息系统工程可行性研究报告.pdf", "page:109", ["systems"]),
        ("江西省交通运输统计分析监测和投资计划管理信息系统工程可行性研究报告.pdf", "page:153", ["process_narrative"]),
    ],
    "I018": [
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:2602", ["process_narrative"]),
        ("江西省交通运输资产核查与建养业务支撑系统升级工程初步设计方案.docx", "paragraph:852", ["process_narrative"]),
    ],
    "I014": [
        ("IE-JXLWII-SSWD-0017-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-系统操作与维护手册-V1.0.pdf", "page:65", ["digital_status", "process_narrative", "systems"]),
        ("IE-JXLWII-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-概要设计说明书-V1.0.pdf", "page:393", ["process_narrative"]),
        ("IE-JXLWII-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-概要设计说明书-V1.0.pdf", "page:395", ["process_narrative"]),
    ],
    "I015": [
        ("IE-JXLWII-SSWD-0017-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-系统操作与维护手册-V1.0.pdf", "page:23", ["systems", "process_narrative"]),
    ],
    "I016": [
        ("IE-JXLWII-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-概要设计说明书-V1.0.pdf", "page:378", ["digital_status", "process_narrative", "systems"]),
        ("IE-JXLWII-江西省普通干线路网运行监测与应急处置平台（二期）应用软件开发项目-概要设计说明书-V1.0.pdf", "page:382", ["process_narrative"]),
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    args = parser.parse_args()
    case = Path(args.case_dir).resolve()
    index = json.loads((case / "stage-2/index/document-index.json").read_text(encoding="utf-8"))
    docs = {d["document_id"]: d for d in index["documents"]}
    by_key = {}
    for chunk in index["chunks"]:
        filename = docs[chunk["document_id"]]["filename"]
        by_key.setdefault((filename, chunk["locator"]), []).append(chunk)
    result = {"schema_version": "0.1.0", "case_id": index["case_id"], "items": []}
    missing = []
    for item_id, selections in SELECTION.items():
        refs = []
        for filename, locator, supports in selections:
            matches = by_key.get((filename, locator), [])
            if not matches:
                missing.append(f"{filename}#{locator}"); continue
            match_hashes = {docs[value["document_id"]]["sha256"] for value in matches}
            if len(match_hashes) != 1:
                raise ValueError(f"同名同定位文档内容不一致，必须指定来源：{filename}#{locator}")
            chunk = matches[0]
            duplicate_sources = [docs[value["document_id"]]["path"] for value in matches]
            quote = chunk["text"][:500]
            # Remove incidental contact/address text from review-facing quotes;
            # the indexed source remains immutable and hash-addressed.
            if "地址：" in quote:
                parts = quote.split("地址：", 1)
                tail = parts[1]
                for marker in ("", "4."):
                    if marker in tail:
                        tail = tail[tail.index(marker):]
                        break
                quote = (parts[0] + tail).strip()
            refs.append({
                "evidence_id": f"EV-{item_id}-{len(refs)+1}", "document_id": chunk["document_id"],
                "document_sha256": docs[chunk["document_id"]]["sha256"], "filename": filename,
                "locator": locator, "quote": quote, "supports": supports,
                "duplicate_source_paths": duplicate_sources,
                "strength": "direct", "review_status": "pilot-verified"
            })
        result["items"].append({"item_id": item_id, "evidence_refs": refs})
    if missing:
        raise ValueError("缺少选定定位：" + "；".join(missing))
    output = case / "stage-2/drafts/verified-evidence-pilot.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "item_count": len(result["items"]), "evidence_count": sum(len(i["evidence_refs"]) for i in result["items"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
