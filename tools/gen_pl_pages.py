"""Polish Services (pl/uslugi.html), About (pl/o-nas.html), FAQ (pl/faq.html), Research index (pl/badania.html),
company details (pl/dane-spolki.html), privacy notice (pl/prywatnosc.html) and terms of use (pl/warunki.html)."""
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
      <a href="./badania.html"{cur('research')}>Badania</a>
      <a class="lang-switch" href="{en_rel}" hreflang="en" lang="en" aria-label="English">EN</a>
    </nav>
  </header>

  <main id="main-content" class="{main_class}">
{body}
    <p class="research-foot"><a href="./index.html">Start</a> · <a href="./uslugi.html">Usługi</a> · <a href="./o-nas.html">O nas</a> · <a href="./faq.html">FAQ</a> · <a href="./badania.html">Badania</a> · <a href="https://www.linkedin.com/company/liscere" target="_blank" rel="noopener">LinkedIn</a> · <a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> · <a href="./prywatnosc.html">Prywatność</a> · <a href="./dane-spolki.html">Dane spółki</a> · <a href="./warunki.html">Warunki korzystania</a><br />Siedziba w Polsce, działamy w całej Europie i na świecie.<br />© 2026 Liscere sp. z o.o.</p>
  </main>

  <script src="{R}assets/js/site.js?v=4" defer></script>
{scripts}</body>
</html>
"""

ORG = {"@type": "Organization", "@id": SITE + "#org", "name": "Liscere", "url": SITE}

def contact_form(selected=None):
    opts = "\n".join(f'                <option value="{attr(v)}"{" selected" if v == selected else ""}>{esc(PL_NAMES[v])}</option>' for v, _ in SERVICES)
    return f"""        <form class="form-card" data-contact data-endpoint="https://formspree.io/f/xdegodog" data-mailto="hello@liscere.com" novalidate>
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
              <label for="f-consent">Wyrażam zgodę na przetwarzanie przez Liscere sp. z o.o. danych z tego formularza w celu odpowiedzi na moje zapytanie, zgodnie z <a href="./prywatnosc.html">informacją o prywatności</a>.</label>
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
                 scripts=f'  <script src="{R}assets/js/contact-form.js?v=20261111-fs1" defer></script>\n')

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
        <p>Framework jest w fazie aktywnego rozwoju i został zweryfikowany w naszym laboratorium. Wyniki publikujemy w dziale <a href="./badania.html">Badania</a> (raporty w języku angielskim).</p>
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
                 desc="Europejska firma cyberbezpieczeństwa przemysłowego z siedzibą w Polsce, działająca na całym świecie: bezpieczeństwo OT, bezpieczna automatyka, badania.",
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

