"""Build sitemap.xml from the pages themselves.

Every published .html page is read: its canonical URL becomes <loc>, its rel="alternate" hreflang
links become xhtml:link pairs, and pages marked noindex (or without a canonical) are left out.
<lastmod> changes only when the visible text of a page changes (tools/sitemap_state.json keeps a
hash per URL), so a cache-busting version bump does not mark every page as modified.
Run from anywhere: python3 tools/gen_sitemap.py
"""
import datetime
import hashlib
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE = os.path.join(HERE, "sitemap_state.json")
SKIP_DIRS = {".git", ".github", "tools", "assets", "node_modules"}
TODAY = datetime.date.today().isoformat()


def pages():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            if f.endswith(".html"):
                yield os.path.join(d, f)


def text_hash(s):
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S)
    body = re.sub(r"<head>.*?</head>", lambda m: " ".join(re.findall(r'<title>.*?</title>|name="description" content="[^"]*"', m.group(0))), body, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return hashlib.sha256(" ".join(text.split()).encode()).hexdigest()[:16]


def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    entries = []
    for path in pages():
        s = open(path, encoding="utf-8").read()
        if re.search(r'<meta name="robots" content="[^"]*noindex', s):
            continue
        can = re.search(r'<link rel="canonical" href="([^"]+)"', s)
        if not can:
            continue
        url = can.group(1)
        alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', s)
        h = text_hash(s)
        old = state.get(url)
        lastmod = old[1] if old and old[0] == h else TODAY
        state[url] = [h, lastmod]
        entries.append((url, lastmod, alts))
    entries.sort(key=lambda e: (e[0] != "https://liscere.com/", e[0]))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for url, lastmod, alts in entries:
        out += ["  <url>", f"    <loc>{url}</loc>", f"    <lastmod>{lastmod}</lastmod>"]
        out += [f'    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in alts]
        out.append("  </url>")
    out.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(out) + "\n")
    json.dump({u: state[u] for u, _, _ in entries}, open(STATE, "w"), indent=1, sort_keys=True)
    print(f"sitemap: {len(entries)} URLs")


if __name__ == "__main__":
    main()
