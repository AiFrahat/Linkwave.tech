/* Integration tests for the FormSubmit-based contact form (network fully mocked). */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8793/';
const OUT = process.env.OUT_DIR || path.join(process.cwd(), 'OUTPUT', 'AUDIT', 'impl');
const FORM_ORIGIN = 'https://formsubmit.co';
const failures = [];
const results = {};

function check(name, condition, detail) {
  results[name] = { pass: !!condition, detail: detail === undefined ? '' : detail };
  if (!condition) failures.push(name + (detail ? ': ' + detail : ''));
}

async function newPage(browser, options = {}) {
  const ctx = await browser.newContext({ viewport: options.viewport || { width: 1440, height: 1000 } });
  const requests = [];
  let mode = options.mode || 'success';
  await ctx.route(FORM_ORIGIN + '/**', async (route) => {
    const request = route.request();
    requests.push({
      url: request.url(),
      method: request.method(),
      headers: request.headers(),
      body: request.postData(),
    });
    if (mode === 'abort') return route.abort();
    if (mode === 'error') {
      return route.fulfill({ status: 500, contentType: 'application/json',
        headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ success: 'false' }) });
    }
    if (mode === 'rate') {
      return route.fulfill({ status: 429, contentType: 'application/json',
        headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ success: 'false' }) });
    }
    if (mode === 'rejected') {
      return route.fulfill({ status: 200, contentType: 'application/json',
        headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ success: 'false', message: 'error' }) });
    }
    return route.fulfill({ status: 200, contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*', 'access-control-allow-headers': 'Content-Type, Accept' },
      body: JSON.stringify({ success: 'true', message: 'Form submitted successfully' }) });
  });
  const page = await ctx.newPage();
  return { ctx, page, requests, setMode: (m) => { mode = m; } };
}

