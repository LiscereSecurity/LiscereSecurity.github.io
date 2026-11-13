"""Generate the seven service pages in English (services/<slug>.html) and Polish
(pl/uslugi/<pl-slug>.html) from one template, with hreflang pairs."""
import json, html, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
exec(open(os.path.join(HERE, "data_en.py")).read())
from data_pl import PL, PL_NAMES

SITE = "https://liscere.com/"
AUTO = {"automation-projects", "automation-modernisation", "industrial-training"}

UI = {
 "en": dict(lang="en-GB", ogloc="en_GB", skip="Skip to content", navlabel="Site navigation", pages="Pages",
   home="Home", reach="Based in Poland, working across Europe and worldwide.", services="Services", about="About", research="Research", faq="FAQ", privacy="Privacy", legal="Legal", terms="Terms", enlink="",
   privacy_page="privacy.html", legal_page="legal.html", terms_page="terms.html",
   logo_label="Liscere home", what="What it is", who="Who it is for", why="Why it is needed",
   scroll="Scroll", qk="Questions we hear", qh="Straight answers.", ck="Contact us",
   gk="Background reading", gh="Guides on the rules and the standards.",
   ch="Tell us what you need. We will find the solution.",
   cs="Our goal is to keep what is critical protected, and we work hard to make that possible.",
   name="Name", company="Company", email="Work email", interest="What are you interested in?",
   general="General enquiry", message="Message", ph="Describe what you need in a few lines.",
   consent='I agree that Liscere sp. z o.o. may process the data in this form to answer my enquiry, as described in the <a href="{root}privacy.html">privacy notice</a>.',
   send="Send message", back_label="Back to services", switch="PL", switch_label="Polski", switch_lang="pl"),
 "pl": dict(lang="pl-PL", ogloc="pl_PL", skip="Przejdź do treści", navlabel="Nawigacja", pages="Strony",
   home="Start", reach="Siedziba w Polsce, działamy w całej Europie i na świecie.", services="Usługi", about="O nas", research="Badania", faq="FAQ", privacy="Prywatność", legal="Dane spółki", terms="Warunki korzystania", enlink=' hreflang="en"',
   privacy_page="prywatnosc.html", legal_page="dane-spolki.html", terms_page="warunki.html",
   logo_label="Liscere, strona główna", what="Czym jest", who="Dla kogo", why="Dlaczego jest potrzebny",
   scroll="Przewiń", qk="Pytania, które słyszymy", qh="Konkretne odpowiedzi.", ck="Kontakt",
   gk="Do poczytania", gh="Poradniki o przepisach i normach.",
   ch="Powiedz nam, czego potrzebujesz. Znajdziemy rozwiązanie.",
   cs="Naszym celem jest ochrona tego, co krytyczne, i ciężko pracujemy, aby to było możliwe.",
   name="Imię i nazwisko", company="Firma", email="Służbowy e-mail", interest="Czego dotyczy zapytanie?",
   general="Zapytanie ogólne", message="Wiadomość", ph="Opisz w kilku zdaniach, czego potrzebujesz.",
   consent='Wyrażam zgodę na przetwarzanie przez Liscere sp. z o.o. danych z tego formularza w celu odpowiedzi na moje zapytanie, zgodnie z <a href="{root}prywatnosc.html">informacją o prywatności</a>.',
   send="Wyślij wiadomość", back_label="Powrót do usług", switch="EN", switch_label="English", switch_lang="en"),
}

def esc(t): return html.escape(t, quote=False)
def attr(t): return html.escape(t, quote=True)

def urls(slug):
    en = f"{SITE}services/{slug}.html"
    pl = f"{SITE}pl/uslugi/{PL[slug]['pl']}.html"
    return en, pl

