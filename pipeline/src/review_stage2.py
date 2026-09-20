#!/usr/bin/env python3
"""Record Gate 2 decisions and freeze an approved Stage 2 assessment artifact."""
from __future__ import annotations
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from validate_stage2 import validate

def sha(p):h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def decide(a):
 case=Path(a.case_dir).resolve();draft=case/a.draft;errors,report=validate(case,draft)
 if errors:raise ValueError('；'.join(errors))
 data=json.loads(draft.read_text(encoding='utf-8')); decision={'gate':'gate-2','decision':a.decision,'draft_path':a.draft.replace('\\','/'),'reviewed_draft_sha256':sha(draft),'stage_1_artifact_sha256':data['stage_1_artifact_sha256'],'reviewer':a.reviewer,'reviewed_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'comments':a.comments or '','summary':report};out=case/'reviews/gate-2-decision.json';write(out,decision);print(out);return 0
def freeze(a):
 case=Path(a.case_dir).resolve();dp=case/'reviews/gate-2-decision.json';d=json.loads(dp.read_text(encoding='utf-8'))
 if d['decision']!='approved':raise ValueError('Gate 2 未批准')
 src=case/d['draft_path']
 if sha(src)!=d['reviewed_draft_sha256']:raise ValueError('Stage 2 草稿审核后已变化')
 errors,_=validate(case,src)
 if errors:raise ValueError('；'.join(errors))
 target=case/'stage-2/approved'/f"assessments-{d['reviewed_draft_sha256'][:12]}.json";target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and sha(target)!=d['reviewed_draft_sha256']:raise ValueError('批准路径存在不同内容')
 if not target.exists():shutil.copyfile(src,target)
 mp=case/'case.json';m=json.loads(mp.read_text(encoding='utf-8'));m.update({'stage':'gate-2','status':'approved','stage_2_approval':'reviews/gate-2-decision.json','stage_2_approved_artifact':target.relative_to(case).as_posix(),'stage_2_approved_sha256':sha(target),'updated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat()});write(mp,m);print(target);return 0
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True);d=s.add_parser('decide');d.add_argument('case_dir');d.add_argument('--draft',default='stage-2/drafts/assessments-decided-v1.json');d.add_argument('--decision',choices=['approved','request_changes','rejected'],required=True);d.add_argument('--reviewer',required=True);d.add_argument('--comments');f=s.add_parser('freeze');f.add_argument('case_dir');a=p.parse_args();return decide(a) if a.cmd=='decide' else freeze(a)
if __name__=='__main__':raise SystemExit(main())