# ---------------------------------------------------------------- Badania (research index)
# Field Notes have Polish versions; reports are in English (marked "po angielsku").
BADANIA = [
    ("guides", "./badania/gd-2026-03/", "GD-2026-03 · Poradnik · listopad 2026", "IEC 62443 w praktyce",
     "Seria liczy kilkanaście dokumentów, więc pytanie „czy jesteśmy zgodni z 62443” rzadko ma sens. Jak zbudowane są części i którą naprawdę czytać w zakładzie, czym są strefy i kanały, siedem wymagań podstawowych oraz dlaczego SL-T, SL-C i SL-A dzielą deklarację od ustalenia audytu.",
     False, "Czytaj poradnik"),
    ("guides", "./badania/gd-2026-02/", "GD-2026-02 · Poradnik · listopad 2026", "Zgłaszanie incydentu w OT",
     "Terminy zgłoszenia są te same dla biura i dla hali produkcyjnej, ale praca pod nimi wygląda inaczej. Wczesne ostrzeżenie w 24 godziny, zgłoszenie w 72 godziny i sprawozdanie końcowe w miesiąc, wraz z decyzjami, które w OT są najtrudniejsze: izolacja działającego procesu i dowody znikające przy pierwszym restarcie.",
     False, "Czytaj poradnik"),
    ("guides", "./badania/gd-2026-01/", "GD-2026-01 · Poradnik · listopad 2026", "NIS2 i ustawa o KSC",
     "Kogo dotyczą przepisy, co trzeba mieć i do kiedy. Sektory i progi wielkości z dyrektywy, polskie daty, które łatwo pomylić, obowiązki, kary oraz część pomijana w większości projektów zgodności: sterowniki, stacje operatorskie i sieci sterujące procesem fizycznym.",
     False, "Czytaj poradnik"),
    ("fieldnotes", "./badania/fn-2026-01/", "FN-2026-01 · Field Notes · listopad 2026", "Atak na chłodnie supermarketów",
     "W październiku 2026 atakujący dostali się do sterowników chłodniczych około 700 supermarketów we Francji i za pomocą cykli odszraniania oraz nastaw temperatury ogrzali w nocy lodówki i zamrażarki. Nic nie zostało zepsute: każde polecenie było autoryzowane. Co się stało, co zaleca CERT-FR i dlaczego kontekst jest pytaniem, które pozwoliłoby to wychwycić. Z dwuminutowym filmem.",
     False, "Czytaj artykuł"),
    ("landscape", "../research/lb-2026-05/", "LB-2026-05 · Przegląd · lipiec 2026", "Metody pasywne i aktywne w OT",
     "Metody pasywne i aktywne to nie rywale, lecz narzędzia o różnym zasięgu. OT zmienia rachunek: urządzenia są delikatne, nieplanowane przestoje są nie do przyjęcia, a sprzęt pracuje przez dziesięciolecia. Wytyczne czynią monitoring pasywny punktem wyjścia; dojrzałe podejście jest hybrydowe.",
     True, "Czytaj przegląd"),
    ("landscape", "../research/lb-2026-04/", "LB-2026-04 · Przegląd · lipiec 2026", "Luka szyfrowania w sterownikach S7",
     "Komunikacja Siemens S7 jest domyślnie szyfrowana w obecnych sterownikach, a mimo to w zainstalowanej bazie dominują tryby czytelne: jawny S7comm na S7-300 i S7-400 oraz S7CommPlus szyfrowany w warstwie aplikacji. Luka utrzymuje się z powodów ekonomicznych, nie z niewiedzy.",
     True, "Czytaj przegląd"),
    ("research", "../research/ltr-2026-05/", "LTR-2026-05 · Raport techniczny · lipiec 2026", "Tryby bezpieczeństwa OPC UA",
     "OPC UA oferuje trzy tryby bezpieczeństwa komunikatów zamiast wyboru zero-jedynkowego. To tryb, a nie polityka, decyduje o tym, co odczyta pasywny obserwator: None i Sign pozostawiają wymianę w pełni czytelną, SignAndEncrypt tylko kopertę transportową.",
     True, "Czytaj raport"),
    ("landscape", "../research/lb-2026-03/", "LB-2026-03 · Przegląd · lipiec 2026", "Przewodnik po protokołach OT",
     "Przystępna mapa tego, jak komunikują się systemy przemysłowe: warstwy środowiska OT, protokoły dominujące w każdej z nich, główni producenci sterowników oraz relacje między producentami a protokołami.",
     True, "Czytaj przegląd"),
    ("landscape", "../research/lb-2026-02/", "LB-2026-02 · Przegląd · lipiec 2026", "Szyfrowanie protokołów OT",
     "Przegląd szyfrowania w głównych klasach protokołów OT: ustandaryzowane mechanizmy, zmierzony stopień wdrożenia i punkt obserwacji, na jaki pozwala każda klasa. Możliwość szyfrowania i jego faktyczne włączenie trwale się rozmijają.",
     True, "Czytaj przegląd"),
    ("research", "../research/ltr-2026-04/", "LTR-2026-04 · Raport techniczny · lipiec 2026", "Kanały szyfrowane",
     "Charakterystyka szyfrowanego kanału OT, Web API przez TLS 1.3, pod kątem wymagań oceny kontekstowej. Pasywny obserwator nie widzi treści; szyfrowanie zmienia punkt obserwacji, a nie rdzeń oceny.",
     True, "Czytaj raport"),
    ("research", "../research/ltr-2026-03/", "LTR-2026-03 · Raport techniczny · lipiec 2026", "Weryfikacja na sprzęcie",
     "Kontekstowa ocena działań sterujących zweryfikowana na fizycznym sprzęcie w trzech etapach: kontekst z obserwacji, odporne rozpoznawanie fazy procesu i gramatyka operacyjna wyuczona z obserwacji.",
     True, "Czytaj raport"),
    ("research", "../research/ltr-2026-02/", "LTR-2026-02 · Raport techniczny · czerwiec 2026", "Framework",
     "Niezależny od protokołu łańcuch oceny działania przemysłowego w czterech wymiarach: operacja protokołu, artefakt automatyki, kontekst operacyjny i ograniczenie polityki.",
     True, "Czytaj raport"),
    ("research", "../research/ltr-2026-01/", "LTR-2026-01 · Raport techniczny · czerwiec 2026", "Ocena na Modbus/TCP",
     "Para kontrolna Modbus/TCP, w której ten sam wrażliwy zapis daje alert podczas produkcji i zgodę w zadeklarowanym oknie serwisowym.",
     True, "Czytaj raport"),
    ("landscape", "../research/lb-2026-01/", "LB-2026-01 · Przegląd · czerwiec 2026", "Krajobraz zagrożeń OT",
     "Przegląd tego, dlaczego środek ciężkości ataków na OT przesunął się od zdobywania dostępu do wydawania poprawnych poleceń, i jaką lukę zostawia to obrońcom.",
     True, "Czytaj przegląd"),
]


