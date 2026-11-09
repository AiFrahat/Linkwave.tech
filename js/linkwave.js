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

  /* 4. Enquiry form: accessible validation + secure JSON submission to a configured
   server-side endpoint. No success is shown unless the endpoint explicitly accepts. */
  var form = document.getElementById('quote-form');
  if (form) {
    var FIELD_IDS = ['name', 'email', 'phone', 'subject', 'message'];
    var fields = FIELD_IDS.map(function (id) { return document.getElementById(id); }).filter(Boolean);
    var statusEl = document.getElementById('form-status');
    var submitButton = form.querySelector('button[type="submit"]');
    var submitLabel = submitButton ? submitButton.querySelector('[data-i18n], span') : null;
    var validateButton = document.getElementById('validate-form');
    var honey = form.querySelector('input[name="_gotcha"]');
    var endpoint = '';
    var endpointConfig = typeof config.formEndpoint === 'string' ? config.formEndpoint.trim() : '';
    if (/^https?:\/\//.test(endpointConfig) || /^\/[^\/]/.test(endpointConfig)) {
      endpoint = endpointConfig;
    }
    var cooldownMs = Number(config.formCooldownMs) > 0 ? Number(config.formCooldownMs) : 30000;
    var validated = false;
    var submitting = false;
    var cooldownUntil = 0;
    var requestTimer = null;

    var setStatus = function (message) {
      if (statusEl) statusEl.textContent = message || '';
    };

    var setSubmitEnabled = function (enabled) {
      if (!submitButton) return;
      submitButton.disabled = !enabled;
      submitButton.setAttribute('aria-busy', 'false');
    };

    var setSubmitLabel = function (key, fallback) {
      if (submitLabel) submitLabel.textContent = t(key, fallback);
    };

    var setBusy = function (busy) {
      submitting = busy;
      if (submitButton) {
        submitButton.setAttribute('aria-busy', busy ? 'true' : 'false');
        submitButton.disabled = busy;
      }
      if (busy) setSubmitLabel('sending', 'Sending…');
      else setSubmitLabel('send', 'Send message');
    };

    var fieldMessage = function (field) {
      var value = (field.value || '').trim();
      if (field.required && !value) return t('required', 'Please complete this field.');
      if (field.type === 'email' && value && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) {
        return t('badEmail', 'Enter a valid email address.');
      }
      if (field.type === 'tel' && value && !/^[+()0-9\s-]{7,30}$/.test(value)) {
        return t('phoneBad', 'Enter a valid phone number.');
      }
      if (field.maxLength > 0 && field.value.length > field.maxLength) {
        return t('tooLong', 'Please shorten this entry.');
      }
      return '';
    };

    var showFieldError = function (field, message) {
      field.setAttribute('aria-invalid', message ? 'true' : 'false');
      var target = document.getElementById(field.id + '-error');
      if (target) target.textContent = message;
    };

    var validate = function (focusFirst) {
      var firstInvalid = null;
      fields.forEach(function (field) {
        var message = fieldMessage(field);
        showFieldError(field, message);
        if (message && !firstInvalid) firstInvalid = field;
      });
      if (firstInvalid) {
        setStatus(t('invalid', 'Please review the highlighted fields. Nothing has been sent.'));
        if (focusFirst) firstInvalid.focus();
      } else if (!submitting) {
        setStatus(t('valid', 'Your details look valid. Submit the form to send them.'));
      }
      return firstInvalid;
    };

    var clearFieldErrors = function () {
      fields.forEach(function (field) { showFieldError(field, ''); });
    };

    var finishSuccess = function () {
      setBusy(false);
      cooldownUntil = Date.now() + cooldownMs;
      setStatus(t('accepted', 'Your message was accepted for delivery.'));
      form.reset();
      clearFieldErrors();
      validated = false;
      if (submitButton) {
        submitButton.disabled = true;
        window.setTimeout(function () {
          if (!submitting && endpoint) submitButton.disabled = false;
        }, cooldownMs);
      }
    };

    var finishError = function (message) {
      setBusy(false);
      setStatus(message);
      if (submitButton) submitButton.disabled = false;
    };

    var parseErrors = function (data) {
      if (!data || !Array.isArray(data.errors) || !data.errors.length) return null;
      var error = data.errors[0];
      if (!error || typeof error !== 'object') return null;
      return {
        field: typeof error.field === 'string' ? error.field : '',
        code: typeof error.code === 'string' ? error.code : ''
      };
    };

    var submitRequest = function () {
      if (!endpoint) return;
      if (submitting) return;
      if (Date.now() < cooldownUntil) {
        setStatus(t('rateLimited', 'Too many attempts. Please wait a minute and try again.'));
        return;
      }
      if (honey && honey.value.trim()) {
        /* Honeypot: behave neutrally for bots, never transmit the message. */
        finishSuccess();
        return;
      }
      var payload = {};
      fields.forEach(function (field) {
        payload[field.name] = (field.value || '').trim();
      });
      payload.language = lang;
      payload.page = window.location.pathname;
      setBusy(true);
      setStatus(t('sending', 'Sending…'));
      var controller = typeof AbortController === 'function' ? new AbortController() : null;
      requestTimer = window.setTimeout(function () {
        if (controller) controller.abort();
      }, 20000);
      window.fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload),
        signal: controller ? controller.signal : undefined
      }).then(function (response) {
        return response.text().then(function (text) {
          var data = null;
          try { data = text ? JSON.parse(text) : null; } catch (error) { data = null; }
          if (response.status === 429) {
            var rate = { isRate: true };
            throw rate;
          }
          if (!response.ok) {
            var provider = { fieldError: parseErrors(data) };
            throw provider;
          }
          if (!data || data.ok !== true) throw { isProvider: true };
          return data;
        });
      }).then(function () {
        window.clearTimeout(requestTimer);
        requestTimer = null;
        finishSuccess();
      }).catch(function (error) {
        window.clearTimeout(requestTimer);
        requestTimer = null;
        if (error && error.isRate) {
          finishError(t('rateLimited', 'Too many attempts. Please wait a minute and try again.'));
        } else if (error && error.fieldError) {
          var field = document.getElementById(error.fieldError.field);
          var codeMap = {
            required: 'required', badEmail: 'badEmail', badPhone: 'phoneBad', tooLong: 'tooLong'
          };
          if (field && codeMap[error.fieldError.code]) {
            showFieldError(field, t(codeMap[error.fieldError.code], 'Please check this field.'));
            setStatus(t('invalid', 'Please review the highlighted fields. Nothing has been sent.'));
            finishError(statusEl ? statusEl.textContent : '');
          } else {
            finishError(t('sentErr', 'Sending failed. Please try again or use the phone/WhatsApp.'));
          }
        } else {
          finishError(t('sentErr', 'Sending failed. Please try again or use the phone/WhatsApp.'));
        }
      });
    };

    if (endpoint && submitButton) {
      submitButton.disabled = false;
      setSubmitLabel('send', 'Send message');
    }
    var onSubmit = function (event) {
      event.preventDefault();
      validated = true;
      if (validate(true)) return;
      submitRequest();
    };
    form.addEventListener('submit', onSubmit);
    if (validateButton) {
      validateButton.addEventListener('click', function () {
        validated = true;
        validate(true);
      });
    }
    form.addEventListener('input', function () {
      if (validated && !submitting) validate(false);
    });
    form.addEventListener('change', function () {
      if (validated && !submitting) validate(false);
    });
  }

