"""Publish the six most-starred repositories in the public mystuff list."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.request
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LIST_URL = 'https://github.com/stars/giulioturrisi/lists/mystuff'
START = '<!-- software:start -->'
END = '<!-- software:end -->'


class ListParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = False
        self.repositories = []
        self.next_page = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('h2', 'h3'):
            self.heading = True
        if tag == 'a':
            href = a.get('href', '')
            if self.heading and re.fullmatch(r'/[\w.-]+/[\w.-]+', href):
                self.repositories.append(href.lstrip('/'))
            if 'next' in a.get('rel', '').split() or 'next_page' in a.get('class', '').split():
                self.next_page = href

    def handle_endtag(self, tag):
        if tag in ('h2', 'h3'):
            self.heading = False


def fetch(url):
    headers = {'User-Agent': 'GiulioTurrisi-website-software-sync'}
    if urlsplit(url).netloc == 'api.github.com':
        headers['Accept'] = 'application/vnd.github+json'
        token = os.environ.get('GH_TOKEN')
        if token:
            headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode(response.headers.get_content_charset() or 'utf-8')


def list_repositories():
    url = LIST_URL
    visited = set()
    repositories = set()
    while url:
        if url in visited:
            raise ValueError('Repeated list pagination URL.')
        parsed = urlsplit(url)
        if parsed.netloc != 'github.com' or parsed.path != urlsplit(LIST_URL).path:
            raise ValueError('Unexpected list pagination URL.')
        visited.add(url)
        parser = ListParser()
        parser.feed(fetch(url))
        if not parser.repositories:
            raise ValueError('No repositories found; the list may be private or unavailable.')
        repositories.update(parser.repositories)
        url = urljoin(url, parser.next_page) if parser.next_page else None
    return sorted(repositories)


def repository_metadata(name):
    data = json.loads(fetch(f'https://api.github.com/repos/{name}'))
    if data.get('private') is not False:
        raise ValueError('Expected a public repository.')
    full_name = data.get('full_name', '')
    stars = data.get('stargazers_count')
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', full_name) or type(stars) is not int or stars < 0:
        raise ValueError('Invalid repository metadata.')
    return {'name': full_name, 'url': f'https://github.com/{full_name}',
            'description': data.get('description') or '', 'stars': stars}


def select_top(repositories):
    unique = {r['name'].casefold(): r for r in repositories}
    if len(unique) < 6:
        raise ValueError('The list has fewer than six repositories; preserving existing software.')
    return sorted(unique.values(), key=lambda r: (-r['stars'], r['name'].casefold()))[:6]


def render(repositories):
    repositories = select_top(repositories)
    items = []
    for r in repositories:
        items.append(f'<li><h3><a href="{escape(r["url"], quote=True)}">{escape(r["name"])}</a> '
                     f'<span class="repo-stars" aria-label="{r["stars"]} stars">★ {r["stars"]:,}</span></h3>'
                     f'<p>{escape(r["description"])}</p></li>')
    return ('<p>The six most-starred repositories in my '
            f'<a href="{LIST_URL}">mystuff list</a>, ordered by stars.</p>\n'
            '<ul class="projects">\n' + '\n'.join(items) + '\n</ul>')


def update_page(page, repositories):
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError('Missing or duplicate software markers.')
    before, rest = page.split(START)
    _, after = rest.split(END)
    return before + START + '\n' + render(repositories) + '\n' + END + after


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-only', action='store_true')
    args = parser.parse_args()
    cache = ROOT / 'data/software.json'
    if args.render_only:
        repositories = json.loads(cache.read_text())
    else:
        names = list_repositories()
        with ThreadPoolExecutor(max_workers=4) as pool:
            repositories = select_top(list(pool.map(repository_metadata, names)))
    page = ROOT / 'index.html'
    updated = update_page(page.read_text(), repositories)
    if not args.render_only:
        cache.parent.mkdir(exist_ok=True)
        cache.write_text(json.dumps(repositories, ensure_ascii=False, indent=2) + '\n')
    page.write_text(updated)
    for r in repositories:
        print(f'{r["stars"]:>6} stars  {r["name"]}')


if __name__ == '__main__':
    main()
