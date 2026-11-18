"""Daily OT and ICS radar: read the security feeds, keep what matters to an
industrial operator, and write a short brief for Bruno to read over coffee.

Usage: python3 tools/radar.py              (items from the last 2 days)
       python3 tools/radar.py --days 7     (wider window, e.g. after a break)
       python3 tools/radar.py --all        (ignore what was already reported)

It writes radar/YYYY-MM-DD.md and never touches the website. Nothing here
publishes anything: choosing what becomes a Field Note stays a human decision.
Standard library only, so it runs anywhere python3 does.
"""
import argparse, datetime as dt, html, json, os, re, ssl, sys, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "radar")
STATE = os.path.join(OUT_DIR, "seen.json")
ATOM = "{http://www.w3.org/2005/Atom}"

# topical=True  -> the whole feed is about industrial control systems, keep everything
# topical=False -> a general security feed, keep only what matches a keyword
SOURCES = [
    ("CISA ICS advisories", "https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml", True,  "advisory"),
    ("Siemens ProductCERT", "https://cert-portal.siemens.com/productcert/rss/advisories.atom", True,  "advisory"),
    ("CERT Polska",         "https://cert.pl/feed/",                                           False, "poland"),
    ("Industrial Cyber",    "https://industrialcyber.co/feed/",                                True,  "news"),
    ("SecurityWeek ICS/OT", "https://www.securityweek.com/category/ics-ot/feed/",              True,  "news"),
    ("The Record",          "https://therecord.media/feed",                                    False, "news"),
    ("BleepingComputer",    "https://www.bleepingcomputer.com/feed/",                          False, "news"),
]

# A trailing * means "this is a stem, match longer words too" (manufactur* -> manufacturing).
# Everything else is matched on whole words, so "port" does not fire inside "support".
VENDORS = ["siemens", "schneider", "rockwell", "allen-bradley", "mitsubishi", "omron", "abb",
           "honeywell", "yokogawa", "emerson", "phoenix contact", "wago", "beckhoff", "moxa",
           "hirschmann", "advantech", "delta electronics", "unitronics", "codesys", "ge vernova",
           "hitachi energy", "bosch rexroth", "festo", "pilz", "sick ag", "ifm", "turck"]
PRODUCTS = ["plc", "plcs", "hmi", "scada", "dcs", "rtu", "historian", "simatic", "step 7", "tia portal",
            "modbus", "profinet", "profibus", "opc ua", "dnp3", "iec 61850", "iec 60870", "ethernet/ip",
            "bacnet", "building automation", "safety instrumented", "firmware", "ladder logic",
            "engineering workstation", "remote access", "vpn appliance"]
SECTORS = ["water", "wastewater", "energy", "power grid", "electric utility", "substation", "pipeline",
           "oil and gas", "refinery", "manufactur*", "factory", "plant", "hospital", "hospitals",
           "healthcare", "rail", "railway", "port", "ports", "maritime", "airport",
           "critical infrastructure", "food", "chemical", "pharmaceutical", "automotive"]
REGULATION = ["nis2", "nis 2", "iec 62443", "62443", "cyber resilience act", "cra", "ksc",
              "krajowy system cyberbezpieczenstwa", "enisa", "nist 800-82"]
GENERIC_OT = ["ot security", "it/ot", "it-ot", "ics", "industrial control", "operational technology",
              "industrial automation", "cyber-physical", "purdue model", "air-gapped", "air gap"]
# Polish, for CERT Polska. Stems, because Polish inflects: one scan covers every case ending.
POLISH = ["przemyslow*", "sterownik*", "automatyk*", "infrastruktur* krytyczn*", "energetyk*",
          "wodociag*", "elektrowni*", "szpital*", "kolej*", "rafineri*", "fabryk*", "zaklad*"]

# A second tier. These stories rarely name a PLC, so the OT keywords above miss them, but they
# are what decides how an operator's board thinks about risk: state actors, infrastructure-wide
# failures, and the platform flaws that end up inside SCADA without anyone having chosen them.
# They are kept apart from the advisories rather than mixed in, because they are context, not work.
CONTEXT = ["volt typhoon", "salt typhoon", "sandworm", "nation-state", "nation state",
           "state-sponsored", "state-backed", "state group", "state hackers",
           "pre-positioning", "prepositioning", "apt", "espionage", "cyberwar*", "sabotage",
           "nsa", "cisa", "fbi", "classified network", "government network",
           "power outage", "blackout", "grid failure", "ground stop", "air traffic",
           "undersea cable", "subsea cable", "gps jamming", "gps spoofing",
           "log4shell", "log4j", "java4shell", "node.js", "nodejs", "openssl",
           "actively exploited", "zero-day", "zero day", "known exploited",
           "supply chain attack", "supply-chain attack"]

# Court reporting is not operational news. An extradition or a sentencing changes nothing on a
# plant floor, and these headlines were crowding out the ones that do.
# Deliberately not here: "fined", "lawsuit", "penalty". A regulator fining an operator is
# exactly our subject, so those headlines must survive.
NOISE = ["extradited", "extradition", "sentenced", "pleads guilty", "pleaded guilty",
         "arrested", "indicted", "convicted", "court clears", "jailed", "charges filed"]


def build(keys):
    """Whole-word matchers. A trailing * means a stem, so manufactur* also hits manufacturing."""
    out = []
    for k in keys:
        if k.endswith("*"):
            rx = r"(?<![\w-])" + re.escape(k[:-1]).replace(r"\ ", r"\s+")
        else:
            rx = r"(?<![\w-])" + re.escape(k).replace(r"\ ", r"\s+") + r"(?![\w-])"
        out.append((k.replace("*", ""), re.compile(rx)))
    return out


