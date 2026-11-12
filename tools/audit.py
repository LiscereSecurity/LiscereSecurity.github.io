"""Site audit: SEO, links, languages and structured data on every published page.
Run from anywhere: python3 tools/audit.py   (exit code 1 if any ERROR)
"""
import collections
import html
import json
import os
import re
import sys
from urllib.parse import urlparse, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = "https://liscere.com/"
SKIP = {".git", ".github", "tools", "node_modules"}
errors, warns = [], []


def E(p, m): errors.append(f"ERROR {p}: {m}")
def W(p, m): warns.append(f"warn  {p}: {m}")


def files():
    for d, dirs, fs in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in fs:
            yield os.path.relpath(os.path.join(d, f), ROOT)


ALL = set(files())
PAGES = sorted(f for f in ALL if f.endswith(".html") and not f.startswith("assets/"))


def url_to_file(u):
    p = unquote(urlparse(u).path).lstrip("/")
    if p == "" or p.endswith("/"):
        p += "index.html"
    return p


def resolve(page, href):
    href = html.unescape(href)
    if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None, None
    if href.startswith("http"):
        if not href.startswith(SITE):
            return None, None
        href = "/" + href[len(SITE):]
    path, _, frag = href.partition("#")
    path = path.split("?")[0]
    if path == "":
        return page, frag
    base = os.path.dirname(page)
    target = os.path.normpath(path.lstrip("/") if path.startswith("/") else os.path.join(base, path))
    if path.endswith("/") or os.path.isdir(os.path.join(ROOT, target)):
        target = os.path.normpath(os.path.join(target, "index.html"))
    return target, frag


ids_cache = {}
def ids_of(f):
    if f not in ids_cache:
        s = open(os.path.join(ROOT, f), encoding="utf-8").read()
        ids_cache[f] = set(re.findall(r'\sid="([^"]+)"', s))
    return ids_cache[f]


titles, descs = collections.defaultdict(list), collections.defaultdict(list)
alt_map = {}
sitemap = open(os.path.join(ROOT, "sitemap.xml")).read()
in_sitemap = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))

for p in PAGES:
    s = open(os.path.join(ROOT, p), encoding="utf-8").read()
    head = s.split("</head>")[0]
    noindex = bool(re.search(r'name="robots" content="[^"]*noindex', head))
    lang = re.search(r'<html lang="([^"]+)"', s)
    if not lang: E(p, "no html lang")
    t = re.search(r"<title>(.*?)</title>", head, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', head)
    if not t: E(p, "no title")
    else:
        tt = html.unescape(t.group(1)); titles[tt].append(p)
        if not noindex and len(tt) > 70: W(p, f"title {len(tt)} chars: {tt}")
    if not noindex:
        if not d: E(p, "no meta description")
        else:
            dd = html.unescape(d.group(1)); descs[dd].append(p)
            if not 70 <= len(dd) <= 160: W(p, f"description {len(dd)} chars")
    if "Content-Security-Policy" not in head: E(p, "no CSP")
    if 'name="viewport"' not in head: E(p, "no viewport")
    h1 = len(re.findall(r"<h1[\s>]", s))
    if h1 != 1: E(p, f"{h1} h1 elements")
    can = re.search(r'<link rel="canonical" href="([^"]+)"', head)
    if not noindex:
        if not can: E(p, "no canonical")
        else:
            cu = can.group(1)
            if url_to_file(cu) != p: E(p, f"canonical {cu} does not point to this file")
            if cu not in in_sitemap: E(p, "indexable page not in sitemap")
        for prop in ("og:title", "og:description", "og:image", "og:url", "og:type"):
            if f'property="{prop}"' not in head: E(p, f"missing {prop}")
        if 'name="twitter:card"' not in head: W(p, "missing twitter:card")
        if "application/ld+json" not in head and "application/ld+json" not in s: W(p, "no JSON-LD")
    elif can and can.group(1) in in_sitemap:
        E(p, "noindex page listed in sitemap")
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(blk)
        except Exception as ex: E(p, f"JSON-LD does not parse: {ex}")
    alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', head))
    if alts:
        alt_map[p] = alts
        if can and can.group(1) not in alts.values(): E(p, "hreflang set does not include the page itself")
    # links and anchors
    for href in re.findall(r'(?:href|src)="([^"]+)"', s):
        tgt, frag = resolve(p, href)
        if tgt is None: continue
        if tgt not in ALL:
            E(p, f"broken link {href}")
        elif frag and tgt.endswith(".html") and frag not in ids_of(tgt) and frag not in ("top", "fieldnotes", "landscape", "research"):
            E(p, f"missing anchor {href}")
    # language switch points to the paired page (or the Polish notice)
    sw = re.search(r'<a class="lang-switch" href="([^"]+)"', s)
    if sw and alts and "tylko-po-angielsku" not in sw.group(1):
        tgt, _ = resolve(p, sw.group(1))
        other = [u for l, u in alts.items() if l not in ("x-default",) and url_to_file(u) != p]
        if other and tgt != url_to_file(other[0]): E(p, f"lang switch {sw.group(1)} is not the hreflang pair {other[0]}")
    for img in re.findall(r"<img\b[^>]*>", s):
        if "alt=" not in img: E(p, f"img without alt: {img[:80]}")
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<pre.*?</pre>", " ", s, flags=re.S)
    vis = html.unescape(re.sub(r"<[^>]+>", " ", vis))
    if "—" in vis: E(p, "em dash in visible text")
    if "lorem" in vis.lower() or "TODO" in vis: E(p, "placeholder text")

# hreflang reciprocity
for p, alts in alt_map.items():
    for l, u in alts.items():
        f = url_to_file(u)
        if f not in alt_map: E(p, f"hreflang {l} -> {u} has no hreflang set"); continue
        if set(alt_map[f].values()) != set(alts.values()): E(p, f"hreflang set differs from {f}")
for t, ps in titles.items():
    if len(ps) > 1: E(",".join(ps), f"duplicate title: {t}")
for d, ps in descs.items():
    if len(ps) > 1: E(",".join(ps), f"duplicate description")
for u in in_sitemap:
    if url_to_file(u) not in ALL: E("sitemap.xml", f"URL without file: {u}")
robots = open(os.path.join(ROOT, "robots.txt")).read()
if "Sitemap: https://liscere.com/sitemap.xml" not in robots: E("robots.txt", "no Sitemap line")

for line in errors + warns: print(line)
print(f"\n{len(PAGES)} pages, {len(errors)} errors, {len(warns)} warnings")
sys.exit(1 if errors else 0)
