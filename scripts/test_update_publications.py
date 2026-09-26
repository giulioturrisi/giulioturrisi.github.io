import unittest
from html import escape
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path
import update_publications as pub


def row(i, year=2026):
    # Deliberately reverse alphabetical title order and unrelated citation counts.
    return f'''<tr class="gsc_a_tr"><td><a class="gsc_a_at" href="/citations?citation_for_view=yt9v8skAAAAJ:paper{i}">{chr(90-i)} &amp; control</a><div class="gs_gray">A Author, G Turrisi</div><div class="gs_gray">Journal <span>, {year}</span></div></td><td class="gsc_a_c">{i*100}</td><td class="gsc_a_y"><span>{year}</span></td></tr>'''


class PublicationTests(unittest.TestCase):
    def test_keeps_scholar_order_and_ten_unique(self):
        html = row(0) + row(0) + ''.join(row(i, 2026 if i < 6 else 2025) for i in range(1, 12))
        papers = pub.parse_publications(html)
        self.assertEqual(len(papers), 10)
        self.assertEqual([p['title'][0] for p in papers], [chr(90-i) for i in range(10)])
        self.assertEqual(papers[0]['venue'], 'Journal , 2026')
        self.assertIn('&amp;', pub.render(papers))

    def test_rejects_blocked_partial_and_unordered_responses(self):
        for html in ['<html>CAPTCHA</html>', row(0), ''.join(row(i, 2025 if i==0 else 2026) for i in range(10))]:
            with self.assertRaises(ValueError): pub.parse_publications(html)

    def test_render_preserves_other_sections(self):
        papers = pub.parse_publications(''.join(row(i) for i in range(10)))
        page = 'biography'+pub.START+'old'+pub.END+'videos'
        updated = pub.update_page(page, papers)
        self.assertTrue(updated.startswith('biography'+pub.START))
        self.assertTrue(updated.endswith(pub.END+'videos'))
        self.assertEqual(updated.count('<li>'),10)
        self.assertEqual(updated,pub.update_page(updated,papers))

    def test_fetch_failure_preserves_data(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);(root/'data').mkdir()
            (root/'data/publications.json').write_text('previous data')
            (root/'index.html').write_text('previous page')
            with patch.object(pub,'ROOT',root), patch('sys.argv',['update_publications.py']), patch.object(pub.urllib.request,'urlopen',side_effect=OSError('blocked')):
                with self.assertRaises(OSError): pub.main()
            self.assertEqual((root/'data/publications.json').read_text(),'previous data')
            self.assertEqual((root/'index.html').read_text(),'previous page')


if __name__=='__main__':unittest.main()
