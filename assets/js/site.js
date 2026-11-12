/* Liscere shared page behaviour (content pages; the home page has its own script).
   1. The fixed header bar: <html class="past-hero"> while at the very top of the page.
   2. Back links (the "Services" arrow on service pages, the series label on research pages
      and articles, "All research"): when the visitor came from the page the link points to,
      go back in history so the browser restores the exact screen they left; otherwise follow
      the link, which opens the right section or filter.
   3. Research index filter, kept in the URL hash (#fieldnotes, #landscape, #research). */
(function () {
  "use strict";
  var root = document.documentElement;
  function sync() { root.classList.toggle("past-hero", window.scrollY <= 16); }
  sync();
  window.addEventListener("scroll", sync, { passive: true });

  /* Research report pages: on phones the abstract starts expanded (the desktop layout
     carries an interactive PDF preview instead). */
  if (window.matchMedia("(max-width: 900px)").matches) {
    var abstract = document.querySelector(".doc-abstract-toggle");
    if (abstract) { abstract.open = true; }
  }

  /* Research index: filter buttons (All / Research / Landscape / Field Notes). The active
     filter is kept in the URL hash, so a link such as research.html#fieldnotes opens it and
     going back to the index restores it. */
  var buttons = document.querySelectorAll(".research-filter-btn");
  var cards = document.querySelectorAll(".research-cards .paper-card");
  function applyFilter(filter, updateUrl) {
    var found = false;
    Array.prototype.forEach.call(buttons, function (b) {
      var active = b.getAttribute("data-filter") === filter;
      if (active) { found = true; }
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-pressed", active ? "true" : "false");
    });
    if (!found) { return; }
    Array.prototype.forEach.call(cards, function (card) {
      card.hidden = !(filter === "all" || card.getAttribute("data-group") === filter);
    });
    if (updateUrl && history.replaceState) {
      history.replaceState(null, "", filter === "all" ? location.pathname + location.search : "#" + filter);
    }
  }
  Array.prototype.forEach.call(buttons, function (btn) {
    btn.addEventListener("click", function () { applyFilter(btn.getAttribute("data-filter"), true); });
  });
  if (buttons.length && location.hash.length > 1) { applyFilter(location.hash.slice(1), false); }

  var ref;
  try { ref = new URL(document.referrer); } catch (e) { ref = null; }
  Array.prototype.forEach.call(document.querySelectorAll("a.back-fab, a[data-back]"), function (a) {
    a.addEventListener("click", function (ev) {
      if (!ref || ref.origin !== location.origin || history.length < 2) { return; }
      var target = new URL(a.getAttribute("href"), location.href);
      if (ref.pathname === target.pathname) { ev.preventDefault(); history.back(); }
    });
  });
}());
