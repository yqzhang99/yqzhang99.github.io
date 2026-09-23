"""Export the live public journal to the existing GitHub Pages address.

Run from the GitHub repository workflow. Content remains editable in the Site backend;
GitHub Pages receives a static snapshot on each scheduled run.
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ORIGIN='https://yiqing-personal-journal.gottenelm.chatgpt.site'
OUTPUT=Path(sys.argv[1] if len(sys.argv)>1 else 'site-export').resolve()
OUTPUT.mkdir(parents=True,exist_ok=True)

def fetch(path):
    req=urllib.request.Request(ORIGIN+path,headers={'User-Agent':'yiqing-pages-mirror/1.0'})
    with urllib.request.urlopen(req,timeout=45) as response:return response.read()

routes=json.loads(fetch('/api/public-routes'))['paths']
assert '/' in routes and '/Me/introduction/' in routes and '/Movie/movie/' in routes and '/Travel/travel/' in routes

def public_asset(match,path):
    prefix,url,quote=match.groups()
    if url.startswith(('data:','https:','http:','mailto:','#')):return match.group(0)
    return prefix+html.escape(urllib.parse.urljoin(ORIGIN+path,url),quote=True)+quote

asset_pattern=re.compile(r'(<(?:link|script|img|source|video)\b[^>]*?\b(?:href|src)=\s*["\'])([^"\']+)(["\'])',re.I)
image_link_pattern=re.compile(r'(<a\b[^>]*?\bhref=\s*["\'])(/[^"\']+)(["\'])',re.I)
def picture_link(match):
    path=match.group(2)
    if path.startswith('/media/') or re.search(r'\.(?:jpe?g|png|webp|gif|svg|mp4)$',path,re.I):
        return match.group(1)+html.escape(ORIGIN+path,quote=True)+match.group(3)
    return match.group(0)
for path in routes:
    if not path.startswith('/') or '..' in path or not path.endswith('/'):
        raise ValueError('Unexpected public route')
    page=fetch(path).decode('utf-8')
    if '<html' not in page.lower():raise ValueError('Unexpected response: '+path)
    page=asset_pattern.sub(lambda match:public_asset(match,path),page)
    page=image_link_pattern.sub(picture_link,page)
    page=page.replace('href="/studio/"',f'href="{ORIGIN}/studio/"')
    destination=OUTPUT/path.lstrip('/')/'index.html'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(page,encoding='utf-8')

(OUTPUT/'.nojekyll').write_text('',encoding='utf-8')
print(f'Exported {len(routes)} public pages to GitHub Pages')
