"""Polish Services (pl/uslugi.html), About (pl/o-nas.html) and FAQ (pl/faq.html)."""
import json, html, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
exec(open(os.path.join(HERE, "data_en.py")).read())
from data_pl import PL, PL_NAMES
SITE = "https://liscere.com/"
R = "../"  # from /pl/ to the site root

def esc(t): return html.escape(t, quote=False)
def attr(t): return html.escape(t, quote=True)

def shell(*, title, desc, path, en_path, current, main_class, body, ld, scripts="", og_type="website"):
    url = SITE + path
    en_url = SITE + en_path
    ldj = "\n".join("  " + l for l in json.dumps(ld, indent=2, ensure_ascii=False).split("\n"))
    cur = lambda k: ' aria-current="page"' if k == current else ""
    en_rel = R + (en_path if en_path else "index.html")
    return f"""<!doctype html>
<html lang="pl-PL" class="past-hero">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{attr(desc)}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="pl" href="{url}">
  <link rel="alternate" hreflang="x-default" href="{en_url}">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#030405">

  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Liscere">
  <meta property="og:locale" content="pl_PL">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{attr(title)}">
  <meta property="og:description" content="{attr(desc)}">
  <meta property="og:image" content="https://liscere.com/assets/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{attr(title)}">
  <meta name="twitter:description" content="{attr(desc)}">
  <meta name="twitter:image" content="https://liscere.com/assets/og-image.png">

  <link rel="stylesheet" href="{R}assets/css/fonts.css?v=1" />
  <link rel="icon" type="image/svg+xml" href="{R}assets/favicon.svg?v=4" />
  <link rel="icon" type="image/png" sizes="32x32" href="{R}assets/favicon-32.png?v=4" />
  <link rel="icon" type="image/png" sizes="16x16" href="{R}assets/favicon-16.png?v=4" />
  <link rel="icon" type="image/png" sizes="48x48" href="{R}assets/favicon-48.png?v=4" />
  <link rel="apple-touch-icon" sizes="180x180" href="{R}assets/apple-touch-icon.png?v=4" />
  <link rel="stylesheet" href="{R}assets/css/styles.css?v={CSSV}" />

  <script type="application/ld+json">
{ldj}
  </script>
</head>
<body>
  <a class="skip-link" href="#main-content">Przejdź do treści</a>

  <header class="site-chrome" aria-label="Nawigacja">
    <a class="site-logo" href="./index.html" aria-label="Liscere, strona główna">
      <img class="wordmark-svg" src="{R}assets/liscere-wordmark-dark.svg?v=3" alt="Liscere" width="1040" height="216" />
    </a>
    <nav class="site-nav" aria-label="Strony">
      <a href="./index.html"{cur('home')}>Start</a>
      <a href="./uslugi.html"{cur('services')}>Usługi</a>
      <a href="./o-nas.html"{cur('about')}>O nas</a>
      <a href="{R}research.html" hreflang="en">Badania</a>
      <a class="lang-switch" href="{en_rel}" hreflang="en" lang="en" aria-label="English">EN</a>
    </nav>
  </header>

  <main id="main-content" class="{main_class}">
{body}
    <p class="research-foot"><a href="./index.html">Start</a> · <a href="./uslugi.html">Usługi</a> · <a href="./o-nas.html">O nas</a> · <a href="./faq.html">FAQ</a> · <a href="{R}research.html" hreflang="en">Badania</a> · <a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">LinkedIn</a> · <a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> · <a href="{R}privacy.html" hreflang="en">Prywatność</a><br />© 2026 Liscere sp. z o.o.</p>
  </main>

  <script src="{R}assets/js/site.js?v=1" defer></script>
{scripts}</body>
</html>
"""

ORG = {"@type": "Organization", "@id": SITE + "#org", "name": "Liscere", "url": SITE}

