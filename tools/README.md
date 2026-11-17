# Site tools

Not published: the deploy workflow leaves this folder out.

The service pages and the Polish pages are generated. Edit the sources here, not the HTML:

| What | Source |
|---|---|
| English service pages (`services/*.html`) | `data_en.py` (texts) and `gen_service_pages.py` (template) |
| Polish service pages (`pl/uslugi/*.html`) | `data_pl.py` (texts) and `gen_service_pages.py` |
| Polish Services, About, FAQ (`pl/uslugi.html`, `pl/o-nas.html`, `pl/faq.html`) | `gen_pl_pages.py` |
| Polish home (`pl/index.html`) | `gen_home_pl.py`, which translates `index.html` string by string. After changing text on `index.html`, update the matching line here, or the build stops with `NOT FOUND`. |

Hand-written pages: `index.html`, `services.html`, `about.html`, `faq.html`, `research.html`, `research/*/index.html`, `privacy.html`, `404.html`.

After any change, run:

    sh tools/build.sh

The last step (`csp.py`) adds the Content Security Policy to every page and allows each inline
script by its hash, so it must run after any edit to an inline script. To connect the contact form
to a sending service (for example Formspree) or add analytics, add that service's origin to the
`connect-src` / `script-src` lists in `csp.py`, then run the build.

When CSS or JS changes, bump the `?v=` query string on the pages (and `CSSV` in `data_en.py`).

## Zenodo (DOIs for the reports)

    export ZENODO_TOKEN=...                        # zenodo.org, Applications, personal access token
    python3 tools/zenodo.py --list                 # what would be deposited, nothing sent
    python3 tools/zenodo.py --draft                # create or update the drafts and upload the PDFs
    python3 tools/zenodo.py --publish LTR-2026-01  # publish one, which mints a permanent DOI

Metadata comes from `gen_articles.py`, so Zenodo and the site always say the same thing. Drafts can
be edited or deleted; publishing cannot be undone. Add `--sandbox` to try it against
sandbox.zenodo.org first, which needs a token from that site.

## After a deploy

Tell Bing and the other IndexNow search engines about changed pages:

    python3 tools/indexnow.py                 # every URL in sitemap.xml
    python3 tools/indexnow.py https://liscere.com/services.html

The key file `<key>.txt` at the site root proves ownership; do not delete it.

## OT radar (daily reading, not publishing)

    python3 tools/radar.py              # items from the last 2 days
    python3 tools/radar.py --days 7     # wider window, e.g. after a break
    python3 tools/radar.py --all        # ignore what was already reported

Reads seven feeds that answered when tested on 17 November 2026: CISA ICS advisories, Siemens
ProductCERT (its ATOM feed; the RSS one is deprecated), CERT Polska, Industrial Cyber,
SecurityWeek ICS/OT, The Record and BleepingComputer. Dragos, Claroty and Nozomi publish no feed.

Topical feeds pass whole; general feeds must match a keyword. Keywords ending in `*` are stems, so
Polish inflection is covered by one entry. Everything else matches on whole words, which is why
`port` no longer fires inside `support`. CISA writes a two-digit year in `pubDate`, so `%y` is tried
before `%Y`; without that every advisory came through undated and the date window did nothing.

Output goes to `radar/YYYY-MM-DD.md`, which is gitignored and never deployed. `radar/seen.json`
stops an item being reported twice, which also means a second run on the same day finds nothing;
in that case the existing brief is kept rather than overwritten with an empty one. **Nothing here publishes anything.** Deciding what becomes a
Field Note is a human decision, on purpose: an automated pipeline would eventually call an IT
ransomware case an OT incident in public, and Google's scaled content abuse policy targets exactly
the pattern of a site posting generated articles daily.

Run daily by the scheduled task `radar-ot-liscere` (sidebar, Scheduled), which runs this script,
judges each item and writes `radar/YYYY-MM-DD-veredito.md`. Scheduled tasks only run while the
desktop app is open; a missed run fires at next launch.
