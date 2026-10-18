#!/usr/bin/env python3
"""Validate manuscripts, local references, TeX parsing and passive SVG assets."""
from __future__ import annotations
import argparse
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build import ROOT, parse_markdown, render


@dataclass
class Result:
    chapters: int = 0
    svg_files: int = 0
    inline_math: int = 0
    display_math: int = 0
    local_links: int = 0
    external_links: int = 0
    manuscript_characters: int = 0


def walk(node: object):
    if isinstance(node,dict):
        yield node
        for v in node.values():yield from walk(v)
    elif isinstance(node,list):
        for v in node:yield from walk(v)


def svg_errors(path: Path) -> list[str]:
    errors=[]
    try:root=ET.fromstring(path.read_text(encoding='utf-8'))
    except (OSError,ET.ParseError,UnicodeError) as exc:return [f'{path.name}: SVG parse error: {exc}']
    tag=lambda n:n.tag.rsplit('}',1)[-1]
    if tag(root)!='svg':errors.append(f'{path.name}: root must be svg')
    if not root.get('viewBox'):errors.append(f'{path.name}: missing viewBox')
    if root.get('role')!='img':errors.append(f'{path.name}: missing role=img')
    names={tag(n) for n in root.iter()}
    if not {'title','desc'}<=names:errors.append(f'{path.name}: missing title/desc')
    ids=[n.attrib['id'] for n in root.iter() if 'id' in n.attrib]
    if len(ids)!=len(set(ids)):errors.append(f'{path.name}: duplicate id')
    for label_id in root.get('aria-labelledby','').split():
        if label_id not in ids:errors.append(f'{path.name}: unresolved aria-labelledby')
    for n in root.iter():
        if tag(n).lower() in {'script','foreignobject','iframe','image','use','style','animate','set'}:
            errors.append(f'{path.name}: forbidden SVG element {tag(n)}')
        for key,value in n.attrib.items():
            k=key.rsplit('}',1)[-1].lower()
            if k.startswith('on'):errors.append(f'{path.name}: forbidden event handler {k}')
            if k=='href' and not value.startswith('#'):errors.append(f'{path.name}: external href')
            if re.search(r'url\(\s*["\']?(?!#)[^)]',value):errors.append(f'{path.name}: external url()')
    return errors


def figure_in_section(text:str,section:str,filename:str)->bool:
    """True if the figure file is referenced inside the given ### section of a chapter."""
    m=re.search(r'^### '+re.escape(section)+r'\n(.*?)(?=^#{2,3} |\Z)',text,re.M|re.S)
    return bool(m) and filename in m.group(1)


