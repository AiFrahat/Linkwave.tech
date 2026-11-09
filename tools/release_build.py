#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Release build for the Linkwave Technology static website (release/launch-fixes).

Transforms the English pages in place and generates Arabic static pages, legal pages,
404, sitemap, robots, manifest and the new head/header/footer, then removes unused
vendor assets. Run through the reproducible wrapper:  python tools/build_release.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_site_override = os.environ.get("LINKWAVE_SITE")
if not _site_override:
    raise SystemExit(
        "LINKWAVE_SITE is not set.\n"
        "This generator transforms baseline pages into a build directory; run it through the\n"
        "reproducible wrapper instead:  python tools/build_release.py --check --repeat\n"
    )
SITE = Path(_site_override)
BASE = "https://linkwave.tech"

NAV = [
    ("home", "index.html"),
    ("about", "it_about.html"),
    ("services", "it_service.html"),
    ("business", "business-home.html"),
    ("industries", "industries.html"),
    ("contact", "it_contact.html"),
]

PAGES = {
    "index.html": dict(
        path="", nav="home",
        title_en="Linkwave Technology | Telecom & Network Infrastructure",
        desc_en="Telecom infrastructure, network installation, data centers, unified communications, security systems and FTTH services from Linkwave Technology.",
        title_ar="لينك ويف تكنولوجي | الاتصالات والبنية التحتية للشبكات",
        desc_ar="خدمات البنية التحتية للاتصالات وتركيب الشبكات ومراكز البيانات والاتصالات الموحدة وأنظمة الأمن والألياف الضوئية إلى المنازل من لينك ويف تكنولوجي.",
    ),
    "it_about.html": dict(
        path="it_about.html", nav="about",
        title_en="About Linkwave Technology | Infrastructure Partner",
        desc_en="Linkwave Technology focuses on telecommunications and digital infrastructure: networks, data centers, voice, security and FTTH for connected sites.",
        title_ar="من نحن | لينك ويف تكنولوجي",
        desc_ar="تركّز لينك ويف تكنولوجي على البنية التحتية للاتصالات والبنية الرقمية: الشبكات ومراكز البيانات والاتصالات الصوتية والأمن والألياف الضوئية للمواقع المتصلة.",
    ),
    "it_service.html": dict(
        path="it_service.html", nav="services",
        title_en="Telecom, Network & Data Center Services | Linkwave",
        desc_en="Six integrated services: telecom civil works, network installation, data centers, unified communications, security systems and FTTH services.",
        title_ar="خدمات الاتصالات والشبكات ومراكز البيانات | لينك ويف",
        desc_ar="ست خدمات متكاملة: الأعمال المدنية للاتصالات وتركيب الشبكات ومراكز البيانات والاتصالات الموحدة وأنظمة الأمن والألياف الضوئية إلى المنازل.",
    ),
    "industries.html": dict(
        path="industries.html", nav="industries",
        title_en="Industries We Serve | Linkwave Technology",
        desc_en="Service applications for offices and commercial buildings, residential developments, campuses and multi-site operations, and data center facilities.",
        title_ar="القطاعات التي نخدمها | لينك ويف تكنولوجي",
        desc_ar="تطبيقات خدمية للمكاتب والمباني التجارية والمجمعات السكنية والحرمات والعمليات متعددة المواقع ومرافق مراكز البيانات.",
    ),
    "it_contact.html": dict(
        path="it_contact.html", nav="contact",
        title_en="Contact Linkwave Technology",
        desc_en="Contact Linkwave Technology to discuss telecommunications, network, data center, voice, security or FTTH requirements for your site.",
        title_ar="تواصل مع لينك ويف تكنولوجي",
        desc_ar="تواصل مع لينك ويف تكنولوجي لمناقشة متطلبات الاتصالات والشبكات ومراكز البيانات والاتصالات الصوتية والأمن والألياف الضوئية لموقعك.",
    ),
    "service-telecom.html": dict(
        path="service-telecom.html", nav="services",
        title_en="Telecommunications Infrastructure & Civil Works",
        desc_en="Fiber cable installation, ducts and pathways, cabinets, structured cabling, splicing, testing and commissioning for connected sites.",
        title_ar="البنية التحتية للاتصالات والأعمال المدنية",
        desc_ar="تمديد كابلات الألياف الضوئية والقنوات والمسارات والكابينات والكابلات المنظمة واللحام والاختبار والتشغيل للمواقع المتصلة.",
    ),
    "service-network.html": dict(
        path="service-network.html", nav="services",
        title_en="Network Installation | Linkwave Technology",
        desc_en="Wired and wireless networks, rack and cabling installation, switching, Wi-Fi and branch connectivity for offices and connected sites.",
        title_ar="تركيب الشبكات | لينك ويف تكنولوجي",
        desc_ar="شبكات سلكية ولاسلكية وتركيب الراكات والكابلات والتبديل وشبكات Wi-Fi وربط الفروع للمكاتب والمواقع المتصلة.",
    ),
    "service-datacenter.html": dict(
        path="service-datacenter.html", nav="services",
        title_en="Data Center Infrastructure & Services | Linkwave",
        desc_en="Racks, power and cooling, structured cabling, monitoring and infrastructure services for data center facilities and computer rooms.",
        title_ar="البنية التحتية وخدمات مراكز البيانات | لينك ويف",
        desc_ar="الراكات والطاقة والتبريد والكابلات المنظمة والمراقبة وخدمات البنية التحتية لمرافق مراكز البيانات وغرف الحاسبات.",
    ),
    "service-voice.html": dict(
        path="service-voice.html", nav="services",
        title_en="Voice & Unified Communications | Linkwave",
        desc_en="IP telephony, PBX, call handling and collaboration systems integrated within a site's communications infrastructure.",
        title_ar="الاتصالات الصوتية والاتصالات الموحدة | لينك ويف",
        desc_ar="الاتصالات الهاتفية عبر IP وأنظمة PBX وإدارة المكالمات والتعاون، ضمن البنية التحتية للاتصالات في الموقع.",
    ),
    "service-security.html": dict(
        path="service-security.html", nav="services",
        title_en="Security Systems & ELV Solutions | Linkwave",
        desc_en="Monitoring, access control and low-voltage building systems integrated around each site's operational and safety requirements.",
        title_ar="أنظمة الأمن وحلول ELV | لينك ويف",
        desc_ar="المراقبة والتحكم في الوصول وأنظمة المباني منخفضة الجهد بما يلبي احتياجات التشغيل والسلامة في كل موقع.",
    ),
    "service-ftth.html": dict(
        path="service-ftth.html", nav="services",
        title_en="FTTH Services | Linkwave Technology",
        desc_en="Fiber-to-the-home deployment, termination and maintenance for residential developments and small business connectivity.",
        title_ar="خدمات الألياف الضوئية إلى المنازل | لينك ويف",
        desc_ar="تمديد وتوصيل وصيانة الألياف الضوئية إلى المنازل للمجمعات السكنية وربط الأعمال الصغيرة.",
    ),
    "privacy.html": dict(
        path="privacy.html", nav=None,
        title_en="Privacy Policy | Linkwave Technology",
        desc_en="How Linkwave Technology handles information on this website: no analytics, no advertising cookies, and an enquiry form that stays local until verified channels exist.",
        title_ar="سياسة الخصوصية | لينك ويف تكنولوجي",
        desc_ar="كيف تتعامل لينك ويف تكنولوجي مع المعلومات على هذا الموقع: بلا تحليلات وبلا كوكيز إعلانية، ونموذج تواصل محلي حتى نشر القنوات المعتمدة.",
    ),
    "terms.html": dict(
        path="terms.html", nav=None,
        title_en="Terms of Use | Linkwave Technology",
        desc_en="Terms of use for the Linkwave Technology website: informational content, permitted use, intellectual property and limitation of liability.",
        title_ar="شروط الاستخدام | لينك ويف تكنولوجي",
        desc_ar="شروط استخدام موقع لينك ويف تكنولوجي: المحتوى التعريفي والاستخدام المسموح والملكية الفكرية وحدود المسؤولية.",
    ),
}

SERVICE_IMAGES = {
    "datacenter", "ftth", "network", "security", "telecom", "voice", "planning",
}

try:
    from ar_egyptian import AR_EGYPTIAN, PAGES_AR
except ImportError:  # pragma: no cover - keeps the script standalone
    AR_EGYPTIAN, PAGES_AR = {}, {}

try:
    from services_data import LANDING, NEW_SERVICES, SHARED_LABELS
    from hero_data import HERO_SLIDES, WHATSAPP_LABELS, WHATSAPP_NUMBER
except ImportError:  # pragma: no cover
    LANDING, NEW_SERVICES, SHARED_LABELS = None, [], {}
    HERO_SLIDES, WHATSAPP_LABELS, WHATSAPP_NUMBER = [], {}, ""

for _page, _values in PAGES_AR.items():
    PAGES[_page].update(_values)

if LANDING:
    PAGES[LANDING["route"]] = dict(
        path=LANDING["route"], nav="business",
        title_en=LANDING["title_en"], desc_en=LANDING["desc_en"],
        title_ar=LANDING["title_ar"], desc_ar=LANDING["desc_ar"],
    )
for _svc in NEW_SERVICES:
    PAGES[_svc["route"]] = dict(path=_svc["route"], nav="business", **_svc["meta"])


HEAD_EXTRA = (
    '<meta name="theme-color" content="#0278ad">'
    '<meta name="referrer" content="strict-origin-when-cross-origin">'
)

FORM_ORIGIN = os.environ.get("LINKWAVE_FORM_ORIGIN", "").strip()
CSP = (
    "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; "
    "script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self'; connect-src 'self'"
    + ((" " + FORM_ORIGIN) if FORM_ORIGIN else "")
    + "; base-uri 'self'; form-action 'self'; "
    "object-src 'none'\">"
)

NOSCRIPT_STYLE = (
    "<noscript><style>@media(max-width:991px){#navbar_menu>ul{display:flex!important;"
    "flex-direction:column!important;width:100%}#navbar_menu>ul>li{display:block;width:100%}"
    ".lw-menu-toggle{display:none!important}}"
    "<style>.lw-slide:first-child{opacity:1!important;visibility:visible!important}"
    ".lw-hero-controls{display:none!important}"
    ".lw-slide.is-active .lw-slide-img{animation:none!important}</style></noscript>"
)

