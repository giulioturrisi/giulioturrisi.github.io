import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory
import update_bio as bio


class BiographyTests(unittest.TestCase):
    def test_markdown_and_contacts(self):
        rendered = bio.render_bio('A **robotics** researcher at [IIT](https://iit.it).\n\nA new paragraph.\n\nContact: a@example.org\nOther sites: [GitHub](https://github.com)')
        self.assertIn('<strong>robotics</strong>', rendered)
        self.assertIn('href="https://iit.it"', rendered)
        self.assertIn('<p>A new paragraph.</p>', rendered)
        self.assertNotIn('Contact:', rendered)
        self.assertNotIn('Other sites:', rendered)

    def test_preserves_surrounding_page_and_is_repeatable(self):
        original = 'photo and contacts' + bio.START + 'old bio' + bio.END + 'navigation'
        updated = bio.update_page(original, 'New biography.')
        self.assertTrue(updated.startswith('photo and contacts' + bio.START))
        self.assertTrue(updated.endswith(bio.END + 'navigation'))
        self.assertEqual(updated, bio.update_page(updated, 'New biography.'))

    def test_invalid_source_and_markers(self):
        for readme in ['', 'Contact: email\nOther sites: links']:
            with self.assertRaises(ValueError):
                bio.render_bio(readme)
        for page in ['', bio.END + bio.START, bio.START * 2 + bio.END]:
            with self.assertRaises(ValueError):
                bio.update_page(page, 'A biography.')
        self.assertNotIn('<script>', bio.render_bio('<script>alert(1)</script>'))

    def test_fetch_failure_preserves_files(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('original homepage')
            (root / 'profile-readme.md').write_text('original snapshot')
            with patch.object(bio, 'ROOT', root), patch.object(bio.urllib.request, 'urlopen', side_effect=OSError('offline')):
                with self.assertRaises(OSError):
                    bio.main()
            self.assertEqual((root / 'index.html').read_text(), 'original homepage')
            self.assertEqual((root / 'profile-readme.md').read_text(), 'original snapshot')


if __name__ == '__main__':
    unittest.main()
