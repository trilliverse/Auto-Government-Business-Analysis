#!/usr/bin/env python3
"""Compare independent pilot status with the human-reviewed Stage 2 reference."""

from __future__ import annotations
import argparse, json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--candidate',required=True); p.add_argument('--reference',required=True); p.add_argument('--output',required=True); a=p.parse_args()
    c=json.loads(Path(a.candidate).read_text(encoding='utf-8')); r=json.loads(Path(a.reference).read_text(encoding='utf-8'))
    by_text={x['item_text']:x for x in r['items']}; candidate_path=Path(a.candidate).resolve(); case_dir=candidate_path.parents[2]; manifest=json.loads((case_dir/'case.json').read_text(encoding='utf-8')); approved=json.loads((case_dir/manifest['stage_1_approved_artifact']).read_text(encoding='utf-8')); text_by_id={x['item_id']:x['item_text'] for x in approved['items']}
    rows=[]
    for item in c['items']:
        gold=by_text[text_by_id[item['item_id']]]; rows.append({'item_id':item['item_id'],'item_text':gold['item_text'],'candidate_status':item['digital_status'],'gold_status':gold['digital_status'],'status_match':item['digital_status']==gold['digital_status'],'candidate_unresolved':item['unresolved_questions'],'gold_contains_unresolved':gold['contains_unresolved']})
    report={'item_count':len(rows),'status_matches':sum(x['status_match'] for x in rows),'rows':rows,'note':'只比较数字化状态；流程文本不做逐字匹配，需人工比较证据边界和未决问题。'}
    Path(a.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