/* 5. Six-slide accessible hero: fade + slow zoom, deferred image hydration,
   autoplay with pause-on-hover/focus, keyboard controls and reduced-motion support. */
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
    var userPaused = false;
    var hoverPaused = false;

    var hydrate = function (position) {
      var slide = slides[position];
      if (!slide) return;
      var image = slide.querySelector('.lw-slide-img');
      if (!image || image.getAttribute('data-hydrated') === '1') return;
      if (image.getAttribute('data-src')) image.src = image.getAttribute('data-src');
      if (image.getAttribute('data-srcset')) image.srcset = image.getAttribute('data-srcset');
      image.setAttribute('data-hydrated', '1');
    };

    var shouldRun = function () {
      return !userPaused && !hoverPaused && !reduceMotion.matches;
    };

    var announce = function () {
      if (statusNode) statusNode.textContent = (index + 1) + ' / ' + slides.length;
    };

    var show = function (next, shouldAnnounce) {
      index = (next + slides.length) % slides.length;
      hydrate(index);
      hydrate((index + 1) % slides.length);
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
      if (!shouldRun()) return;
      timer = window.setInterval(function () { show(index + 1, true); }, 7000);
    };

    var updatePauseLabel = function () {
      if (!pauseButton) return;
      var effectivePaused = userPaused || reduceMotion.matches;
      pauseButton.setAttribute('aria-pressed', String(effectivePaused));
      var label = pauseButton.querySelector('[data-label]');
      if (label) label.textContent = t(effectivePaused ? 'play' : 'pause');
    };

    var setUserPaused = function (value) {
      userPaused = value;
      hero.classList.toggle('is-paused', userPaused || reduceMotion.matches);
      updatePauseLabel();
      if (shouldRun()) start(); else stop();
    };

    if (prevButton) prevButton.addEventListener('click', function () { show(index - 1, true); start(); });
    if (nextButton) nextButton.addEventListener('click', function () { show(index + 1, true); start(); });
    if (pauseButton) pauseButton.addEventListener('click', function () { setUserPaused(!userPaused); });
    bullets.forEach(function (bullet, position) {
      bullet.addEventListener('click', function () { show(position, true); start(); });
    });
    hero.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowLeft') { show(index - 1, true); start(); }
      if (event.key === 'ArrowRight') { show(index + 1, true); start(); }
    });

    hero.addEventListener('mouseenter', function () { hoverPaused = true; stop(); });
    hero.addEventListener('mouseleave', function () { hoverPaused = false; if (shouldRun()) start(); });
    hero.addEventListener('focusin', function () { hoverPaused = true; stop(); });
    hero.addEventListener('focusout', function (event) {
      if (!hero.contains(event.relatedTarget)) {
        hoverPaused = false;
        if (shouldRun()) start();
      }
    });

    var onMotionChange = function () {
      hero.classList.toggle('is-paused', reduceMotion.matches || userPaused);
      updatePauseLabel();
      if (reduceMotion.matches) stop();
      else if (shouldRun()) start();
    };
    if (reduceMotion.addEventListener) reduceMotion.addEventListener('change', onMotionChange);

    show(0, false);
    hydrate(1);
    if (reduceMotion.matches) {
      userPaused = true;
      hero.classList.add('is-paused');
    }
    updatePauseLabel();
    start();

    window.addEventListener('load', function () {
      window.setTimeout(function () {
        slides.forEach(function (item, position) { hydrate(position); });
      }, 1500);
    });
  }
})();
