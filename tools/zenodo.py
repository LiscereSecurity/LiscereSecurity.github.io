"""Deposit the research reports on Zenodo and get a DOI for each.

The metadata comes from the site itself (gen_articles.py and data_reports.py), so a report is
described on Zenodo exactly as it is on liscere.com. The PDF uploaded is the one the site serves.

    export ZENODO_TOKEN=...            # personal access token, scopes: deposit:write deposit:actions
    python3 tools/zenodo.py --list     # what would be deposited, nothing sent
    python3 tools/zenodo.py --draft    # create or update the drafts, upload the PDFs
    python3 tools/zenodo.py --publish LTR-2026-01   # publish one, which mints the DOI

Drafts can be edited or deleted on zenodo.org. Publishing is final: the DOI is permanent and the
record cannot be removed, so the script never publishes unless an id is named. Use --sandbox
against sandbox.zenodo.org first; it needs its own token from that site.

After publishing, add each DOI to tools/data_reports.py and to the page so the site and Zenodo
point at each other.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LICENCE = "cc-by-4.0"
SERIES_NAME = {"research": "Liscere Technical Report", "landscape": "Liscere Landscape Briefing"}


def reports():
    """Every report with a PDF: id, metadata and the file to upload."""
    import gen_articles as GA
    out = []
    for art in GA.ARTICLES:
        series = art.get("series")
        if series not in SERIES_NAME or not art.get("pdf"):
            continue
        a = art["en"]
        aid = art["id"]
        title = a["title"].split(" | ")[0].strip()
        date = art["date"]
        if len(date) == 7:          # month only in the data; Zenodo wants a full date
            date += "-01"
        out.append({
            "id": aid.upper(),
            "slug": aid,
            "pdf": os.path.join(ROOT, art["pdf"]),
            "url": f"https://liscere.com/research/{aid}/",
            "meta": {
                "upload_type": "publication",
                "publication_type": "report",
                "title": f"{aid.upper()}: {title}",
                "description": (
                    f"<p>{a['description']}</p>"
                    f"<p>{SERIES_NAME[series]} {aid.upper()}, published by Liscere sp. z o.o. "
                    f"The full text is also readable at <a href=\"https://liscere.com/research/{aid}/\">"
                    f"https://liscere.com/research/{aid}/</a>.</p>"),
                "creators": [{"name": "Salmazo, Bruno", "affiliation": "Liscere sp. z o.o.",
                               "orcid": "0009-0000-4410-3616"}],
                "publication_date": date,
                "version": art.get("version", "1.1"),
                "language": "eng",
                "license": LICENCE,
                "access_right": "open",
                "keywords": [k.strip() for k in a["keywords"].split(",") if k.strip()],
                "related_identifiers": [
                    {"identifier": f"https://liscere.com/research/{aid}/",
                     "relation": "isIdenticalTo", "resource_type": "publication-report"}],
                "notes": f"Report identifier {aid.upper()}. Series: {SERIES_NAME[series]}.",
            },
        })
    return out


class Api:
    def __init__(self, token, sandbox=False):
        self.base = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
        self.token = token

    def call(self, method, path, data=None, raw=None, content_type="application/json"):
        url = path if path.startswith("http") else self.base + path
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({"access_token": self.token})
        body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
        req = urllib.request.Request(url, data=body, method=method)
        if body is not None:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req) as r:
                text = r.read().decode()
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            sys.exit(f"{method} {path} failed: {e.code} {e.read().decode()[:400]}")


def find_draft(api, title):
    """An unpublished deposition with this title, so the script can be run twice safely."""
    for d in api.call("GET", "/deposit/depositions?size=100&status=draft"):
        if d.get("title") == title:
            return d
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true")
    p.add_argument("--draft", action="store_true")
    p.add_argument("--publish", metavar="ID")
    p.add_argument("--sandbox", action="store_true")
    args = p.parse_args()
    items = reports()

    if args.list or not (args.draft or args.publish):
        for r in items:
            size = os.path.getsize(r["pdf"]) // 1024
            print(f"{r['id']:12} {r['meta']['publication_date']}  {size:5} kB  {r['meta']['title']}")
        print(f"\n{len(items)} reports. Nothing was sent to Zenodo.")
        return

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        sys.exit("Set ZENODO_TOKEN first (personal access token with deposit:write and deposit:actions).")
    api = Api(token, args.sandbox)

    if args.publish:
        want = args.publish.upper()
        r = next((x for x in items if x["id"] == want), None)
        if not r:
            sys.exit(f"Unknown report {want}")
        d = find_draft(api, r["meta"]["title"])
        if not d:
            sys.exit(f"No draft for {want}. Run --draft first.")
        done = api.call("POST", f"/deposit/depositions/{d['id']}/actions/publish")
        print(f"{want} published: DOI {done.get('doi')}  {done.get('links', {}).get('html')}")
        return

    for r in items:
        d = find_draft(api, r["meta"]["title"])
        if d is None:
            d = api.call("POST", "/deposit/depositions", {"metadata": r["meta"]})
            new = True
        else:
            api.call("PUT", f"/deposit/depositions/{d['id']}", {"metadata": r["meta"]})
            new = False
        name = os.path.basename(r["pdf"])
        have = {f["filename"] for f in api.call("GET", f"/deposit/depositions/{d['id']}/files")}
        if name not in have:
            with open(r["pdf"], "rb") as fh:
                api.call("PUT", d["links"]["bucket"] + "/" + urllib.parse.quote(name),
                         raw=fh.read(), content_type="application/octet-stream")
        print(f"{r['id']:12} {'created' if new else 'updated'}  draft {d['id']}  {name}")
    print("\nDrafts are ready. Review them on zenodo.org, then publish one at a time:"
          "\n  python3 tools/zenodo.py --publish LTR-2026-01")


if __name__ == "__main__":
    main()
