/* White Meat Company - shared product cart (sidebar + floating button +
   navbar icon). Persisted to localStorage so it survives navigation - add
   something on /cages/, browse to /accessories/, add more, then open the
   cart from the navbar (or the floating button) on ANY page and see it all.

   Each item remembers which page/category it came from. At checkout the
   order is filed under that category if everything in the cart shares one,
   or a generic "Mixed cart" category if it spans more than one. */
(function () {
  "use strict";

  var STORAGE_KEY = "wm_cart_v1";
  var cart = [];
  var currentSource = null;

  function load() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      var parsed = raw ? JSON.parse(raw) : [];
      cart = Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      cart = [];
    }
  }

  function persist() {
    try { window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cart)); } catch (e) { /* private mode etc. - cart just won't survive reload */ }
  }

  function els() {
    return {
      list: document.getElementById("cart-items-list"),
      total: document.getElementById("cart-total"),
      fabBadge: document.getElementById("cart-count-badge"),
      navBadge: document.getElementById("nav-cart-badge"),
      sidebar: document.getElementById("cart-sidebar"),
      fab: document.getElementById("open-cart-btn"),
    };
  }

  function add(name, price, source) {
    price = parseFloat(price);
    if (!name || !isFinite(price)) return;
    cart.push({ name: name, price: price, source: source || currentSource || "" });
    persist();
    render();
  }

  function grouped() {
    var g = {}, order = [];
    cart.forEach(function (item) {
      var key = item.name + "|" + item.price;
      if (!g[key]) { g[key] = { key: key, name: item.name, price: item.price, qty: 1, lineTotal: item.price, sources: {} }; order.push(key); }
      else { g[key].qty += 1; g[key].lineTotal += item.price; }
      if (item.source) g[key].sources[item.source] = true;
    });
    return order.map(function (k) { return g[k]; });
  }

  function removeGroup(key) {
    cart = cart.filter(function (item) { return (item.name + "|" + item.price) !== key; });
    persist();
    render();
  }

  function clear() {
    cart = [];
    persist();
    render();
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text == null ? "" : String(text);
    return div.innerHTML;
  }

  function render() {
    var e = els();
    var count = cart.length;

    [e.fabBadge, e.navBadge].forEach(function (badge) {
      if (!badge) return;
      if (count > 0) { badge.style.display = "flex"; badge.textContent = String(count); }
      else { badge.style.display = "none"; badge.textContent = "0"; }
    });
    if (e.fab) e.fab.style.display = count > 0 ? "flex" : "none";

    if (!e.list) return;

    if (count === 0) {
      e.list.innerHTML = '<p style="text-align:center;color:#888;">Your cart is empty</p>';
      if (e.total) e.total.textContent = "$0.00";
      return;
    }

    var items = grouped();
    var total = 0;
    var html = "";
    items.forEach(function (item) {
      total += item.lineTotal;
      html += '<div class="wm-cart-sidebar__row">' +
        "<div><strong>" + escapeHtml(item.name) + "</strong><br><span>$" + item.price.toFixed(2) + " &times; " + item.qty + "</span></div>" +
        '<div><span style="margin-right:8px;">$' + item.lineTotal.toFixed(2) + "</span>" +
        '<button type="button" data-remove-key="' + encodeURIComponent(item.key) + '" class="wm-cart-sidebar__remove">&times;</button></div>' +
        "</div>";
    });
    e.list.innerHTML = html;
    e.list.querySelectorAll("[data-remove-key]").forEach(function (btn) {
      btn.addEventListener("click", function () { removeGroup(decodeURIComponent(btn.dataset.removeKey)); });
    });
    if (e.total) e.total.textContent = "$" + total.toFixed(2);
  }

  function toggle(show) {
    var e = els();
    if (e.sidebar) e.sidebar.classList.toggle("is-open", show);
  }

  function checkout() {
    if (!cart.length) { alert("Your cart is empty!"); return; }
    if (!window.WMCheckout) { alert("Checkout is unavailable right now - please refresh and try again."); return; }

    var items = grouped();
    var total = items.reduce(function (s, i) { return s + i.lineTotal; }, 0);
    var sources = Object.keys(items.reduce(function (acc, i) {
      Object.keys(i.sources).forEach(function (s) { acc[s] = true; });
      return acc;
    }, {}));
    var orderSource = sources.length === 1 ? sources[0] : "mixed";

    window.WMCheckout.open({
      source: orderSource,
      items: items,
      total: total,
      onSuccess: function () { clear(); toggle(false); },
    });
  }

  function init(source) {
    currentSource = source;
  }

  function wireDom() {
    var orderBtn = document.getElementById("order-btn");
    if (orderBtn) orderBtn.addEventListener("click", checkout);
    render();
  }

  load();
  document.addEventListener("DOMContentLoaded", wireDom);

  // Keep multiple open tabs in sync with each other.
  window.addEventListener("storage", function (e) {
    if (e.key === STORAGE_KEY) { load(); render(); }
  });

  window.WMProductCart = { add: add, removeGroup: removeGroup, toggle: toggle, init: init, clear: clear };
})();
