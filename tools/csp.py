"""Add or refresh the Content Security Policy and referrer meta tags on every page.
Inline scripts (other than JSON-LD) are allowed by their SHA-256 hash, computed here,
so re-run this after editing any inline script."""
import re, glob, hashlib, base64, os
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + "/"
os.chdir(ROOT)
fs = sorted(glob.glob('*.html') + glob.glob('services/*.html') + glob.glob('research/*/index.html') + glob.glob('pl/*.html') + glob.glob('pl/uslugi/*.html'))
for f in fs:
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'  <meta http-equiv="Content-Security-Policy"[^>]*>\n', '', s)
    s = re.sub(r'  <meta name="referrer"[^>]*>\n', '', s)
    hashes = []
    for m in re.finditer(r'<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>(.*?)</script>', s, re.S):
        h = base64.b64encode(hashlib.sha256(m.group(1).encode('utf-8')).digest()).decode()
        hashes.append(f"'sha256-{h}'")
    script = " ".join(["'self'"] + hashes)
    csp = ("default-src 'self'; script-src " + script + "; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
           "font-src 'self'; media-src 'self'; connect-src 'self'; object-src 'self'; frame-src 'self'; "
           "base-uri 'self'; form-action 'self'; upgrade-insecure-requests")
    tags = f'  <meta http-equiv="Content-Security-Policy" content="{csp}">\n  <meta name="referrer" content="strict-origin-when-cross-origin">\n'
    s, n = re.subn(r'(<meta charset="utf-8"\s*/?>\n)', lambda m: m.group(1) + tags, s, count=1)
    if n != 1:
        print("no charset meta in", f)
    open(f, 'w', encoding='utf-8').write(s)
print("csp on", len(fs), "pages")