def contact_form(selected=None):
    opts = "\n".join(f'                <option value="{attr(v)}"{" selected" if v == selected else ""}>{esc(PL_NAMES[v])}</option>' for v, _ in SERVICES)
    return f"""        <form class="form-card" data-contact data-mailto="hello@liscere.com" novalidate>
          <div class="form-grid">
            <div>
              <label for="f-name">Imię i nazwisko</label>
              <input id="f-name" name="name" type="text" autocomplete="name" required>
            </div>
            <div>
              <label for="f-company">Firma</label>
              <input id="f-company" name="company" type="text" autocomplete="organization">
            </div>
            <div>
              <label for="f-email">Służbowy e-mail</label>
              <input id="f-email" name="email" type="email" autocomplete="email" required>
            </div>
            <div>
              <label for="f-service">Czego dotyczy zapytanie?</label>
              <select id="f-service" name="service">
                <option value="General enquiry">Zapytanie ogólne</option>
{opts}
              </select>
            </div>
            <div class="full">
              <label for="f-message">Wiadomość</label>
              <textarea id="f-message" name="message" required placeholder="Opisz w kilku zdaniach, czego potrzebujesz."></textarea>
            </div>
            <div class="full consent">
              <input id="f-consent" name="consent" type="checkbox" required>
              <label for="f-consent">Wyrażam zgodę na przetwarzanie przez Liscere sp. z o.o. danych z tego formularza w celu odpowiedzi na moje zapytanie, zgodnie z <a href="{R}privacy.html" hreflang="en">informacją o prywatności</a> (w języku angielskim).</label>
            </div>
            <div class="hp" aria-hidden="true">
              <label for="f-website">Website</label>
              <input id="f-website" name="website" type="text" tabindex="-1" autocomplete="off">
            </div>
            <div class="full actions">
              <button class="primary-cta" type="submit">Wyślij wiadomość</button>
            </div>
            <p class="full form-status" role="status" aria-live="polite"></p>
          </div>
        </form>"""

# ---------------------------------------------------------------- Usługi
CARDS = {
 "ot-security-assessment": ("Audyt", "Przegląd sterowników, stacji operatorskich, dostępu zdalnego i sieci, który wykrywa podatności i luki. Z testami penetracyjnymi uzgodnionych systemów."),
 "ot-visibility-monitoring": ("Widoczność", "Pełna inwentaryzacja zasobów OT i mapa komunikacji w sieci sterowania, z opcjonalnym pilotażem naszego frameworku."),
 "nis2-ksc-compliance": ("Zgodność", "Czego NIS2 i ustawa o KSC wymagają od zakładu: co ma zastosowanie, czego brakuje i jakich dowodów oczekują audytorzy, z uwzględnieniem OT."),
 "ot-incident-response": ("Gotowość", "Plan dopasowany do zakładu: kto decyduje o zatrzymaniu linii, jak izolować bez utraty widoku i jak zgłosić incydent na czas."),
 "automation-projects": ("Projekty", "Od analizy po uruchomienie na miejscu: oprogramowanie PLC i HMI oraz sprzęt, gdy jest potrzebny, na Siemens, Rockwell, Schneider, Beckhoff, CODESYS i innych."),
 "automation-modernisation": ("Istniejące systemy", "Istniejące oprogramowanie PLC i HMI sprawdzane pod kątem błędów, ryzyk i luk bezpieczeństwa, a potem ulepszane lub migrowane ze starszych platform."),
 "industrial-training": ("Ludzie", "Praktyczne szkolenia dla operatorów i inżynierów: sprzęt OT, oprogramowanie, protokoły i sieci, automatyka i bezpieczeństwo. Dopasowane do każdego zespołu."),
}
FEATURED = {"ot-visibility-monitoring", "automation-projects"}
IDS = {"ot-security-assessment": "ot-ics-assessment", "ot-visibility-monitoring": "ot-visibility", "nis2-ksc-compliance": "nis2-ksc",
       "ot-incident-response": "incident-response", "automation-projects": "automation-projects", "automation-modernisation": "modernisation",
       "industrial-training": "training"}