# Guides linked from each service page, so a reader who lands on a service can go deeper.
GUIDES = {
    "gd-2026-01": {
        "en": ("research/gd-2026-01/", "NIS2 and Poland's KSC act",
               "Who is covered, the deadlines, and what the rules mean for control systems."),
        "pl": ("badania/gd-2026-01/", "NIS2 i ustawa o KSC",
               "Kogo dotyczą przepisy, jakie są terminy i co z tego wynika dla systemów sterowania."),
    },
    "gd-2026-02": {
        "en": ("research/gd-2026-02/", "Reporting an OT incident",
               "The 24 hour, 72 hour and one month steps, and what makes them hard in OT."),
        "pl": ("badania/gd-2026-02/", "Zgłaszanie incydentu w OT",
               "Terminy 24 godzin, 72 godzin i miesiąca oraz to, co w OT jest najtrudniejsze."),
    },
    "gd-2026-03": {
        "en": ("research/gd-2026-03/", "IEC 62443 in practice",
               "The parts of the series, zones and conduits, and what SL-T, SL-C and SL-A mean."),
        "pl": ("badania/gd-2026-03/", "IEC 62443 w praktyce",
               "Części serii, strefy i kanały oraz znaczenie poziomów SL-T, SL-C i SL-A."),
    },
}

PAGE_GUIDES = {
    "ot-security-assessment": ["gd-2026-03", "gd-2026-01"],
    "audyt-bezpieczenstwa-ot": ["gd-2026-03", "gd-2026-01"],
    "ot-visibility-monitoring": ["gd-2026-03", "gd-2026-01"],
    "widocznosc-i-monitoring-ot": ["gd-2026-03", "gd-2026-01"],
    "nis2-ksc-compliance": ["gd-2026-01", "gd-2026-02"],
    "nis2-ksc": ["gd-2026-01", "gd-2026-02"],
    "ot-incident-response": ["gd-2026-02", "gd-2026-01"],
    "reagowanie-na-incydenty-ot": ["gd-2026-02", "gd-2026-01"],
    "automation-projects": ["gd-2026-03"],
    "projekty-automatyki": ["gd-2026-03"],
    "automation-modernisation": ["gd-2026-03"],
    "modernizacja-automatyki": ["gd-2026-03"],
    "industrial-training": ["gd-2026-01", "gd-2026-03"],
    "szkolenia-przemyslowe": ["gd-2026-01", "gd-2026-03"],
}


def guides_block(slug, lang, L):
    ids = PAGE_GUIDES.get(slug, [])
    if not ids:
        return ""
    items = "\n".join(
        '            <li><a href="../' + GUIDES[g][lang][0] + '">' + esc(GUIDES[g][lang][1])
        + '</a><span>' + esc(GUIDES[g][lang][2]) + '</span></li>'
        for g in ids)
    return (
        '\n    <section class="section" id="guides">'
        '\n      <div class="faq-layout">'
        '\n        <div>'
        '\n          <p class="kicker">' + L["gk"] + '</p>'
        '\n          <h2>' + L["gh"] + '</h2>'
        '\n        </div>'
        '\n        <div class="service-guides">'
        '\n          <ul class="related-links">\n' + items +
        '\n          </ul>'
        '\n        </div>'
        '\n      </div>'
        '\n    </section>\n')