async function fillValid(page, overrides = {}) {
  const values = {
    name: 'Test Customer', email: 'customer@example.com', phone: '+20 100 000 0000',
    subject: 'Data center enquiry', message: 'We need structured cabling for a new office.',
    ...overrides,
  };
  await page.locator('#name').fill(values.name);
  await page.locator('#email').fill(values.email);
  await page.locator('#phone').fill(values.phone);
  await page.locator('#subject').fill(values.subject);
  await page.locator('#message').fill(values.message);
}
const submit = (page) => page.locator('#quote-form button[type=submit]').click();
async function waitStatus(page, text, timeout = 8000) {
  await page.waitForFunction((needle) => (document.getElementById('form-status') || {}).textContent.includes(needle),
    text, { timeout });
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* 1. structure */
  {
    const { ctx, page } = await newPage(browser);
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(350);
    const s = await page.evaluate(() => ({
      fields: ['name', 'email', 'phone', 'subject', 'message'].every((id) => !!document.getElementById(id)),
      honey: !!document.querySelector('input[name="_honey"]'),
      reserved: ['_subject', '_template', '_captcha'].every((n) => !!document.querySelector('input[name="' + n + '"]')),
      submitDisabled: document.querySelector('#quote-form button[type=submit]').disabled,
      label: document.querySelector('#quote-form button[type=submit]').textContent.trim(),
      statusLive: document.getElementById('form-status').getAttribute('aria-live'),
    }));
    check('structure-fields', s.fields);
    check('structure-honeypot', s.honey);
    check('structure-formsubmit-reserved-fields', s.reserved);
    check('structure-submit-enabled', s.submitDisabled === false);
    check('structure-submit-label', /send/i.test(s.label), s.label);
    check('structure-status-live', s.statusLive === 'polite');
    await ctx.close();
  }

  /* 2. valid submission */
  {
    const { ctx, page, requests } = await newPage(browser);
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await fillValid(page);
    await submit(page);
    await waitStatus(page, 'accepted for delivery');
    await page.waitForTimeout(300);
    const body = requests.length ? JSON.parse(requests[0].body || '{}') : {};
    check('valid-single-request', requests.length === 1, 'requests=' + requests.length);
    check('valid-endpoint', requests[0] && requests[0].url === FORM_ORIGIN + '/ajax/info@linkwave.tech', requests[0] && requests[0].url);
    check('valid-method', requests[0] && requests[0].method === 'POST');
    check('valid-fields', body.name === 'Test Customer' && body.email === 'customer@example.com' &&
      body.phone === '+20 100 000 0000' && body.subject === 'Data center enquiry' && !!body.message);
    check('valid-reserved', body._subject && body._template === 'table' && body._captcha === 'false' && body._honey === '');
    check('valid-language-page', body.language === 'en' && typeof body.page === 'string' && body.page.includes('it_contact'));
    check('valid-form-reset', (await page.locator('#name').inputValue()) === '');
    check('valid-accepted-not-received', !/received|تم الاستلام/i.test(await page.locator('#form-status').textContent()));
    await ctx.close();
  }

  /* 3. client validation, no request */
  {
    const { ctx, page, requests } = await newPage(browser);
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await submit(page);
    await page.waitForTimeout(300);
    const invalid = await page.evaluate(() => [...document.querySelectorAll('[aria-invalid=true]')].map((e) => e.id));
    check('validation-required', ['name', 'email', 'subject', 'message'].every((id) => invalid.includes(id)), JSON.stringify(invalid));
    await fillValid(page, { email: 'bad', phone: 'abc' });
    await submit(page);
    await page.waitForTimeout(300);
    const err = await page.evaluate(() => ({
      email: document.getElementById('email-error').textContent,
      phone: document.getElementById('phone-error').textContent,
    }));
    check('validation-email', /valid email/i.test(err.email), err.email);
    check('validation-phone', /valid phone/i.test(err.phone), err.phone);
    await fillValid(page);
    await page.evaluate(() => { document.getElementById('message').value = 'x'.repeat(3100); });
    await submit(page);
    await page.waitForTimeout(250);
    check('validation-oversized', /shorten/i.test(await page.locator('#message-error').textContent()));
    check('validation-no-requests', requests.length === 0, 'requests=' + requests.length);
    await ctx.close();
  }

  /* 4. honeypot + duplicate prevention */
  {
    const { ctx, page, requests } = await newPage(browser);
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await fillValid(page);
    await page.evaluate(() => { document.querySelector('input[name="_honey"]').value = 'bot'; });
    await submit(page);
    await waitStatus(page, 'accepted for delivery');
    check('honeypot-no-request', requests.length === 0, 'requests=' + requests.length);
    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(300);
    await fillValid(page);
    await page.evaluate(() => { document.getElementById('quote-form').requestSubmit(); document.getElementById('quote-form').requestSubmit(); });
    await page.waitForTimeout(1500);
    check('duplicate-one-request', requests.length === 1, 'requests=' + requests.length);
    await ctx.close();
  }

  /* 5. provider failure modes */
  for (const [mode, expected] of [['error', 'Sending failed'], ['abort', 'Sending failed'], ['rate', 'Too many attempts'], ['rejected', 'Sending failed']]) {
    const { ctx, page, requests } = await newPage(browser, { mode });
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await fillValid(page);
    await submit(page);
    await waitStatus(page, expected);
    check('provider-' + mode + '-no-false-success', !/accepted for delivery/i.test(await page.locator('#form-status').textContent()));
    await ctx.close();
  }

  /* 6. Arabic locale */
  {
    const { ctx, page, requests } = await newPage(browser, { viewport: { width: 390, height: 844 } });
    await page.goto(BASE + 'ar/it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await submit(page);
    const invalidText = await page.locator('#form-status').textContent();
    check('arabic-validation-message', /راجع الحقول/.test(invalidText), invalidText);
    await fillValid(page, { name: 'عميل تجريبي', subject: 'استفسار شبكات', message: 'محتاج تركيب شبكة لمكتب.' });
    await submit(page);
    await waitStatus(page, 'تم قبول رسالتك');
    check('arabic-accepted-message', /تم قبول رسالتك/.test(await page.locator('#form-status').textContent()));
    check('arabic-single-request', requests.length === 1);
    const a11y = await page.evaluate(() => {
      const btn = document.querySelector('#quote-form button[type=submit]');
      const hp = document.querySelector('.lw-hp');
      return {
        dir: document.documentElement.dir,
        labelled: ['name', 'email', 'phone', 'subject', 'message'].every((id) => !!document.querySelector('label[for="' + id + '"]')),
        height: Math.round(btn.getBoundingClientRect().height),
        hpHidden: hp && hp.getAttribute('aria-hidden') === 'true',
        noOverflow: document.documentElement.scrollWidth <= innerWidth + 1,
      };
    });
    check('arabic-rtl', a11y.dir === 'rtl');
    check('a11y-all-labelled', a11y.labelled);
    check('a11y-touch-size', a11y.height >= 44, 'height=' + a11y.height);
    check('a11y-honeypot-hidden', !!a11y.hpHidden);
    check('a11y-no-overflow', a11y.noOverflow);
    await ctx.close();
  }

  /* 7. regression basics */
  {
    const { ctx, page } = await newPage(browser);
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    const info = await page.evaluate(() => ({
      h1: document.querySelectorAll('h1').length,
      whatsapp: document.querySelectorAll('.lw-whatsapp-float').length,
      phone: !!document.querySelector('a[href^="tel:+201276668018"]'),
      email: !!document.querySelector('a[href="mailto:info@linkwave.tech"]'),
      attribution: /AiFrahat\.com/.test(document.body.innerHTML),
      csp: !!document.querySelector('meta[http-equiv="Content-Security-Policy"]'),
      formActionMissing: !document.getElementById('quote-form').getAttribute('action'),
    }));
    check('regression-h1', info.h1 === 1);
    check('regression-whatsapp', info.whatsapp === 1);
    check('regression-phone', info.phone);
    check('regression-email', info.email);
    check('regression-attribution', info.attribution);
    check('regression-csp', info.csp);
    check('regression-no-native-action', info.formActionMissing);
    await ctx.close();
  }

  await browser.close();
  const summary = { tests: Object.keys(results).length, passed: Object.keys(results).filter((k) => results[k].pass).length, failures: failures.length, results, failureList: failures };
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, 'contact-form-tests.json'), JSON.stringify(summary, null, 1));
  console.log(JSON.stringify({ tests: summary.tests, passed: summary.passed, failures: summary.failures, failureList: failures.slice(0, 20) }, null, 1));
  process.exit(failures.length ? 1 : 0);
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
