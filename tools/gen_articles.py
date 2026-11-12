"""Full-text research articles (Field Notes and later the converted reports).

Each article has one body file per language in tools/articles/<id>.<lang>.html
(kicker, h1, lede, optional video figure, sections, tagline, Sources). This
script wraps the body in the site chrome and adds the parts around it: Key
points, the side column (video or contact card, plus contents), How Liscere can
help, Questions, Cite, and the structured data. English and Polish versions are
linked with hreflang. Run from anywhere: python3 tools/gen_articles.py
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(HERE)
SITE = "https://liscere.com/"
CSS_V = "20261112-fn1"
ORG = {"@id": SITE + "#org"}

CSP = ("<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; script-src 'self' "
       "https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
       "font-src 'self'; media-src 'self'; connect-src 'self' https://formspree.io "
       "https://cloudflareinsights.com; object-src 'self'; frame-src 'self'; base-uri 'self'; "
       "form-action 'self'; upgrade-insecure-requests\">")
CF = ('<!-- Cloudflare Web Analytics --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
      'data-cf-beacon=\'{"token": "3280d901c4be4657ba0562ac10e607b7"}\'></script><!-- End Cloudflare Web Analytics -->')

# ---------------------------------------------------------------- languages
UI = {
    "en": dict(
        html_lang="en-GB", og_locale="en_GB", skip="Skip to content", nav_label="Site navigation",
        nav_pages="Pages", logo_label="Liscere home", key_points="Key points", toc="On this page",
        side_label="Video and contents", help="How Liscere can help", questions="Questions",
        sources="Sources", cite="Cite this article", back="&#8592; All research",
        cta_title="Facing something similar?",
        cta_text="We help industrial operators find what is exposed, see what their control network is being told to do, and respond when something goes wrong.",
        cta_button="Talk to us", series="Field Notes", home_name="Home", research_name="Research",
    ),
    "pl": dict(
        html_lang="pl-PL", og_locale="pl_PL", skip="Przejdź do treści", nav_label="Nawigacja",
        nav_pages="Strony", logo_label="Liscere, strona główna", key_points="Najważniejsze punkty",
        toc="Na tej stronie", side_label="Film i spis treści", help="Jak Liscere może pomóc",
        questions="Pytania", sources="Źródła", cite="Cytowanie", back="&#8592; Wszystkie badania",
        cta_title="Podobny problem?",
        cta_text="Pomagamy operatorom przemysłowym sprawdzić, co jest wystawione na zewnątrz, zobaczyć, co trafia do ich sieci sterowania, i reagować, gdy coś pójdzie nie tak.",
        cta_button="Porozmawiaj z nami", series="Field Notes", home_name="Start", research_name="Badania",
    ),
}


def url_of(lang, aid):
    return SITE + (f"research/{aid}/" if lang == "en" else f"pl/badania/{aid}/")


def path_of(lang, aid):
    return os.path.join(ROOT_DIR, *(["research", aid] if lang == "en" else ["pl", "badania", aid]), "index.html")


def chrome(lang, aid, R):
    """Header and footer. R is the relative path to the site root."""
    other = (f"{R}pl/badania/{aid}/" if lang == "en" else f"{R}research/{aid}/")
    if lang == "en":
        nav = (f'      <a href="{R}index.html">Home</a>\n'
               f'      <a href="{R}services.html">Services</a>\n'
               f'      <a href="{R}about.html">About</a>\n'
               f'      <a href="{R}research.html" aria-current="page">Research</a>\n'
               f'      <a class="lang-switch" href="{other}" hreflang="pl" lang="pl" aria-label="Polski">PL</a>')
        logo = f"{R}index.html"
        foot = (f'<a href="{R}index.html">Home</a> · <a href="{R}services.html">Services</a> · '
                f'<a href="{R}about.html">About</a> · <a href="{R}faq.html">FAQ</a> · '
                f'<a href="{R}research.html">Research</a> · '
                '<a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">LinkedIn</a> · '
                '<a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> · '
                f'<a href="{R}privacy.html">Privacy</a> · <a href="{R}legal.html">Legal</a> · '
                f'<a href="{R}terms.html">Terms</a>')
    else:
        nav = (f'      <a href="{R}pl/index.html">Start</a>\n'
               f'      <a href="{R}pl/uslugi.html">Usługi</a>\n'
               f'      <a href="{R}pl/o-nas.html">O nas</a>\n'
               f'      <a href="{R}research.html" hreflang="en" aria-current="page">Badania</a>\n'
               f'      <a class="lang-switch" href="{other}" hreflang="en" lang="en" aria-label="English">EN</a>')
        logo = f"{R}pl/index.html"
        foot = (f'<a href="{R}pl/index.html">Start</a> · <a href="{R}pl/uslugi.html">Usługi</a> · '
                f'<a href="{R}pl/o-nas.html">O nas</a> · <a href="{R}pl/faq.html">FAQ</a> · '
                f'<a href="{R}research.html" hreflang="en">Badania</a> · '
                '<a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">LinkedIn</a> · '
                '<a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> · '
                f'<a href="{R}privacy.html" hreflang="en">Prywatność</a> · '
                f'<a href="{R}legal.html" hreflang="en">Dane spółki</a> · '
                f'<a href="{R}terms.html" hreflang="en">Warunki korzystania</a>')
    t = UI[lang]
    header = f'''  <a class="skip-link" href="#main-content">{t["skip"]}</a>

  <header class="site-chrome" aria-label="{t["nav_label"]}">
    <a class="site-logo" href="{logo}" aria-label="{t["logo_label"]}">
      <img class="wordmark-svg" src="{R}assets/liscere-wordmark-dark.svg?v=3" alt="Liscere" width="1040" height="216" />
    </a>
    <nav class="site-nav" aria-label="{t["nav_pages"]}">
{nav}
    </nav>
  </header>'''
    footer = f'    <p class="research-foot">{foot}<br />© 2026 Liscere sp. z o.o.</p>'
    return header, footer


def ind(text, n):
    return "\n".join((" " * n + line if line.strip() else "") for line in text.splitlines())


def slug(text):
    s = text.lower()
    for a, b in (("ą", "a"), ("ć", "c"), ("ę", "e"), ("ł", "l"), ("ń", "n"), ("ó", "o"), ("ś", "s"), ("ź", "z"), ("ż", "z")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def build(art, lang):
    a = art[lang]
    t = UI[lang]
    aid = art["id"]
    URL = url_of(lang, aid)
    R = "../../" if lang == "en" else "../../../"
    body = open(os.path.join(HERE, "articles", f"{aid}.{lang}.html"), encoding="utf-8").read().strip()
    body = re.sub(r"^\s*<!--.*?-->\s*", "", body, flags=re.S)
    body = body.replace('poster="/assets/video/liscere-supermarket-attack-poster.jpg"',
                        'poster="/assets/video/liscere-supermarket-attack-poster-720.jpg"')

    h1 = html.unescape(re.search(r"<h1>(.*?)</h1>", body, re.S).group(1)).strip()
    i_h2 = body.index("<h2>")
    head_part = body[:i_h2]
    fig = re.search(r'<figure class="video">.*?</figure>', head_part, re.S)
    fig_part = fig.group(0) if fig else ""
    head_part = head_part.replace(fig_part, "").strip()
    rest = body[i_h2:].strip()
    head_part = head_part.replace('<p class="kicker">FIELD NOTES',
        f'<p class="kicker"><a class="series-back" href="{R}research.html#fieldnotes" data-back{"" if lang == "en" else ' hreflang="en"'}>FIELD NOTES</a>', 1)

    # ids on the section headings, for the contents list
    toc = []
    def add_id(m):
        title = m.group(1)
        hid = slug(title) if title != t["sources"] else "sources"
        toc.append((hid, title))
        return f'<h2 id="{hid}">{title}</h2>'
    rest = re.sub(r"<h2>(.*?)</h2>", add_id, rest)
    sources_at = rest.index('<h2 id="sources">')
    main_part, sources_part = rest[:sources_at].rstrip(), rest[sources_at:].strip()
    toc = [x for x in toc if x[0] != "sources"] + [("help", t["help"]), ("questions", t["questions"]), ("sources", t["sources"])]
    sources = re.findall(r'<li>(.*?): <a href="([^"]+)">', sources_part)

    kp = "\n".join(f"          <li>{k}</li>" for k in a["key_points"])
    toc_html = "\n".join(f'              <li><a href="#{i}">{html.escape(n, quote=False)}</a></li>' for i, n in toc)
    if fig_part:
        media = ind(fig_part, 10)
        cta = ""
    else:
        media = ""
        cta = f'''
          <section class="side-cta" aria-labelledby="side-cta-title">
            <h2 id="side-cta-title">{t["cta_title"]}</h2>
            <p>{t["cta_text"]}</p>
            <a class="primary-cta" href="{a["contact"]}">{t["cta_button"]}</a>
          </section>'''
    related = "\n".join(
        f'          <li><a href="{R}{href}">{name}</a><span>{desc}</span></li>' for href, name, desc in a["related"])
    faq = "\n".join(f'''        <div class="faq-item">
          <h3 class="faq-q">{html.escape(q, quote=False)}</h3>
          <p class="faq-a">{html.escape(ans, quote=False)}</p>
        </div>''' for q, ans in a["faq"])

    article = f'''    <article class="article">
      <header class="article-head">
{ind(head_part, 8)}
      </header>

      <aside class="key-points" aria-labelledby="key-points-title">
        <h2 id="key-points-title">{t["key_points"]}</h2>
        <ul>
{kp}
        </ul>
      </aside>

      <aside class="article-side" aria-label="{t["side_label"]}">
        <div class="side-sticky">
{media}
          <nav class="article-toc" aria-labelledby="toc-title">
            <h2 id="toc-title">{t["toc"]}</h2>
            <ol>
{toc_html}
            </ol>
          </nav>{cta}
        </div>
      </aside>

      <div class="article-body">
{ind(main_part, 8)}

        <section class="article-related" aria-labelledby="help">
          <h2 id="help">{t["help"]}</h2>
          <ul class="related-links">
{ind(related, 2)}
          </ul>
        </section>

        <section class="article-faq" aria-labelledby="questions">
          <h2 id="questions">{t["questions"]}</h2>
{ind(faq, 2)}
        </section>

        <section class="article-sources" aria-labelledby="sources">
{ind(sources_part, 10)}
        </section>

        <section class="article-cite" aria-labelledby="cite-title">
          <h2 id="cite-title" class="doc-section-head">{t["cite"]}</h2>
          <pre class="doc-cite">@misc{{liscere_{aid.replace("-", "_")}{"" if lang == "en" else "_pl"},
  author       = {{{{Liscere}}}},
  title        = {{{h1}}},
  howpublished = {{Liscere Field Notes {aid.upper()}}},
  year         = {{{art["date"][:4]}}},
  month        = {art["month_bib"]},{"" if lang == "en" else chr(10) + "  language     = {polish},"}
  url          = {{{URL}}}
}}</pre>
        </section>

        <p class="article-back"><a href="{R}research.html" data-back{"" if lang == "en" else ' hreflang="en"'}>{t["back"]}</a></p>
      </div>
    </article>'''

    other_lang = "pl" if lang == "en" else "en"
    graph_article = {
        "@type": "Article", "@id": URL + "#article", "headline": h1, "name": h1, "description": a["description"],
        "url": URL, "mainEntityOfPage": URL, "inLanguage": t["html_lang"],
        "datePublished": art["date"], "dateModified": art.get("modified", art["date"]),
        "image": [SITE + art["og_image"], SITE + art["poster"]] if art.get("poster") else [SITE + art["og_image"]],
        "author": ORG, "publisher": ORG,
        "isPartOf": {"@type": "CreativeWorkSeries", "name": "Liscere Field Notes", "url": SITE + "research.html"},
        "articleSection": "Field Notes", "about": a["about"], "keywords": a["keywords"],
        ("translationOfWork" if lang == "pl" else "workTranslation"): {"@id": url_of(other_lang, aid) + "#article"},
        "citation": [{"@type": "CreativeWork", "name": html.unescape(re.sub(r"<[^>]+>", "", n)), "url": u} for n, u in sources],
    }
    graph = [graph_article]
    if art.get("video"):
        v = art["video"]
        graph_article["video"] = {"@id": URL + "#video"}
        graph.append({"@type": "VideoObject", "@id": URL + "#video", "name": a["video_name"],
                      "description": a["video_description"], "thumbnailUrl": [SITE + art["poster"], SITE + art["og_image"]],
                      "uploadDate": art["date"], "duration": v["duration"], "contentUrl": SITE + v["src"],
                      "encodingFormat": "video/mp4", "inLanguage": "en-GB", "publisher": ORG})
    graph += [
        {"@type": "Organization", "@id": SITE + "#org", "name": "Liscere", "legalName": "Liscere sp. z o.o.",
         "url": SITE, "logo": SITE + "assets/apple-touch-icon.png"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t["home_name"], "item": SITE if lang == "en" else SITE + "pl/"},
            {"@type": "ListItem", "position": 2, "name": t["research_name"], "item": SITE + "research.html"},
            {"@type": "ListItem", "position": 3, "name": aid.upper(), "item": URL}]},
        {"@type": "FAQPage", "@id": URL + "#faq", "inLanguage": t["html_lang"], "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    header, footer = chrome(lang, aid, R)
    og_video = ""
    if art.get("video"):
        og_video = f'''
  <meta property="og:video" content="{SITE}{art["video"]["src"]}" />
  <meta property="og:video:type" content="video/mp4" />
  <meta property="og:video:width" content="{art["video"]["size"]}" />
  <meta property="og:video:height" content="{art["video"]["size"]}" />'''
    T = lambda s: html.escape(s, quote=True)
    page = f'''<!doctype html>
<html lang="{t["html_lang"]}" class="past-hero article-view">
<head>
  <meta charset="utf-8" />
  {CSP}
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{a["title"]}</title>
  <meta name="description" content="{T(a["description"])}" />
  <meta name="author" content="Liscere" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-video-preview:-1" />
  <meta name="theme-color" content="#030405" />

  <meta property="og:title" content="{T(h1)}" />
  <meta property="og:description" content="{T(a["description"])}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{URL}" />
  <meta property="og:image" content="{SITE}{art["og_image"]}" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{T(a["og_image_alt"])}" />{og_video}
  <meta property="og:site_name" content="Liscere" />
  <meta property="og:locale" content="{t["og_locale"]}" />
  <meta property="og:locale:alternate" content="{UI[other_lang]["og_locale"]}" />
  <meta property="article:published_time" content="{art["date"]}" />
  <meta property="article:section" content="Field Notes" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{T(h1)}" />
  <meta name="twitter:description" content="{T(a["description"])}" />
  <meta name="twitter:image" content="{SITE}{art["og_image"]}" />
  <meta name="twitter:image:alt" content="{T(a["og_image_alt"])}" />

  <link rel="canonical" href="{URL}" />
  <link rel="alternate" hreflang="en" href="{url_of("en", aid)}" />
  <link rel="alternate" hreflang="pl" href="{url_of("pl", aid)}" />
  <link rel="alternate" hreflang="x-default" href="{url_of("en", aid)}" />

  <script type="application/ld+json">
{ld}
  </script>

  <link rel="stylesheet" href="{R}assets/css/fonts.css?v=1" />
  <link rel="icon" type="image/svg+xml" href="{R}assets/favicon.svg?v=4" />
  <link rel="icon" type="image/png" sizes="32x32" href="{R}assets/favicon-32.png?v=4" />
  <link rel="icon" type="image/png" sizes="16x16" href="{R}assets/favicon-16.png?v=4" />
  <link rel="icon" type="image/png" sizes="48x48" href="{R}assets/favicon-48.png?v=4" />
  <link rel="apple-touch-icon" sizes="180x180" href="{R}assets/apple-touch-icon.png?v=4" />
  <link rel="stylesheet" href="{R}assets/css/styles.css?v={CSS_V}" />
</head>
<body>
{header}

  <main id="main-content" class="research-page article-page">
{article}

{footer}
  </main>

  <script src="{R}assets/js/site.js?v=3" defer></script>
  {CF}
</body>
</html>
'''
    assert len(a["description"]) <= 158, (lang, len(a["description"]))
    assert "—" not in page, "em dash"
    out = path_of(lang, aid)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    return out


# ---------------------------------------------------------------- articles
FN_2026_01 = dict(
    id="fn-2026-01", date="2026-11-12", month_bib="nov",
    og_image="assets/video/liscere-supermarket-attack-og.jpg",
    poster="assets/video/liscere-supermarket-attack-poster.jpg",
    video=dict(src="assets/video/liscere-supermarket-attack.mp4", duration="PT1M57S", size=720),
    en=dict(
        title="French Supermarket Refrigeration Attack: OT Lessons | Liscere",
        description="In October 2026 attackers used authorised defrost and setpoint commands to warm fridges in about 700 French supermarkets. What happened and the OT lessons.",
        og_image_alt="Supermarket fridges linked to a Liscere monitor flagging an unexpected command",
        about=["Operational technology security", "Industrial control systems", "Refrigeration controllers", "Cold chain", "Critical infrastructure"],
        keywords="supermarket refrigeration attack, France, October 2026, CERT-FR, OT security, ICS, refrigeration controllers, defrost, setpoint, cold chain",
        video_name="Authorised commands, spoiled food: a two minute explainer",
        video_description="Two minute explainer of the October 2026 supermarket refrigeration attack in France. The scenes showing Liscere are an illustrative reconstruction, not a recording of the incident.",
        contact="../../services.html#contact",
        key_points=[
            "Around 700 supermarkets in France were hit on the night of 11 to 12 October 2026, and controllers from a second manufacturer the following night.",
            "Nothing was broken. The attackers changed defrost cycles and temperature setpoints, normal functions the controllers are built to accept.",
            "Food losses are estimated at tens of millions of euros. On 9 November France attributed the operation to a group it links to Iran&rsquo;s Revolutionary Guard; Tehran rejected the accusation.",
            "The lesson for any OT operator: remove internet exposure first, then ask whether each command makes sense for the process at that moment.",
        ],
        related=[
            ("services/ot-security-assessment.html", "OT and ICS security assessment", "Find what is exposed and what an attacker could change."),
            ("services/ot-visibility-monitoring.html", "OT visibility and monitoring", "See what your control network is actually being told to do."),
            ("services/ot-incident-response.html", "Incident response for OT", "Contain an incident without stopping the process."),
        ],
        faq=[
            ("What happened in the French supermarket refrigeration attack?",
             "On the night of 11 to 12 October 2026 attackers reached the refrigeration controllers of about 700 supermarkets in France and used defrost cycles and temperature setpoints to warm fridges and freezers overnight until the food was lost. A second wave the next night reached controllers from a second manufacturer."),
            ("How did the attackers get in?",
             "It has not been publicly confirmed. Researchers counted thousands of refrigeration controller interfaces reachable from the internet, many of them on end of life systems. CERT-FR's first recommendation is to take the affected controllers off the internet."),
            ("How can an attack like this be detected?",
             "Each command was authorised on its own, so the useful question is whether it makes sense for the process at that moment: a setpoint far outside the normal range, a defrost far longer than usual, the same change pushed to many cabinets within seconds. Removing exposure comes first; contextual monitoring adds a check on what the network is actually being told to do."),
        ],
    ),
    pl=dict(
        title="Cyberatak na chłodnie supermarketów we Francji: lekcje OT | Liscere",
        description="Atakujący użyli autoryzowanych poleceń odszraniania i nastaw, by ogrzać chłodnie ok. 700 supermarketów we Francji. Co się stało i jakie są lekcje dla OT.",
        og_image_alt="Lodówki w supermarkecie połączone z monitorem Liscere, który sygnalizuje nieoczekiwane polecenie",
        about=["Cyberbezpieczeństwo OT", "Przemysłowe systemy sterowania", "Sterowniki chłodnicze", "Łańcuch chłodniczy", "Infrastruktura krytyczna"],
        keywords="cyberatak na chłodnie, supermarkety, Francja, październik 2026, CERT-FR, cyberbezpieczeństwo OT, ICS, sterowniki chłodnicze, odszranianie, nastawy, NIS2, KSC",
        video_name="Autoryzowane polecenia, zepsuta żywność: film (po angielsku)",
        video_description="Dwuminutowy film o cyberataku na chłodnie supermarketów we Francji w październiku 2026. Sceny z Liscere to ilustracyjna rekonstrukcja, a nie nagranie incydentu.",
        contact="../../uslugi.html#contact",
        key_points=[
            "W nocy z 11 na 12 października 2026 zaatakowano około 700 supermarketów we Francji, a następnej nocy także sterowniki drugiego producenta.",
            "Nic nie zostało zepsute. Atakujący zmienili cykle odszraniania i nastawy temperatury, czyli normalne funkcje, które sterowniki mają wykonywać.",
            "Straty żywności szacuje się na dziesiątki milionów euro. 9 listopada Francja przypisała operację grupie, którą łączy z irańskim Korpusem Strażników Rewolucji; Teheran odrzucił oskarżenia.",
            "Lekcja dla każdego operatora OT: najpierw usunąć ekspozycję na internet, potem pytać, czy każde polecenie ma sens dla procesu w danej chwili.",
        ],
        related=[
            ("pl/uslugi/audyt-bezpieczenstwa-ot.html", "Audyt bezpieczeństwa OT i ICS", "Sprawdzamy, co jest wystawione na zewnątrz i co atakujący mógłby zmienić."),
            ("pl/uslugi/widocznosc-i-monitoring-ot.html", "Widoczność i monitoring OT", "Zobacz, co naprawdę trafia do Twojej sieci sterowania."),
            ("pl/uslugi/reagowanie-na-incydenty-ot.html", "Reagowanie na incydenty OT", "Opanowanie incydentu bez zatrzymywania procesu."),
            ("pl/uslugi/nis2-ksc.html", "Gotowość do NIS2 i KSC", "Obowiązki, audyt i plan działań z perspektywą OT."),
        ],
        faq=[
            ("Co się stało podczas cyberataku na chłodnie supermarketów we Francji?",
             "W nocy z 11 na 12 października 2026 atakujący dostali się do sterowników chłodniczych około 700 supermarketów we Francji i użyli cykli odszraniania oraz nastaw temperatury, aby przez noc ogrzać lodówki i zamrażarki, aż żywność się zepsuła. Druga fala następnej nocy objęła sterowniki drugiego producenta."),
            ("Jak atakujący uzyskali dostęp?",
             "Nie zostało to publicznie potwierdzone. Badacze naliczyli tysiące interfejsów sterowników chłodniczych dostępnych z internetu, wiele z nich w systemach bez wsparcia producenta. Pierwsza rekomendacja CERT-FR to odłączenie dotkniętych sterowników od internetu."),
            ("Jak można wykryć taki atak?",
             "Każde polecenie samo w sobie było autoryzowane, więc kluczowe pytanie brzmi, czy ma ono sens dla procesu w danej chwili: nastawa daleko poza normalnym zakresem, odszranianie znacznie dłuższe niż zwykle, ta sama zmiana wysłana do wielu szaf w ciągu kilku sekund. Najpierw trzeba usunąć ekspozycję; monitoring kontekstowy dodaje kontrolę tego, co faktycznie trafia do sieci."),
            ("Czy to dotyczy firm w Polsce?",
             "Może dotyczyć każdego, kto ma sterowniki dostępne z internetu: chłodnie, magazyny, zakłady przetwórcze i automatykę budynkową. Produkcja, przetwarzanie i hurtowa dystrybucja żywności należą do sektorów objętych NIS2, a znowelizowana ustawa o KSC, obowiązująca od 3 kwietnia 2026, obejmuje także systemy OT."),
        ],
    ),
)

ARTICLES = [FN_2026_01]

if __name__ == "__main__":
    for art in ARTICLES:
        for lang in ("en", "pl"):
            print(os.path.relpath(build(art, lang), ROOT_DIR))