def render(p, lang):
    L = UI[lang]
    en_url, pl_url = urls(p["slug"])
    if lang == "en":
        d = p; url = en_url; root = "../"; home = "../index.html"; svc = "../services.html"
        about = "../about.html"; faqp = "../faq.html"; research = "../research.html"
        other = f"../pl/uslugi/{PL[p['slug']]['pl']}.html"
        crumbs = [("Home", SITE), ("Services", SITE + "services.html")]
        names = {v: v for v, _ in SERVICES}
    else:
        d = dict(p); d.update(PL[p["slug"]]); url = pl_url; root = "../../"
        home = "../index.html"; svc = "../uslugi.html"; about = "../o-nas.html"; faqp = "../faq.html"
        research = "../badania.html"; other = f"../../services/{p['slug']}.html"
        crumbs = [("Start", SITE + "pl/"), ("Usługi", SITE + "pl/uslugi.html")]
        names = PL_NAMES
    sec = "automation" if p["slug"] in AUTO else "ot-security"
    back = f"{svc}#{sec}"
    ld = {"@context": "https://schema.org", "@graph": [
      {"@type": "Service", "@id": url + "#service", "name": names[p["service"]], "serviceType": d["stype"],
       "description": d["what"], "inLanguage": L["lang"],
       "provider": {"@type": "Organization", "@id": SITE + "#org", "name": "Liscere", "url": SITE},
       "areaServed": p.get("area", "Worldwide"), "url": url},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": crumbs[0][0], "item": crumbs[0][1]},
        {"@type": "ListItem", "position": 2, "name": crumbs[1][0], "item": crumbs[1][1]},
        {"@type": "ListItem", "position": 3, "name": d["crumb"], "item": url}]},
      {"@type": "FAQPage", "inLanguage": L["lang"], "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]}]}
    ldj = "\n".join("  " + l for l in json.dumps(ld, indent=2, ensure_ascii=False).split("\n"))
    opts = "\n".join(f'                <option value="{attr(v)}"{" selected" if v == p["service"] else ""}>{esc(names[v])}</option>' for v, _ in SERVICES)
    faqs = "".join(f"""          <details>
            <summary>{esc(q)}</summary>
            <p>{esc(a)}</p>
          </details>
""" for q, a in d["faq"])
    lroot = root if lang == "en" else "../"   # legal pages: site root (EN) or /pl/ (PL)
    consent = L["consent"].format(root=lroot)
    nav_cur = 'aria-current="page"'
    return f"""<!doctype html>
<html lang="{L['lang']}" class="past-hero">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(d['title'])}</title>
  <meta name="description" content="{attr(d['desc'])}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="pl" href="{pl_url}">
  <link rel="alternate" hreflang="x-default" href="{en_url}">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#030405">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Liscere">
  <meta property="og:locale" content="{L['ogloc']}">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{attr(d['title'])}">
  <meta property="og:description" content="{attr(d['desc'])}">
  <meta property="og:image" content="https://liscere.com/assets/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{attr(d['title'])}">
  <meta name="twitter:description" content="{attr(d['desc'])}">
  <meta name="twitter:image" content="https://liscere.com/assets/og-image.png">

  <link rel="stylesheet" href="{root}assets/css/fonts.css?v=1" />
  <link rel="icon" type="image/svg+xml" href="{root}assets/favicon.svg?v=4" />
  <link rel="icon" type="image/png" sizes="32x32" href="{root}assets/favicon-32.png?v=4" />
  <link rel="icon" type="image/png" sizes="16x16" href="{root}assets/favicon-16.png?v=4" />
  <link rel="icon" type="image/png" sizes="48x48" href="{root}assets/favicon-48.png?v=4" />
  <link rel="apple-touch-icon" sizes="180x180" href="{root}assets/apple-touch-icon.png?v=4" />
  <link rel="stylesheet" href="{root}assets/css/styles.css?v={CSSV}" />

  <script type="application/ld+json">
{ldj}
  </script>
</head>
<body>
  <a class="skip-link" href="#main-content">{L['skip']}</a>

  <header class="site-chrome" aria-label="{L['navlabel']}">
    <a class="site-logo" href="{home}" aria-label="{L['logo_label']}">
      <img class="wordmark-svg" src="{root}assets/liscere-wordmark-dark.svg?v=3" alt="Liscere" width="1040" height="216" />
    </a>
    <nav class="site-nav" aria-label="{L['pages']}">
      <a href="{home}">{L['home']}</a>
      <a href="{svc}" {nav_cur}>{L['services']}</a>
      <a href="{about}">{L['about']}</a>
      <a href="{research}">{L['research']}</a>
      <a class="lang-switch" href="{other}" hreflang="{L['switch_lang']}" lang="{L['switch_lang']}" aria-label="{L['switch_label']}">{L['switch']}</a>
    </nav>
  </header>

  <a class="back-fab" href="{back}" aria-label="{L['back_label']}"><span aria-hidden="true">&larr;</span> {L['services']}</a>

  <main id="main-content" class="services-page sales-page service-page">

    <section class="section hero">
      <div class="hero-copy">
        <p class="kicker"><a href="{back}">{L['services']}</a> / {esc(d['crumb'])}</p>
        <h1>{esc(d['h1'])}</h1>
        <ul class="service-brief">
          <li>
            <h2>{L['what']}</h2>
            <p>{esc(d['what'])}</p>
          </li>
          <li>
            <h2>{L['who']}</h2>
            <p>{esc(d['who'])}</p>
          </li>
          <li>
            <h2>{L['why']}</h2>
            <p>{esc(d['why'])}</p>
          </li>
        </ul>
      </div>
      <div class="hero-scrollcue" aria-hidden="true">
        <span class="hero-scrollcue-label">{L['scroll']}</span>
        <span class="hero-scrollcue-track"><span class="hero-scrollcue-dot"></span></span>
      </div>
    </section>

    <section class="section" id="faq">
      <div class="faq-layout">
        <div>
          <p class="kicker">{L['qk']}</p>
          <h2>{L['qh']}</h2>
        </div>
        <div class="faq">
{faqs}        </div>
      </div>
    </section>

{guides_block(p['slug'], lang, L)}
    <section class="section" id="contact">
      <div class="contact-grid">
        <div class="contact-aside">
          <p class="kicker">{L['ck']}</p>
          <h2>{L['ch']}</h2>
          <p class="section-side">{L['cs']}</p>
          <p class="mono">hello@liscere.com</p>
          <p class="mono"><a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">linkedin.com/company/liscere</a></p>
        </div>
        <form class="form-card" data-contact data-endpoint="https://formspree.io/f/xdegodog" data-mailto="hello@liscere.com" novalidate>
          <div class="form-grid">
            <div>
              <label for="f-name">{L['name']}</label>
              <input id="f-name" name="name" type="text" autocomplete="name" required>
            </div>
            <div>
              <label for="f-company">{L['company']}</label>
              <input id="f-company" name="company" type="text" autocomplete="organization">
            </div>
            <div>
              <label for="f-email">{L['email']}</label>
              <input id="f-email" name="email" type="email" autocomplete="email" required>
            </div>
            <div>
              <label for="f-service">{L['interest']}</label>
              <select id="f-service" name="service">
                <option value="General enquiry">{L['general']}</option>
{opts}
              </select>
            </div>
            <div class="full">
              <label for="f-message">{L['message']}</label>
              <textarea id="f-message" name="message" required placeholder="{attr(L['ph'])}"></textarea>
            </div>
            <div class="full consent">
              <input id="f-consent" name="consent" type="checkbox" required>
              <label for="f-consent">{consent}</label>
            </div>
            <div class="hp" aria-hidden="true">
              <label for="f-website">Website</label>
              <input id="f-website" name="website" type="text" tabindex="-1" autocomplete="off">
            </div>
            <div class="full actions">
              <button class="primary-cta" type="submit">{L['send']}</button>
            </div>
            <p class="full form-status" role="status" aria-live="polite"></p>
          </div>
        </form>
      </div>
    </section>

    <p class="research-foot"><a href="{home}">{L['home']}</a> · <a href="{svc}">{L['services']}</a> · <a href="{about}">{L['about']}</a> · <a href="{faqp}">{L['faq']}</a> · <a href="{research}">{L['research']}</a> · <a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">LinkedIn</a> · <a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> · <a href="{lroot}{L['privacy_page']}">{L['privacy']}</a> · <a href="{lroot}{L['legal_page']}">{L['legal']}</a> · <a href="{lroot}{L['terms_page']}">{L['terms']}</a><br />{L['reach']}<br />© 2026 Liscere sp. z o.o.</p>
  </main>

  <script src="{root}assets/js/site.js?v=4" defer></script>
  <script src="{root}assets/js/contact-form.js?v=20261111-fs1" defer></script>
</body>
</html>
"""

if __name__ == "__main__":
    os.makedirs(ROOT + "pl/uslugi", exist_ok=True)
    for p in PAGES:
        open(ROOT + f"services/{p['slug']}.html", "w", encoding="utf-8").write(render(p, "en"))
        open(ROOT + f"pl/uslugi/{PL[p['slug']]['pl']}.html", "w", encoding="utf-8").write(render(p, "pl"))
    print("ok", len(PAGES) * 2)
