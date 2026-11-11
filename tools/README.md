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

## After a deploy

Tell Bing and the other IndexNow search engines about changed pages:

    python3 tools/indexnow.py                 # every URL in sitemap.xml
    python3 tools/indexnow.py https://liscere.com/services.html

The key file `<key>.txt` at the site root proves ownership; do not delete it.
