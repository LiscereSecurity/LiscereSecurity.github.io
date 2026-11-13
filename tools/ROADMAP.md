# Liscere site: ordem de trabalho

Combinada em 12/11/2026. Este arquivo fica em `tools/`, que não é publicado no site.

1. **FN-2026-01 em polonês**
   - Versão em `/pl/badania/fn-2026-01/`, ligada à versão em inglês.
   - Link de volta no nome da série ("Field Notes", "Landscape Briefing", "Technical Report").
   - Publicar e avisar o IndexNow.
2. **Pendências de ontem**
   - ~~Passo 3: página da empresa no LinkedIn~~ feito em 12/11 (EN e PL), primeiro post do FN-2026-01 publicado.
   - ~~Passo 7.4~~ decidido em 12/11: LB-2026-01, LTR-2026-01 e LTR-2026-02 ficam no nome de Bruno Salmazo, publicados pela Liscere sob CC BY 4.0. PDFs v1.1 aplicados no PR "research v1.1"; PRs #1 e #2 ficam obsoletos.
   - ~~Passo 7.5~~ decidido em 12/11: sem LinkedIn pessoal por enquanto; tudo pela página da Liscere.
   - Post do FN-2026-01 em polonês (1 ou 2 dias depois do inglês).
   - Passos 8 a 12: diretórios, associações, DOIs no Zenodo, posts no LinkedIn, prospecção.
   - Diretórios (ordem): ~~Crunchbase~~ (13/11, no sameAs); ~~NCC-PL / ECCC Atlas~~ (pedido enviado 12/11, aguardando); aleo; Google Business Profile e Bing Places; Clutch; Panorama Firm. Wikidata depois do Zenodo. Cada perfil novo entra no `sameAs` (index, about, services, faq) e no `llms.txt`.
   - Bing: resultado do Site Scan.
3. **Organizar a página Research**
   - Converter os relatórios antigos para o formato artigo (texto na página e PDF como link "Baixar PDF").
   - Feito em 12/11: os 10 relatórios convertidos (PR #13), texto idêntico aos PDFs v1.1, gerados por gen_articles.py com dados em tools/data_reports.py.
   - O gerador precisa de um modo "só em inglês": botão PL apontando para `/pl/tylko-po-angielsku.html?from=...` e sem hreflang pl.
3b. **Versões em polonês e revisão final** (12/11)
   - Badania, Prywatność, Dane spółki e Warunki em polonês, ligadas às versões em inglês.
   - `tools/gen_sitemap.py` gera o sitemap a partir das páginas; `tools/audit.py` confere SEO, links, idiomas e dados estruturados (rodar antes de cada PR).
   - Testado em WebKit (Safari) e Chromium, desktop e celular.
   - Cloudflare feito em 12/11: proxy ligado, SSL Full, HSTS 6 meses, cabeçalhos de segurança por Transform Rule (PR #15).
   - Pendente: revisão do texto jurídico em polonês por alguém fluente.
4. **Palavras-chave e novos artigos**
   - Puxar os preços reais no Keyword Planner (Polônia, idioma polonês).
   - Escrever artigos sobre NIS2 e KSC, em polonês e inglês, para indexar o quanto antes.
5. **Tráfego pago** (só depois do item 4)
   - Teste pequeno no Google Ads na Polônia e impulsionamento no LinkedIn.
   - Antes, registrar a origem de cada contato no formulário, sem cookies.
