/* Liscere home page (English and Polish): one screen per section, the hero animation,
   the card rails and the demo video modal. Moved out of index.html so the site can run
   a strict Content Security Policy with no inline scripts. */
const PL = /^pl/i.test(document.documentElement.lang || "");
const ICONS = new URL("../icons/", document.currentScript.src).href;
{
    const pages = [...document.querySelectorAll(".page")];
    const dots = [...document.querySelectorAll(".section-dots a")];
    const root = document.documentElement;
    let activeIndex = 0;

    const setActivePage = (index) => {
      activeIndex = Math.max(0, Math.min(index, pages.length - 1));
      pages.forEach((page, pageIndex) => page.classList.toggle("active", pageIndex === activeIndex));
      dots.forEach((dot, dotIndex) => dot.classList.toggle("active", dotIndex === activeIndex));
      root.classList.toggle("past-hero", activeIndex > 0);
      history.replaceState(null, "", `#${pages[activeIndex].id}`);
    };

    const goToPage = (targetIndex) => {
      if (targetIndex < 0 || targetIndex >= pages.length) return;
      pages[targetIndex].scrollIntoView({ behavior: "smooth", block: "start" });
    };

    // on phones, content pages can be taller than the screen, so they never reach 0.68
    // visibility - use a lower threshold there so each page still activates (and its
    // entrance animations run). Desktop keeps the original 0.68.
    const pageTh = window.matchMedia("(max-width: 720px)").matches ? 0.3 : 0.68;
    const pageObserver = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;
      const index = pages.indexOf(visible.target);
      if (index >= 0 && index !== activeIndex) {
        setActivePage(index);
      }
    }, { threshold: [pageTh] });

    // Section reveal: a single clean opacity fade (see .js .page.revealed in CSS),
    // fired once when a section first enters the viewport and never reverted, so
    // sections do not re-animate when revisited.
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });

    window.addEventListener("keydown", (event) => {
      if (["ArrowDown", "PageDown", " "].includes(event.key)) {
        event.preventDefault();
        goToPage(activeIndex + 1);
      }

      if (["ArrowUp", "PageUp"].includes(event.key)) {
        event.preventDefault();
        goToPage(activeIndex - 1);
      }
    });

    dots.forEach((dot, index) => {
      dot.addEventListener("click", (event) => {
        event.preventDefault();
        goToPage(index);
      });
    });

    const carousel = document.querySelector(".incident-carousel");
    if (carousel) {
      const track = carousel.querySelector(".incident-track");
      const realSlides = [...carousel.querySelectorAll(".incident-slide")];
      const prevBtn = carousel.querySelector(".carousel-arrow.prev");
      const nextBtn = carousel.querySelector(".carousel-arrow.next");
      const count = realSlides.length;

      // clone slide 1 at the end so advancing past the last wraps to the first
      // seamlessly, moving rightward every time (no leftward rewind).
      const clone = realSlides[0].cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      track.appendChild(clone);

      let pos = 0; // 0..count ; position `count` is the clone (looks like slide 1)
      let animating = false;

      const render = (withTransition) => {
        track.style.transition = withTransition ? "" : "none";
        track.style.transform = `translateX(-${pos * 100}%)`;
        realSlides.forEach((s, i) => s.setAttribute("aria-hidden", i !== (pos % count) ? "true" : "false"));
      };

      // settle after the slide animation via a timer (robust even if a
      // transitionend never fires, which would otherwise lock the carousel)
      const SETTLE = 580;
      const settle = () => {
        animating = false;
        if (pos === count) { // landed on the clone -> snap back to the real first
          pos = 0;
          render(false);
        }
      };
      const next = () => {
        if (animating) return;
        animating = true;
        pos += 1;
        render(true);
        window.setTimeout(settle, SETTLE);
      };

      const prev = () => {
        if (animating) return;
        animating = true;
        if (pos === 0) {
          pos = count; // jump to the clone (visually slide 1) with no transition...
          render(false);
          void track.offsetWidth; // ...force reflow, then animate left to the last
        }
        pos -= 1;
        render(true);
        window.setTimeout(settle, SETTLE);
      };

      // auto-advance (always rightward, seamless loop); pause on hover / off-screen
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      let autoTimer = null;
      const startAuto = () => { if (reduceMotion || autoTimer) return; autoTimer = window.setInterval(next, 5000); };
      const pauseAuto = () => { window.clearInterval(autoTimer); autoTimer = null; };
      const bump = () => { pauseAuto(); startAuto(); }; // restart timer after manual input

      if (prevBtn) prevBtn.addEventListener("click", () => { prev(); bump(); });
      if (nextBtn) nextBtn.addEventListener("click", () => { next(); bump(); });
      carousel.addEventListener("pointerenter", pauseAuto);
      carousel.addEventListener("pointerleave", startAuto);

      const autoVisObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => (entry.isIntersecting ? startAuto() : pauseAuto()));
      }, { threshold: 0.5 });
      autoVisObserver.observe(carousel);

      // touch swipe (mobile has no arrows): horizontal drag changes slide, keeps looping
      const viewport = carousel.querySelector(".incident-viewport");
      let touchStartX = null;
      viewport.addEventListener("touchstart", (e) => { touchStartX = e.touches[0].clientX; }, { passive: true });
      viewport.addEventListener("touchend", (e) => {
        if (touchStartX === null) return;
        const dx = e.changedTouches[0].clientX - touchStartX;
        touchStartX = null;
        if (Math.abs(dx) < 40) return;
        (dx < 0 ? next : prev)();
        bump();
      }, { passive: true });

      render(false);
      startAuto();
    }

    // pg.03 / pg.05 cards = native horizontal scroll-snap carousel (CSS). Add
    // position dots that follow the scroll and jump between cards. Dots are hidden
    // on desktop via CSS (.card-dots { display: none }).
    document.querySelectorAll(".card-rail").forEach((rail) => {
      const track = rail.querySelector(".shift-track, .how-steps");
      if (!track) return;
      const cards = [...track.children];
      if (cards.length < 2) return;
      const dots = document.createElement("div");
      dots.className = "card-dots";
      cards.forEach((card, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.setAttribute("aria-label", (PL ? `Przejdź do karty ${i + 1}` : `Go to card ${i + 1}`));
        b.addEventListener("click", () => {
          track.scrollTo({ left: card.offsetLeft - track.offsetLeft, behavior: "smooth" });
        });
        dots.appendChild(b);
      });
      rail.appendChild(dots);
      const sync = () => {
        const base = track.scrollLeft;
        let best = 0, bestDist = Infinity;
        cards.forEach((card, i) => {
          const dist = Math.abs((card.offsetLeft - track.offsetLeft) - base);
          if (dist < bestDist) { bestDist = dist; best = i; }
        });
        [...dots.children].forEach((d, i) => d.classList.toggle("active", i === best));
      };
      track.addEventListener("scroll", () => requestAnimationFrame(sync), { passive: true });
      sync();
    });

    const initialIndex = Math.max(0, pages.findIndex((page) => `#${page.id}` === window.location.hash));
    setActivePage(initialIndex);
    root.style.scrollBehavior = "auto";
    pages[initialIndex].scrollIntoView({ block: "start" });
    root.style.scrollBehavior = "";
    pages.forEach((page) => pageObserver.observe(page));
    pages.forEach((page) => revealObserver.observe(page));

    /* Hero (conceptual, illustrative): inputs converge into "Liscere", outputs leave as
       evaluated actions tracing industrial-equipment icons. Not real telemetry. */
    (function initHero() {
      const svg = document.querySelector(".hero-field-svg");
      if (!svg) return;
      const inG = svg.querySelector(".hero-inputs");
      const outG = svg.querySelector(".hero-outputs");
      const nameEl = document.querySelector(".hero-name");
      const SVGNS = "http://www.w3.org/2000/svg";
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const rnd = (a, b) => a + Math.random() * (b - a);
      const NS = (t) => document.createElementNS(SVGNS, t);

      // The SVG field is driven in REAL pixel coordinates so it stays aligned with the
      // HTML title on any screen size: the viewBox tracks the element's pixel size, and
      // every anchor (where inputs converge, where outputs emerge, the input/output
      // barrier) is measured from the live DOM rather than hard-coded.
      let W = 1440, H = 900;            // field size in px
      let NL = 90, NR = 600, NT = 90, NB = 300; // "Liscere" wordmark bounds within the field
      let TOPLIM = 110;                 // ceiling = top of the "scere" x-height (nothing above this)
      let BAR_TX = 590, BAR_TY = 100;   // barrier top = right edge of the wordmark
      // invisible diagonal barrier: inputs to its LEFT, outputs only to its RIGHT
      const barrierX = (y) => BAR_TX + ((y - BAR_TY) * (W - BAR_TX)) / (H - BAR_TY);
      const isMobile = () => W <= 720;
      const measure = () => {
        const hr = svg.getBoundingClientRect();
        W = Math.max(1, Math.round(hr.width));
        H = Math.max(1, Math.round(hr.height));
        svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
        if (nameEl) {
          // measure the GLYPHS (a <p> block is full-column-wide; a Range hugs the text)
          let nr;
          try { const rg = document.createRange(); rg.selectNodeContents(nameEl); nr = rg.getBoundingClientRect(); }
          catch (e) { nr = nameEl.getBoundingClientRect(); }
          if (!nr || !nr.width) nr = nameEl.getBoundingClientRect();
          NL = nr.left - hr.left; NR = nr.right - hr.left;
          NT = nr.top - hr.top;   NB = nr.bottom - hr.top;
          // ceiling = top of the lowercase "scere" (x-height), not the cap top of the "L".
          // a Range rect only gives the line box, so derive the x-height from font metrics:
          // baseline = lineTop + fontAscent; xHeightTop = baseline - lowercaseAscent.
          TOPLIM = NT + (NB - NT) * 0.34; // sensible fallback (~x-height for this display font)
          try {
            const cs = window.getComputedStyle(nameEl);
            const ctx = (measure._ctx || (measure._ctx = document.createElement("canvas").getContext("2d")));
            ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
            ctx.textBaseline = "alphabetic";
            const fm = ctx.measureText("Liscere");
            const xm = ctx.measureText("e");
            if (fm.fontBoundingBoxAscent && xm.actualBoundingBoxAscent) {
              TOPLIM = NT + fm.fontBoundingBoxAscent - xm.actualBoundingBoxAscent;
            }
          } catch (e) {}
        }
        // barrier anchored at the wordmark's bottom-right corner, sloping to the field's
        // bottom-right; this keeps the whole right edge of the text inside the output side
        BAR_TX = NR - 8; BAR_TY = NB;
      };
      measure();
      // on a real resize (not the mobile address bar showing/hiding), redraw the field
      // at the new size; the inputs and outputs were placed in the old coordinates
      let lastW = 0, lastH = 0, resizeTimer = 0;
      const rebuild = () => {
        measure();
        if (!started) return;
        if (Math.abs(W - lastW) < 40 && Math.abs(H - lastH) < 160) return;
        lastW = W; lastH = H;
        inG.replaceChildren();
        outG.replaceChildren();
        active.length = 0;
        buildInputs();
      };
      window.addEventListener("resize", () => {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(rebuild, 250);
      });

      // an industrial command flowing in toward the title (top-left). Sources: the bottom
      // (full width) or the left edge. Lines that start on the right curve left immediately
      // and stay low, so the upper-right and centre stay clear for the outputs.
      const makeInput = () => {
        let sx, sy;
        const r = Math.random();
        if (r < 0.45) { sx = rnd(-80, W * 0.85); sy = rnd(H + 40, H + 200); }       // bottom, full width
        else if (r < 0.82) { sx = rnd(W * 0.46, W + 120); sy = rnd(H, H + 200); }   // bottom-right (emphasis)
        else { sx = rnd(-W * 0.12, -20); sy = rnd(H * 0.06, H); }                   // left edge
        // end INSIDE the wordmark, never above the "scere" x-height ceiling, so the line
        // vanishes within the letters instead of poking out over the title
        const ex = rnd(NL + 20, NR - 20);
        const ey = rnd(TOPLIM + 4, NB - 6);
        // pull the first control point toward the text (left) early and keep it low, so
        // right-side starts bend left at once instead of crossing the open output area
        const c1x = sx + (ex - sx) * 0.55 + rnd(-70, 50);
        const c1y = sy + (ey - sy) * 0.12 + rnd(-40, 60);
        const c2x = ex + rnd(-70, 130);
        const c2y = sy + (ey - sy) * 0.72 + rnd(-60, 60);
        const p = NS("path");
        p.setAttribute("class", "hero-in");
        p.setAttribute("d", `M ${sx.toFixed(0)} ${sy.toFixed(0)} C ${c1x.toFixed(0)} ${c1y.toFixed(0)}, ${c2x.toFixed(0)} ${c2y.toFixed(0)}, ${ex.toFixed(0)} ${ey.toFixed(0)}`);
        p.setAttribute("stroke-width", rnd(0.5, 1.3).toFixed(2));
        return p;
      };

      // OUTPUTS: a random icon (from the library) drawn each cycle, in a random colour
      // (mostly green = coherent, some amber = attention). It appears at a random spot in
      // the free upper / central-right area, reached by a randomly-shaped connector that
      // emerges from BEHIND the title (the text stays in the foreground). The trail
      // accumulates (stroke-dashoffset -> 0, dash = full length so the drawn part stays
      // lit) until the icon is complete, holds, vanishes, pauses, then a new random icon.
      const ICON_FILES = [
        "gear.svg", "valve.svg", "motor.svg", "display.svg", "compressor.svg", "valve2.svg",
        "pool.svg", "robot.svg", "signal.svg", "light.svg", "power.svg", "power2.svg",
        "heater.svg", "geyser.svg", "fan.svg", "parking.svg", "fan2.svg", "windmil.svg",
      ];
      const SPEED = 520; // screen px / s while drawing (faster, agile)

      const loadIcon = async (file) => {
        const res = await fetch(`${ICONS}${file}`);
        const txt = await res.text();
        const doc = new DOMParser().parseFromString(txt, "image/svg+xml");
        const vb = (doc.querySelector("svg").getAttribute("viewBox") || "0 0 100 100").split(/[\s,]+/).map(Number);
        const d = [...doc.querySelectorAll("path")].map((p) => p.getAttribute("d")).join(" ");
        return { w: vb[2], h: vb[3], d };
      };

      // a single-subpath connector of a random shape (straight / quadratic / cubic).
      // takes numbers; formats every coordinate so the arithmetic stays numeric.
      const connectorD = (ox, oy, ax, ay) => {
        const n = (v) => v.toFixed(0);
        const kind = Math.floor(rnd(0, 3));
        if (kind === 0) return `M ${n(ox)} ${n(oy)} L ${n(ax)} ${n(ay)}`;
        if (kind === 1) {
          const cx = ox + (ax - ox) * rnd(0.35, 0.7) + rnd(-60, 60);
          const cy = oy + (ay - oy) * rnd(0.35, 0.7) + rnd(-70, 70);
          return `M ${n(ox)} ${n(oy)} Q ${n(cx)} ${n(cy)} ${n(ax)} ${n(ay)}`;
        }
        const c1x = ox + (ax - ox) * 0.35 + rnd(-60, 60);
        const c1y = oy + (ay - oy) * 0.35 + rnd(-70, 70);
        const c2x = ox + (ax - ox) * 0.7 + rnd(-60, 60);
        const c2y = oy + (ay - oy) * 0.7 + rnd(-70, 70);
        return `M ${n(ox)} ${n(oy)} C ${n(c1x)} ${n(c1y)}, ${n(c2x)} ${n(c2y)}, ${n(ax)} ${n(ay)}`;
      };

      const drawPath = (el, dur, delay) => {
        const L = el.getTotalLength();
        el.style.strokeDasharray = `${L.toFixed(2)} ${L.toFixed(2)}`;
        el.style.setProperty("--len", L.toFixed(2));
        el.style.strokeDashoffset = L.toFixed(2);
        el.style.animation = `heroSnakeGrow ${dur.toFixed(2)}s linear ${delay.toFixed(2)}s forwards`;
      };

      // --- geometry helpers: no output may overlap or cross another that is on screen ---
      const boxOverlap = (a, b, pad) =>
        a.x - pad < b.x + b.w && a.x + a.w + pad > b.x && a.y - pad < b.y + b.h && a.y + a.h + pad > b.y;
      const ptInBox = (x, y, b, pad) =>
        x >= b.x - pad && x <= b.x + b.w + pad && y >= b.y - pad && y <= b.y + b.h + pad;
      const segCross = (a, b, c, d) => {
        const ccw = (p, q, r) => (r[1] - p[1]) * (q[0] - p[0]) > (q[1] - p[1]) * (r[0] - p[0]);
        return ccw(a, c, d) !== ccw(b, c, d) && ccw(a, b, c) !== ccw(a, b, d);
      };
      const samplePts = (el, n) => {
        const L = el.getTotalLength(), out = [];
        for (let i = 0; i <= n; i++) { const p = el.getPointAtLength((L * i) / n); out.push([p.x, p.y]); }
        return out;
      };

      const active = []; // { box, pts } of the outputs currently on screen
      let gradId = 0;

      // build one output (connector + icon) in a spot that doesn't overlap/cross anything
      // already on screen. returns { ok:false } when no free placement was found this turn.
      const buildOutput = (icon, staticMode) => {
        const PAD_BOX = 26, PAD_LINE = 16, SKIP = 4; // skip the shared (behind-title) origin cluster
        let place = null;
        const tries = staticMode ? 1 : 30;
        for (let t = 0; t < tries; t++) {
          const mob = isMobile();
          const sc = (mob ? rnd(80, 118) : rnd(95, 138)) / Math.max(icon.w, icon.h);
          const iw = icon.w * sc, ih = icon.h * sc;
          let iconX, iconY, ox, oy, ax, ay;
          if (mob) {
            // narrow screens: outputs play in the open vertical space BELOW the wordmark
            const yhi = Math.max(NB + 70, H * 0.84 - ih);
            iconY = rnd(NB + 56, yhi);
            iconX = rnd(W * 0.05, Math.max(W * 0.05, W - iw - W * 0.05));
            ox = rnd(NL + (NR - NL) * 0.45, NR);            // emerge from the wordmark
            oy = NB - rnd(0, 8);                            // just under the baseline
            ax = iconX + iw / 2; ay = iconY;                // connector meets the icon's top
          } else {
            iconY = rnd(TOPLIM + 4, H * 0.52);              // never above the "scere" ceiling
            // the icon sits right of the barrier AND clearly clear of the wordmark
            const lo = Math.max(barrierX(iconY + ih) + 16, NR + 110), hi = W - 60 - iw;
            if (lo >= hi) continue;
            iconX = rnd(lo, hi);
            oy = rnd(TOPLIM + 4, NB - 2);                   // emerge at/below the "scere" ceiling
            ox = NR + rnd(-4, 14);                          // ...right at the text's right edge
            ax = iconX; ay = iconY + ih / 2;
          }
          const box = { x: iconX, y: iconY, w: iw, h: ih };
          const d = connectorD(ox, oy, ax, ay);
          const probe = NS("path"); probe.setAttribute("d", d); outG.appendChild(probe);
          const pts = samplePts(probe, 18); probe.remove();
          if (staticMode) { place = { sc, iconX, iconY, ox, oy, ax, ay, box, d, pts }; break; }
          // desktop keeps the diagonal barrier + x-height ceiling; mobile only avoids overlaps
          let bad = mob ? false : pts.some(([x, y]) => x < barrierX(y) - 10 || y < TOPLIM - 4);
          if (!bad) bad = active.some((o) => boxOverlap(box, o.box, PAD_BOX));
          if (!bad) bad = pts.slice(SKIP).some(([x, y]) => active.some((o) => ptInBox(x, y, o.box, PAD_LINE)));
          if (!bad) bad = active.some((o) => o.pts.slice(SKIP).some(([x, y]) => ptInBox(x, y, box, PAD_LINE)));
          if (!bad) {
            outer:
            for (const o of active)
              for (let i = SKIP; i < pts.length - 1; i++)
                for (let j = SKIP; j < o.pts.length - 1; j++)
                  if (segCross(pts[i], pts[i + 1], o.pts[j], o.pts[j + 1])) { bad = true; break outer; }
          }
          if (!bad) { place = { sc, iconX, iconY, ox, oy, ax, ay, box, d, pts }; break; }
        }
        if (!place) return { ok: false };

        const { sc, iconX, iconY, ox, oy, ax, ay, box, d, pts } = place;
        const amber = Math.random() < 0.3;
        const colorClass = amber ? "hero-snake--amber" : "hero-snake--green";
        const colorHex = amber ? "#ffc35c" : "#66f4a4";

        const g = NS("g");
        g.setAttribute("class", "hero-out-group");
        outG.appendChild(g);

        // connector stroke = gradient that fades in from faint (near the text) to full (at the icon)
        const gid = `og${gradId++}`;
        const grad = NS("linearGradient");
        grad.setAttribute("id", gid);
        grad.setAttribute("gradientUnits", "userSpaceOnUse");
        grad.setAttribute("x1", ox.toFixed(0)); grad.setAttribute("y1", oy.toFixed(0));
        grad.setAttribute("x2", ax.toFixed(0)); grad.setAttribute("y2", ay.toFixed(0));
        // super faint along almost the whole connector; full colour is reserved for the icon
        [["0", "0"], ["0.7", "0.015"], ["0.9", "0.08"], ["1", "0.38"]].forEach(([off, op]) => {
          const s = NS("stop");
          s.setAttribute("offset", off);
          s.setAttribute("stop-color", colorHex);
          s.setAttribute("stop-opacity", op);
          grad.appendChild(s);
        });
        g.appendChild(grad);

        const conn = NS("path");
        conn.setAttribute("class", "hero-snake " + colorClass);
        conn.setAttribute("d", d);
        conn.setAttribute("stroke", `url(#${gid})`); // gradient overrides the class colour
        conn.setAttribute("stroke-width", "1.1");
        g.appendChild(conn);

        const ig = NS("g");
        ig.setAttribute("transform", `translate(${iconX.toFixed(1)} ${iconY.toFixed(1)}) scale(${sc.toFixed(4)})`);
        // glow = a wider, translucent copy under the outline (much cheaper than a CSS
        // drop-shadow filter, which Chrome recomputes on every animation frame)
        const glow = NS("path");
        glow.setAttribute("class", "hero-snake hero-snake-glow " + colorClass);
        glow.setAttribute("d", icon.d);
        glow.setAttribute("stroke-width", (5 / sc).toFixed(3));
        ig.appendChild(glow);
        const ip = NS("path");
        ip.setAttribute("class", "hero-snake " + colorClass);
        ip.setAttribute("d", icon.d);
        ip.setAttribute("stroke-width", (1.1 / sc).toFixed(3)); // thin outline (~1.1px on screen)
        ig.appendChild(ip);
        g.appendChild(ig);

        if (staticMode) { g.style.opacity = "0.85"; return { ok: true, total: 0 }; }

        const entry = { box, pts };
        active.push(entry);

        const connDur = Math.min(Math.max(conn.getTotalLength() / SPEED, 0.5), 1.1);
        const iconDur = rnd(2.1, 3.1);
        drawPath(conn, connDur, 0);     // connector draws first
        drawPath(glow, iconDur, connDur); // then the icon accumulates (glow in step)
        drawPath(ip, iconDur, connDur);
        const total = connDur + iconDur;
        const HOLD = 0.55, FADE = 0.5;
        window.setTimeout(() => { g.style.opacity = "0"; }, (total + HOLD) * 1000);
        window.setTimeout(() => {
          g.remove();
          const i = active.indexOf(entry);
          if (i >= 0) active.splice(i, 1);
        }, (total + HOLD + FADE) * 1000);
        return { ok: true, total };
      };

      // build the cyan input lines (deferred until the layout is correctly measured)
      // INPUT LINES are drawn on a <canvas> under the SVG, not as animated SVG paths:
      // Chrome repainted 64 simultaneously animating SVG strokes in pieces on 120Hz
      // screens, so lines flickered. The canvas is redrawn in full every frame with
      // the same geometry, timing and opacity curve as the old CSS keyframes.
      const cv = document.createElement("canvas");
      cv.className = "hero-field-canvas";
      cv.setAttribute("aria-hidden", "true");
      svg.parentNode.insertBefore(cv, svg);
      const ctx2d = cv.getContext("2d");
      let lines = [], dpr = 1, elapsed = 0, lastTs = null, raf = 0;

      const sizeCanvas = () => {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        cv.width = Math.round(W * dpr);
        cv.height = Math.round(H * dpr);
      };

      // same curve as the former @keyframes heroDraw: the line grows over 0-80% of the
      // cycle; it fades in over 0-14%, holds, and fades out over 91-100%
      const drawLines = () => {
        ctx2d.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx2d.clearRect(0, 0, W, H);
        ctx2d.strokeStyle = "#4de6ff";
        ctx2d.lineCap = "round";
        const t = elapsed / 1000;
        for (const l of lines) {
          let offset = 0, alpha = l.op;
          if (!reduce) {
            const tt = t - l.delay;
            if (tt < 0) continue;
            const ph = (tt % l.dur) / l.dur;
            offset = ph < 0.8 ? l.len * (1 - ph / 0.8) : 0;
            alpha = ph < 0.14 ? l.op * (ph / 0.14) : ph < 0.91 ? l.op : l.op * (1 - (ph - 0.91) / 0.09);
          }
          if (alpha <= 0.002) continue;
          ctx2d.globalAlpha = alpha;
          ctx2d.lineWidth = l.w;
          ctx2d.setLineDash([l.len, l.len]);
          ctx2d.lineDashOffset = offset;
          ctx2d.stroke(l.path);
        }
        ctx2d.globalAlpha = 1;
      };

      const frame = (ts) => {
        raf = 0;
        if (paused()) { lastTs = null; return; } // paused() is defined below; frames only run after start()
        if (lastTs !== null) elapsed += Math.min(ts - lastTs, 100); // no jump after a stall
        lastTs = ts;
        drawLines();
        raf = window.requestAnimationFrame(frame);
      };
      const ensureLoop = () => {
        if (reduce) { drawLines(); return; }
        if (!raf) raf = window.requestAnimationFrame(frame);
      };

      const buildInputs = () => {
        sizeCanvas();
        lines = [];
        const count = reduce ? 20 : W <= 720 ? 34 : 64;
        for (let i = 0; i < count; i++) {
          const p = makeInput();
          inG.appendChild(p); // measured in the SVG, then removed: the canvas draws it
          const len = p.getTotalLength();
          const d = p.getAttribute("d");
          const w = parseFloat(p.getAttribute("stroke-width")) || 1;
          p.remove();
          lines.push({
            path: new Path2D(d), len, w,
            op: reduce ? rnd(0.08, 0.2) : rnd(0.18, 0.5),
            dur: rnd(4, 8.5),
            delay: rnd(0, 0.3),
          });
        }
        ensureLoop();
      };

      let icons = [];
      let lastIdx = -1;
      // pause everything while the hero is off screen or the tab is hidden: the CSS
      // animations stop (.is-paused) and no new outputs are scheduled, so the rest of
      // the site never pays for an animation nobody is looking at
      const heroEl = svg.closest(".hero-page");
      let heroVisible = true, pageVisible = !document.hidden, cyclePending = false;
      const paused = () => !heroVisible || !pageVisible;
      const syncPause = () => {
        if (heroEl) heroEl.classList.toggle("is-paused", paused());
        if (!paused()) ensureLoop();
        if (!paused() && cyclePending) { cyclePending = false; cycleOutput(); }
      };
      if (heroEl && "IntersectionObserver" in window) {
        new IntersectionObserver((entries) => {
          heroVisible = entries[0].isIntersecting;
          syncPause();
        }, { threshold: 0.05 }).observe(heroEl);
      }
      document.addEventListener("visibilitychange", () => { pageVisible = !document.hidden; syncPause(); });

      const cycleOutput = () => {
        if (paused()) { cyclePending = true; return; }
        let idx = Math.floor(rnd(0, icons.length));
        if (icons.length > 1 && idx === lastIdx) idx = (idx + 1) % icons.length; // avoid an immediate repeat
        const res = buildOutput(icons[idx], false);
        if (!res.ok) { window.setTimeout(cycleOutput, 360); return; } // no free space yet, retry soon
        lastIdx = idx;
        // start the NEXT output before this one finishes (overlap = agility), but only
        // where it fits without crossing - buildOutput guards the placement.
        const next = Math.max(res.total * 0.8, 1.4);
        window.setTimeout(cycleOutput, next * 1000);
      };

      // kick off only once the layout (and webfont) have settled, so the field is measured
      // at its REAL size - an early/wrong measure was breaking the coordinates on mobile.
      let started = false;
      const start = () => {
        if (started) return;
        started = true;
        measure();
        lastW = W; lastH = H;
        buildInputs();
        (async () => {
          try { icons = await Promise.all(ICON_FILES.map(loadIcon)); }
          catch (e) { return; } // icons unavailable: hero still shows inputs + title
          if (!icons.length) return;
          if (reduce) { buildOutput(icons[0], true); return; }
          // outputs begin as the first (now faster) input lines reach the title - keeps
          // the original input→output relationship, just earlier overall
          window.setTimeout(cycleOutput, 4000);
        })();
      };
      window.addEventListener("orientationchange", measure);
      if (document.fonts && document.fonts.ready) { document.fonts.ready.then(start); }
      window.addEventListener("load", () => { measure(); start(); });
      window.setTimeout(start, 1500); // safety net if fonts.ready / load are slow
    })();
}
{
    // "See it working" demo modal: plain JS, no libraries. Opens on the button and plays the local
    // MP4 with audio (the click is a user gesture, so playback is allowed; if a browser still blocks
    // it, fall back to muted and let the controls unmute). Closes on the X, a backdrop click, or Esc,
    // pausing and rewinding on close and returning focus to the trigger.
    (function () {
      var modal = document.getElementById("demo-modal");
      var openBtn = document.getElementById("demo-open");
      if (!modal || !openBtn) return;
      var video = modal.querySelector(".demo-video");
      var closeBtn = modal.querySelector(".demo-modal-close");

      function open() {
        modal.hidden = false;
        document.documentElement.style.overflow = "hidden"; // lock the background scroll
        closeBtn.focus();
        try { video.currentTime = 0; } catch (e) {}
        var p = video.play();
        if (p && p.catch) {
          p.catch(function () { video.muted = true; var q = video.play(); if (q && q.catch) q.catch(function () {}); });
        }
      }
      function close() {
        video.pause();
        modal.hidden = true;
        document.documentElement.style.overflow = "";
        openBtn.focus(); // return focus to the trigger (the only opener)
      }

      openBtn.addEventListener("click", open);
      modal.addEventListener("click", function (e) {
        if (e.target.hasAttribute("data-demo-close")) close();
      });
      document.addEventListener("keydown", function (e) {
        if (!modal.hidden && (e.key === "Escape" || e.key === "Esc")) close();
      });
      // Minimal focus containment: keep Tab within the dialog (close button <-> video controls).
      modal.addEventListener("keydown", function (e) {
        if (e.key !== "Tab" || modal.hidden) return;
        if (e.shiftKey && document.activeElement === closeBtn) { e.preventDefault(); video.focus(); }
        else if (!e.shiftKey && document.activeElement === video) { e.preventDefault(); closeBtn.focus(); }
      });
    })();
}