KEYWORDS = VENDORS + PRODUCTS + SECTORS + REGULATION + GENERIC_OT + POLISH
MATCHERS = build(KEYWORDS)
CONTEXT_MATCHERS = build(CONTEXT)
NOISE_RX = re.compile("|".join(re.escape(n) for n in NOISE))

PL_MAP = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")


def fold(s):
    """Lowercase and strip Polish diacritics so one keyword list covers both languages."""
    return re.sub(r"\s+", " ", html.unescape(s or "").translate(PL_MAP).lower())


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(s or ""))).strip()


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    # CISA writes a two-digit year ("Thu, 12 Nov 26"), so %y is tried before %Y.
    for fmt in ("%a, %d %b %y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try:
            d = dt.datetime.strptime(s.replace("GMT", "+0000"), fmt)
            return d.replace(tzinfo=d.tzinfo or dt.timezone.utc)
        except ValueError:
            pass
    return None


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Liscere OT radar)"})
    with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
        return r.read()


def read_feed(name, url, topical, kind):
    """Return a list of dicts for one feed, or [] with a note on stderr if it is down."""
    try:
        root = ET.fromstring(fetch(url))
    except Exception as e:
        print(f"  ! {name}: {type(e).__name__} {str(e)[:60]}", file=sys.stderr)
        return []
    out = []
    for el in root.findall(".//item"):
        out.append({"title": strip_tags(el.findtext("title")),
                    "link": (el.findtext("link") or "").strip(),
                    "summary": strip_tags(el.findtext("description"))[:400],
                    "date": parse_date(el.findtext("pubDate")),
                    "source": name, "topical": topical, "kind": kind})
    for el in root.findall(f".//{ATOM}entry"):
        link = el.find(f"{ATOM}link")
        out.append({"title": strip_tags(el.findtext(f"{ATOM}title")),
                    "link": (link.get("href") if link is not None else "") or "",
                    "summary": strip_tags(el.findtext(f"{ATOM}summary"))[:400],
                    "date": parse_date(el.findtext(f"{ATOM}updated") or el.findtext(f"{ATOM}published")),
                    "source": name, "topical": topical, "kind": kind})
    return out


def matches(item):
    """Keywords found in an item, used both to filter general feeds and to tag everything."""
    hay = fold(item["title"] + " " + item["summary"])
    return sorted({label for label, rx in MATCHERS if rx.search(hay)})


def context_matches(item):
    hay = fold(item["title"] + " " + item["summary"])
    return sorted({label for label, rx in CONTEXT_MATCHERS if rx.search(hay)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--all", action="store_true", help="include items reported before")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    seen = set()
    if os.path.exists(STATE) and not args.all:
        seen = set(json.load(open(STATE)).get("links", []))

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.days)
    items, dropped_old, dropped_seen = [], 0, 0
    titles = set()

    print("Reading feeds:", file=sys.stderr)
    for name, url, topical, kind in SOURCES:
        got = read_feed(name, url, topical, kind)
        kept = 0
        for it in got:
            if not it["title"] or not it["link"]:
                continue
            if it["date"] and it["date"] < cutoff:
                dropped_old += 1
                continue
            if it["link"] in seen:
                dropped_seen += 1
                continue
            key = fold(it["title"])[:90]
            if key in titles:
                continue
            it["tags"] = matches(it)
            it["ctx"] = context_matches(it)
            if not it["topical"] and not it["tags"] and not it["ctx"]:
                continue
            # Applied whatever the tags say: a court story that happens to mention hospitals
            # was being kept as a healthcare item, and crowding out the real ones.
            if not it["topical"] and NOISE_RX.search(fold(it["title"])):
                continue
            if not it["topical"] and not it["tags"]:
                it["kind"] = "context"
            titles.add(key)
            items.append(it)
            kept += 1
        if got:
            print(f"  . {name}: {kept} kept of {len(got)}", file=sys.stderr)

    items.sort(key=lambda i: (i["date"] or cutoff), reverse=True)

    today = dt.date.today().isoformat()
    path = os.path.join(OUT_DIR, f"{today}.md")
    # A second run on the same day finds everything already seen. Without this it would
    # overwrite a real brief with "nothing new" and the day's items would be lost.
    if not items and os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  = nothing new; keeping the existing {os.path.basename(path)}", file=sys.stderr)
        print(path)
        return
    groups = [("Advisories", "advisory"), ("Poland", "poland"), ("News", "news"),
              ("Context", "context")]
    lines = [f"# OT radar, {today}", ""]
    if not items:
        lines += ["Nothing new in the window. That happens; it is not a failure.", ""]
    for heading, kind in groups:
        chunk = [i for i in items if i["kind"] == kind]
        if not chunk:
            continue
        lines += [f"## {heading}", ""]
        for i in chunk:
            when = i["date"].strftime("%d %b") if i["date"] else "undated"
            lines.append(f"- **{i['title']}**  ")
            lines.append(f"  {i['source']}, {when} — <{i['link']}>  ")
            shown = i["tags"] or i.get("ctx") or []
            if shown:
                lines.append(f"  tags: {', '.join(shown[:8])}")
            lines.append("")
    lines += ["---", "",
              f"{len(items)} items. Window {args.days} day(s). "
              f"{dropped_old} older than the window, {dropped_seen} reported before.", ""]
    open(path, "w", encoding="utf-8").write("\n".join(lines))

    if not args.all:
        json.dump({"links": sorted(seen | {i["link"] for i in items})[-4000:]},
                  open(STATE, "w"), indent=0)
    print(path)


if __name__ == "__main__":
    main()
