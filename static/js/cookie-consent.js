(function () {
  "use strict";

  var CONSENT_COOKIE = "wm_cookie_consent";
  var PREFERENCES_COOKIE = "wm_preferences";
  var COOKIE_MAX_AGE = 60 * 60 * 24 * 365;
  var consent = null;

  function setCookie(name, value, maxAge) {
    var secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = name + "=" + encodeURIComponent(value) + "; Max-Age=" + maxAge + "; Path=/; SameSite=Lax" + secure;
  }

  function deleteCookie(name) {
    setCookie(name, "", 0);
  }

  function readCookie(name) {
    var prefix = name + "=";
    var match = document.cookie.split("; ").find(function (item) { return item.indexOf(prefix) === 0; });
    return match ? decodeURIComponent(match.slice(prefix.length)) : null;
  }

  function readConsent() {
    var raw = readCookie(CONSENT_COOKIE);
    if (!raw) return null;
    try {
      var parsed = JSON.parse(raw);
      return parsed && parsed.version === 1 ? parsed : null;
    } catch (error) {
      return null;
    }
  }

  function has(category) {
    return category === "necessary" || !!(consent && consent[category]);
  }

  function store(preferences, analytics) {
    consent = {
      version: 1,
      necessary: true,
      preferences: !!preferences,
      analytics: !!analytics,
    };
    setCookie(CONSENT_COOKIE, JSON.stringify(consent), COOKIE_MAX_AGE);
    if (consent.preferences) {
      setCookie(PREFERENCES_COOKIE, JSON.stringify({ version: 1 }), COOKIE_MAX_AGE);
    } else {
      deleteCookie(PREFERENCES_COOKIE);
    }
    document.getElementById("wm-cookie-banner").hidden = true;
    document.getElementById("wm-cookie-preferences").hidden = true;
    document.getElementById("wm-cookie-settings").hidden = false;
    window.dispatchEvent(new CustomEvent("wm:consent-updated", { detail: consent }));
  }

  function openPreferences() {
    var preferences = document.getElementById("wm-cookie-preferences");
    var preferenceChoice = document.getElementById("wm-cookie-preferences-choice");
    var analyticsChoice = document.getElementById("wm-cookie-analytics-choice");
    preferenceChoice.checked = has("preferences");
    analyticsChoice.checked = has("analytics");
    preferences.hidden = false;
  }

  function closePreferences() {
    var preferences = document.getElementById("wm-cookie-preferences");
    preferences.hidden = true;
  }

  function wireActions() {
    document.querySelectorAll("[data-cookie-action]").forEach(function (button) {
      button.addEventListener("click", function () {
        var action = button.dataset.cookieAction;
        if (action === "accept-all") store(true, true);
        if (action === "essential-only") store(false, false);
        if (action === "open-preferences") openPreferences();
        if (action === "close-preferences") closePreferences();
        if (action === "save-preferences") {
          store(
            document.getElementById("wm-cookie-preferences-choice").checked,
            document.getElementById("wm-cookie-analytics-choice").checked
          );
        }
      });
    });
  }

  function init() {
    consent = readConsent();
    wireActions();
    if (consent) {
      document.getElementById("wm-cookie-settings").hidden = false;
      window.dispatchEvent(new CustomEvent("wm:consent-ready", { detail: consent }));
    } else {
      document.getElementById("wm-cookie-banner").hidden = false;
    }
  }

  window.WMConsent = {
    has: has,
    get: function () { return consent; },
    setPreference: function (name, value) {
      if (!has("preferences")) return;
      var preferences = {};
      try { preferences = JSON.parse(readCookie(PREFERENCES_COOKIE) || "{}"); } catch (error) { preferences = {}; }
      preferences[name] = value;
      setCookie(PREFERENCES_COOKIE, JSON.stringify(preferences), COOKIE_MAX_AGE);
    },
  };

  document.addEventListener("DOMContentLoaded", init);
})();
