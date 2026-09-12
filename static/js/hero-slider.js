/* White Meat Company - hero slider
   Vanilla, no dependencies. Auto-advance, dots, arrows, swipe,
   pause on hover / tab-hidden, respects prefers-reduced-motion. */
(function () {
  "use strict";

  function initSlider(root) {
    var slides = Array.prototype.slice.call(root.querySelectorAll(".wm-hero__slide"));
    if (slides.length <= 1) return;

    var dots = Array.prototype.slice.call(root.querySelectorAll(".wm-hero__dots button"));
    var prev = root.querySelector(".wm-hero__arrow--prev");
    var next = root.querySelector(".wm-hero__arrow--next");
    var interval = parseInt(root.dataset.interval, 10) || 6500;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var index = slides.findIndex(function (s) { return s.classList.contains("is-active"); });
    if (index < 0) index = 0;
    var timer = null;

    function show(i) {
      index = (i + slides.length) % slides.length;
      slides.forEach(function (s, n) { s.classList.toggle("is-active", n === index); });
      dots.forEach(function (d, n) {
        d.classList.toggle("is-active", n === index);
        d.setAttribute("aria-selected", n === index ? "true" : "false");
      });
    }
    function nextSlide() { show(index + 1); }
    function start() {
      if (reduce || timer) return;
      timer = window.setInterval(nextSlide, interval);
    }
    function stop() { window.clearInterval(timer); timer = null; }
    function restart() { stop(); start(); }

    dots.forEach(function (d, n) {
      d.addEventListener("click", function () { show(n); restart(); });
    });
    if (prev) prev.addEventListener("click", function () { show(index - 1); restart(); });
    if (next) next.addEventListener("click", function () { show(index + 1); restart(); });

    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    document.addEventListener("visibilitychange", function () {
      document.hidden ? stop() : start();
    });

    // Touch swipe
    var x0 = null;
    root.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    root.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) { show(index + (dx < 0 ? 1 : -1)); restart(); }
      x0 = null;
    }, { passive: true });

    show(index);
    start();
  }

  function initNav() {
    var nav = document.querySelector(".wm-nav");
    if (!nav) return;
    var burger = nav.querySelector(".wm-nav__burger");
    var links = nav.querySelector(".wm-nav__links");
    var scrim = document.querySelector(".wm-nav__scrim");

    function setOpen(open) {
      if (open) {
        // The topbar sits above the nav and isn't sticky, so when the page
        // hasn't been scrolled yet the nav's real bottom edge is further
        // down than --wm-nav-h alone accounts for. Measure it live each
        // time the menu opens instead of trusting the static var.
        var offset = Math.round(nav.getBoundingClientRect().bottom);
        document.documentElement.style.setProperty("--wm-nav-offset", offset + "px");
      }
      burger.classList.toggle("is-open", open);
      links.classList.toggle("is-open", open);
      if (scrim) scrim.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.style.overflow = open ? "hidden" : "";
    }
    if (burger && links) {
      burger.addEventListener("click", function () {
        setOpen(!links.classList.contains("is-open"));
      });
      if (scrim) scrim.addEventListener("click", function () { setOpen(false); });
      links.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () {
          // let sub-menu parents toggle instead of navigating on mobile
          if (a.parentElement.querySelector(".wm-nav__drop") && window.innerWidth <= 1080) return;
          setOpen(false);
        });
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") setOpen(false);
      });
      window.addEventListener("resize", function () {
        if (window.innerWidth > 1080) setOpen(false);
      });
    }

    var onScroll = function () { nav.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    document.querySelectorAll("[data-wm-hero]").forEach(initSlider);
  });
})();
