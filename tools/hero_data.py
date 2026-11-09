# -*- coding: utf-8 -*-
"""Approved six-slide homepage hero data (EN/AR) for the Linkwave website.

Maps the previously approved three-slide content into six thematic slides:
01 Telecom & Fiber (keeps the original "Connecting the Future" hero image),
02 Networks & Data Centers (keeps the original data-center image theme),
03 Voice & UC, 04 Security & ELV, 05 Business IT, 06 Smart Home & Wi-Fi.

Existing slide CTA destination is a real route in the project; no route is invented.
"""

HERO_SLIDES = [
    {
        "image": "hero",
        "route": "service-telecom.html",
        "title_en": "Building the Future of Connectivity",
        "title_ar": "نبني مستقبل الاتصالات",
        "sub_en": "Telecom infrastructure, civil works, fiber optics and FTTH.",
        "sub_ar": "بنية اتصالات وأعمال مدنية وفايبر وخدمات FTTH.",
        "cta_en": "Explore Telecom Solutions",
        "cta_ar": "اكتشف حلول الاتصالات",
    },
    {
        "image": "hero-datacenter",
        "route": "service-datacenter.html",
        "title_en": "Powering Connected Infrastructure",
        "title_ar": "بنية تحتية تربط أعمالك بالمستقبل",
        "sub_en": "LAN/WAN networks, structured cabling, server rooms, data centers and UPS.",
        "sub_ar": "شبكات LAN/WAN وكابلات منظمة وغرف سيرفرات ومراكز بيانات وأنظمة UPS.",
        "cta_en": "Explore Infrastructure",
        "cta_ar": "اكتشف البنية التحتية",
    },
    {
        "image": "hero-voice",
        "route": "service-voice.html",
        "title_en": "Communication Without Boundaries",
        "title_ar": "اتصالات بلا حدود",
        "sub_en": "IP telephony, enterprise voice systems and unified communications.",
        "sub_ar": "تليفونات IP وأنظمة صوتية للمؤسسات واتصالات موحّدة.",
        "cta_en": "Explore Communication Solutions",
        "cta_ar": "اكتشف حلول الاتصالات الموحدة",
    },
    {
        "image": "hero-security",
        "route": "service-security.html",
        "title_en": "Intelligent Security. Complete Confidence.",
        "title_ar": "أنظمة أمن ذكية لحماية ما يهمك",
        "sub_en": "CCTV, access control, ELV, surveillance and security infrastructure.",
        "sub_ar": "كاميرات مراقبة وتحكم في الدخول وأنظمة ELV ومراقبة وبنية أمنية.",
        "cta_en": "Explore Security Solutions",
        "cta_ar": "اكتشف الحلول الأمنية",
    },
    {
        "image": "hero-business",
        "route": "service-business-it.html",
        "title_en": "Technology That Moves Business Forward",
        "title_ar": "تكنولوجيا تدفع أعمالك للأمام",
        "sub_en": "Small business IT, office networking, Wi-Fi and workplace connectivity.",
        "sub_ar": "تكنولوجيا المعلومات للشركات الصغيرة وشبكات المكاتب والواي فاي وربط بيئة العمل.",
        "cta_en": "Explore Business Solutions",
        "cta_ar": "اكتشف حلول الشركات",
    },
    {
        "image": "hero-home",
        "route": "service-home-network.html",
        "title_en": "Smarter Homes. Seamless Connectivity.",
        "title_ar": "منازل أذكى واتصال بلا انقطاع",
        "sub_en": "Home networking, smart home infrastructure, automation and residential connectivity.",
        "sub_ar": "شبكات منزلية وبنية منازل ذكية وتحكم آلي واتصال سكني.",
        "cta_en": "Explore Home Solutions",
        "cta_ar": "اكتشف حلول المنازل",
    },
]

# Published company phone (digits only, E.164 without +). WhatsApp authorisation is
# UNVERIFIED: the number is the verified published phone, but WhatsApp capability must
# be confirmed by the owner before treating the destination as verified.
WHATSAPP_NUMBER = "201276668018"
WHATSAPP_LABELS = {
    "en": "Contact Linkwave on WhatsApp",
    "ar": "تواصل مع لينك ويف عبر واتساب",
}
