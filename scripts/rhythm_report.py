#!/usr/bin/env python3
"""Measure sentence rhythm of chapter manuscripts (guides/STYLE.md). Reports only; never a pass/fail gate."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CONNECTIVES=('しかし','ただし','では','ところが','それでも','だから','つまり','そこで','ここで','もちろん','さらに','また','むしろ','一方','たとえば','例えば','なお','そして','これは','それは','だが')
HEDGES={'ではない':r'ではない','とは限らない':r'とは限らない','てはいけない':r'てはいけない','区別':r'区別','違う':r'違う','本連載/本稿':r'本連載|本稿|この連載','説明用/公式ではない':r'説明用|の公式ではない|法則ではない','必要がある/べき':r'必要がある|べきである|なければならない','太字文':r'\*\*[^*]+\*\*','次回は':r'次回は'}


def prose_paragraphs(text:str)->list[str]:
    """Body paragraphs only: no headings, math blocks, code, figures, captions, footnotes, navigation."""
    out=[];in_math=in_nav=in_code=False
    for line in text.split('\n'):
        s=line.strip()
        if s.startswith('```'):in_code=not in_code;continue
        if in_code:continue
        if s=='$$':in_math=not in_math;continue
        if in_math:continue
        if s.startswith('<!-- NAV:'):in_nav=True
        if in_nav:
            if s.startswith('<!-- /NAV'):in_nav=False
            continue
        if s.startswith('## 参考文献'):break
        if not s or s.startswith(('#','![','[^','*図')) or s=='---':continue
        out.append(s)
    return out


def sentences(paragraph:str)->list[str]:
    p=re.sub(r'\$[^$]*\$','X',paragraph)
    p=re.sub(r'\[\^[a-z]+\]','',p)
    p=p.replace('**','')
    p=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',p)
    return [s.strip() for s in re.split(r'(?<=[。？！])',p) if s.strip()]


def length(s:str)->int:return len(re.sub(r'[、。「」（）？！\s]','',s))


def ending(s:str)->str:
    s=s.rstrip('。？！」')
    for e in ('である','ではない','でもない','ない','ある','なる','いる','れる','える','できる','た','だ','う','か','い','る'):
        if s.endswith(e):return e
    return s[-1:]


def subject_start(s:str)->bool:
    """「〜は／〜が」で始まる文。接続語、時・条件句（「〜とき、」「〜れば、」「〜では、」）で始まる文は除く。"""
    if s.startswith(CONNECTIVES) or re.match(r'^.{1,14}?(とき|れば|たら|ても|ると|では)[、,]',s) or re.match(r'^.{1,6}?(から|まで|では|には|でも)',s):return False
    return re.match(r'^.{1,14}?(は|が)[、,]?',s) is not None


def is_question(s:str)->bool:return '？' in s or s.endswith(('か。','だろう。','だろうか。'))


def measure(text:str)->dict:
    paras=prose_paragraphs(text);lengths=[];para_sizes=[]
    run_end=run_sub=run_mid=1;max_end=max_sub=max_mid=0;prev_end=None;prev_sub=False
    questions=comma0=comma3=0;endings=Counter()
    for p in paras:
        ss=sentences(p);para_sizes.append(len(ss))
        for s in ss:
            L=length(s);lengths.append(L);c=s.count('、')
            comma0+=c==0;comma3+=c>=3;questions+=is_question(s)
            e=ending(s);endings[e]+=1
            run_end=run_end+1 if e==prev_end else 1;max_end=max(max_end,run_end);prev_end=e
            sub=subject_start(s);run_sub=run_sub+1 if sub and prev_sub else 1;max_sub=max(max_sub,run_sub);prev_sub=sub
            run_mid=run_mid+1 if 25<=L<=45 else 0;max_mid=max(max_mid,run_mid)
    n=max(len(lengths),1);body=''.join(paras)
    return dict(sentences=len(lengths),mean_length=round(sum(lengths)/n,1),
        short_le15=sum(L<=15 for L in lengths),mid_25_45=sum(25<=L<=45 for L in lengths),long_ge60=sum(L>=60 for L in lengths),
        longest=max(lengths,default=0),shortest=min(lengths,default=0),
        comma0_pct=round(100*comma0/n),commas_ge3=comma3,
        max_same_ending_run=max_end,max_subject_start_run=max_sub,max_mid_length_run=max_mid,
        questions=questions,paragraphs=len(paras),one_sentence_paragraphs=sum(c==1 for c in para_sizes),
        top_endings=endings.most_common(4),
        hedges={k:len(re.findall(v,body)) for k,v in HEDGES.items()})


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapter',help='例: 03。省略時は全回')
    parser.add_argument('--ref',help='比較するgitリビジョン（例: HEAD）。指定時は前後比較を表示する')
    parser.add_argument('--json',action='store_true',help='JSONで出力する')
    args=parser.parse_args()
    paths=sorted((ROOT/'chapters').glob(f'{args.chapter or ""}*.md'))
    if not paths:print('対象の章がない',file=sys.stderr);return 1
    report={}
    for p in paths:
        now=measure(p.read_text(encoding='utf-8'));entry={'now':now}
        if args.ref:
            rel=p.relative_to(ROOT).as_posix()
            old=subprocess.run(['git','show',f'{args.ref}:{rel}'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
            if old.returncode==0:entry['before']=measure(old.stdout)
        report[p.name]=entry
    if args.json:print(json.dumps(report,ensure_ascii=False,indent=1));return 0
    keys=['sentences','mean_length','short_le15','mid_25_45','long_ge60','longest','comma0_pct','commas_ge3','max_same_ending_run','max_subject_start_run','max_mid_length_run','questions','paragraphs','one_sentence_paragraphs']
    for name,entry in report.items():
        print(name)
        for k in keys:
            line=f'  {k:<24}{entry["now"][k]!s:>8}'
            if 'before' in entry:line+=f'   (before {entry["before"][k]!s})'
            print(line)
        for k,v in entry['now']['hedges'].items():
            line=f'  hedge:{k:<18}{v:>8}'
            if 'before' in entry:line+=f'   (before {entry["before"]["hedges"][k]})'
            print(line)
    return 0

if __name__=='__main__':raise SystemExit(main())
