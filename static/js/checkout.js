/* White Meat Company - shared checkout modal.
   Any cart on the site opens this via WMCheckout.open({source, items, total, onSuccess}).
   items: [{ name, qty, lineTotal }]. Submits to /api/place-order/, then hands
   the order to WhatsApp. Included once, globally, in base.html. */
(function () {
  "use strict";

  var modal, form, itemsBox, totalEl, sourceField, itemsField, totalField,
      proofRow, proofInput, errorBox, submitBtn;
  var state = { source: "", items: [], total: 0, onSuccess: null };

  function fmt(n) { return "$" + Number(n || 0).toFixed(2); }

  function renderSummary() {
    if (!state.items.length) {
      itemsBox.innerHTML = '<p style="color:var(--wm-muted);margin:0">No items.</p>';
    } else {
      itemsBox.innerHTML = state.items.map(function (it) {
        return '<div class="wm-checkout__row"><span>' + escapeHtml(it.name) +
          (it.qty > 1 ? ' &times; ' + it.qty : '') + '</span><span>' + fmt(it.lineTotal) + '</span></div>';
      }).join('');
    }
    totalEl.textContent = fmt(state.total);
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text == null ? '' : String(text);
    return div.innerHTML;
  }

  function csrfToken() {
    var m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    if (m) return decodeURIComponent(m[1]);
    var input = form.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function toggleProofRow() {
    var checked = form.querySelector('input[name=payment_method]:checked');
    var method = checked ? checked.value : 'proof';
    proofRow.style.display = method === 'proof' ? '' : 'none';
    proofInput.required = method === 'proof';
  }

  function open(opts) {
    if (!modal) return;
    state.source = opts.source || '';
    state.items = opts.items || [];
    state.total = opts.total || 0;
    state.onSuccess = typeof opts.onSuccess === 'function' ? opts.onSuccess : null;

    form.reset();
    sourceField.value = state.source;
    itemsField.value = state.items.map(function (it) {
      return it.name + ' x' + it.qty + ' = ' + fmt(it.lineTotal);
    }).join('\n');
    totalField.value = state.total.toFixed(2);
    renderSummary();
    errorBox.hidden = true;
    toggleProofRow();

    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    var nameInput = document.getElementById('wm-co-name');
    if (nameInput) setTimeout(function () { nameInput.focus(); }, 50);
  }

  function close() {
    if (!modal) return;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.hidden = false;
    errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function errorsToText(errors) {
    try {
      return Object.keys(errors).map(function (key) {
        var list = errors[key];
        return (list || []).map(function (e) {
          return typeof e === 'string' ? e : (e && e.message) || '';
        }).join(' ');
      }).filter(Boolean).join(' ');
    } catch (e) {
      return 'Please check the form and try again.';
    }
  }

  function submit(e) {
    e.preventDefault();
    if (!state.items.length) { showError('Your cart is empty.'); return; }

    submitBtn.disabled = true;
    var original = submitBtn.innerHTML;
    submitBtn.innerHTML = 'Sending&hellip;';
    errorBox.hidden = true;

    var fd = new FormData(form);
    fetch('/api/place-order/', {
      method: 'POST',
      body: fd,
      headers: { 'X-CSRFToken': csrfToken() },
      credentials: 'same-origin',
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          return { ok: r.ok, data: data };
        });
      })
      .then(function (res) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = original;
        if (res.ok && res.data && res.data.success) {
          window.open(res.data.whatsapp_url, '_blank');
          close();
          if (state.onSuccess) state.onSuccess();
        } else {
          showError(
            (res.data && res.data.errors && errorsToText(res.data.errors)) ||
            'Please check the form and try again.'
          );
        }
      })
      .catch(function () {
        submitBtn.disabled = false;
        submitBtn.innerHTML = original;
        showError('Network error - please check your connection and try again.');
      });
  }

  function init() {
    modal = document.getElementById('wm-checkout-modal');
    if (!modal) return;
    form = document.getElementById('wm-checkout-form');
    itemsBox = document.getElementById('wm-checkout-items');
    totalEl = document.getElementById('wm-checkout-total');
    sourceField = document.getElementById('wm-checkout-source');
    itemsField = document.getElementById('wm-checkout-items-field');
    totalField = document.getElementById('wm-checkout-total-field');
    proofRow = document.getElementById('wm-checkout-proof-row');
    proofInput = document.getElementById('wm-co-proof');
    errorBox = document.getElementById('wm-checkout-error');
    submitBtn = document.getElementById('wm-checkout-submit');

    form.querySelectorAll('input[name=payment_method]').forEach(function (r) {
      r.addEventListener('change', toggleProofRow);
    });
    form.addEventListener('submit', submit);
    modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  document.addEventListener('DOMContentLoaded', init);
  window.WMCheckout = { open: open, close: close };
})();