NAME_BY_SLUG = {s: n for n, s in SERVICES}

def card(slug):
    tag, txt = CARDS[slug]
    feat = " featured" if slug in FEATURED else ""
    return f"""        <li class="card{feat}" id="{IDS[slug]}">
          <span class="tag">{esc(tag)}</span>
          <h3>{esc(PL_NAMES[NAME_BY_SLUG[slug]])}</h3>
          <p>{esc(txt)}</p>
          <a class="secondary-cta card-cta" href="./uslugi/{PL[slug]['pl']}.html">Więcej</a>
        </li>
"""

def uslugi():
    sec = ["ot-security-assessment", "ot-visibility-monitoring", "nis2-ksc-compliance", "ot-incident-response"]
    aut = ["automation-projects", "automation-modernisation", "industrial-training"]
    body = f"""
    <section class="section hero">
      <div class="hero-copy">
        <p class="kicker">Usługi</p>
        <h1>Bezpieczeństwo i automatyka dla procesów, które nie mogą się zatrzymać.</h1>
        <p class="lead">Chronimy systemy przemysłowe i budujemy automatykę bezpieczną od samego początku.</p>
      </div>
      <div class="hero-scrollcue" aria-hidden="true">
        <span class="hero-scrollcue-label">Przewiń</span>
        <span class="hero-scrollcue-track"><span class="hero-scrollcue-dot"></span></span>
      </div>
    </section>

    <section class="section" id="ot-security">
      <div class="section-head">
        <div>
          <p class="kicker">Bezpieczeństwo przemysłowe i OT</p>
          <h2>Dla sieci, która porusza fizyczny świat.</h2>
        </div>
      </div>
      <ul class="card-grid">
{''.join(card(s) for s in sec)}      </ul>
    </section>

    <section class="section" id="automation">
      <div class="section-head">
        <div>
          <p class="kicker">Inżynieria automatyki</p>
          <h2>Automatyka bezpieczna od pierwszej linii kodu.</h2>
        </div>
      </div>
      <ul class="card-grid cols-3">
{''.join(card(s) for s in aut)}      </ul>
    </section>

    <section class="section" id="contact">
      <div class="contact-grid">
        <div class="contact-aside">
          <p class="kicker">Kontakt</p>
          <h2>Powiedz nam, czego potrzebujesz. Znajdziemy rozwiązanie.</h2>
          <p class="section-side">Naszym celem jest ochrona tego, co krytyczne, i ciężko pracujemy, aby to było możliwe.</p>
          <p class="mono">hello@liscere.com</p>
          <p class="mono"><a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">linkedin.com/company/liscere</a></p>
        </div>
{contact_form()}
      </div>
    </section>
"""
    items = [{"@type": "ListItem", "position": i + 1, "item": {"@type": "Service", "name": PL_NAMES[NAME_BY_SLUG[s]],
              "provider": {"@id": SITE + "#org"}, "url": f"{SITE}pl/uslugi/{PL[s]['pl']}.html"}} for i, s in enumerate(sec + aut)]
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "WebPage", "@id": SITE + "pl/uslugi.html", "url": SITE + "pl/uslugi.html", "inLanguage": "pl-PL",
           "name": "Usługi cyberbezpieczeństwa przemysłowego i automatyki | Liscere", "about": {"@id": SITE + "#org"}},
          {"@type": "ItemList", "name": "Usługi Liscere", "itemListElement": items}]}
    return shell(title="Usługi cyberbezpieczeństwa przemysłowego i automatyki | Liscere",
                 desc="Audyty bezpieczeństwa OT, widoczność OT, gotowość do NIS2 i KSC, reagowanie na incydenty oraz bezpieczne projekty PLC i HMI, modernizacja i szkolenia.",
                 path="pl/uslugi.html", en_path="services.html", current="services",
                 main_class="services-page sales-page", body=body, ld=ld,
                 scripts=f'  <script src="{R}assets/js/contact-form.js?v=20261111-bot4" defer></script>\n')

