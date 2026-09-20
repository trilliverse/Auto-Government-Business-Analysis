#!/usr/bin/env python3
"""Record Gate 3 decisions and freeze an approved swimlane logic artifact."""
from __future__ import annotations
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path

def sha(p):h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def decide(a):
 case=Path(a.case_dir).resolve();draft=case/a.draft;data=json.loads(draft.read_text(encoding='utf-8'));m=json.loads((case/'case.json').read_text(encoding='utf-8'))
 if data['stage_2_draft_sha256']!=m.get('stage_2_approved_sha256'):raise ValueError('Stage 3 草稿未绑定当前批准的 Stage 2 产物')
 decision={'gate':'gate-3','decision':a.decision,'draft_path':a.draft.replace('\\','/'),'reviewed_draft_sha256':sha(draft),'stage_2_approved_sha256':m['stage_2_approved_sha256'],'reviewer':a.reviewer,'reviewed_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat(),'comments':a.comments or ''};out=case/'reviews/gate-3-decision.json';write(out,decision);print(out);return 0
def freeze(a):
 case=Path(a.case_dir).resolve();d=json.loads((case/'reviews/gate-3-decision.json').read_text(encoding='utf-8'));m=json.loads((case/'case.json').read_text(encoding='utf-8'))
 if d['decision']!='approved':raise ValueError('Gate 3 未批准')
 if d['stage_2_approved_sha256']!=m.get('stage_2_approved_sha256'):raise ValueError('Stage 2 批准版本已变化')
 src=case/d['draft_path']
 if sha(src)!=d['reviewed_draft_sha256']:raise ValueError('Stage 3 草稿审核后已变化')
 target=case/'stage-3/approved'/f"swimlanes-{d['reviewed_draft_sha256'][:12]}.json";target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and sha(target)!=d['reviewed_draft_sha256']:raise ValueError('批准路径存在不同内容')
 if not target.exists():shutil.copyfile(src,target)
 m.update({'stage':'gate-3','status':'approved','stage_3_approval':'reviews/gate-3-decision.json','stage_3_approved_artifact':target.relative_to(case).as_posix(),'stage_3_approved_sha256':sha(target),'updated_at':datetime.now(timezone.utc).replace(microsecond=0).isoformat()});write(case/'case.json',m);print(target);return 0
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='cmd',required=True);d=s.add_parser('decide');d.add_argument('case_dir');d.add_argument('--draft',default='stage-3/drafts/swimlane-models-v1.json');d.add_argument('--decision',choices=['approved','request_changes','rejected'],required=True);d.add_argument('--reviewer',required=True);d.add_argument('--comments');f=s.add_parser('freeze');f.add_argument('case_dir');a=p.parse_args();return decide(a) if a.cmd=='decide' else freeze(a)
if __name__=='__main__':raise SystemExit(main())
