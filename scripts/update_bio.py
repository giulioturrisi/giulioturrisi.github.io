"""Synchronize the homepage biography from the public GitHub profile README."""
from pathlib import Path
import re
import urllib.request

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://raw.githubusercontent.com/giulioturrisi/giulioturrisi/master/README.md'
START = '<!-- profile-bio:start -->'
END = '<!-- profile-bio:end -->'


def render_bio(readme):
    # Contacts already live beside the photo; omit only their labeled lines.
    biography = '\n'.join(
        line for line in readme.splitlines()
        if not re.match(r'^\s*(Contact|Other sites)\s*:', line, re.IGNORECASE)
    ).strip()
    if not biography:
        raise ValueError('Empty biography; keeping the existing homepage.')
    return MarkdownIt('commonmark', {'html': False}).render(biography).strip()


def update_page(page, readme):
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError('Missing or duplicate biography markers.')
    before, rest = page.split(START)
    if END not in rest:
        raise ValueError('Biography markers are out of order.')
    _, after = rest.split(END)
    return before + START + '\n' + render_bio(readme) + '\n' + END + after


def main():
    with urllib.request.urlopen(SOURCE, timeout=30) as response:
        readme = response.read().decode('utf-8')
    page = ROOT / 'index.html'
    updated = update_page(page.read_text(), readme)
    page.write_text(updated)
    (ROOT / 'profile-readme.md').write_text(readme)
    print('Homepage biography synchronized from giulioturrisi/giulioturrisi (master).')


if __name__ == '__main__':
    main()
