(function () {
  'use strict';
  var dictionaries = window.LINKWAVE_CONTENT;
  var language = 'en';
  var slider = null;
  var paused = false;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var validated = false;
  var storageKey = 'linkwave-language';
  function text(key) { return dictionaries[language][key]; }
  function validate(focus) {
    var firstInvalid = null;
    document.querySelectorAll('#quote-form input, #quote-form textarea, #quote-form select').forEach(function (field) {
      var error = '';
      if (field.required && !field.value.trim()) error = text('required');
      else if (field.type === 'email' && field.validity.typeMismatch) error = text('badEmail');
      else if (field.maxLength > 0 && field.value.length > field.maxLength) error = text('tooLong');
      field.setAttribute('aria-invalid', error ? 'true' : 'false');
      document.getElementById(field.id + '-error').textContent = error;
      if (error && !firstInvalid) firstInvalid = field;
    });
    document.getElementById('form-status').textContent = text(firstInvalid ? 'invalid' : 'valid');
    if (firstInvalid && focus) firstInvalid.focus();
  }
  function applyLanguage(next, updateUrl) {
    language = next === 'ar' ? 'ar' : 'en';
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-i18n]').forEach(function (element) {
      element.textContent = text(element.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-alt]').forEach(function (element) {
      element.alt = text(element.dataset.i18nAlt);
    });
    document.querySelectorAll('[data-lang]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.lang === language));
    });
    document.querySelectorAll('a[data-local]').forEach(function (a) {
      var url = new URL(a.getAttribute('href'), location.href);
      url.searchParams.set('lang', language);
      a.setAttribute('href', url.pathname.split('/').pop() + url.search + url.hash);
    });
    document.title = text(document.body.dataset.page) + ' | ' + text('brand');
    var description = text(document.body.dataset.page + 'Desc') || text('meta');
    document.querySelector('meta[name="description"]').content = description;
    document.querySelector('meta[property="og:title"]').content = document.title;
    document.querySelector('meta[property="og:description"]').content = description;
    document.querySelector('meta[property="og:locale"]').content = language === 'ar' ? 'ar_AR' : 'en_US';
    if (updateUrl) {
      var url = new URL(location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', url);
      try { localStorage.setItem(storageKey, language); } catch (_) { /* Restricted storage: URL carries the selection. */ }
    }
    if (validated) validate(false);
    updateMotionLabel();
    if (slider) slider.revredraw();
  }
  function updateMotionLabel() {
    var button = document.getElementById('motion-toggle');
    if (!button) return;
    button.textContent = text(paused ? 'play' : 'pause');
    button.setAttribute('aria-pressed', String(paused));
    button.disabled = reduced.matches || !slider;
    ['slide-prev','slide-next'].forEach(function(id){ var control=document.getElementById(id); if(control) control.disabled=reduced.matches||!slider; });
  }
  var requested = new URL(location.href).searchParams.get('lang');
  var saved;
  try { saved = localStorage.getItem(storageKey); } catch (_) {}
  applyLanguage(requested === 'ar' || requested === 'en' ? requested : saved, false);
  document.querySelectorAll('[data-lang]').forEach(function (button) {
    button.addEventListener('click', function () { applyLanguage(button.dataset.lang, true); });
  });
  var toggle = document.querySelector('.lw-menu-toggle');
  var menu = document.getElementById('lw-menu');
  function closeMenu() { toggle.setAttribute('aria-expanded', 'false'); menu.classList.remove('lw-open'); }
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    menu.classList.toggle('lw-open', open);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { closeMenu(); toggle.focus(); }
  });
  document.querySelectorAll('#lw-menu a.active').forEach(function (a) { a.setAttribute('aria-current','page'); });
  var form = document.getElementById('quote-form');
  if (form) {
    form.addEventListener('submit', function (event) { event.preventDefault(); });
    document.getElementById('validate-form').addEventListener('click', function () { validated = true; validate(true); });
    form.addEventListener('input', function () { if (validated) validate(false); });
  }
  var hero = document.getElementById('rev_slider_4_1');
  if (hero && window.jQuery && window.jQuery.fn.revolution) {
    if (reduced.matches) {
      hero.querySelectorAll('li').forEach(function (li) { li.dataset.transition = 'fade'; li.dataset.masterspeed = '0'; });
      hero.querySelectorAll('[data-kenburns]').forEach(function (img) { img.dataset.kenburns = 'off'; });
      hero.querySelectorAll('[data-transform_in]').forEach(function (el) { el.dataset.transform_in = 'opacity:1;s:0;'; el.dataset.start = '0'; });
    }
    slider = window.jQuery(hero).show().revolution({
      sliderType:'standard', jsFileLocation:'revolution/js/', sliderLayout:'fullwidth', dottedOverlay:'none', delay:7000,
      navigation:{keyboardNavigation:'off',mouseScrollNavigation:'off',onHoverStop:'on',touch:{touchenabled:'on',swipe_threshold:75,swipe_min_touches:1,swipe_direction:'horizontal',drag_block_vertical:false},arrows:{style:'zeus',enable:true,hide_onmobile:true,hide_under:600,hide_onleave:true,hide_delay:200,hide_delay_mobile:1200,tmp:'<div class="tp-title-wrap"><div class="tp-arr-imgholder"></div></div>',left:{h_align:'left',v_align:'center',h_offset:30,v_offset:0},right:{h_align:'right',v_align:'center',h_offset:30,v_offset:0}},bullets:{enable:true,hide_onmobile:true,hide_under:600,style:'metis',hide_onleave:true,hide_delay:200,hide_delay_mobile:1200,direction:'horizontal',h_align:'center',v_align:'bottom',h_offset:0,v_offset:30,space:5,tmp:'<span class="tp-bullet-img-wrap"><span class="tp-bullet-image"></span></span>'}},
      viewPort:{enable:true,outof:'pause',visible_area:'80%'},responsiveLevels:[1240,1024,778,480],gridwidth:[1240,1024,778,480],gridheight:[700,700,500,400],lazyType:'none',
      parallax:{type:reduced.matches?'off':'mouse',origo:'slidercenter',speed:2000,levels:[2,3,4,5,6,7,12,16,10,50]},shadow:0,spinner:'off',
      stopLoop:reduced.matches?'on':'off',stopAfterLoops:reduced.matches?0:-1,stopAtSlide:reduced.matches?1:-1,shuffle:'off',autoHeight:'off',hideThumbsOnMobile:'off',hideSliderAtLimit:0,hideCaptionAtLimit:0,hideAllCaptionAtLimit:0,debugMode:false,
      fallbacks:{simplifyAll:'off',nextSlideOnWindowFocus:'off',disableFocusListener:false}
    });
    paused = reduced.matches;
    if (paused) slider.revpause();
    updateMotionLabel();
    document.getElementById('slide-prev').addEventListener('click',function(){slider.revprev();});
    document.getElementById('slide-next').addEventListener('click',function(){slider.revnext();});
    document.getElementById('motion-toggle').addEventListener('click', function () {
      paused = !paused;
      if (paused) slider.revpause(); else slider.revresume();
      document.body.classList.toggle('motion-paused', paused);
      updateMotionLabel();
    });
  }
  function reduceMotion() {
    if (reduced.matches && slider) { paused = true; slider.revpause(); document.body.classList.add('motion-paused'); }
    updateMotionLabel();
  }
  if (reduced.addEventListener) reduced.addEventListener('change', reduceMotion);
})();
