#!/usr/bin/env python3
"""Inventory system-document folders and report indexability without reading contents."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".xlsx", ".md", ".txt"}
IGNORED_NAMES = {".ds_store"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    systems = []
    all_files = []
    for directory in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name):
        files = [p for p in directory.rglob("*") if p.is_file() and p.name.lower() not in IGNORED_NAMES and not p.name.startswith(("._", ".~", "~$"))]
        rows = []
        for path in sorted(files, key=lambda p: str(p).lower()):
            ext = path.suffix.lower()
            status = "supported" if ext in SUPPORTED else "unsupported"
            row = {
                "relative_path": path.relative_to(root).as_posix(), "extension": ext,
                "size": path.stat().st_size, "sha256": sha256(path), "index_status": status
            }
            rows.append(row); all_files.append(row)
        systems.append({
            "system_id": f"SYS{len(systems)+1:02d}", "directory_name": directory.name,
            "file_count": len(rows), "supported_count": sum(r["index_status"] == "supported" for r in rows),
            "unsupported_count": sum(r["index_status"] == "unsupported" for r in rows), "files": rows
        })
    result = {
        "schema_version": "0.1.0", "root": str(root),
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "statistics": {
            "system_directory_count": len(systems), "file_count": len(all_files),
            "supported_count": sum(r["index_status"] == "supported" for r in all_files),
            "unsupported_count": sum(r["index_status"] == "unsupported" for r in all_files),
            "extension_counts": dict(sorted(Counter(r["extension"] or "(none)" for r in all_files).items()))
        }, "systems": systems
    }
    output = Path(args.output).resolve(); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["statistics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
