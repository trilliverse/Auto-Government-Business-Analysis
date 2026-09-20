#!/usr/bin/env python3
"""Compare a full Stage 2 candidate with the development Gold by stable item text."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('case_dir');p.add_argument('--candidate',required=True);p.add_argument('--reference',required=True);p.add_argument('--output',required=True);a=p.parse_args();case=Path(a.case_dir).resolve();m=json.loads((case/'case.json').read_text(encoding='utf-8'));approved=json.loads((case/m['stage_1_approved_artifact']).read_text(encoding='utf-8'));texts={x['item_id']:x['item_text'] for x in approved['items']};candidate=json.loads((case/a.candidate).read_text(encoding='utf-8'));ref=json.loads(Path(a.reference).read_text(encoding='utf-8'));gold={x['item_text']:x for x in ref['items']};rows=[]
 for x in candidate['assessments']:
  g=gold[texts[x['item_id']]];rows.append({'item_id':x['item_id'],'item_text':g['item_text'],'candidate_status':x['digital_status'],'gold_status':g['digital_status'],'match':x['digital_status']==g['digital_status'],'direct_evidence_count':len(x['evidence_refs']),'human_addition_count':len(x['human_additions']),'unresolved_count':len(x['unresolved_questions'])})
 result={'statistics':{'item_count':len(rows),'matches':sum(r['match'] for r in rows),'differences':sum(not r['match'] for r in rows)},'differences':[r for r in rows if not r['match']],'items':rows,'note':'Gold仅作开发回归；差异必须按证据和业务口径人工裁决，不能自动覆盖候选。'};Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['statistics'],ensure_ascii=False,indent=2));print(json.dumps(result['differences'],ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