ENTRY_LINKS = "".join(
    '<li><a href="{p}%s" data-local><span data-i18n="%s">%s</span></a></li>' % (href, key, key)
    for key, href in NAV
)


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def url_for(lang: str, path: str) -> str:
    if lang == "ar":
        return BASE + "/ar/" + path
    return BASE + "/" + path


def build_head(page: str, lang: str, prefix: str, robots: str = "index,follow",
               title_override: str | None = None, desc_override: str | None = None,
               canonical_override: str | None = None, hreflang: bool = True) -> str:
    meta = PAGES[page]
    title = title_override or (meta["title_en"] if lang == "en" else meta["title_ar"])
    desc = desc_override or (meta["desc_en"] if lang == "en" else meta["desc_ar"])
    path = meta["path"]
    en_url = url_for("en", path)
    ar_url = url_for("ar", path)
    canonical = canonical_override or (en_url if lang == "en" else ar_url)
    locale = "en_US" if lang == "en" else "ar_AR"
    locale_alt = "ar_AR" if lang == "en" else "en_US"
    img = BASE + "/images/linkwave/og-cover.jpg"
    parts = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<meta name="robots" content="{robots}">',
        HEAD_EXTRA,
        f'<link rel="canonical" href="{canonical}">',
    ]
    if hreflang:
        parts.extend([
            f'<link rel="alternate" hreflang="en" href="{en_url}">',
            f'<link rel="alternate" hreflang="ar" href="{ar_url}">',
            f'<link rel="alternate" hreflang="x-default" href="{en_url}">',
        ])
    parts.extend([
        '<meta property="og:site_name" content="Linkwave Technology">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:locale" content="{locale}">',
        f'<meta property="og:locale:alternate" content="{locale_alt}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:type" content="image/jpeg">',
        '<meta property="og:image:alt" content="Linkwave Technology — telecommunications and network infrastructure">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{img}">',
        "<meta name=\"format-detection\" content=\"telephone=no\">",
        CSP,
        f'<link rel="icon" href="{prefix}favicon-32.png" sizes="32x32" type="image/png">',
        f'<link rel="icon" href="{prefix}favicon-16.png" sizes="16x16" type="image/png">',
        f'<link rel="apple-touch-icon" href="{prefix}apple-touch-icon-180.png">',
        f'<link rel="manifest" href="{prefix}site.webmanifest">',
    ])
    if page == "index.html":
        parts.append(
            f'<link rel="preload" as="image" href="{prefix}images/linkwave/hero-960.webp" '
            f'imagesrcset="{prefix}images/linkwave/hero-480.webp 480w, {prefix}images/linkwave/hero-960.webp 960w, '
            f'{prefix}images/linkwave/hero.webp 1376w" imagesizes="100vw" fetchpriority="high">'
        )
    parts.extend([
        f'<link rel="preload" href="{prefix}fonts/cairo/cairo-0.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="preload" href="{prefix}fonts/cairo/cairo-3.woff2" as="font" type="font/woff2" crossorigin>',
    ])
    for css in ("cairo", "bootstrap.min", "style", "responsive", "colors1", "linkwave", "refinement"):
        parts.append(f'<link rel="stylesheet" href="{prefix}css/{css}.css">')
    parts.append(NOSCRIPT_STYLE)
    return "<head>" + "".join(parts) + "</head>"


def lang_switch(page: str, lang: str, prefix: str) -> str:
    here = page
    if lang == "en":
        en_href, ar_href = here, "ar/" + here
        en_cls, ar_cls = "is-active", ""
    else:
        en_href, ar_href = "../" + here, here
        en_cls, ar_cls = "", "is-active"
    return (
        '<div class="language-switch" role="group" aria-label="Language / اللغة">'
        f'<a class="{en_cls}" href="{en_href}" hreflang="en" lang="en" dir="ltr"'
        + (' aria-current="true"' if en_cls else "")
        + ">EN</a><span aria-hidden=\"true\">|</span>"
        f'<a class="{ar_cls}" href="{ar_href}" hreflang="ar" lang="ar" dir="rtl"'
        + (' aria-current="true"' if ar_cls else "")
        + " aria-label=\"العربية\">AR</a></div>"
    )


def build_header(page: str, lang: str, prefix: str) -> str:
    active = PAGES[page]["nav"]

    def li(key: str, href: str) -> str:
        cls = ' class="active" aria-current="page"' if key == active else ""
        return f'<li><a href="{href}"{cls} data-local><span data-i18n="{key}">{key}</span></a></li>'

    items = "".join(li(key, href) for key, href in NAV)
    return (
        '<header id="default_header" class="header_style_1">'
        '<div class="header_top"><div class="container"><div class="lw-top">'
        '<span><span data-i18n="tagline">Telecommunications &amp; Network Infrastructure</span></span>'
        '<a href="https://linkwave.tech" dir="ltr">linkwave.tech</a></div></div></div>'
        '<div class="header_bottom"><div class="container"><div class="row align-items-center">'
        '<div class="col-lg-3 col-md-12"><div class="logo"><a href="index.html" data-local>'
        '<span class="lw-brand-lockup">'
        f'<img class="img-responsive lw-logo" src="{prefix}images/linkwave/brand-emblem.webp" '
        'data-i18n-alt="brand" alt="Linkwave Technology" decoding="async" width="96" height="96">'
        '<span class="lw-brand-name" data-i18n="brand">Linkwave Technology</span>'
        '</span></a></div></div>'
        '<div class="col-lg-9 col-md-12"><div class="lw-nav-tools">'
        + lang_switch(page, lang, prefix) +
        '<button class="lw-menu-toggle" type="button" aria-expanded="false" aria-controls="lw-menu">'
        '<span data-i18n="menu">Menu</span></button></div>'
        '<nav id="navbar_menu" aria-label="Main / الرئيسية"><ul id="lw-menu" class="first-ul">'
        + items +
        "</ul></nav></div></div></div></div></header>"
    )


def build_footer(lang: str, prefix: str) -> str:
    services = "".join(
        f'<li><a href="{href}" data-local><span data-i18n="{key}">{key}</span></a></li>'
        for key, href in [
            ("telecom", "service-telecom.html"),
            ("network", "service-network.html"),
            ("datacenter", "service-datacenter.html"),
            ("voice", "service-voice.html"),
            ("security", "service-security.html"),
            ("ftth", "service-ftth.html"),
            ("business", "business-home.html"),
        ]
    )
    return (
        '<footer class="footer_style_2"><div class="container"><div class="row">'
        '<div class="col-md-4"><a href="index.html" data-local><span class="lw-brand-lockup">'
        f'<img class="img-responsive lw-logo" src="{prefix}images/linkwave/brand-emblem.webp" '
        'data-i18n-alt="brand" alt="Linkwave Technology" loading="lazy" decoding="async" width="96" height="96">'
        '<span class="lw-brand-name" data-i18n="brand">Linkwave Technology</span></span></a>'
        '<p data-i18n="footerText">Telecommunications, networks and connected infrastructure.</p></div>'
        '<div class="col-md-4"><h3 data-i18n="services">Services</h3>'
        f'<ul class="footer-menu">{services}</ul></div>'
        '<div class="col-md-4"><h3 data-i18n="contact">Contact</h3>'
        '<p class="lw-contact-direct"><span data-i18n="callUs">Call us</span>: '
        '<a class="lw-contact-link" href="tel:+201276668018" dir="ltr">+20 127 666 8018</a></p>'
        '<div class="lw-contact-channels" data-contact-channels></div>'
        '<a href="it_contact.html" class="btn white_btn" data-local><span data-i18n="quote">Request a Quote</span></a>'
        "</div></div></div>"
        '<div class="cprt"><p>© 2026 <span data-i18n="rights">Linkwave Technology. All rights reserved.</span> '
        '<span class="lw-legal-links"><a href="privacy.html" data-i18n="privacyLink">Privacy Policy</a> · '
        '<a href="terms.html" data-i18n="termsLink">Terms of Use</a></span> '
        '<span class="lw-credit"><span data-i18n="credit">Template by</span> '
        '<a href="https://html.design" rel="nofollow">html.design</a></span> '
        '<span class="lw-owner" dir="rtl">حقوق الملكية لـ <a href="https://aifrahat.com" rel="noopener">AiFRAHAT.com</a></span></p></div></footer>'
    )


def build_scripts(prefix: str, lang: str = "en") -> str:
    return (
        whatsapp_markup(lang)
        + f'<script src="{prefix}js/content.js" defer></script>'
        f'<script src="{prefix}js/site-config.js" defer></script>'
        f'<script src="{prefix}js/linkwave.js" defer></script></body></html>'
    )


def slide(index: int, data: dict, prefix: str, active: bool = False) -> str:
    name = data["image"]
    title_key = "heroTitle%d" % index
    sub_key = "heroSubtitle%d" % index
    cta_key = "heroCta%d" % index
    cls = " is-active" if active else ""
    hidden = "false" if active else "true"
    src = f"{prefix}images/linkwave/{name}.webp"
    srcset = (
        f"{prefix}images/linkwave/{name}-480.webp 480w, "
        f"{prefix}images/linkwave/{name}-960.webp 960w, "
        f"{src} 1376w"
    )
    if active:
        image = (
            f'<img class="lw-slide-img" src="{src}" srcset="{srcset}" '
            'sizes="100vw" width="1376" height="768" alt="" fetchpriority="high" decoding="async">'
        )
    else:
        image = (
            f'<img class="lw-slide-img lw-slide-img--deferred" data-src="{src}" '
            f'data-srcset="{srcset}" sizes="100vw" width="1376" height="768" alt="" decoding="async">'
        )
    return (
        f'<div class="lw-slide{cls}" role="group" aria-roledescription="slide" '
        f'aria-label="{index} / {len(HERO_SLIDES)}" aria-hidden="{hidden}">'
        + image
        + '<span class="lw-shade" aria-hidden="true"></span>'
        '<div class="lw-hero-caption">'
        f'<p class="lw-hero-title"><span data-i18n="{title_key}"></span></p>'
        f'<p class="lw-hero-sub" data-i18n="{sub_key}"></p>'
        f'<a class="btn main_bt lw-hero-cta-btn" href="{data["route"]}" data-local>'
        f'<span data-i18n="{cta_key}"></span></a>'
        "</div></div>"
    )


