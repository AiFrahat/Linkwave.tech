/* Release pre-check: contact form must be disabled (EN + AR) while the rest of the
   approved site remains intact. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8793/';
const OUT = process.env.OUT_DIR || path.join(process.cwd(), 'OUTPUT', 'AUDIT', 'impl');
const failures = [];
const results = {};
function check(name, ok, detail) {
  results[name] = { pass: !!ok, detail: detail === undefined ? '' : detail };
  if (!ok) failures.push(name + (detail ? ': ' + detail : ''));
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  for (const [page, lang] of [['it_contact.html', 'en'], ['ar/it_contact.html', 'ar']]) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const p = await ctx.newPage();
    const external = [];
    p.on('request', (r) => { if (!r.url().startsWith(BASE)) external.push(r.url()); });
    await p.goto(BASE + page, { waitUntil: 'load' });
    await p.waitForTimeout(500);
    const info = await p.evaluate(() => {
      const form = document.getElementById('quote-form');
      const submit = form.querySelector('button[type="submit"]');
      const notice = document.getElementById('contact-notice');
      return {
        formExists: !!form,
        submitDisabled: submit.disabled,
        submitText: submit.textContent.trim(),
        noticeText: notice ? notice.textContent.trim() : '',
        config: window.LINKWAVE_CONFIG || {},
        emailLinks: [...document.querySelectorAll('a[href="mailto:info@linkwave.tech"]')].length,
        waLinks: [...document.querySelectorAll('a[href^="https://wa.me/201276668018"]')].length,
        waFloat: (document.querySelector('.lw-whatsapp-float') || {}).getAttribute ? document.querySelector('.lw-whatsapp-float').getAttribute('href') : null,
        reserved: ['_subject', '_template', '_captcha', '_honey'].every((n) => !!form.querySelector('[name="' + n + '"]')),
        fields: ['name', 'email', 'phone', 'subject', 'message'].every((id) => !!document.getElementById(id)),
        overflow: document.documentElement.scrollWidth > innerWidth + 1,
      };
    });
    check(lang + '-form-exists', info.formExists);
    check(lang + '-submit-disabled', info.submitDisabled === true, 'disabled=' + info.submitDisabled);
    check(lang + '-notice-clear', lang === 'en' ? /not available yet/i.test(info.noticeText) : /غير متاح/.test(info.noticeText), info.noticeText.slice(0, 120));
    check(lang + '-endpoint-disabled', info.config.formEndpoint === null, String(info.config.formEndpoint));
    check(lang + '-pending-endpoint-preserved', info.config.formEndpointPending === 'https://formsubmit.co/ajax/info@linkwave.tech');
    check(lang + '-email-link-active', info.emailLinks >= 1, 'count=' + info.emailLinks);
    check(lang + '-whatsapp-link-active', info.waLinks >= 1 && String(info.waFloat).includes('wa.me/201276668018'));
    check(lang + '-formsubmit-code-preserved', info.reserved, 'hidden fields=' + info.reserved);
    check(lang + '-fields-preserved', info.fields);
    check(lang + '-no-overflow', !info.overflow);
    // Attempt to submit programmatically: must not produce a network request.
    await p.evaluate(() => { document.getElementById('quote-form').requestSubmit(); });
    await p.waitForTimeout(700);
    const status = await p.locator('#form-status').textContent();
    check(lang + '-no-submission-request', external.length === 0, JSON.stringify(external.slice(0, 3)));
    check(lang + '-no-success-message', !/accepted for delivery|تم قبول رسالتك/i.test(status), status);
    await ctx.close();
  }

  // Site integrity on the same build
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const p = await ctx.newPage();
    await p.goto(BASE + 'index.html', { waitUntil: 'load' });
    await p.waitForTimeout(500);
    const home = await p.evaluate(() => ({
      slides: document.querySelectorAll('.lw-slide').length,
      bullets: document.querySelectorAll('.lw-bullet').length,
      rows: document.querySelectorAll('.lw-service-row').length,
      wa: document.querySelectorAll('.lw-whatsapp-float').length,
      attribution: /AiFrahat\.com/.test(document.body.innerHTML),
      h1: document.querySelectorAll('h1').length,
    }));
    check('home-hero-6', home.slides === 6 && home.bullets === 6, JSON.stringify(home));
    check('home-ten-rows', home.rows === 10, 'rows=' + home.rows);
    check('home-whatsapp', home.wa === 1);
    check('home-attribution', home.attribution);
    check('home-single-h1', home.h1 === 1);
    await p.goto(BASE + 'ar/index.html', { waitUntil: 'load' });
    await p.waitForTimeout(300);
    check('arabic-home-rtl', (await p.evaluate(() => document.documentElement.dir)) === 'rtl');
    await ctx.close();
  }

  await browser.close();
  const summary = { tests: Object.keys(results).length, passed: Object.keys(results).filter((k) => results[k].pass).length, failures: failures.length, results, failureList: failures };
  fs.mkdirSync(OUT, { recursive: true });
  fs.writeFileSync(path.join(OUT, 'release-form-disabled-check.json'), JSON.stringify(summary, null, 1));
  console.log(JSON.stringify({ tests: summary.tests, passed: summary.passed, failures: summary.failures, failureList: failures.slice(0, 20) }, null, 1));
  process.exit(failures.length ? 1 : 0);
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