def badania():
    cards = []
    for group, href, eyebrow, title, text, en, cta in BADANIA:
        hl = ' hreflang="en"' if en else ""
        tag = ' <span class="paper-lang">po angielsku</span>' if en else ""
        cards.append(f"""      <a class="paper-card" data-group="{group}" href="{href}"{hl}>
        <p class="paper-eyebrow">{eyebrow}{tag}</p>
        <h2 class="paper-title">{esc(title)}</h2>
        <p class="paper-body">{esc(text)}</p>
        <span class="paper-cta">{cta} <span class="paper-arrow" aria-hidden="true">&#8594;</span></span>
      </a>""")
    body = f"""    <h1 id="research-title">Badania</h1>
    <p class="research-intro">Publikujemy wyniki naszej pracy: raporty techniczne z laboratorium, przeglądy rynku i technologii, poradniki o NIS2 i ustawie o KSC oraz Field Notes o bieżących incydentach. Poradniki i Field Notes są dostępne po polsku; raporty i przeglądy publikujemy po angielsku, z pełnym tekstem na stronie i w PDF, na licencji CC BY 4.0.</p>

    <div class="research-filter" role="group" aria-label="Filtruj publikacje">
      <button type="button" class="research-filter-btn is-active" data-filter="all" aria-pressed="true">Wszystkie</button>
      <button type="button" class="research-filter-btn" data-filter="research" aria-pressed="false">Raporty</button>
      <button type="button" class="research-filter-btn" data-filter="landscape" aria-pressed="false">Przeglądy</button>
      <button type="button" class="research-filter-btn" data-filter="fieldnotes" aria-pressed="false">Field Notes</button>
      <button type="button" class="research-filter-btn" data-filter="guides" aria-pressed="false">Poradniki</button>
    </div>

    <div class="research-cards">
{chr(10).join(cards)}
    </div>
"""
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + ("pl/" + h[2:] if h.startswith("./") else h[3:]), "name": t}
             for i, (_, h, _, t, _, _, _) in enumerate(BADANIA)]
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "CollectionPage", "@id": SITE + "pl/badania.html", "url": SITE + "pl/badania.html", "inLanguage": "pl-PL",
           "name": "Badania Liscere", "about": {"@id": SITE + "#org"}, "mainEntity": {"@type": "ItemList", "itemListElement": items}}]}
    return shell(title="Badania | Raporty i przeglądy bezpieczeństwa OT | Liscere",
                 desc="Raporty techniczne, przeglądy i Field Notes Liscere o cyberbezpieczeństwie przemysłowym: protokoły OT, szyfrowanie, zagrożenia i ocena działań sterujących.",
                 path="pl/badania.html", en_path="research.html", current="research",
                 main_class="research-page", body=body, ld=ld)


