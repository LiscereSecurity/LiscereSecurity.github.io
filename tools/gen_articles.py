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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT_DIR = os.path.dirname(HERE)
SITE = "https://liscere.com/"
CSS_V = "20261113-a5"
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
        cite_report="Cite this report", pdf_title="Full report (PDF)", pdf_text="The same text as a typeset PDF, with page numbers for citation.",
        pdf_button="Download PDF", references="References",
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


# Series: filter key on research.html, label shown in the kicker, name in structured data.
SERIES = {
    "fieldnotes": ("FIELD NOTES", "Field Notes", "Liscere Field Notes"),
    "landscape": ("LANDSCAPE BRIEFING", "Landscape Briefing", "Liscere Landscape Briefings"),
    "research": ("TECHNICAL REPORT", "Technical Report", "Liscere Technical Reports"),
    "guides": ({"en": "GUIDE", "pl": "PORADNIK"}, "Guide", "Liscere Guides"),
}


def url_of(lang, aid):
    return SITE + (f"research/{aid}/" if lang == "en" else f"pl/badania/{aid}/")


def path_of(lang, aid):
    return os.path.join(ROOT_DIR, *(["research", aid] if lang == "en" else ["pl", "badania", aid]), "index.html")


REACH = {"en": "Based in Poland, working across Europe and worldwide.", "pl": "Siedziba w Polsce, działamy w całej Europie i na świecie."}


