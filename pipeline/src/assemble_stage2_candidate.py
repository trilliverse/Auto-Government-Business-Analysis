#!/usr/bin/env python3
"""Assemble a full Stage 2 candidate from verified evidence analyses and explicit human decisions."""
from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

def sha(path):
 h=hashlib.sha256();h.update(path.read_bytes());return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('case_dir');a=p.parse_args();case=Path(a.case_dir).resolve();m=json.loads((case/'case.json').read_text(encoding='utf-8'));approved_path=case/m['stage_1_approved_artifact'];approved=json.loads(approved_path.read_text(encoding='utf-8'));ev=json.loads((case/'stage-2/drafts/verified-evidence-pilot.json').read_text(encoding='utf-8'));ev_by={x['item_id']:x['evidence_refs'] for x in ev['items']};neg=json.loads((case/'stage-2/drafts/human-negative-evidence.json').read_text(encoding='utf-8'));neg_by={x['item_id']:x for x in neg['decisions']};analyses={}
 for fn in ['independent-pilot-analysis.json','independent-pilot-analysis-batch2.json','independent-pilot-analysis-batch3.json','independent-pilot-analysis-batch4.json']:
  path=case/'stage-2/drafts'/fn
  if path.exists():
   for x in json.loads(path.read_text(encoding='utf-8'))['items']: analyses[x['item_id']]=x
 assessments=[]
 for item in approved['items']:
  if item['disposition']!='include':continue
  iid=item['item_id']; refs=ev_by.get(iid,[]); ana=analyses.get(iid); human=[]
  if iid in neg_by:
   status='无'; narrative=''; unresolved=[]; human=[neg_by[iid]['statement'],neg['production_rule']]; inference=[]
  elif ana:
   status=ana['digital_status']; narrative=ana['process_narrative']; unresolved=ana['unresolved_questions']; inference=[ana['evidence_support_summary']]
  elif iid=='I013':
   status='待确认'; narrative='流程线索：公路域15个系统资料中未找到养护资质审批直接依据；人工Gold补充政务服务渠道，但本次公开网站核验因网络检索服务不可用而未完成。'; unresolved=['核实正式办事指南、现行事项名称和许可层级','核实主责审批处室、受理补正、审查决定及送达节点','确认江西政务服务网/省交通运输厅政务服务平台的实际入口和系统编号']; human=['人工Gold记录了政务服务渠道，但尚未形成可复核的网页快照或正式指南证据。']; inference=[]
  else:
   status='待确认'; narrative='现有资料尚不足以形成该事项的主要数字化办理过程。'; unresolved=['补充适用业务范围的系统功能、办理实例和目标处室权限材料']; inference=[]
  systems=[]
  seen=set()
  for ref in refs:
   key=(ref['filename'],ref['document_id'])
   if key not in seen:
    systems.append({'name':ref['filename'],'number':None,'support_strength':'direct','source_type':'document'});seen.add(key)
  assessments.append({'item_id':iid,'digital_status':status,'process_narrative':narrative,'unresolved_questions':unresolved,'systems':systems,'evidence_refs':refs,'inference_notes':inference,'human_additions':human,'status':'draft'})
 result={'schema_version':'0.1.0','case_id':m['case_id'],'stage_1_artifact_sha256':sha(approved_path),'generation_mode':'assembled-independent-evidence-candidate','generated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'document_catalog':[],'assessments':assessments}
 out=case/'stage-2/drafts/assessments-independent-v1.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out);return 0
if __name__=='__main__':raise SystemExit(main())
