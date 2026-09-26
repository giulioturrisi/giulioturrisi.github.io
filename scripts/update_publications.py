"""Fetch Scholar's ten latest publications in its chronological ordering."""
import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urljoin, urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://scholar.google.com/citations?user=yt9v8skAAAAJ&hl=en&sortby=pubdate&pagesize=100'
START = '<!-- publications:start -->'
END = '<!-- publications:end -->'


class ScholarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.field = None
        self.depth = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'tr' and 'gsc_a_tr' in classes:
            self.row = {'details': []}
        if self.row is None:
            return
        if self.field:
            if tag not in ('br', 'img', 'wbr', 'input', 'hr', 'meta', 'link'):
                self.depth += 1
            return
        if tag == 'a' and 'gsc_a_at' in classes:
            self.field = 'title'
            self.row['url'] = urljoin('https://scholar.google.com', attrs.get('href', ''))
        elif tag == 'div' and 'gs_gray' in classes:
            self.field = 'details'
        elif tag == 'td' and 'gsc_a_y' in classes:
            self.field = 'year'
        if self.field:
            self.depth = 1
            self.text = []

    def handle_data(self, data):
        if self.field:
            self.text.append(data)

    def handle_endtag(self, tag):
        if self.field:
            self.depth -= 1
            if self.depth == 0:
                value = ' '.join(''.join(self.text).split())
                if self.field == 'details':
                    self.row['details'].append(value)
                else:
                    self.row[self.field] = value
                self.field = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def parse_publications(html):
    parser = ScholarParser()
    parser.feed(html)
    papers = []
    seen = set()
    for row in parser.rows:
        url = urlsplit(row.get('url', ''))
        citation = parse_qs(url.query).get('citation_for_view', [''])[0]
        if not citation.startswith('yt9v8skAAAAJ:') or citation in seen:
            continue
        if not row.get('title') or not re.fullmatch(r'\d{4}', row.get('year', '')):
            raise ValueError('Incomplete publication metadata; keeping existing data.')
        if len(row['details']) < 2:
            raise ValueError('Missing publication authors or venue.')
        seen.add(citation)
        papers.append({'title': row['title'], 'authors': row['details'][0],
                       'venue': row['details'][1], 'year': int(row['year']),
                       'url': row['url']})
        if len(papers) == 10:
            break
    if len(papers) != 10:
        raise ValueError('Scholar did not return ten valid publications (possibly blocked). Existing list preserved.')
    # Do not sort titles or citations: preserve Scholar's pubdate order within a year.
    if any(a['year'] < b['year'] for a, b in zip(papers, papers[1:])):
        raise ValueError('Scholar returned a non-chronological list.')
    return papers


def render(papers):
    if len(papers) != 10:
        raise ValueError('Expected ten publications.')
    return '<ol class="publications">\n' + '\n'.join(
        f'<li><a href="{escape(p["url"], quote=True)}"><strong>{escape(p["title"])}</strong></a><br>'
        f'{escape(p["authors"])}<br><em>{escape(p["venue"])}</em></li>' for p in papers
    ) + '\n</ol>'


def update_page(page, papers):
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError('Publication markers missing or duplicated.')
    before, rest = page.split(START)
    _, after = rest.split(END)
    return before + START + '\n' + render(papers) + '\n' + END + after


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render-only', action='store_true')
    args = parser.parse_args()
    data = ROOT / 'data/publications.json'
    if args.render_only:
        papers = json.loads(data.read_text())
    else:
        with urllib.request.urlopen(SOURCE, timeout=30) as response:
            papers = parse_publications(response.read().decode(response.headers.get_content_charset() or 'utf-8'))
    page = ROOT / 'index.html'
    updated = update_page(page.read_text(), papers)
    if not args.render_only:
        data.parent.mkdir(exist_ok=True)
        data.write_text(json.dumps(papers, ensure_ascii=False, indent=2) + '\n')
    page.write_text(updated)
    print('Rendered ten publications in Scholar publication-date order (newest first).')


if __name__ == '__main__':
    main()
