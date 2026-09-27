import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path
import update_software as software


def repo(i, stars):
    return {'name':f'owner/repo{i}', 'url':f'https://github.com/owner/repo{i}', 'stars':stars, 'description':'Tools & <robots>'}


class SoftwareTests(unittest.TestCase):
    def test_top_six_and_ties(self):
        repos=[repo(i,i*10) for i in range(9)]
        repos.extend([repo(8,80),repo(9,80)])
        top=software.select_top(repos)
        self.assertEqual([r['name'] for r in top],['owner/repo8','owner/repo9','owner/repo7','owner/repo6','owner/repo5','owner/repo4'])
        self.assertEqual(len(top),6)

    def test_list_parsing_and_pagination(self):
        first='<h2><a href="/owner/one">one</a></h2><a href="/outside/repo">ignore</a><a rel="next" href="?page=2">Next</a>'
        second='<h3><a href="/owner/two">two</a></h3>'
        with patch.object(software,'fetch',side_effect=[first,second]) as fetch:
            self.assertEqual(software.list_repositories(),['owner/one','owner/two'])
            self.assertEqual(fetch.call_args.args[0],software.LIST_URL+'?page=2')
        with patch.object(software,'fetch',return_value='<h1>Sign in</h1>'):
            with self.assertRaises(ValueError):software.list_repositories()

    def test_invalid_pagination_is_rejected(self):
        html='<h2><a href="/owner/one">one</a></h2><a rel="next" href="https://example.com">Next</a>'
        with patch.object(software,'fetch',return_value=html) as fetch:
            with self.assertRaises(ValueError):software.list_repositories()
            self.assertEqual(fetch.call_count,1)

    def test_render_is_escaped_and_preserves_surroundings(self):
        repos=[repo(i,i) for i in range(6)]
        page='bio'+software.START+'old'+software.END+'videos'
        updated=software.update_page(page,repos)
        self.assertTrue(updated.startswith('bio'+software.START))
        self.assertTrue(updated.endswith(software.END+'videos'))
        self.assertIn('Tools &amp; &lt;robots&gt;',updated)
        self.assertEqual(updated.count('<li>'),6)
        self.assertEqual(updated,software.update_page(updated,repos))

    def test_failure_preserves_snapshot(self):
        with TemporaryDirectory() as directory:
            root=Path(directory);(root/'data').mkdir()
            (root/'data/software.json').write_text('old data')
            (root/'index.html').write_text('old page')
            with patch.object(software,'ROOT',root),patch('sys.argv',['update_software.py']),patch.object(software,'fetch',side_effect=OSError('offline')):
                with self.assertRaises(OSError):software.main()
            self.assertEqual((root/'data/software.json').read_text(),'old data')
            self.assertEqual((root/'index.html').read_text(),'old page')


if __name__=='__main__':unittest.main()
