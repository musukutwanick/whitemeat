/* White Meat Company - site motion
   Dependency-free. Scroll reveals (with per-group stagger), hero copy
   entrance, and stat count-up. Fully skipped for prefers-reduced-motion. */
(function () {
  "use strict";

  var REDUCE = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var HAS_IO = "IntersectionObserver" in window;

  /* --- 1. Scroll reveals -------------------------------------------------- */
  // [selector, direction, stagger step in ms]
  var GROUPS = [
    ["main .wm-section__head", "up", 0],
    [".wm-promo", "up", 0],
    [".wm-servicebar__item", "up", 55],
    [".wm-product-grid > *", "up", 65],
    [".wm-services__grid > *", "up", 65],
    [".wm-tip-grid > *", "up", 55],
    [".wm-duo__card", "up", 90],
    [".wm-stat", "up", 55],
    [".wm-menu-grid > *", "zoom", 50],
    [".wm-branch-card", "up", 0],
    [".wm-schedule__card", "up", 45],
    [".wm-buyback > *", "up", 90],
    [".wm-contact > *", "up", 90],
    [".wm-howhear__card", "up", 0],
    [".wm-calendar", "up", 0],
    [".wm-req-box", "up", 0],
    [".wm-band-split", "up", 0],
    [".wm-cta", "zoom", 0],
    [".wm-brand-band__words", "zoom", 0],
    [".wm-promo__list li", "left", 70]
  ];

  function setupReveals() {
    if (REDUCE || !HAS_IO) return;

    var tagged = [];
    var seen = typeof WeakSet === "function" ? new WeakSet() : null;

    GROUPS.forEach(function (g) {
      var sel = g[0], dir = g[1], step = g[2];
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        if (seen) { if (seen.has(el)) return; seen.add(el); }
        else if (el.hasAttribute("data-reveal")) return;

        el.setAttribute("data-reveal", dir);
        if (step && el.parentElement) {
          var sibs = Array.prototype.slice.call(el.parentElement.children);
          var idx = sibs.indexOf(el);
          if (idx > 0) {
            el.style.setProperty("--reveal-delay", (Math.min(idx, 7) * step / 1000) + "s");
          }
        }
        tagged.push(el);
      });
    });

    if (!tagged.length) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });

    tagged.forEach(function (el) { io.observe(el); });

    // Safety net: anything already in view on load reveals on next frame
    requestAnimationFrame(function () {
      tagged.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) el.classList.add("is-in");
      });
    });
  }

  /* --- 2. Stat count-up -------------------------------------------------- */
  function animateCount(el) {
    var m = el.textContent.trim().match(/^(\D*)(\d[\d,]*)(.*)$/);
    if (!m) return;
    var prefix = m[1], suffix = m[3];
    var target = parseInt(m[2].replace(/,/g, ""), 10);
    if (!isFinite(target) || target <= 0) return;

    var dur = 1100, t0 = performance.now();
    (function frame(now) {
      var p = Math.min((now - t0) / dur, 1);
      var v = Math.round(target * (1 - Math.pow(1 - p, 3)));
      el.textContent = prefix + v.toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(frame);
    })(t0);
  }

  function setupCounters() {
    if (REDUCE || !HAS_IO) return;
    var nums = document.querySelectorAll(".wm-stat strong");
    if (!nums.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        animateCount(e.target);
      });
    }, { threshold: 0.75 });
    nums.forEach(function (n) { io.observe(n); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setupReveals();
    setupCounters();
  });
})();
