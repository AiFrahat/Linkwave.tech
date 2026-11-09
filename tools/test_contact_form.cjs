/* Integration tests for the secure contact form (local mock server). */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8796/';
const OUT = process.env.OUT_DIR || path.join(process.cwd(), 'OUTPUT', 'AUDIT', 'impl');
const failures = [];
const results = {};

const EN_ACCEPTED = 'accepted for delivery';
const EN_SENT_ERR = 'Sending failed';
const AR_ACCEPTED = 'تم قبول رسالتك';
const AR_INVALID = 'راجع الحقول';
const AR_SENT_ERR = 'تعذّر الإرسال';

async function reset() {
  await fetch(BASE + '__reset');
}
async function stats() {
  return (await fetch(BASE + '__stats')).json();
}
function check(name, condition, detail) {
  results[name] = { pass: !!condition, detail: detail === undefined ? '' : detail };
  if (!condition) failures.push(name + (detail ? ': ' + detail : ''));
}

async function fillValid(page, overrides = {}) {
  const values = {
    name: 'Test Customer',
    email: 'customer@example.com',
    phone: '+20 100 000 0000',
    subject: 'Data center enquiry',
    message: 'We need structured cabling and rack installation for a new office.',
    ...overrides,
  };
  await page.locator('#name').fill(values.name);
  await page.locator('#email').fill(values.email);
  await page.locator('#phone').fill(values.phone);
  await page.locator('#subject').fill(values.subject);
  await page.locator('#message').fill(values.message);
}
async function waitStatus(page, text, timeout = 6000) {
  await page.waitForFunction(
    (needle) => (document.getElementById('form-status') || {}).textContent.includes(needle),
    text, { timeout }
  );
}
async function submit(page) {
  await page.locator('#quote-form button[type=submit]').click();
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* ---------- UI: valid submission ---------- */
  {
    await reset();
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await ctx.newPage();
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    const state = await page.evaluate(() => {
      const btn = document.querySelector('#quote-form button[type=submit]');
      return {
        fields: ['name', 'email', 'phone', 'subject', 'message'].every((id) => !!document.getElementById(id)),
        honeypot: !!document.querySelector('input[name="_gotcha"]'),
        submitDisabled: btn.disabled,
        submitLabel: btn.textContent.trim(),
        statusLive: document.getElementById('form-status').getAttribute('aria-live'),
      };
    });
    check('fields-present', state.fields);
    check('honeypot-present', state.honeypot);
    check('submit-enabled-with-endpoint', state.submitDisabled === false, 'disabled=' + state.submitDisabled);
    check('submit-label-send', /send message/i.test(state.submitLabel), state.submitLabel);
    check('status-live-region', state.statusLive === 'polite');
    await fillValid(page);
    await submit(page);
    await waitStatus(page, EN_ACCEPTED);
    await page.waitForTimeout(300);
    const after = { stats: await stats(), name: await page.locator('#name').inputValue() };
    check('valid-submit-accepted', after.stats.valid === 1, JSON.stringify(after.stats));
    check('valid-submit-resets-form', after.name === '');
    check('success-not-claimed-as-receipt', !/received|تم الاستلام/i.test(await page.locator('#form-status').textContent()));
    await ctx.close();
  }

  /* ---------- UI: required, email, phone, oversized ---------- */
  {
    await reset();
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await ctx.newPage();
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(250);
    await submit(page);
    await page.waitForTimeout(300);
    const errors = await page.evaluate(() => ({
      invalid: [...document.querySelectorAll('[aria-invalid=true]')].map((el) => el.id),
      status: document.getElementById('form-status').textContent,
    }));
    const st = await stats();
    check('required-errors-shown', ['name', 'email', 'subject', 'message'].every((id) => errors.invalid.includes(id)), JSON.stringify(errors));
    check('required-submit-no-request', st.requests === 0, JSON.stringify(st));
    await fillValid(page, { email: 'not-an-email', phone: 'abc' });
    await submit(page);
    await page.waitForTimeout(300);
    const fieldErrors = await page.evaluate(() => ({
      email: document.getElementById('email-error').textContent,
      phone: document.getElementById('phone-error').textContent,
    }));
    check('invalid-email-error', /valid email/i.test(fieldErrors.email), fieldErrors.email);
    check('invalid-phone-error', /valid phone/i.test(fieldErrors.phone), fieldErrors.phone);
    await page.evaluate(() => { document.getElementById('message').value = 'x'.repeat(3100); });
    await fillValid(page);
    await page.evaluate(() => { document.getElementById('message').value = 'x'.repeat(3100); });
    await submit(page);
    await page.waitForTimeout(300);
    const oversize = await page.evaluate(() => ({
      error: document.getElementById('message-error').textContent,
      invalid: document.getElementById('message').getAttribute('aria-invalid'),
    }));
    check('oversized-message-blocked', /shorten/i.test(oversize.error) && oversize.invalid === 'true', JSON.stringify(oversize));
    check('oversized-no-second-request', (await stats()).valid === 0);
    await ctx.close();
  }

  /* ---------- UI: honeypot + duplicate submit ---------- */
  {
    await reset();
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await ctx.newPage();
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(250);
    await fillValid(page);
    await page.evaluate(() => { document.querySelector('input[name="_gotcha"]').value = 'bot-filled'; });
    await submit(page);
    await waitStatus(page, EN_ACCEPTED);
    const hp = await stats();
    check('honeypot-neutral-and-not-sent', hp.requests === 0 && hp.submissions === 0, JSON.stringify(hp));
    await reset();
    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(250);
    await fillValid(page);
    await page.evaluate(() => {
      const form = document.getElementById('quote-form');
      form.requestSubmit();
      form.requestSubmit();
    });
    await page.waitForTimeout(1200);
    const dup = await stats();
    check('duplicate-submission-prevented', dup.valid === 1, JSON.stringify(dup));
    await ctx.close();
  }

  /* ---------- UI: provider error + network abort ---------- */
  for (const scenario of ['error', 'abort']) {
    await reset();
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await ctx.addCookies([{ name: 'scenario', value: scenario, url: BASE }]);
    const page = await ctx.newPage();
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(250);
    await fillValid(page);
    await submit(page);
    await waitStatus(page, EN_SENT_ERR, 8000);
    const st = await stats();
    check('provider-' + scenario + '-error-handled', st.submissions === 0, JSON.stringify(st));
    await ctx.close();
  }

  /* ---------- UI: rate limit ---------- */
  {
    await reset();
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await ctx.newPage();
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(250);
    for (let attempt = 0; attempt < 3; attempt++) {
      await fillValid(page, { subject: 'Attempt ' + (attempt + 1) });
      await submit(page);
      await page.waitForTimeout(500);
    }
    await waitStatus(page, 'Too many attempts', 5000);
    const st = await stats();
    check('rate-limit-message', /too many attempts/i.test(await page.locator('#form-status').textContent()));
    check('rate-limit-server-counted', st.rate >= 1, JSON.stringify(st));
    await ctx.close();
  }

  /* ---------- UI: Arabic locale ---------- */
  {
    await reset();
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    await page.goto(BASE + 'ar/it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(250);
    await submit(page);
    await waitStatus(page, AR_INVALID);
    const arabicInvalidText = await page.locator('#form-status').textContent();
    await fillValid(page, { name: 'عميل تجريبي', subject: 'استفسار شبكات', message: 'محتاج تركيب شبكة لمكتب جديد.' });
    await submit(page);
    await waitStatus(page, AR_ACCEPTED);
    const st = await stats();
    check('arabic-invalid-message', /راجع الحقول/.test(arabicInvalidText), arabicInvalidText);
    check('arabic-valid-accepted', st.valid === 1, JSON.stringify(st));
    const a11y = await page.evaluate(() => {
      const btn = document.querySelector('#quote-form button[type=submit]');
      const hp = document.querySelector('.lw-hp');
      return {
        dir: document.documentElement.dir,
        labelled: ['name', 'email', 'phone', 'subject', 'message'].every((id) => !!document.querySelector('label[for="' + id + '"]')),
        buttonHeight: Math.round(btn.getBoundingClientRect().height),
        honeypotHidden: hp && hp.getAttribute('aria-hidden') === 'true',
      };
    });
    check('arabic-rtl', a11y.dir === 'rtl');
    check('all-fields-labelled', a11y.labelled);
    check('submit-touch-size', a11y.buttonHeight >= 44, 'height=' + a11y.buttonHeight);
    check('honeypot-aria-hidden', !!a11y.honeypotHidden);
    await ctx.close();
  }

  /* ---------- server contract (direct requests) ---------- */
  {
    await reset();
    const post = async (body, headers = {}) => {
      const res = await fetch(BASE + '__form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...headers },
        body: typeof body === 'string' ? body : JSON.stringify(body),
      });
      return { status: res.status, json: await res.json().catch(() => null) };
    };
    const valid = {
      name: 'Contract Test', email: 'test@example.com', phone: '+20 100 000 0000',
      subject: 'Server validation', message: 'Checking server-side validation.',
    };
    const postFresh = async (body) => { await reset(); return post(body); };
    let r = await postFresh({ ...valid, subject: '' });
    check('server-requires-subject', r.status === 400 && r.json.errors[0].field === 'subject', JSON.stringify(r));
    r = await postFresh({ ...valid, email: 'bad' });
    check('server-rejects-bad-email', r.status === 400, JSON.stringify(r));
    r = await postFresh({ ...valid, message: 'x'.repeat(4000) });
    check('server-rejects-oversized', r.status === 400, JSON.stringify(r));
    r = await postFresh({ ...valid, subject: 'Hello\r\nBcc: attacker@example.com' });
    check('server-rejects-header-injection', r.status === 400, JSON.stringify(r));
    r = await postFresh({ ...valid, _gotcha: 'bot' });
    check('server-rejects-honeypot', r.status === 400, JSON.stringify(r));
    r = await postFresh('{not json');
    check('server-rejects-invalid-json', r.status === 400, JSON.stringify(r));
    r = await postFresh(valid);
    check('server-accepts-valid', r.status === 200 && r.json.ok === true && r.json.accepted === true, JSON.stringify(r));
    const get = await fetch(BASE + '__form');
    check('server-rejects-get', get.status >= 400, 'status=' + get.status);
    // rate limit: the mock allows 2 requests / 10s per IP
    const r1 = await post(valid);
    const r2 = await post(valid);
    check('server-rate-limit', [r1.status, r2.status].includes(429), JSON.stringify([r1.status, r2.status]));
    await reset();
  }

  /* ---------- regression basics ---------- */
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await ctx.newPage();
    await page.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
    await page.waitForTimeout(300);
    const info = await page.evaluate(() => ({
      h1: document.querySelectorAll('h1').length,
      whatsapp: document.querySelectorAll('.lw-whatsapp-float').length,
      phone: !!document.querySelector('a[href^="tel:+201276668018"]'),
      attribution: /html\.design/.test(document.body.innerHTML),
      csp: !!document.querySelector('meta[http-equiv="Content-Security-Policy"]'),
      overflow: document.documentElement.scrollWidth > innerWidth + 1,
    }));
    check('regression-h1', info.h1 === 1);
    check('regression-whatsapp', info.whatsapp === 1);
    check('regression-phone', info.phone);
    check('regression-attribution', info.attribution);
    check('regression-csp', info.csp);
    check('regression-no-overflow', !info.overflow);
    await ctx.close();
  }

  await browser.close();
  const summary = { tests: Object.keys(results).length, passed: Object.keys(results).filter((k) => results[k].pass).length, failures: failures.length, results, failureList: failures };
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, 'contact-form-tests.json'), JSON.stringify(summary, null, 1));
  console.log(JSON.stringify({ tests: summary.tests, passed: summary.passed, failures: summary.failures, failureList: failures.slice(0, 20) }, null, 1));
  process.exit(failures.length ? 1 : 0);
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
