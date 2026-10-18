from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import parse_markdown,render,map_url,build,site_index_text
from validate import validate,svg_errors,walk,figure_in_section
from check_html import check,Document


class RepositoryTests(unittest.TestCase):
    def test_entire_repository(self):
        result,errors=validate()
        self.assertEqual(errors,[])
        self.assertEqual(result.chapters,12)
        series=json.loads((ROOT/'series.json').read_text(encoding='utf-8'))
        self.assertEqual(result.svg_files,1+12+sum(len(c.get('figures',[])) for c in series['chapters']))
        self.assertGreater(result.display_math,15)

    def test_math_becomes_native_mathml(self):
        output=render('Inline $x^2$.\n\n$$\nE(n)=\\frac{n(n-1)}{2}.\n$$\n')
        self.assertEqual(output.count('<math '),2)
        self.assertIn('<mfrac>',output)
        self.assertNotIn('cdn',output)
        self.assertNotIn('<script',output)

    def test_code_fence_is_not_equation(self):
        ast=parse_markdown('```text\n$x$\n```\n')
        self.assertFalse(any(n.get('t')=='Math' for n in walk(ast)))

    def test_site_index_stops_at_marker(self):
        text='# T\n\n本文\n\n<!-- SITE-INDEX-END -->\n\n## GitHubで読む\n\n運用\n'
        self.assertEqual(site_index_text(text),'# T\n\n本文\n')
        self.assertEqual(site_index_text('# T\n\n本文\n'),'# T\n\n本文\n')
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('## 全12回の目次',site_index_text(readme))
        self.assertNotIn('## GitHubで読む',site_index_text(readme))

    def test_figure_section_check(self):
        text='### 一\n\n本文\n\n![a](../assets/illustrations/x-2-a.svg)\n\n### 二\n\n本文\n\n## 参考文献・注記\n'
        self.assertTrue(figure_in_section(text,'一','x-2-a.svg'))
        self.assertFalse(figure_in_section(text,'二','x-2-a.svg'))
        self.assertFalse(figure_in_section(text,'三','x-2-a.svg'))

    def test_relative_links(self):
        self.assertEqual(map_url('../README.md'),'../index.html')
        self.assertEqual(map_url('one.md#test'),'one.html#test')
        self.assertEqual(map_url('https://example.org/a.md'),'https://example.org/a.md')
        self.assertEqual(map_url('../assets/a.svg'),'../assets/a.svg')

    def test_svg_rejects_executable_content(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.svg'
            p.write_text('<svg viewBox="0 0 10 10" role="img"><title>X</title><desc>Y</desc><script>alert(1)</script></svg>')
            self.assertTrue(any('forbidden SVG' in x for x in svg_errors(p)))

    def test_svg_rejects_external_href(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.svg'
            p.write_text('<svg viewBox="0 0 10 10" role="img"><title>X</title><desc>Y</desc><a href="https://example.org"/></svg>')
            self.assertTrue(any('external href' in x for x in svg_errors(p)))

    def test_svg_rejects_malformed_xml(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.svg';p.write_text('<svg>')
            self.assertTrue(svg_errors(p))

    def test_publish_defaults_to_dry_run(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/publish.py'),'--owner','example'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0)
        self.assertIn('DRY RUN',p.stdout)
        self.assertIn('private',p.stdout)

    def test_publish_rejects_path_injection(self):
        p=subprocess.run([sys.executable,str(ROOT/'scripts/publish.py'),'--owner','../bad'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)

    def test_build_refuses_source_overwrite(self):
        with self.assertRaises(RuntimeError):build(ROOT)

    def test_math_numeric_examples(self):
        self.assertEqual(12*11//2,66)
        self.assertEqual(3*(4*3//2)+2,20)
        self.assertEqual(1000*9//2+100-1,4599)
        self.assertEqual(2**24,16777216)
        self.assertEqual(6*2**4,96)
        self.assertEqual(64//16,4)

    def test_chapter_ids_and_sources_are_unique(self):
        data=json.loads((ROOT/'series.json').read_text())
        self.assertEqual(len(set(c['slug'] for c in data['chapters'])),12)
        for c in data['chapters']:
            self.assertEqual(len(c['sources']),len(set(c['sources'])))


    def test_complete_reader_links_and_math(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'reader'
            build(output)
            report=check(output)
            self.assertEqual(report['errors'],[])
            self.assertEqual(report['chapter_math'],report['standalone_math'])
            self.assertEqual(report['chapter_pages'],12)

    def test_combined_footnote_ids_are_namespaced(self):
        text='A[^a].\n\n[^a]: A source.\n'
        doc=Document(render(text,prefix='a-')+render(text,prefix='b-'))
        self.assertEqual(len(doc.ids),len(set(doc.ids)))

    def test_html_checker_detects_missing_target(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            (output/'index.html').write_text('<html><a href="missing.html">Link</a></html>')
            self.assertTrue(any('missing target' in e for e in check(output)['errors']))

    def test_html_checker_rejects_network_images(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            (output/'index.html').write_text('<html><img src="https://example.org/image.svg"></html>')
            self.assertTrue(any('external resource' in e for e in check(output)['errors']))

if __name__=='__main__':unittest.main()
