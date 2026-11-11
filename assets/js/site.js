/* Liscere shared page behaviour (content pages; the home page has its own script).
   1. The fixed header bar: <html class="past-hero"> while at the very top of the page.
   2. "Back to services" links: when the visitor came from the Services page, go back in
      history so the browser restores the exact screen they left; otherwise follow the link,
      which opens the right section. */
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

  /* Research index: filter buttons (All / Reports / Briefings). */
  var buttons = document.querySelectorAll(".research-filter-btn");
  var cards = document.querySelectorAll(".research-cards .paper-card");
  Array.prototype.forEach.call(buttons, function (btn) {
    btn.addEventListener("click", function () {
      var filter = btn.getAttribute("data-filter");
      Array.prototype.forEach.call(buttons, function (b) {
        var active = b === btn;
        b.classList.toggle("is-active", active);
        b.setAttribute("aria-pressed", active ? "true" : "false");
      });
      Array.prototype.forEach.call(cards, function (card) {
        card.hidden = !(filter === "all" || card.getAttribute("data-group") === filter);
      });
    });
  });

  var ref;
  try { ref = new URL(document.referrer); } catch (e) { ref = null; }
  Array.prototype.forEach.call(document.querySelectorAll('a[href*="services.html#"], a[href*="uslugi.html#"]'), function (a) {
    a.addEventListener("click", function (ev) {
      if (!ref || ref.origin !== location.origin || history.length < 2) { return; }
      var target = new URL(a.getAttribute("href"), location.href);
      if (ref.pathname === target.pathname) { ev.preventDefault(); history.back(); }
    });
  });
}());
