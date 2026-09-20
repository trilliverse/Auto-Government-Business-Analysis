#!/usr/bin/env python3
"""Apply explicit human Stage 2 item decisions to a new immutable draft candidate."""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
ALLOWED={"有","无","待确认","不纳入本次梳理范畴"}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('case_dir');p.add_argument('--draft',default='stage-2/drafts/assessments-independent-v1.json');p.add_argument('--decisions',required=True);p.add_argument('--output',default='stage-2/drafts/assessments-decided-v1.json');a=p.parse_args();case=Path(a.case_dir).resolve();draft=json.loads((case/a.draft).read_text(encoding='utf-8'));dec=json.loads(Path(a.decisions).resolve().read_text(encoding='utf-8'));by={x['item_id']:x for x in draft['assessments']};audit=[]
 for d in dec['decisions']:
  if d['item_id'] not in by:raise ValueError('未知事项 '+d['item_id'])
  if d['digital_status'] not in ALLOWED:raise ValueError('状态无效 '+d['digital_status'])
  item=by[d['item_id']]; before=item['digital_status']; item['digital_status']=d['digital_status']; item['human_additions'].append(f"人工裁决：{d['reason']}（裁决人：{dec['decided_by']}）")
  if d.get('process_narrative') is not None:item['process_narrative']=d['process_narrative']
  if d.get('unresolved_questions') is not None:item['unresolved_questions']=d['unresolved_questions']
  audit.append({'item_id':d['item_id'],'before':before,'after':d['digital_status'],'reason':d['reason']})
 draft['generation_mode']='independent-evidence-candidate-plus-human-decisions';draft['decision_source']=str(Path(a.decisions).resolve());draft['decided_at']=datetime.now(timezone.utc).replace(microsecond=0).isoformat();draft['decision_audit']=audit
 out=case/a.output;out.write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'output':str(out),'audit':audit},ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
