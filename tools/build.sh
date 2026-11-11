#!/bin/sh
# Regenerate the generated pages, then refresh the Content Security Policy on every page.
# Run from anywhere: sh tools/build.sh
set -e
cd "$(dirname "$0")"
python3 gen_service_pages.py   # services/*.html and pl/uslugi/*.html (EN + PL service pages)
python3 gen_pl_pages.py        # pl/uslugi.html, pl/o-nas.html, pl/faq.html
python3 gen_home_pl.py         # pl/index.html, built from index.html
python3 csp.py                 # CSP and referrer meta tags on all pages (run last)