# ---------------------------------------------------------------- Dane spółki (legal information)
def dane_spolki():
    body = """    <article class="aeo-doc">
      <h1 class="doc-title">Dane spółki</h1>

      <section class="about-item">
        <h2>Spółka</h2>
        <p>Serwis liscere.com prowadzi <strong>LISCERE SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ</strong> (Liscere sp. z o.o.), polska spółka z ograniczoną odpowiedzialnością.</p>
        <ul>
          <li><strong>Siedziba:</strong> ul. Prezydenta Gabriela Narutowicza 40/1, 90-135 Łódź</li>
          <li><strong>Sąd rejestrowy:</strong> Sąd Rejonowy dla Łodzi-Śródmieścia w Łodzi, XX Wydział Gospodarczy Krajowego Rejestru Sądowego</li>
          <li><strong>KRS:</strong> 0001256054</li>
          <li><strong>NIP:</strong> 7252369168</li>
          <li><strong>REGON:</strong> 545329293</li>
          <li><strong>Kapitał zakładowy:</strong> 5 000,00 zł</li>
          <li><strong>Data rejestracji:</strong> 27 lipca 2026</li>
        </ul>
      </section>

      <section class="about-item">
        <h2>Zarząd</h2>
        <p>Bruno Salmazo, Prezes Zarządu. Zarząd jest jednoosobowy, a prezes reprezentuje spółkę samodzielnie.</p>
      </section>

      <section class="about-item">
        <h2>Kontakt</h2>
        <ul>
          <li><strong>E-mail:</strong> <a href="mailto:hello@liscere.com">hello@liscere.com</a></li>
          <li><strong>Adres do korespondencji:</strong> ul. Prezydenta Gabriela Narutowicza 40/1, 90-135 Łódź</li>
          <li><strong>Adres do e-Doręczeń:</strong> AE:PL-91027-44061-ADVTU-15</li>
        </ul>
      </section>

      <section class="about-item">
        <h2>Sprawdź samodzielnie</h2>
        <p>Wszystkie dane z tej strony można sprawdzić w publicznym Krajowym Rejestrze Sądowym: wyszukaj numer KRS 0001256054 w <a href="https://wyszukiwarka-krs.ms.gov.pl/" target="_blank" rel="noopener">wyszukiwarce KRS Ministerstwa Sprawiedliwości</a>. Zobacz też <a href="./prywatnosc.html">informację o prywatności</a> oraz <a href="./warunki.html">warunki korzystania</a>.</p>
      </section>
    </article>
"""
    ld = {"@context": "https://schema.org", "@graph": [
          {"@type": "Organization", "@id": SITE + "#org", "name": "Liscere",
           "legalName": "LISCERE SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "url": SITE,
           "address": {"@type": "PostalAddress", "streetAddress": "ul. Prezydenta Gabriela Narutowicza 40/1",
                       "postalCode": "90-135", "addressLocality": "Łódź", "addressCountry": "PL"},
           "email": "hello@liscere.com", "taxID": "7252369168", "vatID": "PL7252369168",
           "identifier": [{"@type": "PropertyValue", "propertyID": "KRS", "value": "0001256054"},
                          {"@type": "PropertyValue", "propertyID": "REGON", "value": "545329293"}],
           "foundingDate": "2026-07-27"},
          {"@type": "WebPage", "@id": SITE + "pl/dane-spolki.html", "url": SITE + "pl/dane-spolki.html",
           "inLanguage": "pl-PL", "name": "Dane spółki", "about": {"@id": SITE + "#org"}}]}
    return shell(title="Dane spółki | Liscere sp. z o.o.",
                 desc="Dane Liscere sp. z o.o.: siedziba, sąd rejestrowy, KRS, NIP, REGON, kapitał zakładowy i zarząd.",
                 path="pl/dane-spolki.html", en_path="legal.html", current="legal",
                 main_class="research-page about-main", body=body, ld=ld)


