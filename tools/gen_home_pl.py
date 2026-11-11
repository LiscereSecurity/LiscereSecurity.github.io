"""Build pl/index.html from index.html: same page and scripts, Polish text, paths for /pl/."""
import re, json, sys
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + "/"
s = open(ROOT + "index.html", encoding="utf-8").read()
NB = " "  # non-breaking space for Polish thousands separators

def rep(en, pl, count=1):
    """Replace en with pl, matching any run of whitespace in en flexibly."""
    global s
    pat = r"\s+".join(re.escape(w) for w in en.split())
    new, n = re.subn(pat, lambda m: pl, s)
    if n == 0:
        sys.exit("NOT FOUND: " + en[:80])
    s = new

# ---------- head
rep('<html lang="en-GB"', '<html lang="pl-PL"')
title = "Liscere: cyberbezpieczeństwo przemysłowe i OT, bezpieczna automatyka"
desc = "Cyberbezpieczeństwo przemysłowe dla procesów, które nie mogą się zatrzymać: audyty bezpieczeństwa OT, gotowość do NIS2 i KSC oraz bezpieczna automatyka PLC i HMI."
s = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", s, count=1)
s = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, s, count=1)
for k in ("og:title", "twitter:title"):
    s = re.sub(r'(<meta (?:property|name)="' + k + r'" content=")[^"]*', lambda m: m.group(1) + title, s)
for k in ("og:description", "twitter:description"):
    s = re.sub(r'(<meta (?:property|name)="' + k + r'" content=")[^"]*', lambda m: m.group(1) + desc, s)
s = s.replace('<meta property="og:url" content="https://liscere.com/" />', '<meta property="og:url" content="https://liscere.com/pl/" />\n  <meta property="og:locale" content="pl_PL" />')
s = s.replace('<meta property="og:image:alt" content="Liscere: OT Cybersecurity" />', '<meta property="og:image:alt" content="Liscere: cyberbezpieczeństwo OT" />')
s = s.replace('<link rel="canonical" href="https://liscere.com/" />',
  '<link rel="canonical" href="https://liscere.com/pl/" />\n'
  '  <link rel="alternate" hreflang="en" href="https://liscere.com/" />\n'
  '  <link rel="alternate" hreflang="pl" href="https://liscere.com/pl/" />\n'
  '  <link rel="alternate" hreflang="x-default" href="https://liscere.com/" />')
# JSON-LD: the Polish home describes itself and points at the one Organization on the English home
blocks = re.findall(r'  <script type="application/ld\+json">.*?</script>\n', s, re.S)
for b in blocks:
    s = s.replace(b, "")
ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": "https://liscere.com/pl/", "url": "https://liscere.com/pl/",
      "name": title, "description": desc, "inLanguage": "pl-PL",
      "about": {"@id": "https://liscere.com/#org"},
      "isPartOf": {"@type": "WebSite", "name": "Liscere", "url": "https://liscere.com/"}}
ldtxt = "  <script type=\"application/ld+json\">\n" + "\n".join("  " + l for l in json.dumps(ld, indent=2, ensure_ascii=False).split("\n")) + "\n  </script>\n"
s = s.replace('  <link rel="stylesheet" href="./assets/css/fonts.css', ldtxt + '  <link rel="stylesheet" href="./assets/css/fonts.css', 1)

# ---------- paths
s = s.replace('"./assets/', '"../assets/').replace("`./assets/", "`../assets/")
s = s.replace('href="./services.html"', 'href="./uslugi.html"')
s = s.replace('href="./about.html"', 'href="./o-nas.html"')
s = s.replace('href="./research.html"', 'href="../research.html" hreflang="en"')
s = s.replace('href="./privacy.html"', 'href="../privacy.html" hreflang="en"')

