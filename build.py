#!/usr/bin/env python3
"""Build an entirely static, SEO-friendly personal archive.

Content: content/notes/*.md, content/projects.yml, config.yml
Output:  dist/ (uploadable to GitHub Pages)
No JavaScript or backend is required to render written articles.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

import mistune
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
CONTENT = ROOT / 'content'
TEMPLATE_DIR = ROOT / 'templates'
STATIC = ROOT / 'static'


def load_yaml(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def calculated_url(configured: str) -> str:
    configured = (configured or '').strip()
    if configured:
        if not configured.startswith(('https://', 'http://')):
            raise ValueError('config.yml: site.url 应当以 https:// 或 http:// 开头')
        return configured.rstrip('/') + '/'
    # On GitHub Actions the repository is known, even for project subpaths.
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    if '/' not in repo:
        return ''
    owner, name = repo.split('/', 1)
    if not owner or not name:
        return ''
    if name.lower() == f'{owner.lower()}.github.io':
        return f'https://{owner}.github.io/'
    return f'https://{owner}.github.io/{quote(name)}/'


def load_notes() -> list[dict]:
    notes = []
    markdown = mistune.create_markdown(escape=True, plugins=['strikethrough', 'table', 'url'])
    seen = set()
    for path in sorted((CONTENT / 'notes').glob('*.md')):
        raw = path.read_text(encoding='utf-8')
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
        if not match:
            raise ValueError(f'{path.name}: 需要以 --- YAML --- 开头')
        meta = yaml.safe_load(match.group(1)) or {}
        if meta.get('draft', False):
            continue
        required = ('title', 'slug', 'date', 'category', 'description')
        for key in required:
            if not meta.get(key):
                raise ValueError(f'{path.name}: 缺少必填字段 {key}')
        slug = str(meta['slug'])
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError(f'{path.name}: slug 只能包含小写英文、数字和连接符')
        if slug in seen:
            raise ValueError(f'文章 slug 重复: {slug}')
        seen.add(slug)
        date = meta['date']
        if isinstance(date, dt.datetime):
            date = date.date()
        elif isinstance(date, str):
            date = dt.date.fromisoformat(date)
        if not isinstance(date, dt.date):
            raise ValueError(f'{path.name}: 日期格式应为 YYYY-MM-DD')
        meta.update({
            'date_iso': date.isoformat(),
            'display_date': date.strftime('%Y.%m.%d'),
            'html': markdown(match.group(2).strip()),
            'plain_text': match.group(2).strip(),
            'sample': bool(meta.get('sample', False)),
            'reading_time': int(meta.get('reading_time', 3)),
            'number': str(meta.get('number', f'{len(notes)+1:02d}')),
        })
        notes.append(meta)
    notes.sort(key=lambda a: a['date_iso'], reverse=True)
    return notes


def schema(site: dict, base: str, note: dict | None = None) -> str:
    person = {
        '@context': 'https://schema.org', '@type': 'Person',
        'name': site['name'], 'alternateName': [site['brand'], 'Jikang', 'liujikang'],
        'description': site['description'],
        'sameAs': [site['github']],
        'alumniOf': {'@type': 'CollegeOrUniversity', 'name': '长安大学'},
    }
    if base:
        person['url'] = base
        person['image'] = base + 'assets/portrait.webp'
    if note:
        data = {
            '@context': 'https://schema.org', '@type': 'BlogPosting',
            'headline': note['title'], 'description': note['description'],
            'datePublished': note['date_iso'], 'dateModified': note['date_iso'],
            'author': {'@type': 'Person', 'name': site['name']},
            'inLanguage': 'zh-CN',
        }
        if base:
            data['mainEntityOfPage'] = base + f'notes/{note["slug"]}/'
        out = json.dumps([person, data], ensure_ascii=False)
    else:
        out = json.dumps(person, ensure_ascii=False)
    # The JSON is embedded in <script>: make the content inert even if edited later.
    return out.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def xml_cdata(value: str) -> str:
    return '<![CDATA[' + str(value).replace(']]>', ']]]]><![CDATA[>') + ']]>'


def main():
    settings = load_yaml(ROOT / 'config.yml')
    site = settings['site']
    base = calculated_url(site.get('url', ''))
    notes = load_notes()
    projects = load_yaml(CONTENT / 'projects.yml') or []
    if not isinstance(projects, list):
        raise ValueError('projects.yml 格式应为 YAML 数组')
    for project in projects:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', project['slug']):
            raise ValueError('project slug 只能包含小写英文、数字和 -')
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(['html', 'xml']), trim_blocks=True, lstrip_blocks=True)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for thing in STATIC.iterdir():
        dst = DIST / thing.name
        if thing.is_dir():
            shutil.copytree(thing, dst)
        else:
            shutil.copy2(thing, dst)
    (DIST / '.nojekyll').write_text('', encoding='utf-8')

    def render(template: str, relative: str, title: str, description: str, root: str, **kwargs):
        file = DIST / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        canonical = (base + relative.replace('index.html', '')) if base else ''
        data = {
            'site': site, 'site_url': base, 'root': root,
            'page_title': title, 'description': description,
            'canonical': canonical,
            'schema_json': schema(site, base, kwargs.get('note')),
            **kwargs,
        }
        file.write_text(env.get_template(template).render(**data), encoding='utf-8')
        print(f'  ✓ {relative}')

    render('index.html', 'index.html', f'{site["name"]} {site["brand"]} | {site["subtitle"]}', site['description'], './', notes=notes, projects=projects, project=projects[0] if projects else None, body_class='homepage')
    counts = {}
    for n in notes:
        counts[n['category']] = counts.get(n['category'], 0) + 1
    categories = [{'name': key, 'count': value} for key, value in counts.items()]
    render('notes.html', 'notes/index.html', f'文字档案 | {site["name"]}', '记录 AI 实践、成长与思考的文字档案。', '../', notes=notes, categories=categories, body_class='listing-page')
    for n in notes:
        related = [other for other in notes if other['slug'] != n['slug']][:2]
        render('article.html', f'notes/{n["slug"]}/index.html', f'{n["title"]} | {site["name"]}', n['description'], '../../', note=n, related=related, robots='noindex, follow' if n['sample'] else 'index, follow', og_type='article', body_class='reading-page')
    for p in projects:
        render('project.html', f'projects/{p["slug"]}/index.html', f'{p["title"]} {p["subtitle"]} | {site["name"]}', p['description'], '../../', project=p, body_class='project-page')
    render('404.html', '404.html', f'找不到这一页 | {site["name"]}', '这一页尚未被写下。', './', body_class='error-page')

    urls = [''] + ['notes/'] + [f'notes/{n["slug"]}/' for n in notes if not n['sample']] + [f'projects/{p["slug"]}/' for p in projects]
    if base:
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for path in urls:
            sitemap += '  <url><loc>' + xml_escape(base + path) + '</loc></url>\n'
        sitemap += '</urlset>\n'
        (DIST / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    robots = 'User-agent: *\nAllow: /\n'
    if base:
        robots += f'Sitemap: {base}sitemap.xml\n'
    (DIST / 'robots.txt').write_text(robots, encoding='utf-8')

    rss = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
    rss += f'<title>{xml_escape(site["brand"])} · 文字档案</title>\n'
    rss += f'<link>{xml_escape(base or "./")}</link>\n'
    rss += f'<description>{xml_escape(site["description"])}</description>\n'
    rss += '<language>zh-cn</language>\n'
    for n in notes:
        if n['sample']:
            continue  # example drafts remain visible, but are not syndicated
        url = (base or './') + f'notes/{n["slug"]}/'
        rss += '<item>\n'
        rss += f'<title>{xml_escape(n["title"])}</title><link>{xml_escape(url)}</link><guid>{xml_escape(url)}</guid>\n'
        rss += f'<pubDate>{dt.datetime.strptime(n["date_iso"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate>\n'
        rss += f'<description>{xml_cdata(n["description"])}</description>\n'
        rss += '</item>\n'
    rss += '</channel></rss>\n'
    (DIST / 'feed.xml').write_text(rss, encoding='utf-8')
    print(f'\nGenerated {len(notes)} notes, {len(projects)} project(s).')
    print('Canonical base:', base or '(not set; automatically set on GitHub Actions)')


if __name__ == '__main__':
    main()