# ---------------------------------------------------------------- Prywatność (privacy notice)
def prywatnosc():
    body = """    <section class="section hero">
      <div class="wrap narrow legal">
        <p class="kicker">Informacje prawne</p>
        <h1>Informacja o prywatności</h1>
        <p class="meta">Wersja 1.5, obowiązuje od 12 listopada 2026</p>
        <p class="lead">Ta informacja wyjaśnia, jakie dane osobowe Liscere sp. z o.o. zbiera, gdy odwiedzasz liscere.com lub do nas piszesz, w jakim celu, jak długo je przechowuje i jakie prawa przysługują Ci na podstawie ogólnego rozporządzenia o ochronie danych (RODO).</p>

        <h2>1. Administrator danych</h2>
        <p>Administratorem Twoich danych osobowych jest <strong>Liscere sp. z o.o.</strong> z siedzibą przy ul. Prezydenta Gabriela Narutowicza 40/1, 90-135 Łódź, wpisana do Krajowego Rejestru Sądowego pod numerem KRS 0001256054, NIP 7252369168, REGON 545329293.</p>
        <p>We wszystkich sprawach dotyczących Twoich danych osobowych napisz na adres <a href="mailto:hello@liscere.com">hello@liscere.com</a> lub na powyższy adres pocztowy. Nie wyznaczyliśmy inspektora ochrony danych, ponieważ przepisy nie wymagają tego od organizacji naszej wielkości i o naszym profilu działalności.</p>

        <h2>2. Jakie dane przetwarzamy i w jakim celu</h2>
        <table>
          <thead>
            <tr><th>Sytuacja</th><th>Dane</th><th>Cel i podstawa prawna</th><th>Okres przechowywania</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>Korzystasz z formularza kontaktowego lub piszesz do nas e-mail</td>
              <td>Imię i nazwisko, firma, służbowy adres e-mail, usługa, której dotyczy zapytanie, treść wiadomości oraz wszystko, co zdecydujesz się dodać</td>
              <td>Odpowiedź na zapytanie i podjęcie działań, o które prosisz przed zawarciem umowy, takich jak rozmowa wstępna lub wycena (art. 6 ust. 1 lit. b RODO). Prowadzenie zapisu korespondencji i w razie potrzeby obrona naszych interesów (prawnie uzasadniony interes, art. 6 ust. 1 lit. f RODO).</td>
              <td>Do czasu załatwienia zapytania, a następnie do 12 miesięcy od ostatniej wymiany wiadomości. Jeśli dojdzie do zawarcia umowy, przez czas jej trwania oraz przez okresy wymagane przepisami o rachunkowości i przedawnieniu roszczeń.</td>
            </tr>
            <tr>
              <td>Odwiedzasz stronę internetową</td>
              <td>Dane techniczne wysyłane przez przeglądarkę przy pobieraniu strony: adres IP, typ przeglądarki, żądana strona, czas żądania</td>
              <td>Bezpieczne udostępnianie strony i utrzymanie jej działania (prawnie uzasadniony interes, art. 6 ust. 1 lit. f RODO). Strona jest hostowana przez GitHub i udostępniana za pośrednictwem Cloudflare, który ją chroni i przyspiesza; obaj dostawcy prowadzą w tym celu standardowe logi żądań.</td>
              <td>Logi żądań są przechowywane przez tych dostawców przez krótki, ograniczony czas ze względów bezpieczeństwa.</td>
            </tr>
            <tr>
              <td>Kontaktujesz się z nami przez LinkedIn lub GitHub</td>
              <td>Twój publiczny profil i treść wiadomości, które nam tam wysyłasz</td>
              <td>Komunikacja z Tobą (prawnie uzasadniony interes, art. 6 ust. 1 lit. f RODO). Te platformy są odrębnymi administratorami i mają własne informacje o prywatności.</td>
              <td>Przez czas trwania kontaktu lub rozmowy.</td>
            </tr>
          </tbody>
        </table>
        <p>Podanie danych jest dobrowolne. Jeśli nie podasz danych oznaczonych w formularzu jako wymagane, nie będziemy mogli Ci odpowiedzieć. Nie podejmujemy na podstawie Twoich danych zautomatyzowanych decyzji i nie stosujemy profilowania.</p>

        <h2>3. Pliki cookie i analityka</h2>
        <p>liscere.com nie zapisuje plików cookie i nie korzysta z technologii śledzących ani reklamowych.</p>
        <p>Aby wiedzieć, jak strona jest używana, korzystamy z Cloudflare Web Analytics, usługi Cloudflare, Inc. Nie używa ona plików cookie ani pamięci lokalnej przeglądarki i nie identyfikuje ani nie śledzi poszczególnych odwiedzających między stronami. Po załadowaniu strony niewielki skrypt Cloudflare przekazuje zbiorcze informacje, takie jak wyświetlona strona, strona odsyłająca, kraj, typ urządzenia i przeglądarki oraz czas ładowania strony. Twój adres IP służy wyłącznie do przekazania tych informacji i nie jest przechowywany przez Cloudflare na potrzeby analityki. Korzystamy z tej usługi na podstawie naszego prawnie uzasadnionego interesu w utrzymaniu użyteczności i sprawnego działania strony (art. 6 ust. 1 lit. f RODO).</p>
        <p>Kroje pisma używane na stronie są udostępniane z naszego serwisu. Poza opisanym wyżej skryptem analitycznym przy wyświetlaniu strony nie są pobierane żadne czcionki, skrypty ani inne zasoby od podmiotów trzecich. Jedyne inne połączenie z podmiotem trzecim następuje przy wysłaniu formularza kontaktowego (zob. punkt 4).</p>

        <h2>4. Odbiorcy danych</h2>
        <p>Nie sprzedajemy ani nie wynajmujemy danych osobowych. Twoje dane mogą być przetwarzane w naszym imieniu przez dostawców usług, którzy na podstawie umowy przetwarzają je wyłącznie zgodnie z naszymi poleceniami: dostawcę poczty elektronicznej i chmury, dostawcę hostingu strony GitHub, Inc. (Stany Zjednoczone), dostawcę usługi formularza kontaktowego Formspree, Inc. (Stany Zjednoczone) oraz Cloudflare, Inc. (Stany Zjednoczone), który udostępnia i chroni stronę oraz dostarcza jej analitykę. Po wysłaniu formularza jego treść trafia do Formspree, który przekazuje ją nam e-mailem i przechowuje kopię na naszym koncie; usuwamy te kopie według tego samego harmonogramu co pocztę. Jeśli dostawca przetwarza dane poza Europejskim Obszarem Gospodarczym, opieramy się na zabezpieczeniach przewidzianych w RODO, takich jak decyzja stwierdzająca odpowiedni stopień ochrony lub standardowe klauzule umowne zatwierdzone przez Komisję Europejską.</p>
        <p>Możemy również udostępnić dane, gdy wymagają tego przepisy, na przykład sądowi lub organowi publicznemu na podstawie zgodnego z prawem żądania.</p>

        <h2>5. Twoje prawa</h2>
        <p>Na podstawie RODO masz prawo do:</p>
        <ul>
          <li>dostępu do swoich danych osobowych, które przechowujemy, i otrzymania ich kopii;</li>
          <li>sprostowania danych nieprawidłowych i uzupełnienia danych niekompletnych;</li>
          <li>usunięcia danych, jeśli nie mamy już podstawy prawnej do ich przechowywania;</li>
          <li>ograniczenia przetwarzania w sytuacjach określonych w art. 18 RODO;</li>
          <li>sprzeciwu wobec przetwarzania opartego na naszym prawnie uzasadnionym interesie, z przyczyn związanych z Twoją szczególną sytuacją;</li>
          <li>otrzymania przekazanych nam przez Ciebie danych w ustrukturyzowanym, powszechnie używanym formacie nadającym się do odczytu maszynowego, jeśli przetwarzanie odbywa się na podstawie umowy i w sposób zautomatyzowany.</li>
        </ul>
        <p>Aby skorzystać z tych praw, napisz na adres <a href="mailto:hello@liscere.com">hello@liscere.com</a>. Odpowiemy w ciągu miesiąca albo poinformujemy, że potrzebujemy więcej czasu, i wyjaśnimy dlaczego.</p>
        <p>Jeśli uważasz, że przetwarzamy Twoje dane niezgodnie z prawem, masz prawo wnieść skargę do organu nadzorczego. W Polsce jest nim Prezes Urzędu Ochrony Danych Osobowych, ul. Stawki 2, 00-193 Warszawa, <a href="https://uodo.gov.pl/" target="_blank" rel="noopener">uodo.gov.pl</a>. Możesz też złożyć skargę do organu w państwie UE, w którym mieszkasz lub pracujesz.</p>

        <h2>6. Bezpieczeństwo</h2>
        <p>Chronimy dane osobowe za pomocą środków technicznych i organizacyjnych odpowiednich do ryzyka, w tym szyfrowanych połączeń ze stroną, dostępu ograniczonego do osób, które go potrzebują, oraz praktyk bezpieczeństwa stosowanych w naszej pracy.</p>

        <h2>7. Zmiany tej informacji</h2>
        <p>Zaktualizujemy tę informację, gdy zmieni się sposób przetwarzania danych, na przykład gdy zaczniemy korzystać z nowego dostawcy usług. Numer wersji i data obowiązywania na górze strony wskazują, która wersja ma zastosowanie. O istotnych zmianach poinformujemy na tej stronie. Wersja angielska tej informacji ma taką samą treść.</p>

        <p class="actions" style="margin-top:2.4rem">
          <a class="btn btn-secondary" href="./uslugi.html#contact">Wróć do formularza kontaktowego</a>
        </p>
      </div>
    </section>
"""
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "WebPage", "@id": SITE + "pl/prywatnosc.html", "url": SITE + "pl/prywatnosc.html",
           "inLanguage": "pl-PL", "name": "Informacja o prywatności", "about": {"@id": SITE + "#org"}}]}
    return shell(title="Informacja o prywatności (RODO) | Liscere",
                 desc="Jak Liscere sp. z o.o. przetwarza dane osobowe w serwisie liscere.com i przez formularz kontaktowy, zgodnie z RODO.",
                 path="pl/prywatnosc.html", en_path="privacy.html", current="privacy",
                 main_class="services-page", body=body, ld=ld)


