#!/usr/bin/env python3
"""Check that a style revision kept the facts: math, numbers, footnotes, figure, names, headings."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def invariants(text:str)->dict:
    body=text.split('## 参考文献・注記')[0]
    return dict(
        title=text.split('\n',1)[0],
        headings=re.findall(r'^#{2,3} .+$',body,re.M),
        display_math=sorted(m.strip() for m in re.findall(r'\$\$\n(.*?)\n\$\$',body,re.S)),
        inline_math=sorted(set(re.findall(r'\$[^$\n]+\$',body))),
        numbers=sorted(set(re.findall(r'\d[\d,.%]*',re.sub(r'\$[^$\n]+\$','',body)))),
        footnote_uses=sorted(set(re.findall(r'\[\^([^\]]+)\](?!:)',text))),
        footnote_defs=sorted(set(re.findall(r'^\[\^([^\]]+)\]:',text,re.M))),
        figures=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',body),
        captions=re.findall(r'^\*図.+\*$',body,re.M),
        katakana_terms=sorted(set(re.findall(r'[ァ-ヴー]{3,}',body))),
        nav_blocks=text.count('<!-- NAV:'),
        bold=re.findall(r'\*\*[^*]+\*\*',body))


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path)
    parser.add_argument('--ref',default='HEAD')
    parser.add_argument('--allow-figures',action='store_true',help='図とキャプションの追加だけを許容する（削除・変更は検出する）')
    args=parser.parse_args()
    rel=args.path.resolve().relative_to(ROOT).as_posix()
    old=subprocess.run(['git','show',f'{args.ref}:{rel}'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if old.returncode:print(old.stderr.strip(),file=sys.stderr);return 2
    new_text=args.path.read_text(encoding='utf-8')
    a=invariants(old.stdout);b=invariants(new_text)
    if args.allow_figures:
        # 追加された図の行（画像とキャプション）は、数式・数値・カタカナ語の比較から除く。
        before_lines=set(old.stdout.split('\n'))
        kept='\n'.join(l for l in new_text.split('\n') if l in before_lines or not l.startswith(('![','*図')))
        b_core=invariants(kept);b={**b_core,'figures':b['figures'],'captions':b['captions']}
    hard=['title','display_math','inline_math','numbers','footnote_uses','footnote_defs','figures','captions','nav_blocks']
    soft=['headings','katakana_terms','bold']
    def differs(k):
        if args.allow_figures and k in ('figures','captions'):return not set(a[k])<=set(b[k])
        return a[k]!=b[k]
    changed={k:{'before':a[k],'after':b[k]} for k in hard+soft if differs(k)}
    print(json.dumps({'file':rel,'ref':args.ref,'hard_changes':{k:v for k,v in changed.items() if k in hard},'soft_changes':{k:v for k,v in changed.items() if k in soft}},ensure_ascii=False,indent=1))
    return 1 if any(k in hard for k in changed) else 0

if __name__=='__main__':raise SystemExit(main())
