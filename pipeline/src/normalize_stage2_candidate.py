#!/usr/bin/env python3
"""Validate and explicitly normalize free-form model status phrases to the controlled Stage 2 enum."""

from __future__ import annotations
import argparse,json
from pathlib import Path
ALLOWED={"有","无","待确认","不纳入本次梳理范畴"}
MAPPING={"部分数字化":"有","数据支撑层面部分数字化":"待确认","资料不足，无法判断":"待确认"}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args(); data=json.loads(Path(a.input).read_text(encoding='utf-8')); changes=[]
 for item in data.get('items',[]):
  status=item.get('digital_status')
  if status not in ALLOWED:
   if status not in MAPPING: raise ValueError('无法归一化状态：'+str(status))
   normalized=MAPPING[status]; changes.append({'item_id':item['item_id'],'from':status,'to':normalized}); item['digital_status']=normalized
   item.setdefault('normalization_notes',[]).append(f"状态由“{status}”按受控枚举规则归一化为“{normalized}”；不改变流程与待确认内容。")
 Path(a.output).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'changes':changes},ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
