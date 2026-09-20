#!/usr/bin/env python3
"""Summarize direct, human-negative, and independent-analysis coverage for all Stage 1 items."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('case_dir');a=p.parse_args();case=Path(a.case_dir).resolve();m=json.loads((case/'case.json').read_text(encoding='utf-8'));approved=json.loads((case/m['stage_1_approved_artifact']).read_text(encoding='utf-8'));ev=json.loads((case/'stage-2/drafts/verified-evidence-pilot.json').read_text(encoding='utf-8'));neg=json.loads((case/'stage-2/drafts/human-negative-evidence.json').read_text(encoding='utf-8'));ref=json.loads(Path('pipeline/fixtures/maintenance-office-stage2-reference.json').read_text(encoding='utf-8'));ref_by_text={i['item_text']:i for i in ref['items']};ev_by={i['item_id']:i for i in ev['items']};neg_by={i['item_id']:i for i in neg['decisions']};ind={}
 for name in ['independent-pilot-analysis.json','independent-pilot-analysis-batch2.json','independent-pilot-analysis-batch3.json','independent-pilot-analysis-batch4.json']:
  path=case/'stage-2/drafts'/name
  if path.exists():
   for x in json.loads(path.read_text(encoding='utf-8'))['items']:ind[x['item_id']]=x
 rows=[]
 for item in approved['items']:
  if item['disposition']!='include':continue
  gold=ref_by_text[item['item_text']]; refs=ev_by.get(item['item_id'],{}).get('evidence_refs',[]); ana=ind.get(item['item_id'])
  rows.append({'item_id':item['item_id'],'item_text':item['item_text'],'gold_status':gold['digital_status'],'direct_evidence_count':len(refs),'human_negative_evidence':item['item_id'] in neg_by,'independent_status':ana.get('digital_status') if ana else None,'status_match':bool(ana and ana.get('digital_status')==gold['digital_status']),'coverage_class':'direct-pilot' if refs else ('human-negative' if item['item_id'] in neg_by else 'unverified')})
 result={'statistics':{'item_count':len(rows),'direct_pilot_items':sum(r['direct_evidence_count']>0 for r in rows),'human_negative_items':sum(r['human_negative_evidence'] for r in rows),'independently_analyzed':sum(r['independent_status'] is not None for r in rows),'status_matches':sum(r['status_match'] for r in rows),'unverified_items':sum(r['coverage_class']=='unverified' for r in rows)},'items':rows}
 out=case/'stage-2/drafts/evidence-coverage.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result['statistics'],ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