# ---------- header and navigation
s = s.replace('\n      <a class="lang-switch" href="./pl/index.html" hreflang="pl" lang="pl" aria-label="Polski">PL</a>', '')
rep('>Skip to content<', '>Przejdź do treści<')
rep('aria-label="Site navigation"', 'aria-label="Nawigacja"')
rep('aria-label="Liscere home"', 'aria-label="Liscere, strona główna"')
rep('aria-label="Page navigation"', 'aria-label="Nawigacja po stronie"')
for en, pl in [("Thesis", "Teza"), ("Gap", "Luka"), ("Pressure", "Presja"), ("Decision layer", "Warstwa decyzyjna"), ("How it works", "Jak to działa"), ("Evidence", "Dowody")]:
    rep(f'aria-label="{en}"', f'aria-label="{pl}"')
rep('aria-label="Pages"', 'aria-label="Strony"')
rep('aria-current="page">Home</a>', 'aria-current="page">Start</a>')
rep('<a href="./uslugi.html">Services</a>\n      <a href="./o-nas.html">About</a>\n      <a href="../research.html" hreflang="en">Research</a>',
    '<a href="./uslugi.html">Usługi</a>\n      <a href="./o-nas.html">O nas</a>\n      <a href="../research.html" hreflang="en">Badania</a>\n      <a class="lang-switch" href="../index.html" hreflang="en" lang="en" aria-label="English">EN</a>')
for en, pl in [("01 / Thesis", "01 / Teza"), ("02 / Missing question", "02 / Brakujące pytanie"), ("03 / Why now", "03 / Dlaczego teraz"),
               ("05 / How it works", "05 / Jak to działa"), ("06 / Evidence", "06 / Dowody")]:
    rep(f'data-page="{en}"', f'data-page="{pl}"')

# ---------- 01 hero
rep('Authorised is not always appropriate.</h1>', 'Autoryzowane nie zawsze znaczy właściwe.</h1>')
rep('Bringing to life the next layer of industrial cybersecurity.', 'Tworzymy kolejną warstwę cyberbezpieczeństwa przemysłowego.')
rep('<span class="hero-scrollcue-label">Scroll</span>', '<span class="hero-scrollcue-label">Przewiń</span>')

# ---------- 02 gap
rep('<p class="kicker">The missing question</p>', '<p class="kicker">Brakujące pytanie</p>')
rep('Every check can pass.</h2>', 'Kontrole mogą przejść.</h2>')
rep('<p class="lead">The action can still be wrong.</p>', '<p class="lead">A działanie i tak może być błędne.</p>')
rep('aria-label="Checks passing while context remains unresolved"', 'aria-label="Kontrole przechodzą, a kontekst pozostaje nierozstrzygnięty"')
for en, pl in [("Identity", "Tożsamość"), ("Access", "Dostęp"), ("Protocol", "Protokół"), ("Asset", "Zasób")]:
    rep(f"<span>{en} ✓</span>", f"<span>{pl} ✓</span>")
rep("<strong>Context ?</strong>", "<strong>Kontekst ?</strong>")
rep('aria-label="Real industrial incidents"', 'aria-label="Prawdziwe incydenty przemysłowe"')
rep('aria-label="Previous incident"', 'aria-label="Poprzedni incydent"')
rep('aria-label="Next incident"', 'aria-label="Następny incydent"')
for i in (1, 2, 3):
    rep(f'aria-label="{i} of 3"', f'aria-label="{i} z 3"')
rep("<span>Action</span>", "<span>Działanie</span>")
# Oldsmar
rep("Oldsmar Water Treatment <span>·</span> 2021 <span>·</span> Water", "Stacja uzdatniania wody Oldsmar <span>·</span> 2021 <span>·</span> Woda")
rep("At a water plant, the sodium hydroxide setpoint jumped from 100 ppm to 11,100 ppm, over 100× the normal level. Whether by intruder or by mistake, the change reached the process and nothing questioned the value itself.",
    f"W stacji uzdatniania wody nastawa wodorotlenku sodu skoczyła ze 100 do 11{NB}100 ppm, ponad 100 razy powyżej normy. Intruz czy pomyłka, zmiana dotarła do procesu i nic nie zakwestionowało samej wartości.")
