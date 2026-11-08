/* Linkwave Technology site behaviour.
 * Dependency-free, CSP-compatible (no inline handlers, no eval, textContent only).
 * Language is taken from <html lang> because every language now has its own static URL. */
(function () {
  'use strict';

  var root = document.documentElement;
  var lang = root.getAttribute('lang') === 'ar' ? 'ar' : 'en';
  var dict = (window.LINKWAVE_CONTENT && window.LINKWAVE_CONTENT[lang]) || {};
  var config = window.LINKWAVE_CONFIG || {};

  function t(key, fallback) {
    var value = dict[key];
    return typeof value === 'string' && value ? value : (fallback || '');
  }

  function node(tag, className, text) {
    var element = document.createElement(tag);
    if (className) element.className = className;
    if (typeof text === 'string') element.textContent = text;
    return element;
  }

  /* 1. Legacy links (?lang=ar|en) are redirected to the canonical language URL. */
  try {
    var params = new URLSearchParams(window.location.search);
    var requested = params.get('lang');
    if ((requested === 'ar' || requested === 'en') && requested !== lang) {
      var path = window.location.pathname;
      var file = path.substring(path.lastIndexOf('/') + 1) || 'index.html';
      var target;
      if (requested === 'ar') {
        target = path.replace(/\/[^/]*$/, '/ar/' + file);
      } else {
        target = path.replace('/ar/', '/');
      }
      var url = new URL(window.location.href);
      url.searchParams.delete('lang');
      url.pathname = target;
      window.location.replace(url.toString());
      return;
    }
  } catch (error) {
    /* Older browser without URL API: keep the static page as delivered. */
  }

  /* 2. Public contact channels (rendered only when site-config.js is filled in). */
  (function renderContact() {
    var haveChannels = !!(config.phone || config.email || config.whatsapp || config.address);
    if (!haveChannels) return;
    var boxes = document.querySelectorAll('[data-contact-channels]');
    Array.prototype.forEach.call(boxes, function (box) {
      box.textContent = '';
      if (config.phone) {
        var phoneLink = node('a', 'lw-contact-link', config.phone);
        phoneLink.href = 'tel:' + String(config.phone).replace(/[^+0-9]/g, '');
        box.appendChild(phoneLink);
      }
      if (config.email) {
        var mail = node('a', 'lw-contact-link', config.email);
        mail.href = 'mailto:' + config.email;
        box.appendChild(mail);
      }
      if (config.whatsapp) {
        var wa = node('a', 'lw-contact-link', t('contactWhatsapp', 'WhatsApp'));
        wa.href = 'https://wa.me/' + String(config.whatsapp).replace(/[^0-9]/g, '');
        wa.rel = 'noopener';
        box.appendChild(wa);
      }
      if (config.address) box.appendChild(node('span', 'lw-contact-address', config.address));
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-contact-pending]'), function (pending) {
      pending.hidden = true;
    });
    if (config.whatsapp) {
      Array.prototype.forEach.call(document.querySelectorAll('[data-whatsapp-pending]'), function (link) {
        link.hidden = false;
        link.href = 'https://wa.me/' + String(config.whatsapp).replace(/[^0-9]/g, '');
        link.rel = 'noopener';
      });
    }
  })();

  /* 3. Mobile navigation. */
  var toggle = document.querySelector('.lw-menu-toggle');
  var menu = document.getElementById('lw-menu');
  if (toggle && menu) {
    var setMenu = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      menu.classList.toggle('lw-open', open);
    };
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        toggle.focus();
      }
    });
    document.addEventListener('click', function (event) {
      if (toggle.getAttribute('aria-expanded') === 'true' &&
          !menu.contains(event.target) && !toggle.contains(event.target)) {
        setMenu(false);
      }
    });
  }

  /* 4. Enquiry form: local validation; optional endpoint submission when configured. */
  var form = document.getElementById('quote-form');
  if (form) {
    var fields = Array.prototype.slice.call(form.querySelectorAll('input, textarea, select'));
    var validated = false;
    var status = document.getElementById('form-status');
    var submitButton = form.querySelector('button[type="submit"]');
    if (config.formEndpoint && submitButton) {
      submitButton.disabled = false;
      var submitLabel = submitButton.querySelector('[data-i18n], span');
      if (submitLabel) submitLabel.textContent = t('send', 'Send enquiry');
    }

    var fieldError = function (field) {
      if (field.required && !field.value.trim()) return t('required');
      if (field.type === 'email' && field.validity.typeMismatch) return t('badEmail');
      if (field.maxLength > 0 && field.value.length > field.maxLength) return t('tooLong');
      return '';
    };

    var validate = function (focus) {
      var firstInvalid = null;
      fields.forEach(function (field) {
        var message = fieldError(field);
        field.setAttribute('aria-invalid', message ? 'true' : 'false');
        var target = document.getElementById(field.id + '-error');
        if (target) target.textContent = message;
        if (message && !firstInvalid) firstInvalid = field;
      });
      if (status) {
        status.textContent = t(firstInvalid ? 'invalid' : 'valid');
      }
      if (firstInvalid && focus) firstInvalid.focus();
      return firstInvalid;
    };

    var submitRequest = function () {
      if (!config.formEndpoint) {
        if (status) status.textContent = t('valid');
        return;
      }
      var payload = {};
      fields.forEach(function (field) {
        if (field.name) payload[field.name] = field.value;
      });
      payload.language = lang;
      if (status) status.textContent = t('sending', 'Sending…');
      if (submitButton) submitButton.disabled = true;
      window.fetch(config.formEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        if (status) status.textContent = t('sentOk');
        form.reset();
        validated = false;
      }).catch(function () {
        if (status) status.textContent = t('sentErr');
      }).then(function () {
        if (submitButton) submitButton.disabled = false;
      });
    };

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      validated = true;
      if (validate(true)) return;
      submitRequest();
    });

    var validateButton = document.getElementById('validate-form');
    if (validateButton) {
      validateButton.addEventListener('click', function () {
        validated = true;
        validate(true);
      });
    }
    form.addEventListener('input', function () {
      if (validated) validate(false);
    });
    form.addEventListener('change', function () {
      if (validated) validate(false);
    });
  }

  /* 5. Accessible hero slider (fade + slow zoom, pauses on demand, respects reduced motion). */
  var hero = document.getElementById('lw-hero');
  if (hero) {
    var slides = Array.prototype.slice.call(hero.querySelectorAll('.lw-slide'));
    var bullets = Array.prototype.slice.call(hero.querySelectorAll('.lw-bullet'));
    var prevButton = document.getElementById('lw-prev');
    var nextButton = document.getElementById('lw-next');
    var pauseButton = document.getElementById('lw-pause');
    var statusNode = hero.querySelector('[data-slide-status]');
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    var index = 0;
    var timer = null;
    var paused = false;

    var announce = function () {
      if (!statusNode) return;
      var title = slides[index].getAttribute('data-slide-title') || '';
      statusNode.textContent = (index + 1) + ' / ' + slides.length + (title ? ' — ' + title : '');
    };

    var show = function (next, shouldAnnounce) {
      index = (next + slides.length) % slides.length;
      slides.forEach(function (slide, position) {
        var active = position === index;
        slide.classList.toggle('is-active', active);
        slide.setAttribute('aria-hidden', active ? 'false' : 'true');
      });
      bullets.forEach(function (bullet, position) {
        bullet.setAttribute('aria-current', position === index ? 'true' : 'false');
      });
      if (shouldAnnounce) announce();
    };

    var stop = function () {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    };

    var start = function () {
      stop();
      if (paused || reduceMotion.matches) return;
      timer = window.setInterval(function () { show(index + 1, true); }, 7000);
    };

    var setPaused = function (value) {
      paused = value;
      hero.classList.toggle('is-paused', paused);
      if (pauseButton) {
        pauseButton.setAttribute('aria-pressed', String(paused));
        var label = pauseButton.querySelector('[data-label]');
        if (label) label.textContent = t(paused ? 'play' : 'pause');
      }
      if (paused) stop(); else start();
    };

    if (prevButton) prevButton.addEventListener('click', function () { show(index - 1, true); start(); });
    if (nextButton) nextButton.addEventListener('click', function () { show(index + 1, true); start(); });
    if (pauseButton) pauseButton.addEventListener('click', function () { setPaused(!paused); });
    bullets.forEach(function (bullet, position) {
      bullet.addEventListener('click', function () { show(position, true); start(); });
    });
    hero.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowLeft') { show(index - 1, true); start(); }
      if (event.key === 'ArrowRight') { show(index + 1, true); start(); }
    });
    var onMotionChange = function () {
      setPaused(reduceMotion.matches);
      if (!reduceMotion.matches && !paused) start();
    };
    if (reduceMotion.addEventListener) reduceMotion.addEventListener('change', onMotionChange);

    show(0, false);
    setPaused(reduceMotion.matches);
  }
})();
