"""Add or refresh the Content Security Policy, the referrer meta tag and the Cloudflare
Web Analytics snippet on every page.
Inline scripts (other than JSON-LD) are allowed by their SHA-256 hash, computed here,
so re-run this after editing any inline script."""
import re, glob, hashlib, base64, os
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + "/"
os.chdir(ROOT)
# Cloudflare Web Analytics (cookieless). Set CF_TOKEN to "" to remove the snippet from every page.
CF_TOKEN = "3280d901c4be4657ba0562ac10e607b7"
CF_SNIPPET = ("  <!-- Cloudflare Web Analytics --><script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
              "data-cf-beacon='{\"token\": \"%s\"}'></script><!-- End Cloudflare Web Analytics -->\n" % CF_TOKEN)
fs = sorted(glob.glob('*.html') + glob.glob('services/*.html') + glob.glob('research/*/index.html') + glob.glob('pl/*.html') + glob.glob('pl/uslugi/*.html'))
for f in fs:
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'  <meta http-equiv="Content-Security-Policy"[^>]*>\n', '', s)
    s = re.sub(r'  <meta name="referrer"[^>]*>\n', '', s)
    s = re.sub(r'  <!-- Cloudflare Web Analytics -->.*?<!-- End Cloudflare Web Analytics -->\n', '', s)
    if CF_TOKEN:
        s = s.replace("</body>", CF_SNIPPET + "</body>", 1)
    hashes = []
    for m in re.finditer(r'<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>(.*?)</script>', s, re.S):
        h = base64.b64encode(hashlib.sha256(m.group(1).encode('utf-8')).digest()).decode()
        hashes.append(f"'sha256-{h}'")
    script = " ".join(["'self'"] + hashes)
    csp = ("default-src 'self'; script-src " + script + (" https://static.cloudflareinsights.com" if CF_TOKEN else "") + "; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
           "font-src 'self'; media-src 'self'; connect-src 'self' https://formspree.io" + (" https://cloudflareinsights.com" if CF_TOKEN else "") + "; object-src 'self'; frame-src 'self'; "
           "base-uri 'self'; form-action 'self'; upgrade-insecure-requests")
    tags = f'  <meta http-equiv="Content-Security-Policy" content="{csp}">\n  <meta name="referrer" content="strict-origin-when-cross-origin">\n'
    s, n = re.subn(r'(<meta charset="utf-8"\s*/?>\n)', lambda m: m.group(1) + tags, s, count=1)
    if n != 1:
        print("no charset meta in", f)
    open(f, 'w', encoding='utf-8').write(s)
print("csp on", len(fs), "pages")
