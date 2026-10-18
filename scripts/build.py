#!/usr/bin/env python3
"""Build a portable HTML reader with native MathML. Requires Pandoc 3.x."""
from __future__ import annotations
import argparse
import base64
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
READER = 'markdown+tex_math_dollars+footnotes+pipe_tables'
SITE_INDEX_END = '<!-- SITE-INDEX-END'


def site_index_text(text: str) -> str:
    """README本文のうち、HTML閲覧版のトップページへ載せる範囲(マーカーより前)を返す。"""
    head, marker, _ = text.partition(SITE_INDEX_END)
    return head.rstrip() + '\n' if marker else text


def run_pandoc(text: str, args: list[str]) -> str:
    if not shutil.which('pandoc'):
        raise RuntimeError('Pandoc 3.x が必要である。guides/READING.md を参照。')
    result = subprocess.run(['pandoc', *args], input=text, text=True, encoding='utf-8', capture_output=True, check=False)
    if result.returncode or result.stderr.strip():
        raise RuntimeError(f'Pandoc conversion failed: {result.stderr.strip()}')
    return result.stdout


def parse_markdown(text: str) -> dict:
    return json.loads(run_pandoc(text, ['--from', READER, '--to', 'json']))


def map_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme or url.startswith(('#', '//')):
        return url
    path = parsed.path
    if path.endswith('.md'):
        path = path[:-3] + '.html'
        if Path(path).name == 'README.html':
            path = path[:-len('README.html')] + 'index.html'
    return path + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')


def transform_links(node: object) -> None:
    if isinstance(node, dict):
        if node.get('t') in ('Link', 'Image'):
            node['c'][-1][0] = map_url(node['c'][-1][0])
        for child in node.values(): transform_links(child)
    elif isinstance(node, list):
        for child in node: transform_links(child)


def render(text: str, prefix: str = '') -> str:
    ast = parse_markdown(text)
    transform_links(ast)
    args = ['--from', 'json', '--to', 'html5', '--mathml', '--wrap=none']
    if prefix: args += ['--id-prefix', prefix]
    output = run_pandoc(json.dumps(ast, ensure_ascii=False), args)
    if prefix:
        output = output.replace('id="footnotes"', f'id="{prefix}footnotes"')
    return output