# ---------------------------------------------------------------- O nas
def o_nas():
    body = f"""    <article class="aeo-doc">
      <h1 class="doc-title">O Liscere</h1>

      <section class="about-item">
        <h2>Czym jest Liscere</h2>
        <p>Liscere jest firmą zajmującą się cyberbezpieczeństwem przemysłowym. Pomagamy operatorom przemysłowym i infrastruktury krytycznej chronić systemy, które prowadzą ich procesy fizyczne, i działamy jednocześnie w trzech obszarach:</p>
        <ul>
          <li><strong>Usługi bezpieczeństwa:</strong> audyty bezpieczeństwa OT i ICS, widoczność i monitoring OT, gotowość do NIS2 i KSC oraz reagowanie na incydenty OT.</li>
          <li><strong>Inżynieria automatyki:</strong> projekty PLC i HMI bezpieczne od samego początku, przegląd i modernizacja istniejącej automatyki oraz szkolenia przemysłowe.</li>
          <li><strong>Badania i rozwój:</strong> nowe narzędzia dla bezpieczeństwa przemysłowego, począwszy od frameworku, który ocenia, czy polecenie przemysłowe pasuje do stanu procesu.</li>
        </ul>
        <p>Każdy obszar zasila pozostałe. To, co widzimy w terenie, kształtuje narzędzia, które budujemy, i automatykę, którą dostarczamy, a badania stojące za tymi narzędziami wyostrzają każdy audyt.</p>
      </section>

      <section class="about-item">
        <h2>O nas</h2>
        <p>Liscere powstało w Polsce w 2026 roku z przekonania, że cyberbezpieczeństwo przemysłowe stało się pilną potrzebą. Działamy globalnie, wszędzie tam, gdzie krytyczne systemy wymagają ochrony.</p>
      </section>

      <section class="about-item">
        <h2>Dlaczego bezpieczeństwo przemysłowe ma znaczenie</h2>
        <p>Uzdatnianie wody, energetyka, produkcja i transport działają na systemach sterowania, które zbudowano po to, by utrzymywać proces w ruchu, a nie by się bronić. Wielu z nich nie da się załatać, zrestartować ani wymienić bez zatrzymania procesu, którym sterują. Gdy zostają zaatakowane, skutki są fizyczne: linia staje, dawka się zmienia, sprzęt ulega uszkodzeniu albo ludzie są narażeni na niebezpieczeństwo.</p>
        <p>Zmieniły się też same ataki. Napastnicy coraz częściej docierają do tych sieci przez legalny dostęp, a następnie działają jak operatorzy, wydając polecenia, które przechodzą każdą kontrolę techniczną. Nasz <a href="{R}research/lb-2026-01/" hreflang="en">raport o krajobrazie zagrożeń</a> (w języku angielskim) opisuje to przejście od dostępu do działania.</p>
        <p>Regulacje nadrabiają zaległości. NIS2 czyni cyberbezpieczeństwo obowiązkiem kierownictwa podmiotów kluczowych i ważnych w całej UE, a w Polsce wdraża ją nowelizacja ustawy o krajowym systemie cyberbezpieczeństwa. Systemy, które mają największe znaczenie, często są chronione najsłabiej. Dlatego się nimi zajmujemy.</p>
      </section>

      <section class="about-item">
        <h2>Framework, który budujemy</h2>
        <p>Równolegle z usługami rozwijamy framework do kontekstowej oceny działań sterujących w systemach przemysłowych. Jego myśl przewodnia jest krótka: autoryzowane nie zawsze znaczy właściwe. Polecenie może przejść każdą kontrolę tożsamości, dostępu i protokołu, a mimo to być niewłaściwe dla bieżącego stanu procesu fizycznego.</p>
        <p>Framework obserwuje kopię ruchu OT z portu mirror przełącznika i nigdy nie znajduje się na ścieżce sterowania. Na podstawie tego ruchu odtwarza wykonane działania, rozpoznaje fazę pracy procesu i ocenia, czy każde działanie do niej pasuje. Jego celem jest niezależność od producenta i protokołu. Uzupełnia istniejące zabezpieczenia: nie zastępuje zapór sieciowych, segmentacji sieci ani kontroli dostępu.</p>
        <p>Framework jest w fazie aktywnego rozwoju i został zweryfikowany w naszym laboratorium. Wyniki publikujemy w naszych <a href="{R}research.html" hreflang="en">badaniach</a> (w języku angielskim).</p>
      </section>

      <section class="about-item">
        <h2>Niezależność</h2>
        <p class="aeo-note">Liscere sp. z o.o. jest niezależną spółką. Nie jest powiązana z żadnym innym dostawcą ani produktem z zakresu cyberbezpieczeństwa i nie należy jej z nimi mylić.</p>
      </section>
    </article>
"""
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "AboutPage", "@id": SITE + "pl/o-nas.html", "url": SITE + "pl/o-nas.html", "inLanguage": "pl-PL",
           "name": "O Liscere", "about": {"@id": SITE + "#org"}}]}
    return shell(title="O Liscere | Firma cyberbezpieczeństwa przemysłowego",
                 desc="Liscere to europejska firma cyberbezpieczeństwa przemysłowego z siedzibą w Polsce: usługi bezpieczeństwa OT, bezpieczna automatyka oraz badania i rozwój.",
                 path="pl/o-nas.html", en_path="about.html", current="about",
                 main_class="research-page about-main", body=body, ld=ld)