def build_hero(prefix: str) -> str:
    total = len(HERO_SLIDES)
    slides = "".join(
        slide(i, data, prefix, active=(i == 1))
        for i, data in enumerate(HERO_SLIDES, 1)
    )
    bullets = "".join(
        f'<button class="lw-bullet{" is-active" if i == 1 else ""}" type="button" aria-label="{i}" '
        f'aria-current="{"true" if i == 1 else "false"}"><span aria-hidden="true"></span></button>'
        for i in range(1, total + 1)
    )
    return (
        '<section class="lw-hero" id="lw-hero" aria-roledescription="carousel" '
        'aria-label="Linkwave Technology">'
        '<div class="lw-hero-track">' + slides + "</div>"
        '<div class="lw-hero-controls">'
        '<button id="lw-prev" type="button" class="lw-hero-arrow"><span class="sr-only" data-i18n="previous">Previous slide</span>'
        '<span aria-hidden="true">‹</span></button>'
        f'<div class="lw-hero-bullets" role="group" aria-label="1 / {total}">{bullets}</div>'
        '<button id="lw-next" type="button" class="lw-hero-arrow"><span class="sr-only" data-i18n="nextSlide">Next slide</span>'
        '<span aria-hidden="true">›</span></button>'
        '<button id="lw-pause" type="button" class="lw-hero-pause" aria-pressed="false">'
        '<span data-label data-i18n="pause">Pause animation</span></button>'
        "</div>"
        '<p class="sr-only" data-slide-status role="status" aria-live="polite"></p>'
        "</section>"
        '<div class="lw-hero-cta container"><a href="it_service.html" class="btn main_bt" data-local>'
        '<span data-i18n="all">Explore our services</span></a></div>'
    )


WHATSAPP_SVG_PATH = (
    "M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164"
    "-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059"
    "-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371"
    "-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01"
    "-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198"
    " 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719"
    " 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0"
    " 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436"
    "-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884"
    "-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142"
    " 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893"
    "-11.893a11.821 11.821 0 00-3.48-8.413Z"
)


def whatsapp_markup(lang: str = "en") -> str:
    if not WHATSAPP_NUMBER:
        return ""
    label = WHATSAPP_LABELS.get(lang, WHATSAPP_LABELS.get("en", "WhatsApp"))
    return (
        '<a class="lw-whatsapp-float" href="https://wa.me/%s" target="_blank" '
        'rel="noopener noreferrer" aria-label="%s">'
        '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" '
        'aria-hidden="true" focusable="false"><path d="%s"/></svg></a>'
    ) % (WHATSAPP_NUMBER, label, WHATSAPP_SVG_PATH)


def update_dictionary() -> dict:
    path = SITE / "js" / "content.js"
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw.split("=", 1)[1].strip().rstrip(";"))
    additions = {
        "privacyLink": ("Privacy Policy", "سياسة الخصوصية"),
        "termsLink": ("Terms of Use", "شروط الاستخدام"),
        "reqNote": ("Fields marked * are required.", "الحقول المعلَّمة بـ* مطلوبة."),
        "sentOk": ("Your request has been sent. We will get back to you.", "تم إرسال طلبك، وسنتواصل معك."),
        "sentErr": ("Sending failed. Please use the official channels on this page.", "تعذّر الإرسال. استخدم قنوات التواصل الرسمية في هذه الصفحة."),
        "sending": ("Sending…", "جارٍ الإرسال…"),
        "send": ("Send enquiry", "أرسل الطلب"),
        "slide": ("Slide", "شريحة"),
        "contactPhone": ("Phone", "الهاتف"),
        "contactEmail": ("Email", "البريد الإلكتروني"),
        "contactAddress": ("Address", "العنوان"),
        "contactWhatsapp": ("WhatsApp", "واتساب"),
        "callUs": ("Call us", "اتصل بنا"),
    }
    for key, (en, ar) in additions.items():
        data["en"].setdefault(key, en)
        data["ar"].setdefault(key, ar)
    form_copy = {
        "name": ("Full name", "الاسم بالكامل"),
        "email": ("Email address", "البريد الإلكتروني"),
        "phone": ("Phone (optional)", "رقم الهاتف (اختياري)"),
        "subject": ("Subject", "الموضوع"),
        "message": ("Message", "رسالتك"),
        "validate": ("Check details", "راجع البيانات"),
        "submit": ("Submission unavailable", "الإرسال غير متاح"),
        "send": ("Send message", "إرسال الرسالة"),
        "sending": ("Sending…", "جارٍ الإرسال…"),
        "accepted": ("Your message was accepted for delivery.", "تم قبول رسالتك للإرسال."),
        "sentErr": ("Sending failed. Please try again or use the phone/WhatsApp.",
                    "تعذّر الإرسال. حاول تاني أو استخدم الهاتف/واتساب."),
        "rateLimited": ("Too many attempts. Please wait a minute and try again.",
                        "محاولات كتير. استنى دقيقة وحاول تاني."),
        "phoneBad": ("Enter a valid phone number.", "اكتب رقم هاتف صحيح."),
        "privacy": ("Your details are sent by email to Linkwave and are not stored on this website.",
                    "بياناتك بتتبعت على إيميل لينك ويف ومش بتتخزن على الموقع ده."),
        "reqNote": ("Fields marked * are required.", "الحقول المعلَّمة بـ* مطلوبة."),
        "valid": ("Your details look valid. Submit the form to send them.",
                  "بياناتك شكلها صحيح. اضغط إرسال عشان تتبعت."),
        "invalid": ("Please review the highlighted fields. Nothing has been sent.",
                    "راجع الحقول المعلّمة. مفيش أي حاجة اتبعتت."),
    }
    for _key, (_en, _ar) in form_copy.items():
        data["en"][_key] = _en
        data["ar"][_key] = _ar
    data["en"]["unavailable"] = ("Online enquiries are being configured. "
                                 "Please use the phone or WhatsApp meanwhile.")
    data["ar"]["unavailable"] = ("الاستفسارات أونلاين قيد التجهيز. "
                                 "استخدم الهاتف أو واتساب في الوقت الحالي.")
    data["en"]["pause"] = "Pause"
    data["ar"]["pause"] = "إيقاف"
    data["en"]["play"] = "Play"
    data["ar"]["play"] = "تشغيل"
    if AR_EGYPTIAN:
        data["ar"].update(AR_EGYPTIAN)
    # The new contact-form copy must win over the legacy Egyptian overrides.
    for _key, (_en, _ar) in form_copy.items():
        data["ar"][_key] = _ar
    data["ar"]["unavailable"] = (
        "الاستفسارات أونلاين قيد التجهيز. استخدم الهاتف أو واتساب في الوقت الحالي."
    )
    if SHARED_LABELS:
        for _key, (_en, _ar) in SHARED_LABELS.items():
            data["en"][_key] = _en
            data["ar"][_key] = _ar
    if LANDING:
        data["en"]["bhIntro"] = LANDING["intro_en"]
        data["ar"]["bhIntro"] = LANDING["intro_ar"]
    for _i, _hero in enumerate(HERO_SLIDES, 1):
        data["en"]["heroTitle%d" % _i] = _hero["title_en"]
        data["ar"]["heroTitle%d" % _i] = _hero["title_ar"]
        data["en"]["heroSubtitle%d" % _i] = _hero["sub_en"]
        data["ar"]["heroSubtitle%d" % _i] = _hero["sub_ar"]
        data["en"]["heroCta%d" % _i] = _hero["cta_en"]
        data["ar"]["heroCta%d" % _i] = _hero["cta_ar"]
    data["en"]["whatsappFloat"] = WHATSAPP_LABELS["en"]
    data["ar"]["whatsappFloat"] = WHATSAPP_LABELS["ar"]
    for _svc in NEW_SERVICES:
        _key = _svc["key"]
        _en, _ar = _svc["en"], _svc["ar"]
        data["en"][_key] = _en["title"]
        data["ar"][_key] = _ar["title"]
        data["en"][_key + "Hero"] = _en["hero"]
        data["ar"][_key + "Hero"] = _ar["hero"]
        data["en"][_key + "Desc"] = _en["desc"]
        data["ar"][_key + "Desc"] = _ar["desc"]
        data["en"][_key + "Alt"] = _en["alt"]
        data["ar"][_key + "Alt"] = _ar["alt"]
        for _group, _suffix in (("bullets", ""), ("equipment", "Eq"), ("process", "Pr")):
            for _i, _text in enumerate(_en.get(_group, [])):
                data["en"]["%s%s%d" % (_key, _suffix, _i)] = _text
                data["ar"]["%s%s%d" % (_key, _suffix, _i)] = _ar[_group][_i]
        for _group, _suffix in (("notes", "Note"), ("security", "Sec")):
            for _i, _text in enumerate(_en.get(_group, [])):
                data["en"]["%s%s%d" % (_key, _suffix, _i)] = _text
                data["ar"]["%s%s%d" % (_key, _suffix, _i)] = _ar[_group][_i]
        if _en.get("target"):
            data["en"][_key + "Target"] = _en["target"]
            data["ar"][_key + "Target"] = _ar["target"]
    missing = [key for key in data["en"] if key not in data["ar"]]
    if missing:
        print("WARNING missing Arabic keys:", missing)
    path.write_text(
        "window.LINKWAVE_CONTENT = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
        newline="\n",
    )
    return data