def chrome(lang, aid, R, has_pl=True):
    """Header and footer. R is the relative path to the site root. English only pages send the
    PL switch to the Polish notice page, which links back here."""
    other = (f"{R}pl/badania/{aid}/" if lang == "en" else f"{R}research/{aid}/")
    pl_attr = ""
    if not has_pl:
        other, pl_attr = f"/pl/tylko-po-angielsku.html?from=/research/{aid}/", ' rel="nofollow"'
    if lang == "en":
        nav = (f'      <a href="{R}index.html">Home</a>\n'
               f'      <a href="{R}services.html">Services</a>\n'
               f'      <a href="{R}about.html">About</a>\n'
               f'      <a href="{R}research.html" aria-current="page">Research</a>\n'
               f'      <a class="lang-switch" href="{other}"{pl_attr} hreflang="pl" lang="pl" aria-label="Polski">PL</a>')
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
               f'      <a href="{R}pl/badania.html" aria-current="page">Badania</a>\n'
               f'      <a class="lang-switch" href="{other}" hreflang="en" lang="en" aria-label="English">EN</a>')
        logo = f"{R}pl/index.html"
        foot = (f'<a href="{R}pl/index.html">Start</a> · <a href="{R}pl/uslugi.html">Usługi</a> · '
                f'<a href="{R}pl/o-nas.html">O nas</a> · <a href="{R}pl/faq.html">FAQ</a> · '
                f'<a href="{R}pl/badania.html">Badania</a> · '
                '<a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">LinkedIn</a> · '
                '<a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> · '
                f'<a href="{R}pl/prywatnosc.html">Prywatność</a> · '
                f'<a href="{R}pl/dane-spolki.html">Dane spółki</a> · '
                f'<a href="{R}pl/warunki.html">Warunki korzystania</a>')
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
    footer = f'    <p class="research-foot">{foot}<br />{REACH[lang]}<br />© 2026 Liscere sp. z o.o.</p>'
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
    series = art.get("series", "fieldnotes")
    s_kicker, s_label, s_name = SERIES[series]
    if isinstance(s_kicker, dict):
        s_kicker = s_kicker[lang]
    is_report = series in ("landscape", "research")
    has_pl = "pl" in art.get("langs", ("en", "pl"))
    head_part = head_part.replace(f'<p class="kicker">{s_kicker}',
        f'<p class="kicker"><a class="series-back" href="{R}{"research.html" if lang == "en" else "pl/badania.html"}#{series}" data-back>{s_kicker}</a>', 1)
    if art.get("byline"):
        # Author, version, copyright and licence, revision note: between the title and the lede.
        meta = (f'<p class="article-byline">{art["byline"]}</p>\n'
                f'<p class="doc-rights">{art["rights"]}</p>\n'
                f'<p class="doc-revised">{art["revised"]}</p>\n')
        head_part = re.sub(r"(</h1>\s*)", lambda m: m.group(1) + meta + "\n", head_part, count=1)

    # ids on the section headings, for the contents list
    toc = []
    def add_id(m):
        title = m.group(1)
        hid = "sources" if title in (t["sources"], t.get("references")) else slug(re.sub(r"^\d+\.\s*", "", title))
        toc.append((hid, title))
        return f'<h2 id="{hid}">{title}</h2>'
    rest = re.sub(r"<h2>(.*?)</h2>", add_id, rest)
    sources_at = rest.index('<h2 id="sources">')
    main_part, sources_part = rest[:sources_at].rstrip(), rest[sources_at:].strip()
    nxt = sources_part.find("<h2", 4)
    if nxt > 0:   # appendices printed after the references go at the end of the text
        main_part += "\n\n" + sources_part[nxt:].strip()
        sources_part = sources_part[:nxt].strip()
    src_title = next(n for i, n in toc if i == "sources")
    toc = ([x for x in toc if x[0] != "sources"] + [("help", t["help"])]
           + ([("questions", t["questions"])] if a.get("faq") else []) + [("sources", src_title)])
    sources = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", sources_part, re.S):
        li = re.sub(r'<span class="ref-label">.*?</span>\s*', "", li)
        link = re.search(r'<a href="([^"]+)"', li)
        name = re.sub(r":\s*<a [^>]*>.*?</a>\s*$", "", li).strip()
        sources.append((name, (SITE + link.group(1).lstrip("/")) if link and link.group(1).startswith("/") else (link.group(1) if link else None)))
    if is_report:
        # numbered references: anchors on the list, and in-text [n] markers link to them
        n = iter(range(1, 1000))
        sources_part = re.sub(r"<li>", lambda m: f'<li id="ref-{next(n)}">', sources_part)
        main_part = re.sub(r"\[(\d+(?:, \d+)*)\]", lambda m: "[" + ", ".join(
            f'<a class="ref" href="#ref-{x}">{x}</a>' for x in m.group(1).split(", ")) + "]", main_part)

    kp = "\n".join(f"          <li>{k}</li>" for k in a["key_points"])
    toc_html = "\n".join(f'              <li><a href="#{i}">{html.escape(n, quote=False)}</a></li>' for i, n in toc)
    pdf_card = ""
    if art.get("pdf"):
        pdf_card = f'''
          <section class="side-pdf" aria-labelledby="side-pdf-title">
            <h2 id="side-pdf-title">{t["pdf_title"]}</h2>
            <p>{t["pdf_text"]}</p>
            <a class="secondary-cta" href="{R}{art["pdf"]}" target="_blank" rel="noopener">{t["pdf_button"]} &#8599;</a>
          </section>'''
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
        </div>''' for q, ans in a.get("faq", []))
    faq_section = f'''

        <section class="article-faq" aria-labelledby="questions">
          <h2 id="questions">{t["questions"]}</h2>
{ind(faq, 2)}
        </section>''' if a.get("faq") else ""
    if art.get("bibtex"):
        cite = f'''<h2 id="cite-title" class="doc-section-head">{t["cite_report"]}</h2>
          <pre class="doc-cite">{art["bibtex"]}</pre>'''
    else:
        cite = f'''<h2 id="cite-title" class="doc-section-head">{t["cite"]}</h2>
          <pre class="doc-cite">@misc{{liscere_{aid.replace("-", "_")}{"" if lang == "en" else "_pl"},
  author       = {{{{Liscere}}}},
  title        = {{{h1}}},
  howpublished = {{{s_name} {aid.upper()}}},
  year         = {{{art["date"][:4]}}},
  month        = {art["month_bib"]},{"" if lang == "en" else chr(10) + "  language     = {polish},"}
  url          = {{{URL}}}
}}</pre>'''

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
          </nav>{pdf_card}{cta}
        </div>
      </aside>

      <div class="article-body">
{ind(main_part, 8)}

        <section class="article-related" aria-labelledby="help">
          <h2 id="help">{t["help"]}</h2>
          <ul class="related-links">
{ind(related, 2)}
          </ul>
        </section>{faq_section}

        <section class="article-sources" aria-labelledby="sources">
{ind(sources_part, 10)}
        </section>

        <section class="article-cite" aria-labelledby="cite-title">
          {cite}
        </section>

        <p class="article-back"><a href="{R}{"research.html" if lang == "en" else "pl/badania.html"}" data-back>{t["back"]}</a></p>
      </div>
    </article>'''

    other_lang = "pl" if lang == "en" else "en"
    graph_article = {
        "@type": "Article", "@id": URL + "#article", "headline": h1, "name": h1, "description": a["description"],
        "url": URL, "mainEntityOfPage": URL, "inLanguage": t["html_lang"],
        "datePublished": art["date"], "dateModified": art.get("modified", art["date"]),
        "image": [SITE + art["og_image"], SITE + art["poster"]] if art.get("poster") else [SITE + art["og_image"]],
        "author": art.get("author", ORG), "publisher": ORG,
        "isPartOf": {"@type": "CreativeWorkSeries", "name": s_name, "url": SITE + "research.html#" + series},
        "articleSection": s_label, "about": a["about"], "keywords": a["keywords"],
        "citation": [dict({"@type": "CreativeWork", "name": html.unescape(re.sub(r"<[^>]+>", "", n))}, **({"url": u} if u else {}))
                     for n, u in sources],
    }
    if has_pl:
        graph_article[("translationOfWork" if lang == "pl" else "workTranslation")] = {"@id": url_of(other_lang, aid) + "#article"}
    if is_report:
        graph_article["@type"] = "ScholarlyArticle"
        graph_article["abstract"] = " ".join(html.unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r'<p class="lede">(.*?)</p>', head_part, re.S))
        graph_article.update({"version": art["version"], "license": "https://creativecommons.org/licenses/by/4.0/",
                              "copyrightHolder": art.get("copyright_holder", ORG), "identifier": aid.upper()})
    if art.get("pdf"):
        graph_article["encoding"] = {"@type": "MediaObject", "contentUrl": SITE + art["pdf"], "encodingFormat": "application/pdf"}
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
            {"@type": "ListItem", "position": 2, "name": t["research_name"], "item": SITE + ("research.html" if lang == "en" else "pl/badania.html")},
            {"@type": "ListItem", "position": 3, "name": aid.upper(), "item": URL}]},
    ]
    if a.get("faq"):
        graph.append({"@type": "FAQPage", "@id": URL + "#faq", "inLanguage": t["html_lang"], "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    header, footer = chrome(lang, aid, R, has_pl)
    img_type = "image/png" if art["og_image"].endswith(".png") else "image/jpeg"
    alternates = (f'''
  <link rel="alternate" hreflang="en" href="{url_of("en", aid)}" />
  <link rel="alternate" hreflang="pl" href="{url_of("pl", aid)}" />
  <link rel="alternate" hreflang="x-default" href="{url_of("en", aid)}" />''' if has_pl else "")
    locale_alt = f'''
  <meta property="og:locale:alternate" content="{UI[other_lang]["og_locale"]}" />''' if has_pl else ""
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
  <meta name="author" content="{art.get("author_name", "Liscere")}" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-video-preview:-1" />
  <meta name="theme-color" content="#030405" />

  <meta property="og:title" content="{T(h1)}" />
  <meta property="og:description" content="{T(a["description"])}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{URL}" />
  <meta property="og:image" content="{SITE}{art["og_image"]}" />
  <meta property="og:image:type" content="{img_type}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{T(a["og_image_alt"])}" />{og_video}
  <meta property="og:site_name" content="Liscere" />
  <meta property="og:locale" content="{t["og_locale"]}" />{locale_alt}
  <meta property="article:published_time" content="{art["date"]}" />
  <meta property="article:section" content="{s_label}" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{T(h1)}" />
  <meta name="twitter:description" content="{T(a["description"])}" />
  <meta name="twitter:image" content="{SITE}{art["og_image"]}" />
  <meta name="twitter:image:alt" content="{T(a["og_image_alt"])}" />

  <link rel="canonical" href="{URL}" />{alternates}

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

  <script src="{R}assets/js/site.js?v=4" defer></script>
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


CC_BY = '<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener license">CC BY 4.0</a>'
SALMAZO = {"@type": "Person", "name": "Bruno Salmazo", "@id": "https://orcid.org/0009-0000-4410-3616",
           "identifier": "https://orcid.org/0009-0000-4410-3616", "sameAs": "https://orcid.org/0009-0000-4410-3616"}

LB_2026_01 = dict(
    id="lb-2026-01", series="landscape", langs=("en",), date="2026-06-23", modified="2026-10-07",
    og_image="assets/og-image.png", pdf="assets/papers/liscere-ot-threat-landscape.pdf", version="1.1",
    author=SALMAZO, author_name="Bruno Salmazo", copyright_holder=SALMAZO,
    byline="By Bruno Salmazo · Liscere",
    rights="Version 1.1 · © 2026 Bruno Salmazo · Published by Liscere · Licensed under " + CC_BY,
    revised="Revised 7 October 2026: date corrected from May to June 2026 (first published 23 June 2026); NIS2 reference added; licence statement added.",
    bibtex="""@techreport{salmazo_threatlandscape_2026,
  author      = {Bruno Salmazo},
  title       = {The Operational Technology Threat Landscape, 2026: From Access to Action},
  institution = {Liscere},
  year        = {2026},
  month       = jun,
  number      = {LB-2026-01},
  type        = {Landscape Briefing},
  url         = {https://liscere.com/research/lb-2026-01/}
}""",
    en=dict(
        title="The OT Threat Landscape 2026: From Access to Action | Liscere",
        description="Why the centre of gravity in OT attacks has moved from gaining access to issuing valid commands: a Liscere briefing on the 2026 threat landscape.",
        og_image_alt="Liscere: OT Cybersecurity",
        about=["Operational technology security", "Industrial control systems", "OT threat landscape", "Ransomware", "NIS2"],
        keywords="OT threat landscape 2026, ICS security, industrial cyber incidents, OT ransomware, engineering workstation, Modbus, NIS2, IEC 62443, context-aware security",
        contact="../../services.html#contact",
        key_points=[
            "In the 2025 SANS survey, more than one in five organisations reported an OT security incident, and around four in ten of those disrupted operations.",
            "Dragos tracked 119 ransomware groups affecting roughly 3,300 industrial organisations in 2025, up from 80 groups the year before.",
            "Attackers increasingly enter through legitimate access and then act like operators, issuing commands that are valid at the protocol level.",
            "Protocol checks, access control and anomaly detection leave one question open: is this valid action appropriate for the state the plant is in?",
        ],
        related=[
            ("services/ot-security-assessment.html", "OT and ICS security assessment", "Find what is exposed and what an attacker could change."),
            ("services/ot-visibility-monitoring.html", "OT visibility and monitoring", "See what your control network is actually being told to do."),
            ("services/nis2-ksc-compliance.html", "NIS2 and KSC readiness", "Turn the directive's expectations into concrete OT controls."),
        ],
        faq=[
            ("How have OT attacks changed?",
             "Access is increasingly the way in rather than the obstacle. Adversaries reach industrial networks through legitimate access, learn how the control system operates and then issue commands that are valid at the protocol level, so their activity looks like an operator's."),
            ("Why do current OT defences leave a gap?",
             "Protocol checks confirm a message is well formed, access control confirms the sender may act, and anomaly detection flags unusual traffic. A command can pass all three and still be wrong for the moment, such as a configuration change during production or a setpoint that is unsafe for the current process state."),
            ("Do NIS2 and IEC 62443 close this gap?",
             "They raise expectations for monitoring, segmentation and least privilege in industrial environments, and they motivate context-aware control of individual actions. They do not implement it themselves, so operators still have to close the distance between what is permitted and what is appropriate."),
        ],
    ),
)

# ---------------------------------------------------------------- converted reports (English only)
from data_reports import REPORT_META

S_ASSESS = ("services/ot-security-assessment.html", "OT and ICS security assessment", "Find what is exposed and what an attacker could change.")
S_MONITOR = ("services/ot-visibility-monitoring.html", "OT visibility and monitoring", "See what your control network is actually being told to do.")
S_NIS2 = ("services/nis2-ksc-compliance.html", "NIS2 and KSC readiness", "Turn the directive's expectations into concrete OT controls.")
S_IR = ("services/ot-incident-response.html", "Incident response for OT", "Contain an incident without stopping the process.")
S_PROJECTS = ("services/automation-projects.html", "Automation projects", "PLC, HMI and SCADA engineering built secure from the start.")


def report(aid, title, about, keywords, key_points, faq, related, holder=None):
    m = REPORT_META[aid]
    series = "landscape" if aid.startswith("lb") else "research"
    return dict(
        id=aid, series=series, langs=("en",), date=m["date"], modified="2026-10-07",
        og_image="assets/og-image.png", pdf=m["pdf"], version="1.1",
        author=SALMAZO, author_name="Bruno Salmazo", copyright_holder=holder or ORG,
        byline="By Bruno Salmazo · Liscere", rights=m["rights"], revised=m["revised"], bibtex=m["bibtex"],
        en=dict(title=title, description=m["description"], og_image_alt="Liscere: OT Cybersecurity",
                about=about, keywords=keywords, contact="../../services.html#contact",
                key_points=key_points, faq=faq, related=related),
    )


LB_2026_02 = report(
    "lb-2026-02", "OT Protocol Encryption: A Landscape Survey | Liscere",
    ["Operational technology security", "Industrial protocols", "Encryption", "OPC UA", "IEC 62351"],
    "OT protocol encryption, industrial protocols, OPC UA security, IEC 62351, PROFINET security, CIP Security, TLS adoption, passive monitoring",
    ["Encryption capability and encryption activation are different things: internet-wide scans place TLS adoption on industrial protocols in single-digit percentages.",
     "OT security standards deliberately favour integrity and authenticity over confidentiality for real-time control data.",
     "Encryption arrives by functional plane: vendor management channels first, supervisory links slowly, the real-time protection plane last or never.",
     "An opaque channel with no natural point of legitimate access is confined to a single protocol class, and even there secondary evidence exists."],
    [("How much OT traffic is encrypted?",
      "Little, as far as can be measured. Internet-wide scans place TLS adoption on industrial protocols in single-digit percentages, and the OPC UA misconfiguration pattern documented in 2020 is still present in 2025. These scans cover internet-exposed devices; internal networks cannot be measured from outside."),
     ("Why do OT standards not encrypt everything?",
      "Where OT security standards land, they prioritise integrity and authenticity over confidentiality for real-time control data. In substations this is codified: the applicable standard stipulates that time-critical protection traffic is not to be encrypted."),
     ("Does encryption stop passive OT monitoring?",
      "Mostly not today. Encryption arrives first on vendor management channels and last, if ever, on the real-time plane. The case of an opaque channel with no point of legitimate access is confined to a single protocol class.")],
    [S_MONITOR, S_ASSESS, S_NIS2])

LB_2026_03 = report(
    "lb-2026-03", "OT Protocols and Vendors: A Field Guide | Liscere",
    ["Industrial protocols", "Operational technology", "Industrial control systems", "PLC vendors"],
    "OT protocols, industrial protocols explained, Modbus, PROFINET, EtherNet/IP, OPC UA, S7, PLC vendors, Purdue model, industrial networks",
    ["A single industrial facility usually speaks several protocols at once, each serving a different layer of the operation.",
     "Field devices, engineering stations, supervisory systems and cloud platforms each communicate in their own way.",
     "The briefing maps which protocols dominate each layer, who the major controller vendors are and how they relate.",
     "It is a reference map: it argues no thesis and evaluates no product."],
    [("Why do industrial plants use so many protocols?",
      "Because each layer of the operation has a different job: field devices exchange real-time signals with controllers, engineering stations program those controllers, supervisory systems collect data from them and cloud platforms receive it all. Each job has its own protocols."),
     ("Who is this guide for?",
      "Anyone who needs to reason about OT security without blurring the layers together: what a given protocol actually does and where a given product actually sits.")],
    [S_ASSESS, S_MONITOR, S_PROJECTS])

LB_2026_04 = report(
    "lb-2026-04", "The S7 Encryption Gap in the Installed Base | Liscere",
    ["Siemens S7", "Industrial protocols", "Encryption", "Operational technology security"],
    "Siemens S7 encryption, S7comm, S7CommPlus, S7-1200, S7-1500, S7-300, S7-400, PLC security, TLS, passive monitoring",
    ["Current Siemens controllers protect programming and HMI traffic with certificate-based transport security by default.",
     "Most of the installed S7 base still carries communication that a passive observer can read.",
     "Three regimes coexist: cleartext S7comm on S7-300 and S7-400, application-layer encrypted S7CommPlus, and S7CommPlus in TLS on current hardware.",
     "The gap persists through economics rather than ignorance. Encryption is the state of the art, not yet the state of the field."],
    [("Is Siemens S7 traffic encrypted?",
      "On current controllers configured with the current engineering toolchain, yes, by default. Across the installed base, mostly not: the widely deployed S7-300 and S7-400 families use cleartext S7comm."),
     ("Why does the installed base stay unencrypted?",
      "The briefing finds that the gap persists through economics rather than ignorance, and that the readable regime still dominates the field."),
     ("What does this mean for passive monitoring of S7 networks?",
      "Across most of the deployed estate passive observation remains viable because the traffic is readable. Where encryption is in force, it marks the boundary of the passive vantage.")],
    [S_MONITOR, S_ASSESS, S_NIS2])

LB_2026_05 = report(
    "lb-2026-05", "Passive vs Active Methods in OT Security | Liscere",
    ["Operational technology security", "Passive monitoring", "Active scanning", "Asset inventory"],
    "passive vs active OT, OT asset discovery, OT scanning, passive monitoring, ICS asset inventory, OT network monitoring, encryption",
    ["Discovery and inventory are one question, continuous monitoring and detection another; the debate usually conflates them.",
     "Active methods reach silent devices and recover metadata traffic does not carry, at a disruption risk that OT-safe scanners reduce but do not eliminate.",
     "Passive methods add no traffic and observe continuously, but are blind to silent devices, depend on a vantage point and are increasingly limited by encryption.",
     "Federal and sector guidance sets passive monitoring as the baseline; the mature pattern is hybrid."],
    [("Should OT networks be scanned actively or monitored passively?",
      "Both, for different questions. Passive monitoring is the baseline in federal and sector guidance; active methods reach silent devices and recover metadata, at a disruption risk that must be justified. The mature pattern is hybrid."),
     ("Why is OT different from IT here?",
      "For concrete reasons: industrial devices are fragile, priorities do not tolerate unplanned outages, and equipment stays in service for decades."),
     ("How does encryption affect passive monitoring?",
      "Hardware measurement shows that what an encrypted channel changes is less the method of observation than its location.")],
    [S_MONITOR, S_ASSESS, S_IR])

LTR_2026_01 = report(
    "ltr-2026-01", "Context-Aware Evaluation of Modbus/TCP Actions | Liscere",
    ["Industrial control systems", "Modbus/TCP", "Context-aware security", "Operational technology security"],
    "Modbus/TCP security, context-aware evaluation, industrial control actions, maintenance window, OT lab, action-evaluation chain, ICS security",
    ["Classic Modbus/TCP carries no notion of authorisation or operational appropriateness.",
     "The Liscere action-evaluation chain assesses an action by protocol operation, automation artefact, operational context and policy constraint.",
     "The same sensitive configuration write yields an alert in production and an allow during a declared maintenance window.",
     "Two negative controls show the maintenance window is not a blanket alert suppressor; all four scenarios returned their expected decision."],
    [("What does this report demonstrate?",
      "That a protocol-valid write can be judged by context: holding the operation, the target and the value constant, and varying only a declared maintenance window, the same write yields an alert in production and an allow during maintenance."),
     ("What does it not yet measure?",
      "Detection performance, robustness, and generality across context dimensions and protocols. It is a feasibility baseline.")],
    [S_MONITOR, S_ASSESS, S_NIS2], holder=SALMAZO)

LTR_2026_02 = report(
    "ltr-2026-02", "The Liscere Framework for ICS Control Actions | Liscere",
    ["Industrial control systems", "Operational technology security", "Context-aware security", "Policy evaluation"],
    "Liscere framework, operational legitimacy, industrial control actions, ICS security model, Modbus/TCP, automation artefact, operational context, policy",
    ["An action can be valid at the protocol level, sent over an authorised channel and still be wrong for the plant's operational state.",
     "The framework evaluates each control action by protocol operation, automation artefact, operational context and policy constraint.",
     "It reconstructs the action, resolves the artefact, adds declared context, evaluates policy and returns a decision with an evidence record.",
     "The model sits above protocol encodings; Modbus/TCP is its first instantiation."],
    [("What is the Liscere framework?",
      "A protocol-agnostic model for evaluating an industrial control action along four dimensions: the protocol operation, the automation artefact it affects, the operational context in which it occurs and the applicable policy constraint."),
     ("What decision does it return?",
      "A decision together with an evidence record. The report defines four decisions: allow, alert, deny and escalate.")],
    [S_MONITOR, S_ASSESS, S_NIS2], holder=SALMAZO)

LTR_2026_03 = report(
    "ltr-2026-03", "Contextual ICS Evaluation on a Siemens S7-1200 | Liscere",
    ["Industrial control systems", "Siemens S7-1200", "Modbus/TCP", "Passive monitoring", "Context-aware security"],
    "contextual evaluation, Siemens S7-1200, Modbus/TCP, operational phase inference, learned grammar, passive OT monitoring, ICS security",
    ["Liscere judges not whether an action is permitted but whether it is coherent with the operational phase the process is in.",
     "Validated on a physical Siemens S7-1200 tank process with a strictly passive observer on mirrored traffic.",
     "The same valid write is allowed or alerted according to a phase the evaluator infers from observed process state.",
     "The artefact-to-phase grammar can be learned from observation; decision logs, captures and grammar files are published."],
    [("How is this different from anomaly detection?",
      "The approach is structural rather than value-based: it asks whether a given write to a given control artefact is coherent with the current operational phase, not whether values are statistically unusual. It also differs from process interlocks and from formal preventive enforcement."),
     ("What are its limits?",
      "The evaluator is still told which signal carries process state, learning assumes a clean and representative baseline, the inferred context is not resistant to forged telemetry, and validation rests on one cyclic process, protocol and controller.")],
    [S_MONITOR, S_ASSESS, S_NIS2])

LTR_2026_04 = report(
    "ltr-2026-04", "Passive OT Monitoring under TLS 1.3 | Liscere",
    ["Encryption", "Siemens S7-1200", "Passive monitoring", "TLS 1.3", "Operational technology security"],
    "TLS 1.3 OT, encrypted OT traffic, Siemens S7-1200 G2 Web API, passive monitoring encryption, JSON-RPC, traffic metadata, ICS security",
    ["Under TLS 1.3 a passive observer on a mirror port cannot see the method, target, value or session token of a control action.",
     "A size and timing sensor detects bursts of activity but is unreliable for an isolated, well-chosen write.",
     "With a legitimate decryption point, the process variable needed for contextual evaluation is recoverable at a workable rate.",
     "Encryption changes the observation vantage, not the evaluation core."],
    [("Can encrypted OT traffic be monitored passively?",
      "Not its content. On a Siemens S7-1200 G2 Web API over TLS 1.3, a passive observer on a mirror port is blind to the method, the target, the value and the session token. Traffic metadata reveals bursts of activity but not a single well-chosen write."),
     ("What does this mean for contextual evaluation?",
      "The evaluation logic is protocol-independent; what encryption changes is where its evidence must come from. The report points to the point of legitimate decryption as the place to position it.")],
    [S_MONITOR, S_ASSESS, S_NIS2])

LTR_2026_05 = report(
    "ltr-2026-05", "OPC UA Security Modes and Passive Observation | Liscere",
    ["OPC UA", "Encryption", "Passive monitoring", "Operational technology security"],
    "OPC UA security modes, OPC UA Sign, SignAndEncrypt, OPC UA security policy, passive monitoring, OT encryption, IEC 62541",
    ["OPC UA has three message security modes: None, Sign and SignAndEncrypt. The mode, not the policy, decides what a passive observer recovers.",
     "Under None and under Sign the full exchange is legible; under SignAndEncrypt only the transport envelope survives.",
     "Sign gives integrity and authenticity on the wire while leaving traffic visible to a legitimate observer.",
     "Studies from 2020 and from 2024 to 2025 agree that a large share of observable OPC UA runs without confidentiality."],
    [("Is OPC UA traffic encrypted?",
      "Only under the SignAndEncrypt mode. Under None and under Sign the full exchange can be read; Sign adds integrity and authenticity but leaves the payload in clear."),
     ("How common is unencrypted OPC UA?",
      "Internet-wide studies five years apart agree that a large and persistent fraction of observable OPC UA runs without confidentiality, because of the configuration burden of activating it rather than any weakness in the cryptography.")],
    [S_MONITOR, S_ASSESS, S_NIS2])


# ---------------------------------------------------------------- guides (EN + PL)
GD_2026_01 = dict(
    id="gd-2026-01", series="guides", date="2026-11-13", month_bib="nov", og_image="assets/og-image.png",
    en=dict(
        title="NIS2 and Poland's KSC act: who is covered and by when | Liscere",
        description="Who NIS2 covers, when Poland's KSC act applies, the deadlines and fines, and what the rules mean for the control systems that run the plant.",
        og_image_alt="Liscere: industrial cybersecurity",
        about=["NIS2", "Cybersecurity regulation", "Operational technology security", "Critical infrastructure", "Compliance"],
        keywords="NIS2, NIS2 scope, KSC act, Poland, 3 April 2026, 3 April 2027, essential entities, important entities, incident reporting, OT security, IEC 62443",
        contact="../../services.html#contact",
        key_points=[
            "NIS2 covers medium and large entities in the sectors of Annexes I and II, and suppliers are increasingly asked for evidence too.",
            "In Poland the amended KSC act has been in force since 3 April 2026; risk management measures are due by 3 April 2027.",
            "The deadline to apply for entry in the register of essential and important entities passed on 3 October 2026.",
            "The obligations cover information systems, and in a plant that includes controllers, operator stations and the control network.",
        ],
        related=[
            ("services/nis2-ksc-compliance.html", "NIS2 readiness", "Turn the directive's expectations into concrete OT controls."),
            ("services/ot-visibility-monitoring.html", "OT visibility and monitoring", "The asset inventory that risk analysis starts from."),
            ("services/ot-incident-response.html", "Incident response for OT", "A plan that works when the process cannot simply be stopped."),
        ],
        faq=[
            ("Who does NIS2 cover?",
             "Medium and large entities, meaning at least 50 staff or more than 10 million euros of turnover or balance sheet, in the sectors listed in Annexes I and II of the directive: energy, transport, banking, financial market infrastructure, health, water, waste water, digital infrastructure, ICT service management, public administration, space, postal services, waste management, chemicals, food, manufacturing, digital providers and research. Some services are covered regardless of size."),
            ("When did Poland's KSC act start to apply?",
             "The act of 23 January 2026 amending the national cybersecurity system act was published on 2 March 2026 and entered into force on 3 April 2026. Entities that existed at that point have until 3 April 2027 to put risk management measures in place."),
            ("Who has to register?",
             "Entities that meet the criteria apply for entry in the register of essential and important entities. For those covered when the act entered into force, the deadline was 3 October 2026, so a company that has not applied should do so without waiting to be asked."),
            ("What are the fines?",
             "The directive sets a maximum of 10 million euros or 2% of total worldwide annual turnover, whichever is higher, for essential entities, and 7 million euros or 1.4% for important entities. Published guidance on the Polish act indicates that administrative fines can in most cases only be imposed from April 2028."),
            ("Does NIS2 cover OT systems?",
             "Yes. The obligations apply to information systems, and in an industrial company those include PLCs, operator stations, SCADA and the networks between them. Compliance work that stops at the office network leaves the part that runs the physical process uncovered."),
        ],
    ),
    pl=dict(
        title="NIS2 i ustawa o KSC: kogo dotyczy i jakie są terminy | Liscere",
        description="Kogo dotyczy NIS2, od kiedy obowiązuje ustawa o KSC, jakie są terminy i kary oraz co z tego wynika dla systemów sterowania OT w zakładzie.",
        og_image_alt="Liscere: cyberbezpieczeństwo przemysłowe",
        about=["NIS2", "Ustawa o KSC", "Bezpieczeństwo OT", "Infrastruktura krytyczna", "Zgodność"],
        keywords="NIS2, kogo dotyczy NIS2, ustawa o KSC, nowelizacja KSC, 3 kwietnia 2026, 3 kwietnia 2027, podmiot kluczowy, podmiot ważny, wykaz, zgłaszanie incydentów, bezpieczeństwo OT",
        contact="../../../pl/uslugi.html#contact",
        key_points=[
            "NIS2 obejmuje średnie i duże podmioty z sektorów wymienionych w załącznikach I i II, a dostawcy coraz częściej są pytani o dowody przez swoich klientów.",
            "W Polsce znowelizowana ustawa o KSC obowiązuje od 3 kwietnia 2026 roku, a środki zarządzania ryzykiem trzeba wdrożyć do 3 kwietnia 2027 roku.",
            "Termin na wniosek o wpis do wykazu podmiotów kluczowych i ważnych upłynął 3 października 2026 roku.",
            "Obowiązki dotyczą systemów informacyjnych, a w zakładzie należą do nich także sterowniki, stacje operatorskie i sieć sterowania.",
        ],
        related=[
            ("pl/uslugi/nis2-ksc.html", "Gotowość do NIS2 i KSC", "Obowiązki, audyt i plan działań z perspektywą OT."),
            ("pl/uslugi/widocznosc-i-monitoring-ot.html", "Widoczność i monitoring OT", "Inwentaryzacja, od której zaczyna się analiza ryzyka."),
            ("pl/uslugi/reagowanie-na-incydenty-ot.html", "Reagowanie na incydenty OT", "Plan, który działa, gdy procesu nie można po prostu zatrzymać."),
        ],
        faq=[
            ("Kogo dotyczy NIS2?",
             "Średnich i dużych podmiotów, czyli zatrudniających co najmniej 50 osób albo z obrotem lub sumą bilansową powyżej 10 milionów euro, z sektorów wymienionych w załącznikach I i II dyrektywy: energetyka, transport, bankowość, infrastruktura rynków finansowych, ochrona zdrowia, woda, ścieki, infrastruktura cyfrowa, zarządzanie usługami ICT, administracja publiczna, przestrzeń kosmiczna, usługi pocztowe, gospodarowanie odpadami, chemia, żywność, produkcja, dostawcy cyfrowi i badania naukowe. Część usług jest objęta niezależnie od wielkości."),
            ("Od kiedy obowiązuje ustawa o KSC?",
             "Ustawa z 23 stycznia 2026 roku o zmianie ustawy o krajowym systemie cyberbezpieczeństwa została ogłoszona 2 marca 2026 roku i weszła w życie 3 kwietnia 2026 roku. Podmioty istniejące w tym dniu mają czas na wdrożenie środków zarządzania ryzykiem do 3 kwietnia 2027 roku."),
            ("Kto musi zarejestrować się w wykazie?",
             "Podmioty spełniające kryteria składają wniosek o wpis do wykazu podmiotów kluczowych i ważnych. Dla objętych w dniu wejścia ustawy w życie termin upłynął 3 października 2026 roku, więc firma, która tego nie zrobiła, powinna złożyć wniosek niezwłocznie."),
            ("Jakie są kary?",
             "Dyrektywa przewiduje maksymalnie 10 milionów euro lub 2% całkowitego rocznego światowego obrotu, w zależności od tego, która kwota jest wyższa, dla podmiotów kluczowych, oraz 7 milionów euro lub 1,4% dla podmiotów ważnych. Z dostępnych opracowań wynika, że kary administracyjne na gruncie polskiej ustawy mogą być w większości przypadków nakładane dopiero od kwietnia 2028 roku."),
            ("Czy NIS2 obejmuje systemy OT?",
             "Tak. Obowiązki dotyczą systemów informacyjnych, a w firmie przemysłowej należą do nich sterowniki PLC, stacje operatorskie, SCADA i łączące je sieci. Projekt zgodności, który kończy się na sieci biurowej, pomija tę część, która steruje procesem fizycznym."),
        ],
    ),
)

GD_2026_02 = dict(
    id="gd-2026-02", series="guides", date="2026-11-13", month_bib="nov", og_image="assets/og-image.png",
    en=dict(
        title="Reporting an OT incident: 24 hours, 72 hours, one month | Liscere",
        description="How to report a significant incident within 24 hours, 72 hours and one month when it hits the control network: deadlines, recipients and evidence.",
        og_image_alt="Liscere: industrial cybersecurity",
        about=["Incident reporting", "NIS2", "Operational technology security", "Incident response", "CSIRT"],
        keywords="incident reporting, NIS2, KSC act, 24 hours, 72 hours, final report, CSIRT NASK, CSIRT GOV, CSIRT MON, OT incident response, evidence",
        contact="../../services.html#contact",
        key_points=[
            "A significant incident is reported in three steps: an early warning within 24 hours, a notification within 72 hours and a final report within one month.",
            "Reports go to the sector CSIRT and, until it is operational, to CSIRT NASK, CSIRT GOV or CSIRT MON.",
            "In OT the hard part is not the form but the decision: isolating a system touches a process that is still running.",
            "Evidence in OT is fragile, so a packet capture and a copy of the configuration come before any restart.",
        ],
        related=[
            ("services/ot-incident-response.html", "Incident response for OT", "A plan that works when the process cannot simply be stopped."),
            ("services/nis2-ksc-compliance.html", "NIS2 readiness", "Turn the directive's expectations into concrete OT controls."),
            ("services/ot-visibility-monitoring.html", "OT visibility and monitoring", "See what the control network is actually being told to do."),
        ],
        faq=[
            ("What are the incident reporting deadlines?",
             "An early warning within 24 hours of detecting a significant incident, a full notification within 72 hours, and a final report within one month of the notification. If the incident is still ongoing at that point, a progress report is filed and the final report follows once handling is complete. Trust service providers have 24 hours for the notification."),
            ("Who receives the report?",
             "The sector CSIRT for the sector concerned. Until it declares operational capability, reports are taken by CSIRT NASK, CSIRT GOV or CSIRT MON, and the information flows through the S46 system. If personal data is involved, a separate 72 hour deadline runs towards the data protection authority."),
            ("When does the clock start?",
             "At detection, which is the moment someone recognises the event as an incident, including at night and at the weekend. In OT the event is often noticed first as a process problem, so the recognition point matters more than the alert."),
            ("What should be preserved before restarting anything?",
             "A capture of the network traffic, a copy of the controller program and configuration, photographs of the screens and a record of the times. Many controllers keep no logs, and a restart or a restore from backup erases the state that would have been the evidence."),
        ],
    ),
    pl=dict(
        title="Zgłaszanie incydentu w OT: 24 h, 72 h, miesiąc | Liscere",
        description="Jak zgłosić incydent poważny w 24 godziny, 72 godziny i miesiąc, gdy dotyczy on sieci sterowania: terminy, adresat, dowody i procedura dla OT.",
        og_image_alt="Liscere: cyberbezpieczeństwo przemysłowe",
        about=["Zgłaszanie incydentów", "NIS2", "Ustawa o KSC", "Bezpieczeństwo OT", "CSIRT"],
        keywords="zgłoszenie incydentu, incydent poważny, NIS2, ustawa o KSC, 24 godziny, 72 godziny, sprawozdanie końcowe, CSIRT NASK, CSIRT GOV, CSIRT MON, reagowanie na incydenty OT",
        contact="../../../pl/uslugi.html#contact",
        key_points=[
            "Incydent poważny zgłasza się w trzech krokach: wczesne ostrzeżenie w 24 godziny, zgłoszenie w 72 godziny i sprawozdanie końcowe w miesiąc.",
            "Zgłoszenie trafia do CSIRT sektorowego, a zanim ogłosi on zdolność operacyjną, do CSIRT NASK, CSIRT GOV lub CSIRT MON.",
            "W OT najtrudniejszy nie jest formularz, lecz decyzja: izolacja systemu dotyka procesu, który nadal trwa.",
            "Dowody w OT są ulotne, więc zrzut ruchu i kopia konfiguracji powinny powstać przed jakimkolwiek restartem.",
        ],
        related=[
            ("pl/uslugi/reagowanie-na-incydenty-ot.html", "Reagowanie na incydenty OT", "Plan, który działa, gdy procesu nie można po prostu zatrzymać."),
            ("pl/uslugi/nis2-ksc.html", "Gotowość do NIS2 i KSC", "Obowiązki, audyt i plan działań z perspektywą OT."),
            ("pl/uslugi/widocznosc-i-monitoring-ot.html", "Widoczność i monitoring OT", "Zobacz, co naprawdę trafia do Twojej sieci sterowania."),
        ],
        faq=[
            ("Jakie są terminy zgłoszenia incydentu?",
             "Wczesne ostrzeżenie w ciągu 24 godzin od wykrycia incydentu poważnego, pełne zgłoszenie w ciągu 72 godzin i sprawozdanie końcowe w ciągu miesiąca od zgłoszenia. Jeżeli incydent nadal trwa, w tym terminie składa się sprawozdanie z postępu, a końcowe po zakończeniu obsługi. Dostawcy usług zaufania mają na zgłoszenie 24 godziny."),
            ("Do kogo trafia zgłoszenie?",
             "Do CSIRT sektorowego właściwego dla danego sektora. Zanim ogłosi on zdolność operacyjną, zgłoszenia przyjmują CSIRT NASK, CSIRT GOV i CSIRT MON, a obieg informacji prowadzi system S46. Jeżeli incydent obejmuje dane osobowe, osobno biegnie termin 72 godzin wobec organu ochrony danych."),
            ("Od kiedy liczy się czas?",
             "Od wykrycia, czyli od chwili, w której ktoś rozpoznał zdarzenie jako incydent, także w nocy i w weekend. W OT zdarzenie bywa najpierw zauważone jako problem technologiczny, więc moment rozpoznania waży więcej niż sam alarm."),
            ("Co zabezpieczyć przed restartem?",
             "Zrzut ruchu sieciowego, kopię programu i konfiguracji sterownika, zdjęcia ekranów oraz zapis czasów. Wiele sterowników nie prowadzi logów, a restart lub przywrócenie z kopii kasuje stan, który byłby dowodem."),
        ],
    ),
)

GD_2026_03 = dict(
    id="gd-2026-03", series="guides", date="2026-11-13", month_bib="nov", og_image="assets/og-image.png",
    en=dict(
        title="IEC 62443 in practice: the parts, zones and security levels | Liscere",
        description="How the IEC 62443 series is organised, which part a plant should read, what zones and conduits are, and what SL-T, SL-C and SL-A actually mean.",
        og_image_alt="Liscere: industrial cybersecurity",
        about=["IEC 62443", "Industrial control systems", "Operational technology security", "Security levels", "Zones and conduits"],
        keywords="IEC 62443, ISA 62443, 62443-3-3, 62443-4-2, 62443-4-1, 62443-2-4, 62443-3-2, zones and conduits, security levels, SL-T, SL-C, SL-A, foundational requirements, ISASecure",
        contact="../../services.html#contact",
        key_points=[
            "IEC 62443 is a series, not a single standard, and it is organised around three roles: asset owner, service provider and product supplier.",
            "A plant usually needs 62443-3-2 for zones and risk, 62443-3-3 for system requirements and 62443-2-1 as the organisational frame.",
            "Security levels only mean something with the variant attached: SL-T is the target, SL-C what a product can deliver, SL-A what the installation actually reaches.",
            "Products, development processes and service providers can be certified. There is no 62443 certificate for a plant.",
        ],
        related=[
            ("services/ot-security-assessment.html", "OT and ICS security assessment", "An assessment aligned with the IEC 62443 method."),
            ("services/nis2-ksc-compliance.html", "NIS2 readiness", "Turn the directive's expectations into concrete OT controls."),
            ("services/ot-visibility-monitoring.html", "OT visibility and monitoring", "The inventory that zones and conduits are drawn from."),
        ],
        faq=[
            ("What is IEC 62443?",
             "A series of standards for the cybersecurity of industrial automation and control systems, developed jointly by ISA99 and IEC TC 65 and often written ISA/IEC 62443. It is organised in four groups: general concepts (1-x), policies and procedures (2-x), system requirements (3-x) and component requirements (4-x), and it addresses asset owners, service providers and product suppliers separately."),
            ("Which part of IEC 62443 applies to a plant?",
             "In practice three: 62443-3-2 for risk assessment and the division into zones and conduits, 62443-3-3 for the system security requirements, which can be written straight into a tender specification, and 62443-2-1 for the security programme itself. Integrators work to 2-4, and product vendors to 4-1 and 4-2."),
            ("What do SL-T, SL-C and SL-A mean?",
             "SL-T is the target security level for a zone, taken from the risk assessment. SL-C is the capability a product or system can deliver when it is configured correctly. SL-A is the level actually achieved in the running installation. Saying a site is at SL 2 without naming the variant says very little, and the gap between SL-C and SL-A is usually where the real findings are."),
            ("Can a plant be certified to IEC 62443?",
             "Products, vendor development processes and service organisations can be certified, through schemes such as ISASecure. An asset owner builds a security programme in line with 62443-2-1 and can have it assessed, but there is no plant certificate in the sense of ISO 9001. When a supplier claims compliance, ask which part, what SL-C, and whether there is an independent certificate or only a self declaration."),
            ("Does IEC 62443 help with NIS2?",
             "The law does not name the standard, but NIS2 requires measures appropriate to the risk, and 62443 is a recognised way of showing what that means in an industrial environment. A zone model under 3-2 evidences the risk analysis, the requirements in 3-3 become concrete technical measures, and 2-4 supports the supply chain obligation."),
        ],
    ),
    pl=dict(
        title="IEC 62443 w praktyce: części, strefy i poziomy SL | Liscere",
        description="Z ilu części składa się IEC 62443, którą czytać w zakładzie, czym są strefy i kanały oraz co naprawdę znaczą poziomy SL-T, SL-C i SL-A.",
        og_image_alt="Liscere: cyberbezpieczeństwo przemysłowe",
        about=["IEC 62443", "Przemysłowe systemy sterowania", "Bezpieczeństwo OT", "Poziomy bezpieczeństwa", "Strefy i kanały"],
        keywords="IEC 62443, norma 62443, 62443-3-3, 62443-4-2, 62443-4-1, 62443-2-4, 62443-3-2, strefy i kanały, poziomy bezpieczeństwa, SL-T, SL-C, SL-A, wymagania podstawowe, ISASecure, certyfikat",
        contact="../../../pl/uslugi.html#contact",
        key_points=[
            "IEC 62443 to seria, a nie jedna norma, zbudowana wokół trzech ról: właściciela zasobu, dostawcy usług i producenta.",
            "Zakładowi zwykle potrzebne są 62443-3-2 (strefy i ryzyko), 62443-3-3 (wymagania dla systemu) oraz 62443-2-1 jako rama organizacyjna.",
            "Poziomy bezpieczeństwa mają sens dopiero z odmianą: SL-T to cel, SL-C to możliwości produktu, SL-A to stan faktyczny instalacji.",
            "Certyfikować można produkt, proces rozwoju i firmę usługową. Nie istnieje certyfikat 62443 dla zakładu.",
        ],
        related=[
            ("pl/uslugi/audyt-bezpieczenstwa-ot.html", "Audyt bezpieczeństwa OT i ICS", "Audyt prowadzony zgodnie z metodyką IEC 62443."),
            ("pl/uslugi/nis2-ksc.html", "Gotowość do NIS2 i KSC", "Obowiązki, audyt i plan działań z perspektywą OT."),
            ("pl/uslugi/widocznosc-i-monitoring-ot.html", "Widoczność i monitoring OT", "Inwentaryzacja, z której rysuje się strefy i kanały."),
        ],
        faq=[
            ("Czym jest IEC 62443?",
             "To seria norm dotyczących cyberbezpieczeństwa przemysłowych systemów automatyki i sterowania, tworzona wspólnie przez komitet ISA99 i IEC TC 65, stąd oznaczenie ISA/IEC 62443. Dzieli się na cztery grupy: pojęcia ogólne (1-x), polityki i procedury (2-x), wymagania dla systemu (3-x) i wymagania dla komponentów (4-x), a osobno adresuje właścicieli zasobów, dostawców usług i producentów."),
            ("Którą część IEC 62443 czytać w zakładzie?",
             "W praktyce trzy: 62443-3-2 dla oceny ryzyka oraz podziału na strefy i kanały, 62443-3-3 dla wymagań bezpieczeństwa systemu, które można wpisać wprost do specyfikacji przetargowej, oraz 62443-2-1 dla samego programu bezpieczeństwa. Integratorzy pracują według 2-4, a producenci według 4-1 i 4-2."),
            ("Co oznaczają SL-T, SL-C i SL-A?",
             "SL-T to docelowy poziom bezpieczeństwa strefy, wynikający z oceny ryzyka. SL-C to poziom, jaki produkt lub system jest w stanie zapewnić przy prawidłowej konfiguracji. SL-A to poziom faktycznie osiągnięty w działającej instalacji. Stwierdzenie „mamy SL 2” bez podania odmiany niewiele znaczy, a różnica między SL-C a SL-A jest zwykle miejscem, w którym znajdują się realne ustalenia audytu."),
            ("Czy zakład może uzyskać certyfikat IEC 62443?",
             "Certyfikować można produkty, procesy rozwoju u producenta i firmy usługowe, w schematach takich jak ISASecure. Właściciel zasobu buduje program bezpieczeństwa zgodny z 62443-2-1 i może poddać go ocenie, ale certyfikat dla zakładu w rozumieniu ISO 9001 nie istnieje. Gdy dostawca deklaruje zgodność, warto zapytać: która część, jaki SL-C i czy jest certyfikat niezależnej jednostki, czy deklaracja własna."),
            ("Czy IEC 62443 pomaga w NIS2?",
             "Przepisy nie wskazują normy z nazwy, ale NIS2 wymaga środków adekwatnych do ryzyka, a 62443 jest uznanym sposobem pokazania, co to oznacza w środowisku przemysłowym. Model stref według 3-2 stanowi dowód analizy ryzyka, wymagania z 3-3 przekładają się na konkretne środki techniczne, a 2-4 wspiera obowiązek bezpieczeństwa łańcucha dostaw."),
        ],
    ),
)

ARTICLES = [GD_2026_01, GD_2026_02, GD_2026_03, FN_2026_01, LB_2026_01, LB_2026_02, LB_2026_03, LB_2026_04, LB_2026_05,
            LTR_2026_01, LTR_2026_02, LTR_2026_03, LTR_2026_04, LTR_2026_05]

if __name__ == "__main__":
    for art in ARTICLES:
        for lang in art.get("langs", ("en", "pl")):
            print(os.path.relpath(build(art, lang), ROOT_DIR))
