"""Tell Bing, Yandex and other IndexNow engines that pages changed.
Usage: python3 tools/indexnow.py            (submits every URL in sitemap.xml)
       python3 tools/indexnow.py URL [URL]  (submits only those)
Run it after a deploy has finished. The key file (<key>.txt) sits at the site root."""
import glob, json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
keyfile = [f for f in glob.glob(os.path.join(ROOT, "*.txt")) if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(f))][0]
key = os.path.basename(keyfile)[:-4]
urls = sys.argv[1:] or re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())
body = json.dumps({"host": "liscere.com", "key": key, "keyLocation": f"https://liscere.com/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req) as r:
    print(r.status, "submitted", len(urls), "URLs")