def translate(html: str, dictionary: dict, lang: str = "ar") -> str:
    values = dictionary[lang]

    pattern = re.compile(
        r'(?P<open><(?P<tag>[a-zA-Z0-9]+)\b[^>]*\bdata-i18n="(?P<key>[^"]+)"[^>]*>)(?P<inner>[^<]*)(?P<close></(?P=tag)>)'
    )

    def swap(match: re.Match) -> str:
        value = values.get(match.group("key"))
        if not value:
            return match.group(0)
        return match.group("open") + value + match.group("close")

    html = pattern.sub(swap, html)

    img_pattern = re.compile(r'(<img\b[^>]*\bdata-i18n-alt="(?P<key>[^"]+)"[^>]*>)')

    def swap_alt(match: re.Match) -> str:
        value = values.get(match.group("key"))
        if not value:
            return match.group(0)
        tag = match.group(1)
        return re.sub(r'\balt="[^"]*"', 'alt="' + value.replace('"', "&quot;") + '"', tag, count=1)

    return img_pattern.sub(swap_alt, html)


def prefix_assets(html: str, prefix: str = "../") -> str:
    if not prefix:
        return html
    dirs = r"(?:images|css|js|fonts)/"

    def fix_src(match: re.Match) -> str:
        return match.group(1) + prefix + match.group(2)

    html = re.sub(r'(\bsrc=")(?!https?:|\.\./|/|data:)(?=[^"]*' + dirs + r'|favicon|apple-touch|site\.webmanifest)([^"]*")', fix_src, html)
    html = re.sub(r'(\bsrcset=")([^"]*)"', lambda m: m.group(1) + ", ".join(
        (prefix + part.strip() if part.strip() and not part.strip().startswith(("http", "../", "/", "data:")) else part.strip())
        for part in m.group(2).split(",")
    ) + '"', html)
    return html


def add_srcsets(html: str, grid: bool) -> str:
    sizes = ('(max-width: 575px) 100vw, (max-width: 991px) 50vw, 370px'
             if grid else '(max-width: 991px) 100vw, 760px')
    pattern = re.compile(r'<img\b[^>]*\bsrc="images/linkwave/(?P<name>[a-z]+)\.webp"[^>]*>')

    def repl(match: re.Match) -> str:
        tag = match.group(0)
        name = match.group("name")
        if name not in SERVICE_IMAGES or "srcset=" in tag or name == "hero":
            return tag
        srcset = (
            f'srcset="images/linkwave/{name}-480.webp 480w, '
            f'images/linkwave/{name}-960.webp 960w, images/linkwave/{name}.webp 1000w" '
            f'sizes="{sizes}"'
        )
        return tag[:-1] + " " + srcset + ">"

    return pattern.sub(repl, html)


def replace_block(html: str, start: str, end: str, replacement: str) -> str:
    i = html.find(start)
    if i == -1:
        raise SystemExit("start marker not found: " + start[:60])
    j = html.find(end, i)
    if j == -1:
        raise SystemExit("end marker not found: " + end[:60])
    return html[:i] + replacement + html[j + len(end):]



# ---------------------------------------------------------------------------
# Ten-service component: alternating horizontal rows + generated pages
# ---------------------------------------------------------------------------

EXISTING_SERVICES = [
    {"key": "telecom", "number": 1, "route": "service-telecom.html", "image": "telecom"},
    {"key": "network", "number": 2, "route": "service-network.html", "image": "network"},
    {"key": "datacenter", "number": 3, "route": "service-datacenter.html", "image": "datacenter"},
    {"key": "voice", "number": 4, "route": "service-voice.html", "image": "voice"},
    {"key": "security", "number": 5, "route": "service-security.html", "image": "security"},
    {"key": "ftth", "number": 6, "route": "service-ftth.html", "image": "ftth"},
]


def all_services():
    return EXISTING_SERVICES + [
        {"key": s["key"], "number": s["number"], "route": s["route"], "image": s["image"]}
        for s in NEW_SERVICES
    ]


def _service_row(service):
    key, num, image, route = service["key"], "%02d" % service["number"], service["image"], service["route"]
    bullets = "".join('<li data-i18n="%s%d"></li>' % (key, i) for i in range(4))
    return (
        '<article class="lw-service-row" id="service-%s" aria-labelledby="service-%s-title">'
        '<div class="lw-service-row__media">'
        '<img class="lw-service-row__img" src="images/linkwave/%s.webp" '
        'srcset="images/linkwave/%s-480.webp 480w, images/linkwave/%s-960.webp 960w, images/linkwave/%s.webp 1000w" '
        'sizes="(max-width: 767px) 100vw, 46vw" width="1000" height="563" alt="" '
        'data-i18n-alt="%sAlt" loading="lazy" decoding="async"></div>'
        '<div class="lw-service-row__body">'
        '<span class="lw-service-row__index" aria-hidden="true">%s</span>'
        '<h3 id="service-%s-title" data-i18n="%s"></h3>'
        '<p class="lw-service-row__desc" data-i18n="%sDesc"></p>'
        '<ul class="scope-list lw-service-row__list">%s</ul>'
        '<a class="btn main_bt" href="%s" data-local><span data-i18n="view"></span></a>'
        '</div></article>'
    ) % (key, key, image, image, image, image, key, num, key, key, key, bullets, route)


def _rows(services):
    return "".join(_service_row(s) for s in services)


def _business_section():
    rows = _rows([s for s in all_services() if s["number"] > 6])
    return (
        '<section class="section padding_layout_1 lw-services-business" id="business-solutions">'
        '<div class="container">'
        '<div class="main_heading text_align_center">'
        '<h2 data-i18n="bhTitle"></h2>'
        '<p data-i18n="bhIntro" class="large"></p>'
        '</div>'
        '<div class="lw-services-group">' + rows + '</div>'
        '<div class="lw-services__more">'
        '<a class="btn main_bt" href="business-home.html" data-local>'
        '<span data-i18n="viewAllBusiness"></span></a>'
        '</div></div></section>'
    )


def services_section_html():
    six = _rows([s for s in all_services() if s["number"] <= 6])
    return (
        '<section class="section padding_layout_1 lw-services-section" id="services">'
        '<div class="container">'
        '<div class="main_heading text_align_center">'
        '<h2 data-i18n="servicesHeading"></h2>'
        '<p data-i18n="servicesIntro" class="large"></p>'
        '</div>'
        '<div class="lw-services-group">' + six + '</div>'
        '</div></section>' + _business_section()
    )


def replace_services_section(html):
    marker = 'data-i18n="servicesHeading"'
    idx = html.find(marker)
    if idx == -1:
        raise SystemExit("services heading marker not found")
    start = html.rfind("<section", 0, idx)
    end = html.find("</section>", idx)
    if start == -1 or end == -1:
        raise SystemExit("services section bounds not found")
    return html[:start] + services_section_html() + html[end + len("</section>"):]


def banner_html(title_key, with_business_crumb=True):
    crumbs = '<li><a href="index.html" data-local><span data-i18n="home"></span></a></li>'
    if with_business_crumb:
        crumbs += '<li><a href="business-home.html" data-local><span data-i18n="business"></span></a></li>'
    crumbs += '<li class="active" aria-current="page"><span data-i18n="%s"></span></li>' % title_key
    return (
        '<div id="inner_banner" class="section inner_banner_section"><div class="container">'
        '<div class="title-holder"><div class="title-holder-cell">'
        '<h1 class="page-title" data-i18n="%s"></h1>' % title_key
        + '<ol class="breadcrumb">' + crumbs + '</ol>'
        '</div></div></div></div>'
    )


def sidebar_html(current_key=None):
    items = []
    for service in all_services():
        active = ' class="active"' if service["key"] == current_key else ""
        items.append(
            '<li><a href="%s"%s data-local><span data-i18n="%s"></span></a></li>'
            % (service["route"], active, service["key"])
        )
    return (
        '<aside class="col-md-3"><h2 class="sidebar-title" data-i18n="services"></h2>'
        '<ul class="service-sidebar">' + "".join(items) + '</ul>'
        '<p class="lw-sidebar-more"><a href="business-home.html" data-local>'
        '<span data-i18n="viewAllBusiness"></span></a></p></aside>'
    )


def _page_shell(page, banner, body):
    return (
        '<!DOCTYPE html><html lang="en" dir="ltr" data-static-lang="en">'
        + build_head(page, "en", "")
        + '<body id="default_theme" data-page="%s">' % PAGES[page]["nav"]
        + '<a class="skip-link" href="#main"><span data-i18n="skip"></span></a>'
        + build_header(page, "en", "")
        + '<main id="main" tabindex="-1">' + banner + body + '</main>'
        + build_footer("en", "")
        + build_scripts("")
        + '</body></html>'
    )


def business_page_html():
    banner = banner_html("bhTitle", with_business_crumb=False)
    rows = _rows([s for s in all_services() if s["number"] > 6])
    body = (
        '<section class="section padding_layout_1 lw-services-section"><div class="container">'
        '<p class="large text_align_center" data-i18n="bhIntro"></p>'
        '<div class="lw-services-group">' + rows + '</div>'
        '<div class="lw-services__more"><a class="btn main_bt" href="it_contact.html" data-local>'
        '<span data-i18n="siteSurvey"></span></a></div>'
        '</div></section>'
        '<section class="section padding_layout_1 light_silver"><div class="container">'
        '<div class="row align-items-center">'
        '<div class="col-md-8"><h2 data-i18n="next"></h2><p data-i18n="nextText"></p></div>'
        '<div class="col-md-4"><a href="it_contact.html" class="btn main_bt" data-local>'
        '<span data-i18n="quote"></span></a></div>'
        '</div></div></section>'
    )
    return _page_shell(LANDING["route"], banner, body)


