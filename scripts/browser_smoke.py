#!/usr/bin/env python3
"""Optional browser smoke test. Install Playwright separately; it is not a build dependency.

The generated HTML is loaded with set_content. SVG relative resources are embedded
for this test only. No file/network browser navigation is required or tested.
"""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser',help='Chromium executable path; omit for Playwright installed Chromium')
    parser.add_argument('--output',type=Path,default=ROOT/'verification-artifacts')
    args=parser.parse_args()
    try:from playwright.sync_api import sync_playwright
    except ImportError:print('Optional dependency required: pip install playwright && playwright install chromium',file=sys.stderr);return 2
    args.output.mkdir(parents=True,exist_ok=True)
    def show(page,path):
        content=path.read_text(encoding='utf-8')
        def replace(m):
            value=m.group(1)
            if value.startswith('data:'):return m.group(0)
            target=(path.parent/value).resolve();target.relative_to(ROOT)
            if target.suffix!='.svg':raise ValueError(f'Unexpected resource: {value}')
            return 'src="data:image/svg+xml;base64,'+base64.b64encode(target.read_bytes()).decode()+'"'
        content=re.sub(r'src="([^"]+)"',replace,content)
        page.set_content(content,wait_until='load')
    rows=[]
    with sync_playwright() as p:
        options={'headless':True}
        if args.browser:options['executable_path']=args.browser
        browser=p.chromium.launch(**options)
        page=browser.new_page()
        for width,height in [(1440,1080),(390,844)]:
            page.set_viewport_size({'width':width,'height':height})
            for path in sorted((ROOT/'_site/chapters').glob('*.html')):
                show(page,path)
                state=page.evaluate('''()=>({math:document.querySelectorAll('math').length,brokenImages:[...document.images].filter(e=>!e.complete||!e.naturalWidth).length,overflow:document.documentElement.scrollWidth>innerWidth+1})''')
                rows.append({'file':path.name,'width':width,**state})
            show(page,ROOT/'_site/chapters/01-complexity-hierarchy.html')
            page.screenshot(path=str(args.output/f'reader-{width}.png'))
        show(page,ROOT/'_site/complete.html')
        rows.append({'file':'complete.html','width':390,**page.evaluate('''()=>({math:document.querySelectorAll('math').length,brokenImages:[...document.images].filter(e=>!e.complete||!e.naturalWidth).length,overflow:document.documentElement.scrollWidth>innerWidth+1})''')})
        report={'browser':browser.version,'mode':'set_content; relative SVGs embedded for testing; file/HTTP navigation untested','pages':rows}
        browser.close()
    (args.output/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    failures=[r for r in rows if r['brokenImages'] or r['overflow']]
    print(json.dumps({'cases':len(rows),'failures':failures},ensure_ascii=False,indent=2))
    return 1 if failures else 0

if __name__=='__main__':raise SystemExit(main())
