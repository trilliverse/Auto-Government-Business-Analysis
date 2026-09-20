#!/usr/bin/env python3
"""Print concise case status and deterministic next-step advice."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('case_dir');a=p.parse_args();case=Path(a.case_dir).resolve();m=json.loads((case/'case.json').read_text(encoding='utf-8'));stage=m['stage'];status=m['status'];actions={('gate-0','awaiting-input-review'):['确认 inputs/stage-1-input-declaration.json','记录 Gate 0 决定'],('stage-1','drafting'):['生成并审核职责拆解草稿','通过 Gate 1 后冻结'],('gate-1','approved'):['推进 Stage 2 文档索引'],('stage-2','indexing'):['筛选证据并生成 Stage 2 草稿','完成 Gate 2'],('gate-2','approved'):['从批准 Stage 2 生成泳道逻辑','完成 Gate 3'],('gate-3','approved'):['业务人员复核 Draw.io 布局、主体和分支','处理 Stage 2 未决问题后形成最终交付']};result={'case_id':m['case_id'],'stage':stage,'status':status,'next_actions':actions.get((stage,status),['查看 case-audit.md 并按未通过检查处理']),'approved_artifacts':{k:m.get(k) for k in ['stage_1_approved_artifact','stage_2_approved_artifact','stage_3_approved_artifact']}};print(json.dumps(result,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
