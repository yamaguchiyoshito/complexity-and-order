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
    args=parser.parse_args()
    rel=args.path.resolve().relative_to(ROOT).as_posix()
    old=subprocess.run(['git','show',f'{args.ref}:{rel}'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if old.returncode:print(old.stderr.strip(),file=sys.stderr);return 2
    a=invariants(old.stdout);b=invariants(args.path.read_text(encoding='utf-8'))
    hard=['title','display_math','inline_math','numbers','footnote_uses','footnote_defs','figures','captions','nav_blocks']
    soft=['headings','katakana_terms','bold']
    changed={k:{'before':a[k],'after':b[k]} for k in hard+soft if a[k]!=b[k]}
    print(json.dumps({'file':rel,'ref':args.ref,'hard_changes':{k:v for k,v in changed.items() if k in hard},'soft_changes':{k:v for k,v in changed.items() if k in soft}},ensure_ascii=False,indent=1))
    return 1 if any(k in hard for k in changed) else 0

if __name__=='__main__':raise SystemExit(main())