# ---------------------------------------------------------------- FAQ
U = lambda slug: f"./uslugi/{PL[slug]['pl']}.html"
FAQ1 = [
 ("Czym zajmuje się Liscere?", "Liscere jest europejską firmą zajmującą się cyberbezpieczeństwem przemysłowym, z siedzibą w Polsce i działającą globalnie. Świadczymy usługi bezpieczeństwa i bezpiecznej inżynierii automatyki dla operatorów przemysłowych i infrastruktury krytycznej oraz rozwijamy nowe narzędzia dla bezpieczeństwa przemysłowego, począwszy od frameworku do kontekstowej oceny działań sterujących.", None),
 ("Jakie usługi oferuje Liscere?", "Dwie grupy usług. Bezpieczeństwo przemysłowe i OT: audyty bezpieczeństwa OT i ICS, widoczność i monitoring OT, gotowość do NIS2 i KSC oraz reagowanie na incydenty OT. Inżynieria automatyki: projekty automatyki (programowanie PLC i HMI, sprzęt i uruchomienie), przegląd i modernizacja istniejącej automatyki oraz szkolenia przemysłowe. Każda usługa ma własną stronę, dostępną ze {a}.", ("strony usług", "./uslugi.html")),
 ("Dlaczego firma zajmująca się cyberbezpieczeństwem buduje też automatykę?", "Ponieważ wiele problemów z bezpieczeństwem OT powstaje już pierwszego dnia: otwarty dostęp do sterowników, płaskie sieci, brak kopii zapasowych. Projektowanie automatyki z myślą o bezpieczeństwie od początku pozwala ich uniknąć, a nasza praca w obszarze bezpieczeństwa pokazuje, gdzie projekty zwykle zawodzą.", None),
 ("Z kim współpracuje Liscere?", "Z organizacjami przemysłowymi i infrastruktury krytycznej każdej wielkości: zakładami produkcyjnymi, przedsiębiorstwami użyteczności publicznej, energetyką, wodociągami i kanalizacją, transportem i systemami budynkowymi oraz ich dostawcami.", None),
 ("Gdzie działa Liscere?", "Globalnie. Liscere jest europejską firmą z siedzibą w Polsce i realizuje projekty w Europie i poza nią. Prace związane z gotowością do NIS2 obejmują UE, gdzie każde państwo członkowskie stosuje dyrektywę poprzez własne prawo krajowe, w Polsce poprzez ustawę o krajowym systemie cyberbezpieczeństwa.", None),
 ("Czy Liscere pomoże nam przygotować się do NIS2 i KSC?", "Tak. Nasza ocena gotowości odnosi każdy obowiązek do stanu obecnego, gromadzi dane o widoczności OT jako dowody, przygotowuje procedurę reagowania na incydenty w OT i porządkuje pakiet gotowości do audytu. Kwestie interpretacji prawnej pozostają po stronie doradców prawnych, z którymi chętnie współpracujemy. Zobacz {a}.", ("gotowość do NIS2 i KSC", U("nis2-ksc-compliance"))),
 ("Czy audyt zakłóci naszą produkcję?", "Nie. W działających sieciach OT obserwujemy, zamiast sondować: podczas pracy procesu nic nie jest skanowane, wstrzykiwane ani zmieniane. Aktywne testy, takie jak testy penetracyjne, prowadzimy wyłącznie na systemach i w oknach czasowych uzgodnionych z zespołem zakładu.", None),
 ("Jak zaczyna się współpraca i jak jest wyceniana?", "Od krótkiej rozmowy: opowiadają nam Państwo, co działa w zakładzie i co budzi obawy, a my uczciwie mówimy, czy jesteśmy właściwym partnerem i jaki pierwszy krok ma sens. Zakres i cena są następnie ustalane z góry, a w przypadku audytów klient otrzymuje uszeregowany według priorytetów raport napisany prostym językiem, z dołączonymi dowodami.", None),
 ("Jak skontaktować się z Liscere?", "Prosimy pisać na {m} lub skorzystać z formularza kontaktowego na {a}.", ("stronie usług", "./uslugi.html#contact")),
]
FAQ2 = [
 ("Czym jest kontekstowa ocena działań sterujących?", "To idea stojąca za frameworkiem rozwijanym przez Liscere: ocenianie działania nie tylko według tego, czy jest dozwolone, ale także według tego, czy pasuje do kontekstu operacyjnego procesu w danej chwili. Działanie może być autoryzowane, zgodne z protokołem i mieścić się w dopuszczalnych zakresach, a mimo to być niewłaściwe dla bieżącej fazy pracy. Framework rozpoznaje tę fazę na podstawie obserwowanego ruchu i ocenia, czy działanie do niej pasuje.", None),
 ("Czy framework jest dostępny jako produkt?", "Jeszcze nie. Framework jest w fazie aktywnego rozwoju i został zweryfikowany w naszym laboratorium. Organizacje, które chcą zobaczyć go we własnej sieci, mogą przeprowadzić pilotaż w ramach usługi {a}.", ("widoczność i monitoring OT", U("ot-visibility-monitoring"))),
 ("Czym framework różni się od systemu wykrywania włamań?", "System wykrywania włamań analizuje ruch; framework analizuje proces. IDS oparty na sygnaturach porównuje pakiety z wzorcami znanych ataków, a IDS oparty na anomaliach wskazuje naruszenia protokołu lub statystyczne odchylenia od wzorca sieci. Oba szukają ruchu nieprawidłowego, nieautoryzowanego lub nietypowego. Framework odtwarza natomiast stan operacyjny zakładu z obserwowanych zmiennych procesowych i ocenia każde działanie względem tego stanu. Zdarzenia, które wskazuje, są poprawnie sformułowane, dozwolone i statystycznie zwyczajne, dlatego czujniki działające na poziomie ruchu nie mają powodu, by je oznaczać.", None),
 ("Czy framework znajduje się na ścieżce sterowania?", "Nie. Jest zewnętrznym obserwatorem. Podłącza się do portu mirror przełącznika, otrzymuje kopię ruchu i niczego nie wstrzykuje; nie może wysłać, zablokować ani zmienić żadnego polecenia, a z założenia i dzięki konfiguracji nie ma drogi, by wysłać ruch do sieci sterowania.", None),
 ("Czy framework zależy od konkretnego producenta lub protokołu?", "Nie. Niezależność od producenta i protokołu jest celem projektowym. Framework ocenia proces, a nie implementację konkretnego producenta, więc nie jest związany z określonym sterownikiem, magistralą polową ani systemem SCADA. Ponieważ obserwuje jedynie kopię ruchu, nic nie jest instalowane na sterownikach, nic nie jest rekonfigurowane i nie powstaje nowa droga do sieci sterowania.", None),
 ("Jak framework jest weryfikowany?", "Na prawdziwym sprzęcie przemysłowym, w realistycznych warunkach i na rosnącej liczbie procesów i protokołów. Weryfikacja odbywa się w naszym laboratorium na sterownikach Siemens S7-1200 i S7-1200 G2 z rzeczywistymi konfiguracjami inżynierskimi, przez Modbus/TCP i OPC UA, a każdy wynik jest powtarzany w wielu wariantach pracy, a nie w jednym przypadku.", None),
 ("Gdzie można przeczytać badania Liscere?", "W {a} (w języku angielskim), gdzie zebrano raporty techniczne Liscere (seria LTR) i opracowania przeglądowe (seria LB). Każdy raport ma własną stronę ze streszczeniem i odnośnikiem do pełnego pliku PDF.", ("sekcji badań", R + "research.html")),
]

