"""Render the five newest published videos from the Research playlist feed."""
from datetime import datetime
from html import escape
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET

PLAYLIST = 'PLuRYpfDLgzSKk17CeJCtnyi84Y7XvPaBV'
FEED = f'https://www.youtube.com/feeds/videos.xml?playlist_id={PLAYLIST}'
PAGE = Path(__file__).resolve().parents[1] / 'videos/index.html'
NS = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
START = '<!-- latest-videos:start -->'
END = '<!-- latest-videos:end -->'


def latest_videos(xml):
    root = ET.fromstring(xml)
    if root.findtext('yt:playlistId', namespaces=NS) != PLAYLIST:
        raise ValueError('Unexpected playlist feed; keeping existing videos.')
    videos = {}
    for entry in root.findall('atom:entry', NS):
        video_id = entry.findtext('yt:videoId', namespaces=NS) or ''
        title = entry.findtext('atom:title', namespaces=NS)
        published = entry.findtext('atom:published', namespaces=NS)
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id) or not title or not published:
            raise ValueError('Invalid video metadata; keeping existing videos.')
        videos[video_id] = (datetime.fromisoformat(published.replace('Z', '+00:00')), video_id, title)
    if len(videos) < 5:
        raise ValueError('Feed contains fewer than five videos; keeping existing videos.')
    return sorted(videos.values(), reverse=True)[:5]


def render(videos):
    articles = []
    for published, video_id, title in videos:
        title = escape(title, quote=True)
        articles.append(f'''<article class="research-video">
  <h3><a href="https://www.youtube.com/watch?v={video_id}">{title}</a></h3>
  <p class="video-date"><time datetime="{published.date().isoformat()}">{published.strftime('%d %B %Y')}</time></p>
  <iframe class="playlist-player"
    src="https://www.youtube-nocookie.com/embed/{video_id}"
    title="{title}"
    width="750" height="422" loading="lazy"
    referrerpolicy="strict-origin-when-cross-origin"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</article>''')
    return '\n'.join(articles)


def main():
    with urllib.request.urlopen(FEED, timeout=30) as response:
        videos = latest_videos(response.read())
    page = PAGE.read_text()
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError('Missing or duplicate video markers.')
    before, rest = page.split(START)
    _, after = rest.split(END)
    PAGE.write_text(before + START + '\n' + render(videos) + '\n' + END + after)
    print('Rendered five videos, newest publication first:')
    for date, _, title in videos:
        print(date.date(), title)


if __name__ == '__main__':
    main()