def new_service_page_html(service):
    key, image, route = service["key"], service["image"], service["route"]
    banner = banner_html(key)
    bullets = "".join('<li data-i18n="%s%d"></li>' % (key, i) for i in range(len(service["en"]["bullets"])))
    equipment = "".join('<li data-i18n="%sEq%d"></li>' % (key, i) for i in range(len(service["en"]["equipment"])))
    process = "".join('<li data-i18n="%sPr%d"></li>' % (key, i) for i in range(len(service["en"]["process"])))
    extra = ""
    if service["en"].get("target"):
        extra += '<h2 data-i18n="targetHeading"></h2><p data-i18n="%sTarget"></p>' % key
    if service["en"].get("notes"):
        items = "".join('<li data-i18n="%sNote%d"></li>' % (key, i) for i in range(len(service["en"]["notes"])))
        extra += '<h2 data-i18n="notesHeading"></h2><ul class="scope-list">' + items + '</ul>'
    if service["en"].get("security"):
        items = "".join('<li data-i18n="%sSec%d"></li>' % (key, i) for i in range(len(service["en"]["security"])))
        extra += '<h2 data-i18n="securityHeading"></h2><ul class="scope-list">' + items + '</ul>'
    content = (
        '<p class="large" data-i18n="%sDesc"></p>' % key
        + '<h2 data-i18n="scope"></h2><ul class="scope-list">' + bullets + '</ul>'
        + '<h2 data-i18n="equipmentHeading"></h2><ul class="scope-list">' + equipment + '</ul>'
        + '<h2 data-i18n="processHeading"></h2><ol class="lw-process">' + process + '</ol>'
        + extra
        + '<p data-i18n="scopeNote"></p>'
        + '<p class="lw-service-cta"><a class="btn main_bt" href="it_contact.html" data-local>'
        + '<span data-i18n="siteSurvey"></span></a></p>'
    )
    article = (
        '<article class="col-md-9"><div class="service_blog"><div class="service_img">'
        '<img class="img-responsive" src="images/linkwave/%s.webp" '
        'srcset="images/linkwave/%s-480.webp 480w, images/linkwave/%s-960.webp 960w, images/linkwave/%s.webp 1000w" '
        'sizes="(max-width: 991px) 100vw, 760px" width="1000" height="563" alt="" '
        'data-i18n-alt="%sAlt" fetchpriority="high" decoding="async"></div>'
        '<div class="service_cont">' % (image, image, image, image, image)
        + content
        + '</div></div></article>'
    )
    body = (
        '<section class="section padding_layout_1 service_list"><div class="container"><div class="row">'
        + article + sidebar_html(key)
        + '</div></div></section>'
        '<section class="section padding_layout_1 light_silver"><div class="container">'
        '<div class="row align-items-center">'
        '<div class="col-md-8"><h2 data-i18n="next"></h2><p data-i18n="nextText"></p></div>'
        '<div class="col-md-4"><a href="it_contact.html" class="btn main_bt" data-local>'
        '<span data-i18n="quote"></span></a></div>'
        '</div></div></section>'
    )
    return _page_shell(route, banner, body)


GENERATED_PAGES = {LANDING["route"]: business_page_html if LANDING else None}
for _svc in NEW_SERVICES:
    GENERATED_PAGES[_svc["route"]] = (lambda svc=_svc: new_service_page_html(svc))


def build_contact_form() -> str:
    """Secure enquiry form. Fields: name, email, phone (optional), subject, message.
    The submit button stays disabled until a formEndpoint is configured in site-config.js."""
    def field(field_id: str, label_key: str, required: bool, input_html: str) -> str:
        req = '<span class="lw-req" aria-hidden="true">*</span> ' if required else ""
        return (
            '<div class="col-md-6 lw-field">'
            f'<label for="{field_id}">{req}<span data-i18n="{label_key}"></span></label>'
            + input_html
            + f'<span id="{field_id}-error" class="field-error"></span></div>'
        )

    name = field("name", "name", True,
        '<input id="name" name="name" type="text" maxlength="100" required dir="auto" '
        'autocomplete="name" aria-describedby="name-error">')
    email = field("email", "email", True,
        '<input id="email" name="email" type="email" maxlength="254" required dir="ltr" '
        'autocomplete="email" inputmode="email" aria-describedby="email-error">')
    phone = field("phone", "phone", False,
        '<input id="phone" name="phone" type="tel" maxlength="30" dir="ltr" '
        'autocomplete="tel" inputmode="tel" aria-describedby="phone-error">')
    subject = field("subject", "subject", True,
        '<input id="subject" name="subject" type="text" maxlength="150" required dir="auto" '
        'autocomplete="off" aria-describedby="subject-error">')
    return (
        '<form id="quote-form" class="form_contant" novalidate aria-describedby="contact-notice">'
        '<div class="row">'
        + name + email + phone + subject
        + '<div class="col-md-12 lw-field"><label for="message">'
        '<span class="lw-req" aria-hidden="true">*</span> <span data-i18n="message"></span></label>'
        '<textarea id="message" name="message" dir="auto" rows="6" maxlength="3000" required '
        'aria-describedby="message-error"></textarea>'
        '<span id="message-error" class="field-error"></span></div>'
        '<div class="lw-hp" aria-hidden="true">'
        '<label for="lw-website">Company website</label>'
        '<input id="lw-website" name="_gotcha" type="text" tabindex="-1" autocomplete="off">'
        '</div>'
        '</div>'
        '<p data-i18n="privacy"></p>'
        '<div class="lw-form-actions">'
        '<button class="btn sqaure_bt" type="button" id="validate-form">'
        '<span data-i18n="validate"></span></button>'
        '<button type="submit" class="btn main_bt" disabled aria-busy="false">'
        '<span data-i18n="submit"></span></button>'
        '</div>'
        '<p id="form-status" role="status" aria-live="polite"></p>'
        '</form>'
    )


def transform_english(dictionary: dict) -> None:
    for page in PAGES:
        if page in ("privacy.html", "terms.html"):
            continue
        path = SITE / page
        if page in GENERATED_PAGES:
            html = translate(GENERATED_PAGES[page](), dictionary, "en")
            path.write_text(html, encoding="utf-8", newline="\n")
            print("GEN ", page, len(html))
            continue
        html = path.read_text(encoding="utf-8")
        if "data-static-lang" in html:
            raise SystemExit("already transformed: " + page)
        html = html.replace('<html lang="en" dir="ltr">',
                            '<html lang="en" dir="ltr" data-static-lang="en">', 1)
        html = re.sub(r"<head>.*?</head>", lambda m: build_head(page, "en", ""), html, count=1, flags=re.S)
        html = re.sub(r'<header id="default_header".*?</header>',
                      lambda m: build_header(page, "en", ""), html, count=1, flags=re.S)
        html = re.sub(r"<footer class=\"footer_style_2\">.*?</footer>",
                      lambda m: build_footer("en", ""), html, count=1, flags=re.S)
        html = re.sub(r'<script src="js/jquery[\s\S]*?(?=</body>)',
                      lambda m: build_scripts(""), html, count=1)
        if page == "index.html":
            html = replace_block(
                html,
                '<div class="lw-reduced-hero">',
                '<section class="section padding_layout_1 ">',
                build_hero("") + '<section class="section padding_layout_1 ">',
            )
        if page == "it_contact.html":
            html = html.replace(' onsubmit="return false"', "")
            html = re.sub(r'<form id="quote-form".*?</form>',
                          lambda m: build_contact_form(), html, count=1, flags=re.S)
            html = html.replace(
                '<p data-i18n="contactPending" >Phone, email and address: awaiting verified company details.</p>',
                '<p data-i18n="reqNote" class="lw-req-note">Fields marked * are required.</p>'
                '<p class="lw-contact-direct"><span data-i18n="callUs">Call us</span>: '
                '<a class="lw-contact-link" href="tel:+201276668018" dir="ltr">+20 127 666 8018</a></p>'
                '<div class="lw-contact-channels" data-contact-channels></div>',
                1,
            )
            html = html.replace(
                '<button type="button" class="btn sqaure_bt" disabled><span data-i18n="whatsapp" >WhatsApp — coming soon</span></button>',
                '<a class="btn sqaure_bt lw-whatsapp" href="#" data-whatsapp-pending hidden><span data-i18n="contactWhatsapp">WhatsApp</span></a>',
                1,
            )
        if page in ("index.html", "it_service.html"):
            html = replace_services_section(html)
        html = translate(html, dictionary, "en")
        html = re.sub(r'<p data-i18n="illustration"[^>]*>.*?</p>', "", html)
        html = add_srcsets(html, grid=page in ("index.html", "it_service.html"))
        path.write_text(html, encoding="utf-8", newline="\n")
        print("EN  ", page, len(html))


def transform_arabic(dictionary: dict) -> None:
    ar_dir = SITE / "ar"
    ar_dir.mkdir(exist_ok=True)
    for page in PAGES:
        if page in ("privacy.html", "terms.html"):
            continue
        html = (SITE / page).read_text(encoding="utf-8")
        html = html.replace('<html lang="en" dir="ltr" data-static-lang="en">',
                            '<html lang="ar" dir="rtl" data-static-lang="ar">', 1)
        html = re.sub(r"<head>.*?</head>", lambda m: build_head(page, "ar", "../"), html, count=1, flags=re.S)
        html = re.sub(r'<header id="default_header".*?</header>',
                      lambda m: build_header(page, "ar", "../"), html, count=1, flags=re.S)
        html = re.sub(r"<footer class=\"footer_style_2\">.*?</footer>",
                      lambda m: build_footer("ar", "../"), html, count=1, flags=re.S)
        html = re.sub(r'(?:<a class="lw-whatsapp-float"[\s\S]*?)?<script src="js/content[\s\S]*?(?=</body>)',
                      lambda m: build_scripts("../", "ar"), html, count=1)
        html = translate(html, dictionary, "ar")
        html = prefix_assets(html, "../")
        (ar_dir / page).write_text(html, encoding="utf-8", newline="\n")
        print("AR  ", page, len(html))