rep("Set chemical dose: 100 ppm → 11,100 ppm", f"Ustaw dawkę chemikaliów: 100 ppm → 11{NB}100 ppm")
rep("The process runs at ~100 ppm. Why suddenly 11,100 ppm?", f"Proces pracuje przy ~100 ppm. Dlaczego nagle 11{NB}100 ppm?")
rep("A valid workstation. A valid user. A valid protocol. Identity, access, and protocol checks can all pass, and none of them asks whether 11,100 ppm makes sense for the physical process. That is the question Liscere is built to ask.",
    f"Prawidłowa stacja, użytkownik i protokół. Kontrole tożsamości, dostępu i protokołu przechodzą, a żadna nie pyta, czy 11{NB}100 ppm ma sens dla procesu. To pytanie zadaje Liscere.")
# Ukraine
rep("Ukraine Power Grid <span>·</span> 2015 <span>·</span> Energy", "Sieć energetyczna Ukrainy <span>·</span> 2015 <span>·</span> Energetyka")
rep("Attackers used hijacked operator workstations to open breakers across 30 substations, cutting power to hundreds of thousands of people. Operators watched their own cursors move and could not stop it.",
    "Napastnicy przez przejęte stacje operatorskie otworzyli wyłączniki w 30 podstacjach, odcinając prąd setkom tysięcy ludzi. Operatorzy widzieli, jak ruszają się ich kursory, i nie mogli tego zatrzymać.")
rep("Open breakers across ~30 substations", "Otwórz wyłączniki w ~30 podstacjach")
rep("Dozens of breakers, all at once, out of nowhere. Does this fit how the grid normally operates?", "Dziesiątki wyłączników naraz, bez powodu. Czy to pasuje do normalnej pracy sieci?")
rep('Liscere aims to learn what "normal" looks like for a process, and judge every action against it.<br />',
    "Liscere chce poznać „normalną” pracę procesu i oceniać względem niej każde działanie.<br />")
rep("An action this far outside the norm is exactly what should be surfaced for review the moment it happens, not after the lights go out.",
    "Tak nietypowe działanie powinno trafić do weryfikacji od razu, a nie po tym, jak zgasną światła.")
# Stuxnet
rep("Stuxnet <span>·</span> 2010 <span>·</span> Nuclear enrichment", "Stuxnet <span>·</span> 2010 <span>·</span> Wzbogacanie uranu")
rep('Malware drove centrifuge rotor speeds far outside their normal operating range, causing gradual physical destruction, while feeding recorded "normal" data back to operator screens.',
    "Złośliwe oprogramowanie wyprowadzało obroty wirówek daleko poza normalny zakres, stopniowo je niszcząc, a operatorom wyświetlało nagrane „normalne” dane.")
rep("Drive rotor RPM from ~63,000 to 84,600", f"Zmień obroty wirnika z ~63{NB}000 na 84{NB}600 obr./min")
rep("A speed the centrifuges had never run before. Why now, and why at all?", "Prędkość, z jaką wirówki nigdy nie pracowały. Dlaczego teraz i dlaczego w ogóle?")
rep('Stuxnet fed operators fake "normal" readings while the centrifuges tore themselves apart.<br />',
    "Stuxnet pokazywał operatorom fałszywe „normalne” odczyty, gdy wirówki same się niszczyły.<br />")
rep("That is where Liscere is going: judging actions against the real process state, not the one on the screen.",
    "Liscere zmierza do oceny działań względem rzeczywistego stanu procesu, a nie tego na ekranie.")

# ---------- 03 pressure
rep('<p class="kicker">Why this is becoming urgent</p>', '<p class="kicker">Dlaczego to staje się pilne</p>')
rep("Permission is becoming a weaker <br />signal of safety.", "Uprawnienie coraz słabiej <br />świadczy o bezpieczeństwie.")
rep("The harder question is no longer who can act, but whether the action fits the moment.", "Trudniejsze pytanie nie brzmi już, kto może działać, ale czy działanie pasuje do chwili.")
rep('aria-label="Previous card"', 'aria-label="Poprzednia karta"')
rep('aria-label="Next card"', 'aria-label="Następna karta"')
rep("The door is already open.", "Drzwi są już otwarte.")
rep("Attackers increasingly arrive through legitimate access: stolen credentials, remote sessions, IT/OT convergence.",
    "Napastnicy coraz częściej wchodzą przez legalny dostęp: skradzione dane logowania, sesje zdalne, konwergencję IT i OT.")
