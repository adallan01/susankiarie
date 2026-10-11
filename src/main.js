(function () {
  "use strict";
  var doc = document;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var yr = doc.getElementById("yr");
  if (yr) yr.textContent = String(new Date().getFullYear());

  /* Mobile menu */
  var btn = doc.querySelector(".menu-btn");
  var links = doc.getElementById("nav-links");
  function setMenu(open) {
    btn.setAttribute("aria-expanded", String(open));
    btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    links.setAttribute("data-open", String(open));
  }
  if (btn && links) {
    btn.addEventListener("click", function () { setMenu(btn.getAttribute("aria-expanded") !== "true"); });
    links.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") { setMenu(false); btn.focus(); }
    });
    var mq = window.matchMedia("(min-width: 961px)");
    var sync = function () { if (mq.matches) setMenu(false); };
    mq.addEventListener ? mq.addEventListener("change", sync) : mq.addListener(sync);
  }

  /* Current section in nav */
  if ("IntersectionObserver" in window) {
    var navMap = {};
    doc.querySelectorAll('.nav-links a[href^="#"]:not(.btn)').forEach(function (a) { navMap[a.getAttribute("href").slice(1)] = a; });
    var alias = { markets: "milestones", education: "leadership" };
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var id = en.target.id;
        if (en.target.closest("#milestones")) id = "milestones";
        id = alias[id] || id;
        Object.keys(navMap).forEach(function (k) { navMap[k].removeAttribute("aria-current"); });
        if (navMap[id]) navMap[id].setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    doc.querySelectorAll("main section[id], #milestones > section").forEach(function (s) { spy.observe(s); });
  }

  /* Links to the career chronology open it */
  var chrono = doc.getElementById("career");
  function openChrono() { if (chrono && !chrono.open) chrono.open = true; }
  doc.querySelectorAll('a[href="#career"]').forEach(function (a) { a.addEventListener("click", openChrono); });
  if (location.hash === "#career") openChrono();

  /* Odometer: digits roll through 0-9 like a counter, then settle on the real value.
     The final value is in the HTML; motion only runs when the visitor allows it. */
  function buildOdo(el) {
    if (el.dataset.built) return;
    var txt = el.textContent.trim(), from = (el.getAttribute("data-from") || "").trim();
    var hidden = el.parentElement && el.parentElement.closest("[aria-hidden='true']");
    if (!hidden) { var sr = doc.createElement("span"); sr.className = "sr-only"; sr.textContent = txt; el.after(sr); }
    el.setAttribute("aria-hidden", "true");
    el.textContent = "";
    var digits = 0;
    for (var i = 0; i < txt.length; i++) {
      var ch = txt[i];
      if (/[0-9]/.test(ch)) {
        var dg = doc.createElement("span"); dg.className = "dg";
        var ph = doc.createElement("span"); ph.className = "ph"; ph.textContent = ch; dg.appendChild(ph);
        var win = doc.createElement("span"); win.className = "win"; dg.appendChild(win);
        var strip = doc.createElement("span"); strip.className = "strip";
        for (var k = 0; k < 30; k++) { var c = doc.createElement("span"); c.textContent = String(k % 10); strip.appendChild(c); }
        var start = from && /[0-9]/.test(from[i] || "") ? +from[i] : 0;
        strip.dataset.start = String(start);
        strip.dataset.end = String(20 + (+ch));
        strip.style.setProperty("--pos", String(start));
        strip.style.setProperty("--delay", (digits * 0.12).toFixed(2) + "s");
        strip.style.setProperty("--dur", (1.6 + digits * 0.25).toFixed(2) + "s");
        win.appendChild(strip); el.appendChild(dg); digits++;
      } else {
        var s2 = doc.createElement("span"); s2.className = "ch"; s2.textContent = ch; el.appendChild(s2);
      }
    }
    el.dataset.built = "1";
  }
  function runOdo(el) {
    el.classList.add("run");
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      el.querySelectorAll(".strip").forEach(function (st) { st.style.setProperty("--pos", st.dataset.end); });
    }); });
  }
  var odos = doc.querySelectorAll(".odo");
  if (!reduce && "IntersectionObserver" in window) {
    odos.forEach(buildOdo);
    var oio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { runOdo(en.target); oio.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -10% 0px" });
    odos.forEach(function (el) {
      if (el.hasAttribute("data-load")) setTimeout(function () { runOdo(el); }, 350);
      else oio.observe(el);
    });
  }

  /* Transform-only reveals and bar growth below the fold */
  var vh = window.innerHeight || 800;
  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.remove("pre");
        en.target.querySelectorAll(".track.pre").forEach(function (t) { t.classList.remove("pre"); });
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -12% 0px" });
    doc.querySelectorAll(".rv").forEach(function (el) {
      if (el.getBoundingClientRect().top > vh) {
        el.classList.add("pre");
        el.querySelectorAll(".track").forEach(function (t) { t.classList.add("pre"); });
        io.observe(el);
      }
    });
  }

  /* Scroll-driven market story: the active step lights its countries on the sticky map */
  var scrolly = doc.querySelector(".scrolly");
  if (scrolly && "IntersectionObserver" in window) {
    var steps = scrolly.querySelectorAll(".step");
    var ind = scrolly.querySelectorAll(".step-ind i");
    var landsAll = scrolly.querySelectorAll(".land[data-name]");
    var rays = scrolly.querySelectorAll(".ray");
    var cities = scrolly.querySelectorAll(".city");
    function activate(step) {
      steps.forEach(function (s) { s.classList.toggle("on", s === step); });
      var idx = +step.dataset.step;
      ind.forEach(function (i, n) { i.classList.toggle("on", n <= idx); });
      var hl = step.dataset.hl;
      scrolly.setAttribute("data-active", hl === "all" ? "all" : String(idx));
      var set = hl === "all" ? null : hl.split("|");
      landsAll.forEach(function (l) { l.classList.toggle("lit", !set || set.indexOf(l.dataset.name) > -1); });
      rays.forEach(function (r) { r.classList.toggle("lit", !set || set.indexOf(r.dataset.to) > -1); });
      cities.forEach(function (c) { c.classList.toggle("on", step.dataset.city === c.dataset.city); });
    }
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) activate(en.target); });
    }, { rootMargin: "-45% 0px -45% 0px" });
    steps.forEach(function (s) { sio.observe(s); });
  }

  /* 3D logo gallery: slow auto-rotation, drag or swipe to turn, arrows and keyboard focus bring a logo to the front */
  var stage = doc.querySelector("[data-ring]");
  if (stage) {
    var ring = stage.querySelector(".ring");
    var faces = stage.querySelectorAll(".face");
    var n = faces.length, step = 360 / n, angle = 0, target = null, playing = !reduce, hover = false, dragging = false, lastX = 0, vel = 0;
    var playBtn = doc.querySelector("[data-ring-play]");
    function paint() {
      ring.style.setProperty("--a", angle.toFixed(2) + "deg");
      faces.forEach(function (f, i) {
        var a = ((i * step + angle) % 360 + 360) % 360;
        var facing = Math.cos(a * Math.PI / 180);
        var tile = f.firstElementChild;
        tile.style.setProperty("--lit", (0.45 + 0.55 * Math.max(0, facing)).toFixed(3));
        tile.tabIndex = tile.tagName === "A" ? 0 : -1;
        f.style.zIndex = String(Math.round(facing * 100) + 100);
      });
    }
    function setPlay(on) { playing = on; if (playBtn) { playBtn.textContent = on ? "Pause" : "Play"; playBtn.setAttribute("aria-pressed", String(!on)); } }
    setPlay(!reduce);
    function goTo(i) { target = -i * step; var d = ((target - angle) % 360 + 540) % 360 - 180; target = angle + d; }
    function frontIndex() { return ((Math.round(-angle / step) % n) + n) % n; }
    function tick() {
      if (target !== null) { angle += (target - angle) * 0.12; if (Math.abs(target - angle) < 0.05) { angle = target; target = null; } }
      else if (!dragging) {
        if (Math.abs(vel) > 0.02) { angle += vel; vel *= 0.94; }
        else if (playing && !hover) angle -= 0.09;
      }
      paint();
      requestAnimationFrame(tick);
    }
    stage.addEventListener("pointerenter", function () { hover = true; });
    stage.addEventListener("pointerleave", function () { hover = false; });
    stage.addEventListener("pointerdown", function (e) { dragging = true; target = null; lastX = e.clientX; vel = 0; stage.classList.add("drag"); stage.setPointerCapture && stage.setPointerCapture(e.pointerId); });
    stage.addEventListener("pointermove", function (e) { if (!dragging) return; var dx = e.clientX - lastX; lastX = e.clientX; vel = dx * 0.25; angle += vel; });
    var moved = 0;
    function endDrag() { if (!dragging) return; dragging = false; stage.classList.remove("drag"); }
    stage.addEventListener("pointerup", endDrag); stage.addEventListener("pointercancel", endDrag);
    stage.addEventListener("click", function (e) { if (Math.abs(vel) > 1.2) e.preventDefault(); }, true);
    faces.forEach(function (f, i) { f.firstElementChild.addEventListener("focus", function () { setPlay(false); goTo(i); }); });
    var prev = doc.querySelector("[data-ring-prev]"), next = doc.querySelector("[data-ring-next]");
    if (prev) prev.addEventListener("click", function () { setPlay(false); goTo((frontIndex() - 1 + n) % n); });
    if (next) next.addEventListener("click", function () { setPlay(false); goTo((frontIndex() + 1) % n); });
    if (playBtn) playBtn.addEventListener("click", function () { setPlay(!playing); });
    paint();
    requestAnimationFrame(tick);
  }

  /* Gentle 3D tilt on the featured figures (pointer devices only) */
  if (!reduce && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    doc.querySelectorAll("[data-tilt]").forEach(function (el) {
      var host = el.closest(".feat") || el;
      host.addEventListener("pointermove", function (e) {
        var r = host.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        el.style.setProperty("--ry", (x * 10).toFixed(2) + "deg");
        el.style.setProperty("--rx", (-y * 8).toFixed(2) + "deg");
      });
      host.addEventListener("pointerleave", function () { el.style.setProperty("--ry", "0deg"); el.style.setProperty("--rx", "0deg"); });
    });
  }

  /* Map legend: highlight a country on hover or focus */
  var lands = {};
  doc.querySelectorAll(".land[data-name]").forEach(function (p) { lands[p.getAttribute("data-name")] = p; });
  doc.querySelectorAll(".legend [data-country]").forEach(function (b) {
    var p = lands[b.getAttribute("data-country")];
    if (!p) return;
    var on = function () { p.classList.add("hot"); b.classList.add("on"); };
    var off = function () { p.classList.remove("hot"); b.classList.remove("on"); };
    b.addEventListener("mouseenter", on); b.addEventListener("mouseleave", off);
    b.addEventListener("focus", on); b.addEventListener("blur", off);
  });

  /* Copy buttons */
  var status = doc.querySelector(".status");
  function say(msg) { if (status) { status.textContent = msg; clearTimeout(say.t); say.t = setTimeout(function () { status.textContent = ""; }, 4000); } }
  doc.querySelectorAll("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var v = b.getAttribute("data-copy");
      var label = b.querySelector("span");
      var done = function () { if (label) { label.textContent = "Copied"; setTimeout(function () { label.textContent = "Copy"; }, 2000); } say("Copied " + v); };
      var fallback = function () {
        var target = b.closest(".ch").querySelector("dd a, dd .v");
        var r = doc.createRange(); r.selectNodeContents(target);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        say("Selected. Press Ctrl+C or Cmd+C to copy.");
      };
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(v).then(done, fallback);
        else fallback();
      } catch (e) { fallback(); }
    });
  });

  /* CV download. On a normal web host the link downloads the PDF directly.
     Inside a Claude artifact viewer, plain download links are blocked, so the file is offered through the viewer's save dialog. */
  var hasViewer = window.claude && typeof window.claude.use === "function";
  if (hasViewer) {
    doc.querySelectorAll("[data-cv]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        window.claude.use("downloads").then(function (dl) {
          if (!dl) throw { code: "unavailable" };
          return fetch(a.getAttribute("href")).then(function (r) {
            if (!r.ok) throw { code: "unavailable" };
            return r.blob();
          }).then(function (blob) {
            return dl.save({ filename: a.getAttribute("data-filename"), data: blob });
          });
        }).then(function () { say("CV saved."); }, function (err) {
          if (err && err.code === "declined") return;
          if (err && err.code === "rate_limited") { say("A save prompt is already open."); return; }
          say("The download isn't available in this view. Please request the CV by email.");
        });
      });
    });
  }
})();
