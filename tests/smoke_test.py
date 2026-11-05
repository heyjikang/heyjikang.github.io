"""Lightweight checks for generated static HTML; Python stdlib only."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        opts = dict(attrs)
        if tag in ('a', 'script', 'img', 'link'):
            key = 'src' if tag in ('img', 'script') else 'href'
            if opts.get(key):
                self.links.append((tag, key, opts[key]))

def test():
    htmls = sorted(DIST.rglob('*.html'))
    assert htmls, 'No site generated'
    broken = []
    for file in htmls:
        parser = Links()
        parser.feed(file.read_text(encoding='utf-8'))
        for tag, key, url in parser.links:
            if url.startswith(('#', '//', 'mailto:', 'tel:', 'data:')):
                continue
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            target = (file.parent / unquote(parts.path)).resolve()
            if not target.is_relative_to(DIST.resolve()):
                broken.append(f'{file.relative_to(DIST)}: attempted path outside site: {url}')
            elif target.is_dir():
                if not (target / 'index.html').exists():
                    broken.append(f'{file.relative_to(DIST)}: directory without index: {url}')
            elif not target.exists():
                broken.append(f'{file.relative_to(DIST)}: missing {url}')
    ET.parse(DIST / 'feed.xml')
    if (DIST / 'sitemap.xml').exists():
        ET.parse(DIST / 'sitemap.xml')
    assert (DIST / '.nojekyll').exists(), '.nojekyll is missing'
    assert not broken, '\n'.join(broken)
    print(f'OK: {len(htmls)} HTML pages, relative links/assets and RSS are valid.')

if __name__ == '__main__':
    test()