rep("Attackers now act like operators.", "Napastnicy działają dziś jak operatorzy.")
rep("They learn how the process runs and act with intent, so a malicious action looks like a legitimate one.",
    "Uczą się, jak działa proces, i działają celowo, więc złośliwe działanie wygląda jak prawidłowe.")
rep("The check that no longer fires.", "Kontrola, która już nie reaguje.")
rep("When access looks valid, checking who is acting no longer reveals the attack.", "Gdy dostęp wygląda na prawidłowy, sprawdzanie, kto działa, nie ujawnia już ataku.")
rep("As the attacker becomes indistinguishable from the operator, the only defence left is asking whether the action fits the process. <strong>That is the layer Liscere is building.</strong>",
    "Gdy napastnika nie da się odróżnić od operatora, jedyną pozostałą obroną jest pytanie, czy działanie pasuje do procesu. <strong>Tę warstwę buduje Liscere.</strong>")

# ---------- 04 Liscere
rep('<p class="kicker">So, what is Liscere?</p>', '<p class="kicker">Czym więc jest Liscere?</p>')
rep("Liscere is an industrial cybersecurity company building the next layer of OT security.</h2>",
    "Liscere to firma cyberbezpieczeństwa przemysłowego, która buduje kolejną warstwę bezpieczeństwa OT.</h2>")
rep("We protect the systems that run physical processes, on three fronts: security services for industrial and critical infrastructure operators, automation engineering built secure from the start, and research and development of new tools for industrial security.",
    "Chronimy systemy, które prowadzą procesy fizyczne, w trzech obszarach: usługi bezpieczeństwa dla operatorów przemysłowych i infrastruktury krytycznej, inżynieria automatyki bezpieczna od samego początku oraz badania i rozwój nowych narzędzi dla bezpieczeństwa przemysłowego.")
rep("We are also building a framework that reads the network the way it already speaks, protocol by protocol, and turns that traffic into a digital model of the physical process. It learns how the process behaves: its normal values, its timing, the commands that come and go. Every new action is then checked against that model, from where it came to what it asks for, and judged on whether it makes sense for the state of the process at that moment.",
    "Budujemy też framework, który czyta sieć protokół po protokole i zamienia ruch w cyfrowy model procesu fizycznego. Uczy się jego normalnych wartości, rytmu i poleceń. Każde nowe działanie jest porównywane z tym modelem, od źródła po treść polecenia, i oceniane pod kątem tego, czy ma sens dla stanu procesu w danej chwili.")
rep("The name says it. From the Latin licere, to be permitted, Liscere begins there and moves past it, because in a live process, permitted is no longer the same as safe.",
    "Nazwa mówi wszystko. Łacińskie licere znaczy „być dozwolonym”. Liscere zaczyna w tym miejscu i idzie dalej, bo w działającym procesie dozwolone nie znaczy już bezpieczne.")
rep("Security that understands the traffic, not just the credentials.", "Bezpieczeństwo, które rozumie ruch, a nie tylko dane logowania.")

# ---------- 05 how
rep('<p class="kicker">And how does it work?</p>', '<p class="kicker">A jak to działa?</p>')
rep("From traffic to judgement.</h2>", "Od ruchu do oceny.</h2>")
rep("The framework we are building, in four steps, from raw traffic to a verdict an operator can review.",
    "Framework, który budujemy, w czterech krokach: od surowego ruchu do oceny, którą operator może zweryfikować.")
rep('aria-label="Previous step"', 'aria-label="Poprzedni krok"')
rep('aria-label="Next step"', 'aria-label="Następny krok"')
rep('<span class="hard-label">The hard part:</span>', '<span class="hard-label">Trudność:</span>')
rep('<h3 class="how-step-name">Observe</h3>', '<h3 class="how-step-name">Obserwacja</h3>')
rep("Read industrial protocol traffic as it flows, without sitting in the path of the process.", "Odczyt ruchu protokołów przemysłowych na bieżąco, bez wchodzenia na ścieżkę procesu.")
rep("extracting meaning from raw control system communication, across protocols never designed to be read by a third party.",
    "wydobycie znaczenia z surowej komunikacji systemów sterowania, w protokołach, których nigdy nie projektowano z myślą o odczycie przez stronę trzecią.")
