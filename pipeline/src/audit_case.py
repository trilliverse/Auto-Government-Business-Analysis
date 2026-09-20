#!/usr/bin/env python3
"""Audit the complete case chain and render JSON/Markdown status reports."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def sha(p):h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('case_dir');a=p.parse_args();case=Path(a.case_dir).resolve();m=json.loads((case/'case.json').read_text(encoding='utf-8'));checks=[]
 def add(name,ok,detail):checks.append({'name':name,'passed':bool(ok),'detail':detail})
 source=case/'inputs/responsibilities.json';decl=case/'inputs/stage-1-input-declaration.json';g0=case/'reviews/gate-0-decision.json';add('职责输入存在',source.is_file(),str(source));add('输入声明存在',decl.is_file(),str(decl));add('Gate 0 决定存在',g0.is_file(),str(g0))
 if source.is_file() and decl.is_file() and g0.is_file():
  s=json.loads(source.read_text(encoding='utf-8'));d=json.loads(decl.read_text(encoding='utf-8'));g=json.loads(g0.read_text(encoding='utf-8'));add('Gate 0 来源哈希有效',g.get('reviewed_responsibilities_sha256')==s['source']['sha256'],s['source']['sha256']);add('Gate 0 声明哈希有效',g.get('input_declaration_sha256')==sha(decl),sha(decl));add('输入声明已确认',d.get('status')=='confirmed',d.get('confirmed_by'))
 for n in (1,2,3):
  decision=case/f'reviews/gate-{n}-decision.json';key=f'stage_{n}_approved_artifact';hashkey=f'stage_{n}_approved_sha256';add(f'Gate {n} 决定存在',decision.is_file(),str(decision));artifact=case/m[key] if m.get(key) else None;add(f'Stage {n} 批准产物存在',bool(artifact and artifact.is_file()),str(artifact) if artifact else 'manifest pointer missing')
  if artifact and artifact.is_file():add(f'Stage {n} 批准哈希有效',sha(artifact)==m.get(hashkey),sha(artifact))
 # upstream bindings
 if m.get('stage_2_approved_artifact'):
  s2=json.loads((case/m['stage_2_approved_artifact']).read_text(encoding='utf-8'));add('Stage 2 绑定 Stage 1',s2.get('stage_1_artifact_sha256')==m.get('stage_1_approved_sha256'),s2.get('stage_1_artifact_sha256'))
 if m.get('stage_3_approved_artifact'):
  s3=json.loads((case/m['stage_3_approved_artifact']).read_text(encoding='utf-8'));add('Stage 3 绑定 Stage 2',s3.get('stage_2_draft_sha256')==m.get('stage_2_approved_sha256'),s3.get('stage_2_draft_sha256'))
 deliverables=[]
 for file in sorted((case/'deliverables').glob('*')):
  # Ignore Office temporary lock files; they are not governance deliverables and
  # may be exclusively locked while a reviewer has the workbook open.
  if file.name.startswith(('~$', '.~', '._')):continue
  if file.is_file():deliverables.append({'path':file.relative_to(case).as_posix(),'size':file.stat().st_size,'sha256':sha(file)})
 s2data=json.loads((case/m['stage_2_approved_artifact']).read_text(encoding='utf-8')) if m.get('stage_2_approved_artifact') else {'assessments':[]}; unresolved=[{'item_id':x['item_id'],'count':len(x['unresolved_questions']),'questions':x['unresolved_questions']} for x in s2data['assessments'] if x['unresolved_questions']]
 result={'case_id':m['case_id'],'stage':m['stage'],'status':m['status'],'valid':all(x['passed'] for x in checks),'checks':checks,'deliverables':deliverables,'unresolved_items':unresolved,'next_action':'业务人员复核 Gate 3 逻辑与 Draw.io；开发基线已冻结，真实交付前处理未决问题。' if m.get('stage')=='gate-3' else '根据当前阶段完成下一 Gate。'}
 reviews=case/'reviews';reviews.mkdir(exist_ok=True);(reviews/'case-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 lines=['# 案件审计报告','',f"- 案件：`{result['case_id']}`",f"- 当前状态：`{result['stage']} / {result['status']}`",f"- 链条有效：**{result['valid']}**",'', '## 版本与 Gate 校验',''];lines += [f"- [{'x' if x['passed'] else ' '}] {x['name']}：`{x['detail']}`" for x in checks];lines += ['', '## 交付物',''];lines += [f"- `{x['path']}`；{x['size']} bytes；SHA-256 `{x['sha256']}`" for x in deliverables] or ['- 无'];lines += ['',f"## 未决问题（{len(unresolved)} 个事项）",''];lines += [f"### {x['item_id']}（{x['count']}）\n"+'\n'.join('- '+q for q in x['questions']) for x in unresolved] or ['- 无'];lines += ['','## 下一步','',result['next_action'],''];(reviews/'case-audit.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps({'valid':result['valid'],'checks':len(checks),'deliverables':len(deliverables),'unresolved_items':len(unresolved)},ensure_ascii=False,indent=2));return 0 if result['valid'] else 1
if __name__=='__main__':raise SystemExit(main())