# ---------------------------------------------------------------- Warunki korzystania (terms of use)
def warunki():
    body = """    <article class="aeo-doc">
      <h1 class="doc-title">Warunki korzystania</h1>
      <p class="meta">Ostatnia aktualizacja: 12 listopada 2026</p>

      <section class="about-item">
        <h2>Kto prowadzi serwis</h2>
        <p>Serwis liscere.com prowadzi Liscere sp. z o.o., ul. Prezydenta Gabriela Narutowicza 40/1, 90-135 Łódź, KRS 0001256054. Pełne dane spółki znajdują się na stronie <a href="./dane-spolki.html">Dane spółki</a>.</p>
      </section>

      <section class="about-item">
        <h2>Wyłącznie informacje, bez gwarancji</h2>
        <p>Wszystkie treści w serwisie, w tym publikacje badawcze, mają charakter informacyjny. Dbamy o ich rzetelność, ale udostępniamy je w obecnej postaci, bez gwarancji, że są kompletne, aktualne lub przydatne do określonego celu. Wyniki badań opisują pracę laboratoryjną w warunkach podanych w każdej publikacji i nie muszą sprawdzać się w innych warunkach.</p>
      </section>

      <section class="about-item">
        <h2>To nie jest gwarancja, certyfikacja ani doradztwo</h2>
        <p>Żadna treść w serwisie nie stanowi gwarancji bezpieczeństwa, certyfikacji produktu lub systemu ani doradztwa zawodowego, inżynierskiego, prawnego czy z zakresu bezpieczeństwa. Nie podejmuj decyzji dotyczących systemu przemysłowego wyłącznie na podstawie tego serwisu. Nasze usługi świadczymy na podstawie odrębnej pisemnej umowy, która ma pierwszeństwo przed treściami w serwisie.</p>
      </section>

      <section class="about-item">
        <h2>Prawa autorskie i licencje</h2>
        <p>Projekt, teksty i grafika serwisu są chronione prawem autorskim. O ile nie wskazano inaczej, nie wolno ich kopiować ani wykorzystywać bez naszej zgody, z wyjątkiem krótkich cytatów z podaniem źródła.</p>
        <p>Publikacje badawcze, czyli raporty, ich ilustracje oraz ich strony w serwisie, są udostępniane na licencji <a href="https://creativecommons.org/licenses/by/4.0/deed.pl" target="_blank" rel="noopener license">Creative Commons Uznanie autorstwa 4.0 Międzynarodowe (CC BY 4.0)</a>. Możesz je rozpowszechniać i adaptować w dowolnym celu, także komercyjnym, pod warunkiem podania autora i Liscere, linku do oryginału oraz informacji o wprowadzonych zmianach.</p>
        <p>Trzy raporty zostały opublikowane przed rejestracją Liscere sp. z o.o.: LB-2026-01, LTR-2026-01 i LTR-2026-02. Prawa autorskie do nich pozostają przy ich autorze, Bruno Salmazo. Liscere publikuje je na tej samej licencji.</p>
        <p>Publiczne repozytoria kodu Liscere w serwisie <a href="https://github.com/LiscereSecurity" target="_blank" rel="noopener">GitHub</a> mają własne pliki licencyjne.</p>
      </section>

      <section class="about-item">
        <h2>Linki do innych stron</h2>
        <p>Linki do innych stron zamieszczamy dla wygody. Nie odpowiadamy za ich treść ani za sposób, w jaki przetwarzają dane osobowe.</p>
      </section>

      <section class="about-item">
        <h2>Prawo właściwe</h2>
        <p>Niniejsze warunki podlegają prawu polskiemu. Jeśli jesteś konsumentem, nie pozbawia Cię to ochrony przysługującej Ci na podstawie bezwzględnie obowiązujących przepisów państwa, w którym mieszkasz.</p>
      </section>

      <section class="about-item">
        <h2>Pytania</h2>
        <p>W sprawie tych warunków napisz na adres <a href="mailto:hello@liscere.com">hello@liscere.com</a>. Sposób przetwarzania danych osobowych opisuje <a href="./prywatnosc.html">informacja o prywatności</a>.</p>
      </section>
    </article>
"""
    ld = {"@context": "https://schema.org", "@graph": [ORG,
          {"@type": "WebPage", "@id": SITE + "pl/warunki.html", "url": SITE + "pl/warunki.html",
           "inLanguage": "pl-PL", "name": "Warunki korzystania", "about": {"@id": SITE + "#org"}}]}
    return shell(title="Warunki korzystania i licencja publikacji | Liscere",
                 desc="Warunki korzystania z liscere.com: charakter informacyjny, brak gwarancji, prawa autorskie, licencja CC BY 4.0 publikacji badawczych i prawo właściwe.",
                 path="pl/warunki.html", en_path="terms.html", current="terms",
                 main_class="research-page about-main", body=body, ld=ld)


if __name__ == "__main__":
    os.makedirs(ROOT + "pl", exist_ok=True)
    for name, fn in [("uslugi.html", uslugi), ("o-nas.html", o_nas), ("faq.html", faq), ("badania.html", badania),
                     ("dane-spolki.html", dane_spolki), ("prywatnosc.html", prywatnosc), ("warunki.html", warunki)]:
        open(ROOT + "pl/" + name, "w", encoding="utf-8").write(fn())
    print("ok")