rep('<h3 class="how-step-name">Reconstruct</h3>', '<h3 class="how-step-name">Odtworzenie</h3>')
rep("Turn that traffic into a live picture of what the process is doing: its state, its rhythm, its normal.",
    "Zamiana tego ruchu w bieżący obraz tego, co robi proces: jego stanu, rytmu i normy.")
rep("inferring physical process context from the network alone, with no sensors and no changes to the plant.",
    "wnioskowanie o kontekście procesu fizycznego wyłącznie z sieci, bez czujników i bez zmian w zakładzie.")
rep('<h3 class="how-step-name">Evaluate</h3>', '<h3 class="how-step-name">Ocena</h3>')
rep("Weigh each action against that picture. Does this command fit the state the process is in right now?",
    "Porównanie każdego działania z tym obrazem. Czy to polecenie pasuje do stanu, w jakim proces jest teraz?")
rep("judging legitimacy in context, where the same valid action can be right in one moment and harmful in the next.",
    "ocena zasadności w kontekście, gdzie to samo prawidłowe działanie może być właściwe w jednej chwili, a szkodliwe w następnej.")
rep('<h3 class="how-step-name">Decide</h3>', '<h3 class="how-step-name">Decyzja</h3>')
rep("Produce a verdict, and the evidence behind it.", "Wydanie oceny wraz z dowodami.")
rep("a verdict an operator can review, made in time to matter.", "ocena, którą operator może zweryfikować, wydana na czas.")
rep("Together, they form the layer that industrial security is missing.", "Razem tworzą warstwę, której brakuje bezpieczeństwu przemysłowemu.")

# ---------- 06 evidence
rep('<p class="kicker">Built on evidence</p>', '<p class="kicker">Oparte na dowodach</p>')
rep("Built from research.<br />Tested in controlled OT scenarios.", "Zbudowane na badaniach.<br />Sprawdzone w laboratorium OT.")
rep("Liscere originates from doctoral research, turning a rigorous academic question into a practical layer of cybersecurity for industrial systems.",
    "Liscere wywodzi się z badań doktoranckich: rygorystyczne pytanie naukowe zamieniamy w praktyczną warstwę cyberbezpieczeństwa przemysłowego.")
rep("We help operators with OT security services and secure automation engineering, and we welcome research partners and real industrial scenarios to test the framework. Write to hello@liscere.com.",
    "Wspieramy operatorów usługami bezpieczeństwa OT i bezpieczną automatyką oraz zapraszamy partnerów badawczych do testowania frameworku. Napisz na hello@liscere.com.")
rep('>Our services</a>', '>Nasze usługi</a>')
rep('subject=Collaboration%20with%20Liscere">Collaborate</a>', 'subject=Wsp%C3%B3%C5%82praca%20z%20Liscere">Współpraca</a>')
rep('hreflang="en">Read the research</a>', 'hreflang="en">Badania</a>')
rep('>See it working</button>', '>Zobacz w działaniu</button>')
rep('<p class="evidence-foot"><a href="./uslugi.html">Services</a> · <a href="./o-nas.html">About</a> · <a href="./faq.html">FAQ</a> · <a href="../research.html" hreflang="en">Research</a>',
    '<p class="evidence-foot"><a href="./uslugi.html">Usługi</a> · <a href="./o-nas.html">O nas</a> · <a href="./faq.html">FAQ</a> · <a href="../research.html" hreflang="en">Badania</a>')
rep('hreflang="en">Privacy</a>', 'hreflang="en">Prywatność</a>')
rep('aria-label="Liscere demo video"', 'aria-label="Wideo demonstracyjne Liscere"')
rep('aria-label="Close video"', 'aria-label="Zamknij wideo"')
rep("Your browser does not support the video tag.", "Twoja przeglądarka nie obsługuje odtwarzania wideo.")

open(ROOT + "pl/index.html", "w", encoding="utf-8").write(s)
print("ok")