LEGAL = {
    "privacy.html": {
        "en": [
            ("Privacy Policy", ""),
            ("Who we are", "This website is operated by Linkwave Technology (\"we\", \"us\"). This policy explains what happens to information when you visit linkwave.tech."),
            ("Information we collect", "This website does not use analytics, advertising, cookies or third-party trackers. No personal data is stored in your browser to run the site. The enquiry form performs local validation only and does not transmit or save the entries; submission stays disabled until verified contact channels and a delivery destination are published."),
            ("Contacting us", "The verified phone number published on this site (+20 127 666 8018) is the official contact channel for enquiries. Using it is voluntary. We use the details you provide only to respond to your enquiry and to follow up on the requested service."),
            ("Hosting", "The site is served by GitHub Pages and its content delivery network, which process technical request data (such as IP address and user agent) to deliver the pages and protect the service. Refer to the hosting provider's privacy statement for details."),
            ("Sharing and retention", "We do not sell or rent information. Enquiry details, once a delivery channel exists, are kept only for as long as needed to handle the request and any resulting business relationship, unless a longer period is required by law."),
            ("Your rights", "Depending on applicable law (for example Egyptian Personal Data Protection Law No. 151 of 2020 or the EU GDPR for visitors from the European Union), you may have the right to request access to, correction of, or deletion of personal data, and to object to certain processing. Use the published contact channels to exercise these rights."),
            ("Changes", "We may update this policy when the site or the applicable rules change. The date below shows the latest revision."),
            ("Latest update", "8 November 2026. Published contact channel: phone +20 127 666 8018. Verified company registration details, e-mail and address will be added once approved."),
        ],
        "ar": [
            ("سياسة الخصوصية", ""),
            ("من نحن", "هذا الموقع تشغّله لينك ويف تكنولوجي («نحن»). توضح هذه السياسة ما يحدث للمعلومات عند زيارتك للموقع linkwave.tech."),
            ("المعلومات التي نجمعها", "لا يستخدم هذا الموقع تحليلات أو إعلانات أو كوكيز أو أدوات تتبّع تابعة لجهات خارجية. لا تُخزَّن بيانات شخصية في متصفحك لتشغيل الموقع. نموذج التواصل يقوم بالتحقق المحلي فقط ولا يرسل أو يحفظ ما تكتبه؛ ويظل الإرسال معطّلًا حتى نشر قنوات تواصل معتمدة ووجهة استقبال محددة."),
            ("التواصل معنا", "رقم الهاتف المعتمد المنشور على الموقع (+20 127 666 8018) هو قناة التواصل الرسمية للاستفسارات. والتواصل معنا عبره اختياري. نستخدم البيانات التي ترسلها فقط للرد على استفسارك ومتابعة الخدمة المطلوبة."),
            ("الاستضافة", "يُقدَّم الموقع عبر GitHub Pages وشبكة توصيل المحتوى التابعة لها، والتي تعالج بيانات الطلب التقنية (مثل عنوان IP ومعرّف المتصفح) لتسليم الصفحات وحماية الخدمة. راجع بيان الخصوصية الخاص بمزوّد الاستضافة للتفاصيل."),
            ("المشاركة والاحتفاظ", "لا نبيع المعلومات أو نؤجّرها. تُحفظ تفاصيل الاستفسار، عند وجود قناة استقبال، للمدة اللازمة للتعامل مع الطلب وأي علاقة عمل ناتجة عنه، إلا إذا طلب القانون مدة أطول."),
            ("حقوقك", "حسب القانون المطبّق (مثل قانون حماية البيانات الشخصية المصري رقم 151 لسنة 2020 أو اللائحة الأوروبية GDPR لزوار الاتحاد الأوروبي)، قد يكون لك حق الوصول إلى البيانات الشخصية أو تصحيحها أو حذفها أو الاعتراض على معالجة معينة. استخدم قنوات التواصل المنشورة لممارسة هذه الحقوق."),
            ("التحديثات", "قد نحدّث هذه السياسة عند تغيّر الموقع أو القواعد المطبّقة. يوضّح التاريخ أدناه آخر مراجعة."),
            ("آخر تحديث", "8 نوفمبر 2026. القناة المنشورة: هاتف +20 127 666 8018. وستُضاف بيانات السجل التجاري الرسمية والبريد والعنوان بعد اعتمادها."),
        ],
    },
    "terms.html": {
        "en": [
            ("Terms of Use", ""),
            ("Acceptance", "By using this website you agree to these terms. If you do not agree, please stop using the site."),
            ("Informational purpose", "The content describes Linkwave Technology and its service capabilities for general information. It is not an offer, quotation, warranty or commitment. Every project is subject to a separate written agreement covering scope, site conditions, equipment, authorizations, schedule and price."),
            ("Intellectual property", "The Linkwave Technology name, logo, illustrations and site content belong to their respective owners. The page template is adapted from IT Next by html.design under its published license and keeps the required attribution in the footer. You may not copy, republish or redistribute the content without written permission, except for normal browsing and citation with attribution."),
            ("Permitted use", "You may use the site for lawful purposes only. You may not attempt to disrupt the site, gain unauthorized access, scrape it at scale, or use its content to misrepresent an affiliation with Linkwave Technology."),
            ("Third-party links", "The site may link to third-party websites. We are not responsible for their content or practices."),
            ("No warranty", "The site is provided \"as is\". While we aim for accuracy, service descriptions and illustrations are indicative, and we make no warranty that the site will be uninterrupted, error-free or complete."),
            ("Limitation of liability", "To the extent permitted by law, Linkwave Technology is not liable for indirect or consequential loss arising from use of this website. Nothing in these terms limits liability that cannot be limited by law."),
            ("Changes", "We may update these terms and the site content at any time. Continued use after a change means you accept the updated terms."),
            ("Latest update", "8 November 2026. Published contact channel: phone +20 127 666 8018. Verified company registration details, address and governing-law clause will be added once approved."),
        ],
        "ar": [
            ("شروط الاستخدام", ""),
            ("القبول", "باستخدامك هذا الموقع فإنك توافق على هذه الشروط. إذا لم توافق، يُرجى التوقف عن استخدام الموقع."),
            ("الغرض التعريفي", "يصف المحتوى لينك ويف تكنولوجي وقدراتها الخدمية لغرض التعريف العام. وهو ليس عرضًا أو عرض سعر أو ضمانًا أو التزامًا. كل مشروع يخضع لاتفاق مكتوب مستقل يغطي النطاق وظروف الموقع والمعدات والتصاريح والجدول والسعر."),
            ("الملكية الفكرية", "اسم لينك ويف تكنولوجي وشعارها ورسومها ومحتوى الموقع مملوكة لأصحابها. قالب الصفحة مُعدَّل من IT Next الخاص بـhtml.design وفق ترخيصه المنشور، مع الاحتفاظ بالإسناد المطلوب في التذييل. لا يجوز نسخ المحتوى أو إعادة نشره أو توزيعه دون إذن كتابي، عدا التصفح العادي والاقتباس مع الإسناد."),
            ("الاستخدام المسموح", "يجوز استخدام الموقع للأغراض المشروعة فقط. لا يجوز محاولة تعطيل الموقع أو الوصول غير المصرح به أو سحبه آليًا على نطاق واسع أو استخدام محتواه للإيحاء بوجود ارتباط غير حقيقي بلينك ويف تكنولوجي."),
            ("روابط الجهات الخارجية", "قد يرتبط الموقع بمواقع جهات خارجية. ولا نتحمل مسؤولية محتواها أو ممارساتها."),
            ("عدم الضمان", "يُقدَّم الموقع «كما هو». ورغم حرصنا على الدقة، فإن أوصاف الخدمات والرسوم توضيحية، ولا نضمن أن الموقع سيعمل دون انقطاع أو أخطاء أو بشكل كامل."),
            ("حدود المسؤولية", "إلى الحد الذي يسمح به القانون، لا تتحمل لينك ويف تكنولوجي مسؤولية أي خسارة غير مباشرة أو تبعية تنشأ عن استخدام هذا الموقع. ولا شيء في هذه الشروط يحدّ من مسؤولية لا يجوز الحد منها قانونًا."),
            ("التحديثات", "قد نحدّث هذه الشروط ومحتوى الموقع في أي وقت. ويُعد استمرارك في الاستخدام بعد التغيير قبولًا للشروط المحدّثة."),
            ("آخر تحديث", "8 نوفمبر 2026. القناة المنشورة: هاتف +20 127 666 8018. وستُضاف بيانات السجل التجاري الرسمية والعنوان وبند القانون الواجب التطبيق بعد اعتمادها."),
        ],
    },
}


def build_legal_page(page: str, lang: str) -> str:
    prefix = "../" if lang == "ar" else ""
    title = PAGES[page]["title_en" if lang == "en" else "title_ar"]
    sections = LEGAL[page][lang]
    body = []
    for heading, text in sections:
        body.append(f"<h2>{esc(heading)}</h2>")
        if text:
            body.append(f"<p>{esc(text)}</p>")
    html = (
        f'<!DOCTYPE html><html lang="{lang}" dir="{"rtl" if lang == "ar" else "ltr"}" data-static-lang="{lang}">'
        + build_head(page, lang, prefix)
        + f'<body id="default_theme" class="legal_page" data-page="legal">'
        '<a class="skip-link" href="#main"><span>Skip to content / تخطَّ إلى المحتوى</span></a>'
        + build_header(page, lang, prefix)
        + '<main id="main" tabindex="-1">'
        '<div id="inner_banner" class="section inner_banner_section"><div class="container">'
        '<div class="title-holder"><div class="title-holder-cell">'
        + f'<h1 class="page-title">{esc(title)}</h1>'
        + "</div></div></div></div>"
        '<section class="section padding_layout_1"><div class="container"><div class="row">'
        '<article class="col-lg-9 lw-legal">'
        + "".join(body)
        + "</article></div></div></section></main>"
        + build_footer(lang, prefix)
        + build_scripts(prefix, lang)
        + "</body></html>"
    )
    return html


def build_404() -> str:
    html = (
        '<!DOCTYPE html><html lang="en" dir="ltr" data-static-lang="en">'
        + build_head("index.html", "en", "", robots="noindex,follow",
                     title_override="Page not found | Linkwave Technology",
                     desc_override="The requested page was not found on linkwave.tech. Return to the home page or contact us.",
                     canonical_override=BASE + "/404.html", hreflang=False)
        + '<body id="default_theme" class="legal_page" data-page="notfound">'
        '<main id="main" tabindex="-1">'
        '<div id="inner_banner" class="section inner_banner_section"><div class="container">'
        '<div class="title-holder"><div class="title-holder-cell">'
        '<h1 class="page-title">Page not found · الصفحة غير موجودة</h1></div></div></div></div>'
        '<section class="section padding_layout_1"><div class="container"><div class="row">'
        '<article class="col-lg-9 lw-legal"><h2>We could not find that page</h2>'
        '<p>The link may be outdated or mistyped. Return to the home page or contact us for help.</p>'
        '<p dir="rtl" lang="ar">لم نعثر على هذه الصفحة. قد يكون الرابط قديمًا أو غير صحيح. ارجع إلى الصفحة الرئيسية أو تواصل معنا للمساعدة.</p>'
        '<p><a class="btn main_bt" href="index.html"><span>Home · الرئيسية</span></a> '
        '<a class="btn sqaure_bt" href="it_contact.html"><span>Contact · تواصل معنا</span></a></p>'
        "</article></div></div></section></main>"
        + build_footer("en", "")
        + build_scripts("")
        + "</body></html>"
    )
    return html


