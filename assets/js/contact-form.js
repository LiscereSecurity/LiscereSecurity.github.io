/* Liscere contact form.
   Works in two modes:
   1. data-endpoint set on the <form>: POSTs the fields there (Formspree,
      Netlify Functions, Cloudflare Pages Functions or any endpoint that
      accepts form-encoded POST and returns JSON).
   2. No data-endpoint: opens the visitor's mail client with the message
      prefilled, addressed to the data-mailto address. Nothing is lost if
      the endpoint is not wired up yet. */
(function () {
  "use strict";

  var forms = document.querySelectorAll("form[data-contact]");
  if (!forms.length) { return; }

  var params = new URLSearchParams(window.location.search);
  var preselect = params.get("service");

  /* Bot checks (with the honeypot below): a real visitor takes more than a few
     seconds and touches the form with a pointer or the keyboard before sending.
     Submissions that fail either check are dropped silently. */
  var MIN_FILL_MS = 3000;
  var openedAt = Date.now();

  Array.prototype.forEach.call(forms, function (form) {
    var status = form.querySelector(".form-status");
    var touched = false;
    ["pointerdown", "keydown", "touchstart"].forEach(function (type) {
      form.addEventListener(type, function () { touched = true; }, { passive: true });
    });
    var select = form.querySelector("select[name=service]");
    if (select && preselect) {
      Array.prototype.forEach.call(select.options, function (opt) {
        if (opt.value === preselect) { opt.selected = true; }
      });
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setStatus("", "");

      if (form.querySelector("input[name=website]").value) { return; } /* honeypot */
      if (!touched || Date.now() - openedAt < MIN_FILL_MS) { return; } /* too fast or no interaction */
      var msg = String(form.querySelector("[name=message]").value || "");
      if ((msg.match(/https?:\/\/|www\./gi) || []).length > 2) { return; } /* link spam */
      if (/<a\s|\[url=/i.test(msg)) { return; } /* markup spam */

      if (!form.checkValidity()) {
        form.reportValidity();
        setStatus("Please complete the required fields.", "err");
        return;
      }

      var data = new FormData(form);
      var endpoint = form.getAttribute("data-endpoint");

      if (endpoint) {
        var btn = form.querySelector("button[type=submit]");
        btn.disabled = true;
        setStatus("Sending…", "");
        fetch(endpoint, {
          method: "POST",
          headers: { "Accept": "application/json" },
          body: data
        }).then(function (res) {
          if (!res.ok) { throw new Error("HTTP " + res.status); }
          form.reset();
          setStatus("Thank you. We will be in touch soon.", "ok");
        }).catch(function () {
          setStatus("Something went wrong. Please email hello@liscere.com directly.", "err");
        }).finally(function () { btn.disabled = false; });
        return;
      }

      var to = form.getAttribute("data-mailto") || "hello@liscere.com";
      var service = data.get("service") || "General enquiry";
      var subject = "[Liscere] " + service + ": " + (data.get("company") || data.get("name"));
      var body = [
        "Name: " + data.get("name"),
        "Company: " + (data.get("company") || ""),
        "Email: " + data.get("email"),
        "Service: " + service
      ].concat(data.get("sector") ? ["Sector: " + data.get("sector")] : []).concat([
        "",
        data.get("message")
      ]).join("\n");
      window.location.href = "mailto:" + to +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);
      setStatus("Your mail client should open with the message prefilled. If it does not, write to " + to + ".", "ok");
    });

    function setStatus(text, cls) {
      if (!status) { return; }
      status.textContent = text;
      status.className = "form-status" + (cls ? " " + cls : "");
    }
  });
}());