def wrap_page(title: str, body: str, source: Path, series: dict, css: str) -> str:
    depth = len(source.parent.parts)
    root_link = '../' * depth
    links = []
    def link(c: dict) -> str:
        current = source.as_posix() == c['path']
        return f'<a class="chapter-link{" current" if current else ""}" href="{root_link}{map_url(c["path"])}"'+(' aria-current="page"' if current else '')+f'><span>{c["number"]:02d}</span>{html.escape(c["title"])}</a>'
    for k in series.get('cours', []):
        lo, hi = k['chapters']
        members = [c for c in series['chapters'] if lo <= c['number'] <= hi]
        if not members: continue
        links.append(f'<div class="toc-cour">第{k["number"]}クール　{html.escape(k["title"])}</div>')
        for c in members:
            for part in k.get('parts', []):
                if c['number'] == part['chapters'][0]: links.append(f'<div class="toc-part">{html.escape(part["label"])}　{html.escape(part["title"])}</div>')
            links.append(link(c))
    footer_label = f'全{len(series["chapters"])}回 / 第{str(series.get("version", "1")).split(".")[0]}版'
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>{html.escape(title)} | 複雑さと秩序</title>
<style>{css}</style></head><body>
<a class="skip" href="#main">本文へ移動</a>
<input type="checkbox" id="toc-state" class="toc-state" aria-label="目次を開く">
<header class="topbar"><a href="{root_link}index.html" class="brand">複雑さと秩序<span>COMPLEXITY / ORDER</span></a><div class="topbar-actions"><a href="{root_link}guides/READING.html">読み方</a><label class="toc-toggle" for="toc-state"><svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 5h14M3 10h14M3 15h14"/></svg>目次</label></div></header>
<label class="toc-backdrop" for="toc-state" aria-hidden="true"></label>
<aside class="toc-drawer" aria-label="連載の目次"><div class="toc-drawer-head"><strong>連載の目次</strong><label class="toc-close" for="toc-state" title="閉じる"><svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 5l10 10M15 5L5 15"/></svg></label></div><nav aria-label="連載の目次">{''.join(links)}</nav><div class="toc-drawer-foot"><p>必要な複雑さを持ち、そのすべてを、すべての参加者へ負わせない。</p><a href="{root_link}references/bibliography.html">文献と確認範囲</a></div></aside>
<div class="layout"><main id="main" tabindex="-1"><article>{body}</article><footer>{footer_label} — 本文はMarkdown、挿絵はSVG、数式はMathML。<br>理論・説明用モデル・工学的応用を区別して読む。</footer></main></div></body></html>'''


def make_book(series: dict, css: str, dest: Path, cour: dict) -> None:
    lo, hi = cour['chapters']
    chapters = [c for c in series['chapters'] if lo <= c['number'] <= hi]
    paths = {str((ROOT/c['path']).resolve()): f'#chapter-{c["number"]:02d}' for c in chapters}
    pieces = []
    for c in chapters:
        source = ROOT/c['path']
        body = render(source.read_text(encoding='utf-8'), prefix=f'c{c["number"]:02d}-')
        def rewrite(match: re.Match) -> str:
            attr, url = match.group(1), html.unescape(match.group(2))
            if attr == 'src' and url.endswith('.svg'):
                path = (source.parent/url).resolve()
                path.relative_to(ROOT)
                encoded = base64.b64encode(path.read_bytes()).decode('ascii')
                return f'src="data:image/svg+xml;base64,{encoded}"'
            if attr == 'href' and not urlsplit(url).scheme and not url.startswith('#'):
                raw = urlsplit(url).path
                if raw.endswith('index.html'): return 'href="#book-contents"'
                md = (source.parent / (raw[:-5]+'.md' if raw.endswith('.html') else raw)).resolve()
                if str(md) in paths:return f'href="{paths[str(md)]}"'
                if md.parent == ROOT/'chapters' and md.suffix == '.md':return f'href="chapters/{md.stem}.html"'
            return match.group(0)
        body = re.sub(r'(href|src)="([^"]*)"', rewrite, body)
        pieces.append(f'<section class="book-chapter" id="chapter-{c["number"]:02d}">{body}</section>')
    toc = ''.join(f'<li><a href="#chapter-{c["number"]:02d}">第{c["number"]}回　{html.escape(c["title"])}</a></li>' for c in chapters)
    heading = f'第{cour["number"]}クール　{html.escape(cour["title"])}（第{lo}〜{hi}回）'
    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>複雑さと秩序 — {heading}</title><style>{css}\n.book{{max-width:860px;margin:auto;padding:32px 24px}}.book-chapter{{padding-top:55px;margin-top:65px;border-top:2px solid var(--line)}}@media print{{.book-chapter{{break-before:page}}}}</style></head><body><main class="book"><section id="book-contents"><p class="eyebrow">COMPLEXITY / ORDER — COMPLETE SERIES</p><h1>複雑さと秩序</h1><h2>{heading}</h2><p>このファイルは外部通信なしで閲覧できる。数式はネイティブMathML、挿絵は埋め込みSVGで表示する。</p><ol>{toc}</ol></section>{''.join(pieces)}</main></body></html>'''
    dest.write_text(doc, encoding='utf-8')


def build(output: Path) -> dict:
    output = output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise RuntimeError('出力先にはリポジトリ自身またはその親を指定できない。')
    output.mkdir(parents=True, exist_ok=True)
    series = json.loads((ROOT/'series.json').read_text(encoding='utf-8'))
    css = (ROOT/'site-src/styles.css').read_text(encoding='utf-8')
    documents = [ROOT/'README.md', *(ROOT/c['path'] for c in series['chapters']), *sorted((ROOT/'guides').glob('*.md')), ROOT/'references/bibliography.md', ROOT/'CHANGELOG.md']
    count = 0
    for p in documents:
        source = p.relative_to(ROOT)
        target = output/map_url(source.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        text=p.read_text(encoding='utf-8')
        if p.name == 'README.md': text = site_index_text(text)
        title = re.search(r'^# (.+)', text, re.M).group(1)
        content=render(text)
        count += content.count('<math ')
        target.write_text(wrap_page(title, content, source, series, css),encoding='utf-8')
    shutil.copytree(ROOT/'assets',output/'assets',dirs_exist_ok=True)
    # README links to source configuration and repository guides remain resolvable offline.
    for p in [ROOT/'series.json', ROOT/'references/sources.json']:
        dest=output/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    (output/'.nojekyll').write_text('',encoding='utf-8')
    standalone=[]
    for k in series.get('cours',[]):
        lo,hi=k['chapters']
        if not any(lo<=c['number']<=hi for c in series['chapters']):continue
        name='complete.html' if k['number']==1 else f'complete-{k["number"]}.html'
        make_book(series,css,output/name,k);standalone.append(name)
    result=dict(pages=len(documents),chapters=len(series['chapters']),math_nodes=count,svg_files=len(list((output/'assets').rglob('*.svg'))),standalone=standalone)
    (output/'build-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'_site')
    args=parser.parse_args()
    try:print(json.dumps(build(args.output),ensure_ascii=False,indent=2));return 0
    except (RuntimeError,OSError,ValueError) as exc:print(str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