def render_faq_item(q, a, link):
    plain = a.replace("{m}", "hello@liscere.com")
    vis = esc(a).replace("{m}", '<a href="mailto:hello@liscere.com">hello@liscere.com</a>')
    if link:
        t, h = link
        hl = ' hreflang="en"' if h.startswith(R) and not h.startswith(R + "pl") else ""
        vis = vis.replace("{a}", f'<a href="{h}"{hl}>{esc(t)}</a>')
        plain = plain.replace("{a}", t)
    return (q, plain), f"""      <div class="faq-item">
        <h3 class="faq-q">{esc(q)}</h3>
        <p class="faq-a">{vis}</p>
      </div>
"""

def faq():
    pairs = []; g1 = ""; g2 = ""
    for q, a, l in FAQ1:
        pr, h = render_faq_item(q, a, l); pairs.append(pr); g1 += "\n" + h
    for q, a, l in FAQ2:
        pr, h = render_faq_item(q, a, l); pairs.append(pr); g2 += "\n" + h
    body = f"""    <article class="aeo-doc">
      <h1 class="doc-title">Najczęściej zadawane pytania</h1>

      <h2 class="faq-group">Współpraca z Liscere</h2>
{g1}
      <h2 class="faq-group">Framework i badania</h2>
{g2}    </article>
"""
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "FAQPage", "@id": SITE + "pl/faq.html", "url": SITE + "pl/faq.html", "inLanguage": "pl-PL",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}]}
    return shell(title="FAQ | Liscere, cyberbezpieczeństwo przemysłowe",
                 desc="Konkretne odpowiedzi o Liscere: usługi bezpieczeństwa OT i automatyki, gotowość do NIS2 i KSC, przebieg współpracy oraz rozwijany framework.",
                 path="pl/faq.html", en_path="faq.html", current="faq",
                 main_class="research-page faq-page", body=body, ld=ld)

if __name__ == "__main__":
    os.makedirs(ROOT + "pl", exist_ok=True)
    for name, fn in [("uslugi.html", uslugi), ("o-nas.html", o_nas), ("faq.html", faq)]:
        open(ROOT + "pl/" + name, "w", encoding="utf-8").write(fn())
    print("ok")
