/* Liscere header menu on phones.

   On a narrow screen the five header links no longer fit beside the wordmark, so they
   used to wrap onto a second row and take a band of the screen on every page. Here they
   collapse behind one button on the opposite side of the wordmark, and drop down as a
   panel when it is pressed.

   The button is created here rather than in the markup, so a visitor without JavaScript
   keeps the links visible instead of a button that cannot open. Everything the stylesheet
   changes is gated on <html class="has-nav-toggle">, which is set below. */
(function () {
  "use strict";
  var root = document.documentElement;
  var nav = document.querySelector(".site-nav");
  var chrome = document.querySelector(".site-chrome");
  if (!nav || !chrome || document.querySelector(".nav-toggle")) { return; }

  if (!nav.id) { nav.id = "site-nav"; }
  nav.setAttribute("data-open", "false");

  var label = root.lang && root.lang.slice(0, 2) === "pl" ? "Menu nawigacji" : "Navigation menu";
  var button = document.createElement("button");
  button.className = "nav-toggle";
  button.type = "button";
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-controls", nav.id);
  button.setAttribute("aria-label", label);
  button.innerHTML = "<span></span><span></span><span></span>";
  chrome.appendChild(button);
  root.classList.add("has-nav-toggle");

  function setOpen(open) {
    nav.setAttribute("data-open", open ? "true" : "false");
    button.setAttribute("aria-expanded", open ? "true" : "false");
  }

  button.addEventListener("click", function (e) {
    e.stopPropagation();
    setOpen(nav.getAttribute("data-open") !== "true");
  });

  /* A link closes the panel: most of them navigate away, but the research filters and the
     in-page anchors stay on the page. */
  nav.addEventListener("click", function (e) {
    /* a link, or the dimmed area under the panel, which is drawn as the nav's own ::after */
    if (e.target === nav || e.target.closest("a")) { setOpen(false); }
  });

  document.addEventListener("click", function (e) {
    if (nav.getAttribute("data-open") !== "true") { return; }
    if (!nav.contains(e.target) && !button.contains(e.target)) { setOpen(false); }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.getAttribute("data-open") === "true") {
      setOpen(false);
      button.focus();
    }
  });

  /* Back on a wide screen the links are shown in full again, so the panel state is dropped. */
  var wide = window.matchMedia("(min-width: 721px)");
  var onWide = function (m) { if (m.matches) { setOpen(false); } };
  if (wide.addEventListener) { wide.addEventListener("change", onWide); }
  else if (wide.addListener) { wide.addListener(onWide); }
})();
