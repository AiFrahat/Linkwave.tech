/* Final polish verification: 6-slide hero, WhatsApp float, real service images,
   ten-service preservation, EN/AR/RTL, a11y basics, links, sitemap. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ROOT = process.env.SITE_ROOT || path.resolve(__dirname, '..');
const BASE = process.env.BASE_URL || 'http://127.0.0.1:8793/';
const OUT = process.env.OUT_DIR || path.join(os.tmpdir(), 'linkwave-verify');
fs.mkdirSync(OUT, { recursive: true });

const EN_PAGES = [
  'index.html', 'it_about.html', 'it_service.html', 'industries.html', 'it_contact.html',
  'service-telecom.html', 'service-network.html', 'service-datacenter.html', 'service-voice.html',
  'service-security.html', 'service-ftth.html',
  'business-home.html',
  'service-business-it.html', 'service-home-network.html', 'service-smart-home.html', 'service-home-security.html',
  'privacy.html', 'terms.html',
];
const AR_PAGES = EN_PAGES.map((p) => 'ar/' + p);
const NEW_PAGES = [
  'business-home.html', 'service-business-it.html', 'service-home-network.html',
  'service-smart-home.html', 'service-home-security.html',
];
const HERO_CTA_ROUTES = [
  'service-telecom.html', 'service-datacenter.html', 'service-voice.html',
  'service-security.html', 'service-business-it.html', 'service-home-network.html',
];
const WA_HREF = 'https://wa.me/201276668018';
const WA_LABEL = {
  en: 'Contact Linkwave on WhatsApp',
  ar: 'تواصل مع لينك ويف عبر واتساب',
};

function dict() {
  const raw = fs.readFileSync(path.join(ROOT, 'js', 'content.js'), 'utf8');
  const i = raw.indexOf('=');
  return JSON.parse(raw.slice(i + 1).trim().replace(/;$/, ''));
}

function staticChecks() {
  const failures = [];
  const pages = [...EN_PAGES, ...AR_PAGES];
  for (const rel of pages) {
    const abs = path.join(ROOT, rel);
    if (!fs.existsSync(abs)) { failures.push('missing page file: ' + rel); continue; }
    const html = fs.readFileSync(abs, 'utf8');
    const dir = path.dirname(abs);
    if (!/AiFrahat\.com/.test(html)) failures.push('AiFrahat.com attribution missing: ' + rel);
    if (!/© 2018/.test(html)) failures.push('2018 copyright year missing: ' + rel);
    if (!/business-home\.html/.test(html)) failures.push('business nav link missing: ' + rel);
    if ((html.match(/lw-call-float/g) || []).length !== 1) failures.push('call button count != 1: ' + rel);
    if (!html.includes('href="tel:+201229030333"')) failures.push('call tel link missing: ' + rel);
    if (!html.includes('lw-call-float') || !html.includes('01229030333')) failures.push('call button label/number missing: ' + rel);
    if (!html.includes(WA_HREF)) failures.push('WhatsApp link missing: ' + rel);
    if ((html.match(/lw-whatsapp-float/g) || []).length !== 1) failures.push('WhatsApp button count != 1: ' + rel);
    if (/LOCAL PREVIEW PLACEHOLDER|Placeholder image/i.test(html)) failures.push('placeholder wording remains: ' + rel);
    if (rel === 'index.html' || rel === 'ar/index.html') {
      if ((html.match(/class="lw-slide[ "]/g) || []).length !== 6) failures.push('hero slide count != 6: ' + rel);
      if ((html.match(/lw-hero-cta-btn/g) || []).length !== 6) failures.push('hero CTA count != 6: ' + rel);
    }
    const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
    const dup = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))];
    if (dup.length) failures.push('duplicate ids in ' + rel + ': ' + dup.slice(0, 4).join(','));
    for (const attr of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
      const url = attr[1];
      if (!url || /^(https?:|mailto:|tel:|data:|#|javascript:)/.test(url)) continue;
      const target = path.resolve(dir, url.split('?')[0].split('#')[0]);
      if (!fs.existsSync(target)) failures.push('broken local ref in ' + rel + ': ' + url);
    }
    for (const srcset of html.matchAll(/srcset="([^"]+)"/g)) {
      for (const part of srcset[1].split(',')) {
        const url = part.trim().split(/\s+/)[0];
        if (!url || /^(https?:|data:)/.test(url)) continue;
        const target = path.resolve(dir, url.split('?')[0]);
        if (!fs.existsSync(target)) failures.push('broken srcset in ' + rel + ': ' + url);
      }
    }
  }
  const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
  const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  if (locs.length !== 36) failures.push('sitemap loc count expected 36, got ' + locs.length);
  for (const page of NEW_PAGES) {
    if (!locs.some((u) => u.endsWith('/' + page))) failures.push('sitemap missing page: ' + page);
  }
  const data = dict();
  if (Object.keys(data.en).length !== Object.keys(data.ar).length) failures.push('dictionary parity mismatch');
  for (const key of ['bizitAlt', 'homenetAlt', 'smarthomeAlt', 'homesecAlt']) {
    if (/placeholder/i.test(data.en[key] || '') || /مؤقتة/.test(data.ar[key] || '')) {
      failures.push('placeholder alt still in dictionary: ' + key);
    }
  }
  return { failures, pageCount: pages.length, sitemapCount: locs.length, dictKeys: Object.keys(data.en).length };
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();
  const failures = [];
  const staticResult = staticChecks();
  failures.push(...staticResult.failures);
  const pages = [];

  for (const width of [1440, 390]) {
    for (const page of [...EN_PAGES, ...AR_PAGES]) {
      const lang = page.startsWith('ar/') ? 'ar' : 'en';
      const p = await ctx.newPage();
      const errors = [];
      const bad = [];
      const external = [];
      await p.addInitScript(() => {
        window.__csp = [];
        document.addEventListener('securitypolicyviolation', (e) => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));
      });
      p.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
      p.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 160)); });
      p.on('response', (r) => {
        if (!r.url().startsWith(BASE)) { external.push(r.url()); return; }
        if (r.status() >= 400) bad.push(r.status() + ' ' + r.url());
      });
      await p.setViewportSize({ width, height: 900 });
      try { await p.goto(BASE + page, { waitUntil: 'load', timeout: 45000 }); }
      catch (e) { failures.push('goto ' + page + ': ' + e.message); await p.close(); continue; }
      await p.waitForTimeout(width === 1440 ? 500 : 300);
      const info = await p.evaluate(({ lang }) => {
        const mismatch = [];
        document.querySelectorAll('[data-i18n]').forEach((el) => {
          // The contact submit label is a dynamic state (send vs unavailable); validate it in the form tests.
          if (el.closest && el.closest('#quote-form button[type=submit]')) return;
          const expected = window.LINKWAVE_CONTENT[lang][el.dataset.i18n];
          if (typeof expected === 'string' && el.textContent !== expected) mismatch.push(el.dataset.i18n + ' => ' + el.textContent.slice(0, 40));
        });
        const altMismatch = [];
        document.querySelectorAll('[data-i18n-alt]').forEach((img) => {
          const expected = window.LINKWAVE_CONTENT[lang][img.dataset.i18nAlt];
          if (typeof expected === 'string' && img.alt !== expected) altMismatch.push(img.dataset.i18nAlt);
        });
        const broken = [...document.images].filter((i) => i.complete && i.naturalWidth === 0 && i.getAttribute('src')).map((i) => i.getAttribute('src'));
        const rows = [...document.querySelectorAll('.lw-service-row')];
        const rowData = rows.map((row) => {
          const media = row.querySelector('.lw-service-row__media');
          const body = row.querySelector('.lw-service-row__body');
          return {
            id: row.id,
            number: (row.querySelector('.lw-service-row__index') || {}).textContent || '',
            mediaLeft: media ? Math.round(media.getBoundingClientRect().left) : null,
            bodyLeft: body ? Math.round(body.getBoundingClientRect().left) : null,
            mediaTop: media ? Math.round(media.getBoundingClientRect().top) : null,
            bodyTop: body ? Math.round(body.getBoundingClientRect().top) : null,
          };
        });
        const wa = document.querySelector('.lw-whatsapp-float');
        return {
          lang: document.documentElement.lang,
          dir: document.documentElement.dir,
          h1: document.querySelectorAll('h1').length,
          overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
          mismatch: mismatch.slice(0, 10),
          altMismatch: altMismatch.slice(0, 10),
          broken,
          canonical: (document.querySelector('link[rel=canonical]') || {}).href || null,
          hreflang: [...document.querySelectorAll('link[rel=alternate][hreflang]')].map((l) => l.hreflang),
          noindex: /noindex/.test((document.querySelector('meta[name=robots]') || {}).content || ''),
          businessNav: [...document.querySelectorAll('#lw-menu a')].map((a) => a.getAttribute('href')).includes('business-home.html'),
          csp: window.__csp.slice(0, 6),
          rows: rowData,
          heroSlides: document.querySelectorAll('.lw-slide').length,
          heroBullets: document.querySelectorAll('.lw-bullet').length,
          heroCtas: [...document.querySelectorAll('.lw-hero-cta-btn')].map((a) => a.getAttribute('href')),
          deferredHero: document.querySelectorAll('.lw-slide-img--deferred').length,
          firstHeroSrc: (document.querySelector('.lw-slide-img') || {}).getAttribute ? document.querySelector('.lw-slide-img').getAttribute('src') : null,
          wa: wa ? {
            count: document.querySelectorAll('.lw-whatsapp-float').length,
            href: wa.getAttribute('href'),
            target: wa.getAttribute('target'),
            rel: wa.getAttribute('rel'),
            label: wa.getAttribute('aria-label'),
          } : null,
          placeholder: /LOCAL PREVIEW PLACEHOLDER|Placeholder image/i.test(document.body.innerHTML),
        };
      }, { lang });
      const prefix = page + '@' + width;
      if (!info.wa) failures.push(prefix + ': WhatsApp button missing');
      else {
        if (info.wa.count !== 1) failures.push(prefix + ': WhatsApp button duplicated');
        if (info.wa.href !== WA_HREF) failures.push(prefix + ': WhatsApp href wrong: ' + info.wa.href);
        if (info.wa.target !== '_blank') failures.push(prefix + ': WhatsApp target missing');
        if (!/noopener/.test(info.wa.rel || '')) failures.push(prefix + ': WhatsApp rel missing noopener');
        if (info.wa.label !== WA_LABEL[lang]) failures.push(prefix + ': WhatsApp label wrong: ' + info.wa.label);
      }
      if (info.placeholder) failures.push(prefix + ': placeholder wording in rendered page');
      if (page === 'index.html' || page === 'ar/index.html') {
        if (info.heroSlides !== 6) failures.push(prefix + ': hero slides ' + info.heroSlides + ' != 6');
        if (info.heroBullets !== 6) failures.push(prefix + ': hero bullets ' + info.heroBullets + ' != 6');
        if (info.heroCtas.length !== 6) failures.push(prefix + ': hero CTAs ' + info.heroCtas.length + ' != 6');
        if (JSON.stringify(info.heroCtas) !== JSON.stringify(HERO_CTA_ROUTES)) failures.push(prefix + ': hero CTA routes mismatch ' + JSON.stringify(info.heroCtas));
        if (info.deferredHero !== 5) failures.push(prefix + ': deferred hero images ' + info.deferredHero + ' != 5');
        if (!info.firstHeroSrc) failures.push(prefix + ': first hero image has no eager src');
      }
      if (page === 'index.html' || page === 'it_service.html') {
        if (info.rows.length !== 10) failures.push(prefix + ': expected 10 rows, got ' + info.rows.length);
        const nums = info.rows.map((r) => r.number).join(',');
        if (nums !== '01,02,03,04,05,06,07,08,09,10') failures.push(prefix + ': row numbers ' + nums);
        if (width === 1440) {
          const ltr = lang === 'en';
          const first = info.rows[0] || {};
          const second = info.rows[1] || {};
          const firstOk = ltr ? first.mediaLeft < first.bodyLeft : first.mediaLeft > first.bodyLeft;
          const secondOk = ltr ? second.mediaLeft > second.bodyLeft : second.mediaLeft < second.bodyLeft;
          const same = Math.abs((first.mediaTop || 0) - (first.bodyTop || 0)) < 80
            && Math.abs((second.mediaTop || 0) - (second.bodyTop || 0)) < 80;
          if (!firstOk || !secondOk) failures.push(prefix + ': row alternation wrong');
          if (!same) failures.push(prefix + ': row media/body not on same row');
        } else {
          const stacked = await p.evaluate(() => {
            const row = document.querySelector('.lw-service-row');
            return !!row && getComputedStyle(row).gridTemplateColumns.split(' ').length === 1;
          });
          if (!stacked) failures.push(prefix + ': rows not stacked on mobile');
        }
      }
      if (!info.businessNav) failures.push(prefix + ': business nav missing');
      if (info.noindex) failures.push(prefix + ': unexpected noindex');
      if (!info.canonical || info.hreflang.length < 3) failures.push(prefix + ': canonical/hreflang incomplete');
      if (info.lang !== lang) failures.push(prefix + ': wrong lang');
      if (info.dir !== (lang === 'ar' ? 'rtl' : 'ltr')) failures.push(prefix + ': wrong dir');
      if (info.h1 !== 1) failures.push(prefix + ': h1 count ' + info.h1);
      if (info.overflow) failures.push(prefix + ': horizontal overflow');
      if (info.broken.length) failures.push(prefix + ': broken images ' + info.broken.slice(0, 3));
      if (info.mismatch.length) failures.push(prefix + ': i18n mismatch ' + info.mismatch.slice(0, 3));
      if (info.altMismatch.length) failures.push(prefix + ': alt mismatch ' + info.altMismatch.slice(0, 3));
      if (errors.length) failures.push(prefix + ': JS errors');
      if (bad.length) failures.push(prefix + ': bad responses ' + bad[0]);
      if (external.length) failures.push(prefix + ': external requests ' + external.slice(0, 2));
      if (info.csp.length) failures.push(prefix + ': CSP violations');
      pages.push({ page, width, info, errors, bad, external });
      await p.close();
    }
  }

  /* functional */
  const functional = {};
  const f = await browser.newContext();
  const p = await f.newPage();

  await p.goto(BASE + 'index.html', { waitUntil: 'load' });
  await p.waitForTimeout(500);
  functional.hero = await p.evaluate(() => ({
    slides: document.querySelectorAll('.lw-slide').length,
    bullets: document.querySelectorAll('.lw-bullet').length,
    active: (document.querySelector('.lw-slide.is-active') || {}).getAttribute ? document.querySelector('.lw-slide.is-active').getAttribute('aria-label') : null,
  }));
  const before = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  await p.locator('#lw-next').click();
  await p.waitForTimeout(300);
  const after = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  functional.next = { before, after, changed: before !== after };
  await p.locator('#lw-pause').click();
  functional.paused = await p.locator('#lw-pause').getAttribute('aria-pressed');
  await p.locator('#lw-pause').click();
  /* hover pause test on a fresh page so focus state from the pause button cannot interfere */
  await p.goto(BASE + 'index.html', { waitUntil: 'load' });
  await p.waitForTimeout(500);
  await p.locator('#lw-hero').hover();
  const hoverStart = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  await p.waitForTimeout(7800);
  const hoverEnd = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  functional.hoverPause = { hoverStart, hoverEnd, paused: hoverStart === hoverEnd };
  if (!functional.hoverPause.paused) failures.push('hover does not pause autoplay');
  await p.mouse.move(5, 5);
  await p.waitForTimeout(7800);
  const afterLeave = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  functional.hoverResume = { hoverEnd, afterLeave, resumed: hoverEnd !== afterLeave };
  if (!functional.hoverResume.resumed) failures.push('autoplay does not resume after hover leaves');
  /* keyboard: focus next button then ArrowRight */
  await p.locator('#lw-next').focus();
  const kbBefore = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  await p.keyboard.press('ArrowRight');
  await p.waitForTimeout(250);
  const kbAfter = await p.locator('.lw-slide.is-active').getAttribute('aria-label');
  functional.keyboard = { kbBefore, kbAfter, changed: kbBefore !== kbAfter };
  /* slide CTA navigation */
  await p.locator('.lw-slide.is-active .lw-hero-cta-btn').click();
  await p.waitForTimeout(400);
  functional.ctaNav = p.url();
  await p.goBack({ waitUntil: 'load' });

  await p.setViewportSize({ width: 390, height: 844 });
  await p.goto(BASE + 'index.html', { waitUntil: 'load' });
  await p.waitForTimeout(300);
  await p.locator('.lw-menu-toggle').click();
  await p.waitForTimeout(200);
  functional.menu = {
    expanded: await p.locator('.lw-menu-toggle').getAttribute('aria-expanded'),
    display: await p.locator('#lw-menu').evaluate((el) => getComputedStyle(el).display),
  };
  await p.keyboard.press('Escape');

  await p.setViewportSize({ width: 1440, height: 900 });
  await p.goto(BASE + 'it_contact.html', { waitUntil: 'load' });
  await p.waitForTimeout(300);
  await p.locator('#validate-form').click();
  await p.waitForTimeout(200);
  functional.form = {
    invalid: await p.locator('[aria-invalid=true]').count(),
    submitDisabled: await p.locator('#quote-form button[type=submit]').isDisabled(),
    fields: await p.evaluate(() => ['name', 'email', 'phone', 'subject', 'message'].every((id) => !!document.getElementById(id))),
    honeypot: await p.locator('#quote-form input[name="_honey"]').count(),
    emailChannel: await p.locator('.lw-contact-channels a[href="mailto:info@linkwave.tech"]').count(),
  };
  if (!functional.form.fields) failures.push('contact form fields missing');
  if (functional.form.honeypot !== 1) failures.push('contact honeypot missing');
  if (functional.form.emailChannel < 1) failures.push('contact email channel missing');

  await p.goto(BASE + 'business-home.html', { waitUntil: 'load' });
  await p.waitForTimeout(300);
  functional.landing = await p.evaluate(() => ({
    rows: document.querySelectorAll('.lw-service-row').length,
    title: document.title,
  }));

  for (const page of NEW_PAGES) {
    await p.goto(BASE + page, { waitUntil: 'load' });
    await p.waitForTimeout(200);
    const d = await p.evaluate(() => ({
      h1: document.querySelectorAll('h1').length,
      sidebar: document.querySelectorAll('.service-sidebar li a').length,
      scope: document.querySelectorAll('.scope-list li').length,
      process: document.querySelectorAll('.lw-process li').length,
      realImg: (() => { const i = document.querySelector('.service_img img'); return !!i && i.complete && i.naturalWidth > 0; })(),
    }));
    const isLanding = page === 'business-home.html';
    const ok = isLanding ? (d.h1 === 1) : (d.h1 === 1 && d.sidebar === 10 && d.scope >= 4 && d.process >= 6 && d.realImg);
    if (!ok) failures.push('new page structure issue: ' + page + ' ' + JSON.stringify(d));
    functional['newPage:' + page] = d;
  }

  /* WhatsApp focus + reduced motion + no-JS + AR */
  await p.goto(BASE + 'index.html', { waitUntil: 'load' });
  await p.locator('.lw-whatsapp-float').focus();
  functional.whatsappFocus = await p.locator('.lw-whatsapp-float').evaluate((el) => {
    const cs = getComputedStyle(el);
    return { outline: cs.outlineStyle + ' ' + cs.outlineWidth, href: el.href, rel: el.rel };
  });

  const rctx = await browser.newContext({ reducedMotion: 'reduce' });
  const rp = await rctx.newPage();
  await rp.goto(BASE + 'index.html', { waitUntil: 'load' });
  await rp.waitForTimeout(400);
  const rmStart = await rp.locator('.lw-slide.is-active').getAttribute('aria-label');
  await rp.waitForTimeout(7600);
  functional.reducedMotion = {
    pauseVisible: await rp.locator('#lw-pause').isVisible(),
    anim: await rp.locator('.lw-slide.is-active .lw-slide-img').evaluate((el) => getComputedStyle(el).animationName),
    start: rmStart,
    end: await rp.locator('.lw-slide.is-active').getAttribute('aria-label'),
  };
  await rctx.close();

  const nctx = await browser.newContext({ javaScriptEnabled: false });
  const np = await nctx.newPage();
  await np.setViewportSize({ width: 390, height: 844 });
  await np.goto(BASE + 'index.html', { waitUntil: 'load' });
  functional.noJs = await np.evaluate(() => {
    const first = document.querySelector('.lw-slide');
    const controls = document.querySelector('.lw-hero-controls');
    const cta = document.querySelector('.lw-hero-cta-btn');
    const cs = first ? getComputedStyle(first) : null;
    return {
      slides: document.querySelectorAll('.lw-slide').length,
      firstVisible: !!cs && cs.visibility !== 'hidden' && cs.opacity !== '0',
      controlsHidden: !!controls && getComputedStyle(controls).display === 'none',
      ctaVisible: !!cta && !!cta.textContent.trim(),
      waVisible: !!document.querySelector('.lw-whatsapp-float'),
    };
  });
  await nctx.close();

  await p.goto(BASE + 'ar/index.html', { waitUntil: 'load' });
  await p.waitForTimeout(300);
  functional.arabic = await p.evaluate(() => ({
    lang: document.documentElement.lang,
    dir: document.documentElement.dir,
    slides: document.querySelectorAll('.lw-slide').length,
    title1: document.querySelector('[data-i18n="heroTitle1"]').textContent,
    cta1: document.querySelector('[data-i18n="heroCta1"]').textContent,
    waLabel: (document.querySelector('.lw-whatsapp-float') || {}).getAttribute ? document.querySelector('.lw-whatsapp-float').getAttribute('aria-label') : null,
  }));

  const summary = {
    pageConfigs: pages.length,
    staticFailures: staticResult.failures.length,
    staticSitemapCount: staticResult.sitemapCount,
    dictKeys: staticResult.dictKeys,
    jsErrors: pages.filter((x) => x.errors.length).length,
    badResponses: pages.filter((x) => x.bad.length).length,
    brokenImages: pages.filter((x) => x.info.broken.length).length,
    i18nMismatch: pages.filter((x) => x.info.mismatch.length).length,
    altMismatch: pages.filter((x) => x.info.altMismatch.length).length,
    externalRequests: pages.filter((x) => x.external.length).length,
    csp: pages.filter((x) => x.info.csp.length).length,
    overflow: pages.filter((x) => x.info.overflow).length,
    waMissing: pages.filter((x) => !x.info.wa).length,
    heroBad: pages.filter((x) => (x.page === 'index.html' || x.page === 'ar/index.html')
      && (x.info.heroSlides !== 6 || x.info.heroBullets !== 6 || x.info.heroCtas.length !== 6)).length,
    failures: failures.length,
  };
  fs.writeFileSync(path.join(OUT, 'final-verify.json'), JSON.stringify({ summary, functional, failures, staticResult }, null, 1));
  console.log(JSON.stringify({ summary, functional, failures }, null, 1));
  await browser.close();
  process.exit(failures.length ? 1 : 0);
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