def validate(root: Path=ROOT) -> tuple[Result,list[str]]:
    root=root.resolve();result=Result();errors=[]
    try:
        series=json.loads((root/'series.json').read_text(encoding='utf-8'))
        sources=json.loads((root/'references/sources.json').read_text(encoding='utf-8'))
    except (OSError,ValueError) as exc:return result,[str(exc)]
    chapters=series.get('chapters',[])
    cours=series.get('cours',[])
    if [c.get('number') for c in chapters]!=list(range(1,len(chapters)+1)):errors.append('series.json: chapter numbers must run 1..N without gaps')
    if len({c['path'] for c in chapters})!=len(chapters):errors.append('series.json: chapter paths must be unique')
    if not cours:errors.append('series.json: cours is missing')
    for k in cours:
        lo,hi=k['chapters'];present=[c for c in chapters if lo<=c['number']<=hi]
        if hi-lo+1!=12:errors.append(f'series.json: cour {k["number"]} must span exactly 12 chapters')
        if k.get('status')=='published' and len(present)!=12:errors.append(f'series.json: cour {k["number"]} has {len(present)} of 12 chapters')
        if [c['number'] for c in present]!=list(range(lo,lo+len(present))):errors.append(f'series.json: cour {k["number"]} chapters must be contiguous from {lo}')
        if not present and k.get('status')!='planned':errors.append(f'series.json: cour {k["number"]} has no chapters and is not marked planned')
        for c in present:
            if c.get('cour')!=k['number']:errors.append(f'{c["path"]}: cour field does not match series.json cours')
        if not (root/k['cover']).exists():errors.append(f'missing cover: {k["cover"]}')
    covered={n for k in cours for n in range(k['chapters'][0],k['chapters'][1]+1)}
    for c in chapters:
        if c['number'] not in covered:errors.append(f'{c["path"]}: chapter is outside every cour')
    md_paths=[root/'README.md',*(root/c['path'] for c in chapters),*sorted((root/'guides').glob('*.md')),root/'references/bibliography.md',root/'CHANGELOG.md']
    asts={};anchors={}
    for path in md_paths:
        if not path.exists():errors.append(f'{path.relative_to(root)}: missing markdown');continue
        text=path.read_text(encoding='utf-8');name=path.relative_to(root).as_posix()
        if any(t in text for t in ['\ue200','\ue201','\ue202',':::writing','```svg','<svg']):errors.append(f'{name}: unsupported conversation artifact or inline SVG')
        # Code examples and inline-code dollar signs are not math delimiters.
        prose=re.sub(r'(?ms)^```[^\n]*\n.*?^```[ \t]*$', '', text)
        prose=re.sub(r'`[^`\n]*`', '', prose)
        if prose.count('$$')%2:errors.append(f'{name}: unbalanced block math delimiters')
        try:ast=parse_markdown(text)
        except (RuntimeError,ValueError) as exc:errors.append(f'{name}: {exc}');continue
        asts[path.resolve()]=ast
        anchors[path.resolve()]={n['c'][1][0] for n in walk(ast) if n.get('t')=='Header'}
        # Explicitly compare TeX nodes against converted MathML, not merely delimiter counts.
        math_nodes=[n for n in walk(ast) if n.get('t')=='Math']
        if path.parent==root/'chapters':
            result.manuscript_characters+=len(text)
            result.inline_math+=sum(n['c'][0]['t']=='InlineMath' for n in math_nodes)
            result.display_math+=sum(n['c'][0]['t']=='DisplayMath' for n in math_nodes)
        try:
            converted=render(text)
            if converted.count('<math ')!=len(math_nodes):errors.append(f'{name}: MathML/TeX node count mismatch')
        except RuntimeError as exc:errors.append(f'{name}: {exc}')
    for c in chapters:
        path=root/c['path']
        if not path.exists():continue
        text=path.read_text(encoding='utf-8');result.chapters+=1
        if not text.startswith(f'# 第{c["number"]}回　{c["title"]}\n'):errors.append(f'{c["path"]}: title mismatch')
        if len(re.sub(r'\s','',text.split('## 参考文献・注記')[0]))<1500:errors.append(f'{c["path"]}: article is too short for a complete essay')
        if text.count('<!-- NAV:')!=2:errors.append(f'{c["path"]}: top/bottom navigation missing')
        if c['figure'].split('/')[-1] not in text:errors.append(f'{c["path"]}: assigned figure is not referenced')
        for fig in c.get('figures',[]):
            name=fig['path'].split('/')[-1]
            if not (root/fig['path']).exists():errors.append(f'missing figure: {fig["path"]}')
            if fig.get('section'):
                if not figure_in_section(text,fig['section'],name):errors.append(f'{c["path"]}: figure {name} is not referenced in section 「{fig["section"]}」')
            elif name not in text:errors.append(f'{c["path"]}: figure {name} is not referenced')
        references=set(re.findall(r'^\[\^([^\]]+)\]:',text,re.M))
        uses=set(re.findall(r'\[\^([^\]]+)\](?!:)',text))
        if references!=set(c['sources']):errors.append(f'{c["path"]}: source list mismatch')
        if references!=uses:errors.append(f'{c["path"]}: unused or undefined footnote')
        if not references<=set(sources):errors.append(f'{c["path"]}: unknown source identifier')
    for path,ast in asts.items():
        for n in walk(ast):
            if n.get('t') not in {'Link','Image'}:continue
            url=n['c'][-1][0];parsed=urlsplit(url)
            if parsed.scheme:
                result.external_links+=1
                if parsed.scheme not in {'https','mailto'}:errors.append(f'{path.name}: unsupported URL scheme {parsed.scheme}')
                if parsed.scheme=='https' and not parsed.netloc:errors.append(f'{path.name}: invalid HTTPS URL')
                continue
            target=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
            result.local_links+=1
            if not target.is_relative_to(root):errors.append(f'{path.name}: path escapes repository: {url}');continue
            if not target.exists():errors.append(f'{path.name}: broken local link: {url}');continue
            if n.get('t')=='Image' and not n['c'][1]:errors.append(f'{path.name}: missing image alt text')
            if parsed.fragment and target.suffix=='.md' and unquote(parsed.fragment) not in anchors.get(target,set()):errors.append(f'{path.name}: unknown anchor: {url}')
    for svg in sorted((root/'assets').rglob('*.svg')):
        result.svg_files+=1;errors+=svg_errors(svg)
    expected_svgs=len(series.get('cours',[]))+len(chapters)+sum(len(c.get('figures',[])) for c in chapters)
    if result.svg_files!=expected_svgs:errors.append(f'expected exactly {expected_svgs} SVG illustrations (one cover per cour + one per chapter + additional figures in series.json)')
    for c in chapters:
        if not (root/c['figure']).exists():errors.append(f'missing figure: {c["figure"]}')
    for p in root.rglob('*'):
        if '_site' in p.parts or '.git' in p.parts:continue
        if p.suffix.lower() in {'.ttf','.otf','.woff','.woff2'}:errors.append(f'font files must not be bundled: {p.name}')
    return result,errors


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',action='store_true');args=parser.parse_args()
    result,errors=validate()
    report={**asdict(result),'errors':errors,'external_url_reachability':'not checked','scientific_correctness':'requires editorial review'}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