def build_sitemap() -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page, meta in PAGES.items():
        en = url_for("en", meta["path"])
        ar = url_for("ar", meta["path"])
        for loc in (en, ar):
            lines.append(f"<url><loc>{loc}</loc>")
            lines.append(f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/>')
            lines.append(f'<xhtml:link rel="alternate" hreflang="ar" href="{ar}"/>')
            lines.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>')
            lines.append("<lastmod>2026-11-08</lastmod></url>")
    lines.append("</urlset>")
    return "".join(lines)


def build_manifest() -> str:
    return json.dumps({
        "name": "Linkwave Technology",
        "short_name": "Linkwave",
        "description": "Telecommunications and network infrastructure services.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#0278ad",
        "icons": [
            {"src": "/favicon-32.png", "sizes": "32x32", "type": "image/png"},
            {"src": "/apple-touch-icon-180.png", "sizes": "180x180", "type": "image/png"},
        ],
    }, ensure_ascii=False)


THIRD_PARTY = """Linkwave Technology website — third-party notices
=====================================================
Template: IT Next by html.design. Adapted under the publisher's license (CC BY 3.0):
https://html.design/license/ ; attribution is kept in the footer of every page.
Bootstrap 4.0.0 (CSS): MIT License, Copyright (c) 2011-2018 The Bootstrap Authors.
https://github.com/twbs/bootstrap/blob/v4.0.0/LICENSE
Cairo font family: SIL Open Font License 1.1 (bundled at fonts/cairo/OFL.txt).
Linkwave Technology brand assets and service illustrations are proprietary company
assets used by the website owner, with rights confirmed by the owner (2026-11-08).
All rights reserved. Site development credit: AiFRAHAT.com.
All other JavaScript and CSS on this site is original to this website and carries no
third-party redistribution requirement.
"""


def cleanup() -> None:
    targets = [
        "css/custom.css",
        "css/animate.css",
        "css/font-awesome.min.css",
        "js/jquery.min.js",
        "js/bootstrap.min.js",
        "js/wow.js",
        "images/linkwave/official-emblem.png",
        "images/linkwave/mark-delivery.png",
        "fonts/fontawesome-webfont.eot",
        "fonts/fontawesome-webfont.svg",
        "fonts/fontawesome-webfont.ttf",
        "fonts/fontawesome-webfont.woff",
        "fonts/fontawesome-webfont.woff2",
        "fonts/cairo/cairo-0.ttf",
        "fonts/cairo/cairo-1.ttf",
        "fonts/cairo/cairo-2.ttf",
        "fonts/cairo/cairo-3.ttf",
        "fonts/cairo/cairo-4.ttf",
    ]
    for rel in targets:
        path = SITE / rel
        if path.exists():
            path.unlink()
    rev = SITE / "revolution"
    if rev.exists():
        shutil.rmtree(rev)


CAIRO_CSS = """/* Cairo variable-free delivery build: WOFF2 only (SIL OFL 1.1, see OFL.txt). */
@font-face{font-family:'Cairo';font-style:normal;font-weight:400;font-display:swap;src:url(../fonts/cairo/cairo-0.woff2) format('woff2');}
@font-face{font-family:'Cairo';font-style:normal;font-weight:500;font-display:swap;src:url(../fonts/cairo/cairo-1.woff2) format('woff2');}
@font-face{font-family:'Cairo';font-style:normal;font-weight:600;font-display:swap;src:url(../fonts/cairo/cairo-2.woff2) format('woff2');}
@font-face{font-family:'Cairo';font-style:normal;font-weight:700;font-display:swap;src:url(../fonts/cairo/cairo-3.woff2) format('woff2');}
@font-face{font-family:'Cairo';font-style:normal;font-weight:800;font-display:swap;src:url(../fonts/cairo/cairo-4.woff2) format('woff2');}
"""

APPEND_LINKWAVE_CSS = """

/* ---- launch-fixes: hero, language links, contact channels, legal links ---- */
.lw-hero { position:relative; height:clamp(420px,46vw,700px); overflow:hidden; background:#0b2233; direction:ltr; }
.lw-hero-track { position:absolute; inset:0; }
.lw-slide { position:absolute; inset:0; opacity:0; visibility:hidden; transition:opacity .7s ease; }
.lw-slide.is-active { opacity:1; visibility:visible; }
.lw-slide-img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.lw-slide.is-active .lw-slide-img { animation:lw-kenburns 14s linear forwards; }
.lw-hero.is-paused .lw-slide-img { animation-play-state:paused; }
.lw-shade { position:absolute; inset:0; background:linear-gradient(180deg,rgba(0,0,0,.18),rgba(0,0,0,.52)); }
.lw-hero-caption { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; width:min(900px,88vw); }
.lw-hero-title { margin:0; background:#0278ad; color:#fff; font-weight:800; font-size:clamp(24px,4.4vw,52px); line-height:1.35; padding:18px 26px; }
.lw-hero-sub { margin:14px auto 0; color:#fff; font-weight:500; font-size:clamp(15px,1.6vw,19px); text-shadow:0 1px 4px rgba(0,0,0,.6); max-width:760px; }
.lw-hero-controls { position:absolute; inset-inline:0; bottom:18px; display:flex; align-items:center; justify-content:center; gap:14px; padding-inline:16px; direction:ltr; }
.lw-hero-arrow, .lw-hero-pause { min-width:44px; min-height:44px; border:0; border-radius:9999px; background:rgba(255,255,255,.92); color:#111; font-weight:700; cursor:pointer; }
.lw-hero-arrow span[aria-hidden] { font-size:22px; line-height:1; }
.lw-hero-pause { padding-inline:16px; font-size:13px; white-space:nowrap; }
.lw-hero-bullets { display:flex; gap:8px; }
.lw-bullet { width:44px; height:44px; border:0; background:transparent; cursor:pointer; display:grid; place-items:center; }
.lw-bullet span { width:12px; height:12px; border-radius:50%; background:rgba(255,255,255,.55); }
.lw-bullet[aria-current=true] span { background:#fff; box-shadow:0 0 0 2px #0278ad; }
.lw-hero-cta { display:flex; justify-content:center; padding-block:26px; }
@keyframes lw-kenburns { from{transform:scale(1)} to{transform:scale(1.07)} }
[dir=rtl] .lw-hero-title, [dir=rtl] .lw-hero-sub { direction:rtl; }
.language-switch a { border:0; background:transparent; color:#333; padding:8px; min-width:44px; min-height:44px; display:inline-flex; align-items:center; justify-content:center; text-decoration:none; }
.language-switch a.is-active { color:#006899; font-weight:700; border-bottom:2px solid var(--lw-blue); }
.lw-contact-channels { display:flex; flex-direction:column; gap:8px; margin-block:12px; }
.lw-contact-direct { margin-block:10px; color:#595959; }
.lw-contact-direct .lw-contact-link { color:#006899; font-weight:700; }
.footer_style_2 .lw-contact-direct { color:#c9d6dd; }
.footer_style_2 .lw-contact-direct .lw-contact-link { color:#fff; }
.lw-owner { display:inline-block; margin-inline-start:8px; }
.lw-owner a { color:#fff; text-decoration:underline; }
.cprt .lw-credit, .cprt .lw-owner { white-space:nowrap; }
.lw-contact-link { color:#006899; font-weight:600; }
.lw-contact-address { color:#595959; }
.lw-legal-links { margin-inline:8px; }
.lw-legal-links a { color:#fff; text-decoration:underline; }
.lw-whatsapp { margin-inline-start:8px; }
.lw-req { color:#a84a00; font-weight:700; }
.lw-req-note { color:#595959; font-size:14px; }
.lw-legal h2 { margin-top:28px; font-size:22px; }
.lw-legal p { margin-block:10px; color:#4a4a4a; }
.lw-legal { padding-block:10px; }
@media(max-width:575px){ .lw-hero { height:380px; } .lw-hero-caption { width:92vw; } .lw-hero-title { padding:12px 16px; } .lw-hero-controls { gap:8px; bottom:12px; } .lw-hero-pause { padding-inline:10px; font-size:12px; } .lw-bullet { width:36px; } }
@media(prefers-reduced-motion:reduce){ .lw-slide-img { animation:none!important; } .lw-slide { transition:none; } #lw-pause { display:none; } }
"""

TEN_SERVICES_CSS = """
/* ---- ten-service alternating rows (launch-fixes: unified services) ---- */
.lw-services-section .main_heading, .lw-services-business .main_heading { margin-bottom: clamp(20px, 3vw, 36px); }
.lw-services-group { display: block; }
.lw-service-row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: clamp(20px, 4vw, 56px); align-items: center; padding-block: clamp(22px, 3vw, 40px); }
.lw-service-row + .lw-service-row { border-top: 1px solid #e7eff4; }
.lw-service-row__media { grid-column: 1; min-width: 0; }
.lw-service-row__media, .lw-service-row__body { grid-row: 1; }
.lw-service-row__body { grid-column: 2; min-width: 0; }
.lw-service-row:nth-child(even) .lw-service-row__media { grid-column: 2; }
.lw-service-row:nth-child(even) .lw-service-row__body { grid-column: 1; }
.lw-service-row__img { width: 100%; height: auto; aspect-ratio: 1000 / 563; object-fit: cover;
  display: block; border-radius: 18px; background: #eaf2f6; }
.lw-service-row__index { display: inline-block; font-weight: 800; font-size: 14px; letter-spacing: .08em;
  color: var(--lw-blue); margin-bottom: 6px; }
.lw-service-row__body h3 { margin: 0 0 10px; font-size: clamp(20px, 2.2vw, 28px); line-height: 1.4; }
.lw-service-row__desc { color: #595959; margin: 0 0 12px; }
.lw-service-row__list { margin: 0 0 18px; padding-inline-start: 20px; }
.lw-service-row__list li { margin-block: 6px; color: #4a4a4a; }
.lw-services__more { display: flex; justify-content: center; margin-top: clamp(24px, 3vw, 36px); }
.lw-services-business { border-top: 1px solid #e7eff4; }
.lw-process { margin: 0 0 16px; padding-inline-start: 20px; list-style: decimal; }
.lw-process li { margin-block: 6px; color: #4a4a4a; }
.lw-service-cta { margin-top: 22px; }
.lw-sidebar-more { margin-top: 16px; }
.lw-sidebar-more a { color: #006899; font-weight: 600; }
@media (max-width: 1199px) { #navbar_menu > ul > li > a { padding-inline: 12px; font-size: 13px; } }
@media (max-width: 767px) {
  .lw-service-row { grid-template-columns: 1fr; gap: 16px; padding-block: 22px; }
  .lw-service-row__media, .lw-service-row__body,
  .lw-service-row:nth-child(even) .lw-service-row__media,
  .lw-service-row:nth-child(even) .lw-service-row__body { grid-column: 1; grid-row: auto; }
  .lw-service-row__img { border-radius: 14px; }
  .lw-service-row__body h3 { font-size: 21px; }
}
.lw-hero-cta-btn { margin-top: 18px; }
.lw-hero-caption .lw-hero-sub { margin-bottom: 4px; }
.lw-slide-img--deferred { background: #0b2233; }
[dir=rtl] .lw-hero-cta-btn { direction: rtl; }
.lw-whatsapp-float { position: fixed; right: 18px; bottom: calc(18px + env(safe-area-inset-bottom, 0px));
  z-index: 1200; display: inline-flex; align-items: center; justify-content: center;
  width: 56px; height: 56px; border-radius: 50%; background: #128C7E; color: #fff;
  box-shadow: 0 8px 22px rgba(0, 0, 0, .28); text-decoration: none;
  transition: transform .18s ease, box-shadow .18s ease, background-color .18s ease; }
.lw-whatsapp-float:hover { transform: translateY(-2px); box-shadow: 0 12px 26px rgba(0, 0, 0, .32); background: #0f7a6d; }
.lw-whatsapp-float:focus-visible { outline: 3px solid #a84a00; outline-offset: 4px; }
.lw-whatsapp-float, .lw-whatsapp-float:hover, .lw-whatsapp-float:focus,
.lw-whatsapp-float:focus-visible, .lw-whatsapp-float:active { color: #fff; }
.lw-whatsapp-float svg { display: block; }
.lw-hp { position: absolute !important; width: 1px !important; height: 1px !important;
  padding: 0 !important; margin: -1px !important; overflow: hidden !important;
  clip: rect(0 0 0 0) !important; white-space: nowrap !important; border: 0 !important; }
#quote-form [aria-busy="true"] { opacity: .7; cursor: progress; }
@media (max-width: 575px) {
  .lw-whatsapp-float { width: 50px; height: 50px; right: 14px; bottom: calc(14px + env(safe-area-inset-bottom, 0px)); }
}
@media (prefers-reduced-motion: reduce) {
  .lw-service-row { transition: none !important; }
  .lw-whatsapp-float { transition: none; }
  .lw-whatsapp-float:hover { transform: none; }
}
"""

APPEND_REFINEMENT_CSS = """

/* ---- launch-fixes: accessibility, contrast, no-JS navigation ---- */
#main p.large, p.large { color:#595959; }
.language-switch a, .language-switch a.is-active { border-radius:9999px; min-height:44px; }
.language-switch a.is-active { box-shadow:inset 0 0 0 1px #0278ad; border-bottom:0; background:#eff8fc; }
[dir=rtl] .breadcrumb > li + li::before { content:'\\2039'; }
[dir=rtl] .lw-hero-title, [dir=rtl] .lw-hero-sub { text-align:center; }
.lw-slide-img { max-width:100%; }
/* ---- unified rounded buttons + hover feedback ---- */
body .btn, body a.btn, body .btn.main_bt, body .btn.sqaure_bt, body .btn.white_btn,
body button, body button.btn, body .lw-menu-toggle, body .lw-hero-arrow,
body .lw-hero-pause, body .lw-bullet, body .language-switch a,
#navbar_menu > ul > li > a { border-radius:9999px; }
body .btn, body button, body .lw-menu-toggle, body .lw-hero-arrow,
body .lw-hero-pause, body .language-switch a, #navbar_menu > ul > li > a {
 transition: background-color .2s ease, color .2s ease, transform .2s ease,
             box-shadow .2s ease, border-color .2s ease;
}
@media (hover:hover) {
 body .btn:hover, body button:hover:not(:disabled), body .lw-menu-toggle:hover,
 body .language-switch a:hover, #navbar_menu > ul > li > a:hover {
   transform:translateY(-2px); box-shadow:0 8px 18px rgba(2,120,173,.28);
 }
 body .btn.main_bt:hover, body a.btn.main_bt:hover, body button.btn.main_bt:hover,
 body .btn.sqaure_bt:hover { background:#00547c; color:#fff; }
 body .btn.white_btn:hover { background:#e8f6fd; color:#00547c; box-shadow:0 8px 18px rgba(255,255,255,.18); }
 body .lw-menu-toggle:hover { background:#eff8fc; }
 body #navbar_menu > ul > li > a:hover { background:#eff8fc; }
 body .lw-hero-arrow:hover, body .lw-hero-pause:hover { background:#fff; }
 body .lw-bullet:hover span { background:#fff; box-shadow:0 0 0 2px #0278ad; }
}
body .btn:active, body button:active:not(:disabled) { transform:translateY(0); box-shadow:none; }
@media (prefers-reduced-motion: reduce) {
 body .btn, body button, body .lw-menu-toggle, body .lw-hero-arrow,
 body .lw-hero-pause, body .language-switch a, #navbar_menu > ul > li > a { transition:none; }
 body .btn:hover, body button:hover, body .btn:active, body button:active { transform:none; }
}
"""


CSS_MINIFY_FILES = ("cairo.css", "style.css", "responsive.css", "colors1.css", "linkwave.css", "refinement.css")


def minify_css(css: str) -> str:
    """Conservative CSS minifier: strip comments (except /*! licenses) and collapse
    whitespace outside strings. No token characters are removed, so values such as
    calc(100% - 10px), data URIs, custom properties and selectors stay intact."""
    out = []
    i = 0
    n = len(css)
    quote = None
    while i < n:
        ch = css[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(css[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "'\"":
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and css[i + 1] == "*":
            end = css.find("*/", i + 2)
            if end == -1:
                break
            comment = css[i:end + 2]
            if comment.startswith("/*!"):
                out.append(comment)
            i = end + 2
            continue
        if ch.isspace():
            j = i
            while j < n and css[j].isspace():
                j += 1
            prev = out[-1] if out else ""
            nxt = css[j] if j < n else ""
            if prev and prev not in "{};," and nxt not in "{};,":
                out.append(" ")
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def update_css() -> None:
    artifacts = Path(__file__).resolve().parent / "artifacts"
    for name in ("linkwave.js", "site-config.js"):
        shutil.copyfile(artifacts / name, SITE / "js" / name)

    style = SITE / "css" / "style.css"
    text = style.read_text(encoding="utf-8")
    text = text.replace("@import url(animate.css);\n", "").replace("@import url(animate.css);", "")
    text = text.replace("@import url(font-awesome.min.css);\n", "").replace("@import url(font-awesome.min.css);", "")
    style.write_text(text, encoding="utf-8", newline="\n")

    (SITE / "css" / "cairo.css").write_text(CAIRO_CSS, encoding="utf-8", newline="\n")

    linkwave = SITE / "css" / "linkwave.css"
    text = linkwave.read_text(encoding="utf-8")
    text = text.replace(
        "url('../images/linkwave/hero.webp')",
        "url('../images/linkwave/hero-banner-1440.webp')",
    )
    linkwave.write_text(text + APPEND_LINKWAVE_CSS + TEN_SERVICES_CSS, encoding="utf-8", newline="\n")

    refinement = SITE / "css" / "refinement.css"
    refinement.write_text(
        refinement.read_text(encoding="utf-8") + APPEND_REFINEMENT_CSS,
        encoding="utf-8",
        newline="\n",
    )

    for css_name in CSS_MINIFY_FILES:
        css_path = SITE / "css" / css_name
        css_path.write_text(minify_css(css_path.read_text(encoding="utf-8")),
                            encoding="utf-8", newline="\n")


def main() -> None:
    dictionary = update_dictionary()
    update_css()
    transform_english(dictionary)
    transform_arabic(dictionary)
    for page in ("privacy.html", "terms.html"):
        (SITE / page).write_text(translate(build_legal_page(page, "en"), dictionary, "en"),
                                 encoding="utf-8", newline="\n")
        (SITE / "ar" / page).write_text(translate(build_legal_page(page, "ar"), dictionary, "ar"),
                                        encoding="utf-8", newline="\n")
        print("LEGAL", page)
    (SITE / "404.html").write_text(translate(build_404(), dictionary, "en"), encoding="utf-8", newline="\n")
    (SITE / "sitemap.xml").write_text(build_sitemap(), encoding="utf-8", newline="\n")
    (SITE / "site.webmanifest").write_text(build_manifest(), encoding="utf-8", newline="\n")
    (SITE / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://linkwave.tech/sitemap.xml\n",
        encoding="utf-8",
        newline="\n",
    )
    (SITE / "THIRD-PARTY-NOTICES.txt").write_text(THIRD_PARTY, encoding="utf-8", newline="\n")
    cleanup()
    print("BUILD DONE")


if __name__ == "__main__":
    main()
