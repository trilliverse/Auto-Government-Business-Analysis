#!/usr/bin/env python3
"""Render validated Stage 3 logic models into an uncompressed multi-page Draw.io file."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def add(container, tag, **attrs):
    return ET.SubElement(container, tag, {key: str(value) for key, value in attrs.items()})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir")
    parser.add_argument("--draft", help="Approved Stage 3 artifact; defaults to case manifest pointer")
    parser.add_argument("--output")
    args = parser.parse_args()
    case_dir = Path(args.case_dir).resolve()
    manifest = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    draft_relative = args.draft or manifest.get("stage_3_approved_artifact")
    if not draft_relative:
        raise ValueError("Draw.io 只能从批准的 Stage 3 产物渲染，或显式指定草稿用于开发预览")
    draft = json.loads((case_dir / draft_relative).read_text(encoding="utf-8"))
    output = Path(args.output).resolve() if args.output else case_dir / "deliverables" / "养护技术服务处-业务泳道图.drawio"
    output.parent.mkdir(parents=True, exist_ok=True)
    mxfile = ET.Element("mxfile", {"host": "app.diagrams.net", "version": "24.7.17"})
    for page_index, model in enumerate(draft["models"], start=1):
        diagram = add(mxfile, "diagram", id=f"page-{page_index}", name=model["page_name"])
        graph = add(diagram, "mxGraphModel", dx="1200", dy="800", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827", math="0", shadow="0")
        root = add(graph, "root")
        add(root, "mxCell", id="0")
        add(root, "mxCell", id="1", parent="0")
        title = add(root, "mxCell", id="title", value=f"业务事项：{model['item_text']}", style="rounded=0;whiteSpace=wrap;html=1;fontStyle=1;align=center;verticalAlign=middle;fillColor=#d9d9d9;strokeColor=#000000;", vertex="1", parent="1")
        add(title, "mxGeometry", x="20", y="20", width="1080", height="40", **{"as": "geometry"})
        lane_width = 1080 / len(model["lanes"])
        lane_x = {}
        for index, lane in enumerate(model["lanes"]):
            x = 20 + index * lane_width
            lane_x[lane["lane_id"]] = x
            cell = add(root, "mxCell", id=f"lane-{lane['lane_id']}", value=lane["name"], style="swimlane;horizontal=1;startSize=30;fillColor=#f2f2f2;strokeColor=#000000;whiteSpace=wrap;html=1;", vertex="1", parent="1")
            add(cell, "mxGeometry", x=x, y="80", width=lane_width, height="680", **{"as": "geometry"})
        node_cells = {}
        lane_counts = {lane["lane_id"]: 0 for lane in model["lanes"]}
        for node in model["nodes"]:
            lane_counts[node["lane_id"]] += 1
            x = lane_x[node["lane_id"]] + 45
            y = 125 + (lane_counts[node["lane_id"]] - 1) * 95
            if node["type"] == "start": style, w, h = "ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;", 44, 44
            elif node["type"] == "end": style, w, h = "ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=3;", 44, 44
            elif node["type"] == "decision": style, w, h = "rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;", 130, 70
            else: style, w, h = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;", 190, 58
            cell = add(root, "mxCell", id=node["node_id"], value=node["label"], style=style, vertex="1", parent="1")
            add(cell, "mxGeometry", x=x, y=y, width=w, height=h, **{"as": "geometry"})
            node_cells[node["node_id"]] = cell
        for edge in model["edges"]:
            cell = add(root, "mxCell", id=edge["edge_id"], value=edge["label"], style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;strokeColor=#000000;", edge="1", parent="1", source=edge["source"], target=edge["target"])
            add(cell, "mxGeometry", relative="1", **{"as": "geometry"})
    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(output, encoding="utf-8", xml_declaration=True)
    print(json.dumps({"output": str(output), "page_count": len(draft["models"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
