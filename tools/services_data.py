# -*- coding: utf-8 -*-
"""Ten-service data model for the Linkwave Technology website.

Source of truth for:
  * the four NEW services (07–10) and their Bilingual (EN/AR) content,
  * the "Business & Home Solutions" landing page,
  * shared labels used by the alternating service rows.

The generator (`release_build.py`) consumes this module to build:
  * the unified 10-row services component (homepage + services overview),
  * the landing page `business-home.html` (+ AR mirror),
  * the four new service detail pages (+ AR mirrors),
  * dictionary keys injected into `js/content.js`,
  * sitemap entries through the shared PAGES registry.

Existing six services are intentionally NOT redefined here: their EN copy stays
in the project's baseline `js/content.js`, and their AR copy stays in
`ar_egyptian.py`. This file only adds what is new.
"""

# ---- Shared labels -----------------------------------------------------------

SHARED_LABELS = {
    "business": ("Business & Home", "الشركات والمنازل"),
    "bhTitle": ("Business & Home Solutions", "حلول الشركات والمنازل"),
    "siteSurvey": ("Request a Site Survey", "طلب معاينة موقع"),
    "equipmentHeading": ("Equipment & Infrastructure", "المعدات والبنية التحتية"),
    "processHeading": ("Implementation Process", "خطوات التنفيذ"),
    "targetHeading": ("Target Customers", "العملاء المستهدفون"),
    "notesHeading": ("Implementation Notes", "ملاحظات التنفيذ"),
    "securityHeading": ("Security Requirements", "متطلبات الأمان"),
    "relatedHeading": ("Related services", "خدمات ذات صلة"),
    "viewAllBusiness": ("Explore Business & Home", "اتعرّف على حلول الشركات والمنازل"),
    "placeholderNote": (
        "Placeholder image used for local review — the real installation photo must be supplied before publication.",
        "صورة مؤقتة لمراجعة محلية — لازم تتوفر صورة التركيب الحقيقية قبل النشر.",
    ),
}

LANDING = {
    "route": "business-home.html",
    "nav": "business",
    "title_en": "Business & Home Solutions | Linkwave Technology",
    "desc_en": (
        "IT, networking, Wi-Fi, smart home and security infrastructure services for small businesses "
        "and modern homes from Linkwave Technology."
    ),
    "title_ar": "حلول الشركات والمنازل | لينك ويف تكنولوجي",
    "desc_ar": (
        "حلول متكاملة لتوريد وتركيب وتجهيز البنية التحتية التقنية والشبكات والأنظمة الذكية "
        "والأمنية للشركات والمنازل من لينك ويف تكنولوجي."
    ),
    "intro_en": (
        "Professional IT, networking, automation and security infrastructure "
        "for businesses and modern homes."
    ),
    "intro_ar": (
        "حلول متكاملة لتوريد وتركيب وتجهيز البنية التحتية التقنية والشبكات "
        "والأنظمة الذكية والأمنية للشركات والمنازل."
    ),
}


def _meta(en_title, en_desc, ar_title, ar_desc):
    return dict(title_en=en_title, desc_en=en_desc, title_ar=ar_title, desc_ar=ar_desc)


NEW_SERVICES = [
    {
        "key": "bizit",
        "number": 7,
        "route": "service-business-it.html",
        "image": "business-it",
        "meta": _meta(
            "Small Business IT Infrastructure | Linkwave",
            "IT infrastructure supply and installation for SMEs: structured cabling, network equipment, "
            "workstations, Wi-Fi, UPS and ongoing testing and maintenance.",
            "البنية التحتية لتكنولوجيا المعلومات للشركات الصغيرة | لينك ويف",
            "توريد وتركيب بنية تحتية لتكنولوجيا المعلومات للشركات الصغيرة والمتوسطة: كابلات منظمة "
            "ومعدات شبكة ومحطات عمل وWi-Fi وUPS واختبار وصيانة.",
        ),
        "en": {
            "title": "Small Business IT Infrastructure",
            "hero": "Complete IT Infrastructure for Your Business",
            "desc": (
                "Professional supply, installation, testing and commissioning of IT infrastructure "
                "for small and medium-sized businesses."
            ),
            "alt": "Technician installing network cabling in a server rack at a modern office",
            "bullets": [
                "Structured Cabling: Cat6/Cat6A, network outlets and patch panels.",
                "Network Equipment: routers, switches, racks and access points.",
                "Workstations: desktops, laptops, monitors and printers.",
                "Power & UPS: UPS systems, PDUs and cable management.",
                "Office Wi-Fi design, installation and configuration.",
                "Infrastructure testing, troubleshooting and maintenance.",
            ],
            "equipment": [
                "Structured cabling, network outlets and patch panels (Cat6/Cat6A).",
                "Racks, network cabinets, switches, routers and access points.",
                "Workstations, printers, UPS systems and PDUs.",
                "Wi-Fi coverage and PoE equipment for the office layout.",
            ],
            "process": [
                "Site survey and requirements gathering.",
                "Network and infrastructure design.",
                "Equipment supply and staging.",
                "Installation and cabling.",
                "Testing, configuration and commissioning.",
                "Documentation and handover.",
            ],
            "target": "Offices, clinics, retail stores, SMEs and new business branches.",
            "notes": [],
            "security": [],
        },
        "ar": {
            "title": "البنية التحتية لتكنولوجيا المعلومات للشركات الصغيرة والمتوسطة",
            "hero": "بنية تحتية متكاملة لتكنولوجيا المعلومات لشركتك",
            "desc": (
                "توريد وتركيب واختبار وتشغيل بنية تحتية متكاملة لتكنولوجيا المعلومات "
                "للشركات الصغيرة والمتوسطة."
            ),
            "alt": "فني بيركّب كابلات شبكة في راك سيرفرات داخل مكتب حديث",
            "bullets": [
                "كابلات منظمة Cat6/Cat6A ومخارج شبكة وباتش بانل.",
                "معدات شبكة: راوترات وسويتشات وراكات وAccess Points.",
                "محطات عمل: ديسكتوب ولابتوب وشاشات وطابعات.",
                "طاقة وUPS: أنظمة UPS وPDUs وتنظيم الكابلات.",
                "تصميم وتركيب وإعداد Wi-Fi للمكتب.",
                "اختبار البنية التحتية وحل المشاكل وصيانتها.",
            ],
            "equipment": [
                "كابلات منظمة ومخارج شبكة وباتش بانل (Cat6/Cat6A).",
                "راكات وكابينات شبكة وسويتشات وراوترات وAccess Points.",
                "محطات عمل وطابعات وأنظمة UPS وPDUs.",
                "تغطية Wi-Fi ومعدات PoE حسب تخطيط المكتب.",
            ],
            "process": [
                "معاينة الموقع وتحديد المتطلبات.",
                "تصميم الشبكة والبنية التحتية.",
                "توريد المعدات وتجهيزها.",
                "التركيب وتمديد الكابلات.",
                "الاختبار والإعداد والتشغيل.",
                "التوثيق والتسليم.",
            ],
            "target": "مكاتب وعيادات ومتاجر وشركات صغيرة ومتوسطة وفروع جديدة.",
            "notes": [],
            "security": [],
        },
    },
    {
        "key": "homenet",
        "number": 8,
        "route": "service-home-network.html",
        "image": "home-network",
        "meta": _meta(
            "Home Networking & Wi-Fi Infrastructure | Linkwave",
            "Professional home network design, structured cabling, mesh Wi-Fi, network cabinets, PoE "
            "and outdoor coverage for reliable connectivity throughout the home.",
            "الشبكات المنزلية وأنظمة الواي فاي | لينك ويف",
            "تصميم شبكة منزلية احترافي وكابلات منظمة وWi-Fi Mesh وكابينات شبكة وPoE وتغطية خارجية "
            "لاثصال ثابت في كل حتة في البيت.",
        ),
        "en": {
            "title": "Home Networking & Wi-Fi Infrastructure",
            "hero": "Reliable Connectivity Throughout Your Home",
            "desc": (
                "Reliable home connectivity through professional network planning, structured cabling "
                "and Wi-Fi installation."
            ),
            "alt": "Technician installing a ceiling Wi-Fi access point in a modern home",
            "bullets": [
                "Home network design and site survey.",
                "Wi-Fi routers, access points and Mesh systems.",
                "Cat6/Cat6A structured cabling, RJ45 outlets and patch panels.",
                "Network cabinets, switches and PoE equipment.",
                "Outdoor Wi-Fi for gardens, terraces and suitable outdoor areas.",
                "Network connections for Smart TVs, gaming consoles and home cameras.",
                "Network testing, troubleshooting and maintenance.",
            ],
            "equipment": [
                "Routers, access points, Mesh nodes and PoE switches.",
                "Structured cabling, RJ45 outlets, patch panels and network cabinets.",
                "Outdoor access points for gardens and terraces where suitable.",
                "Cabling and connectivity for smart TVs, consoles and home cameras.",
            ],
            "process": [
                "Site survey and coverage assessment.",
                "Home network and Wi-Fi design.",
                "Structured cabling installation.",
                "Equipment installation and cabinet setup.",
                "Wi-Fi configuration and roaming testing.",
                "Handover and maintenance guidance.",
            ],
            "target": "Villas, apartments, duplexes and home offices.",
            "notes": [],
            "security": [],
        },
        "ar": {
            "title": "الشبكات المنزلية وأنظمة الواي فاي",
            "hero": "اتصال ثابت في كل حتة في بيتك",
            "desc": (
                "اتصال إنترنت ثابت في البيت من خلال تصميم شبكة احترافي وكابلات منظمة وتركيب Wi-Fi."
            ),
            "alt": "فني بيركّب Access Point للواي فاي في سقف بيت حديث",
            "bullets": [
                "تصميم شبكة المنزل ومعاينة الموقع.",
                "راوترات Wi-Fi وAccess Points وأنظمة Mesh.",
                "كابلات منظمة Cat6/Cat6A ومخارج RJ45 وباتش بانل.",
                "كابينات شبكة وسويتشات ومعدات PoE.",
                "Wi-Fi خارجي للحدائق والتراسات والمساحات المناسبة.",
                "توصيلات شبكة للتلفزيونات الذكية وأجهزة الألعاب وكاميرات المنزل.",
                "اختبار الشبكة وحل المشاكل وصيانتها.",
            ],
            "equipment": [
                "راوترات وAccess Points وعقد Mesh وسويتشات PoE.",
                "كابلات منظمة ومخارج RJ45 وباتش بانل وكابينات شبكة.",
                "Access Points خارجية للحدائق والتراسات عند ملاءمة الموقع.",
                "توصيلات للتلفزيونات الذكية وأجهزة الألعاب وكاميرات المنزل.",
            ],
            "process": [
                "معاينة الموقع وتقييم التغطية.",
                "تصميم شبكة المنزل وWi-Fi.",
                "تمديد الكابلات المنظمة.",
                "تركيب المعدات وتجهيز الكابينة.",
                "إعداد Wi-Fi واختبار التجوال.",
                "التسليم وإرشادات الصيانة.",
            ],
            "target": "فيلات وشقق ودوبلكس ومكاتب منزلية.",
            "notes": [],
            "security": [],
        },
    },
    {
        "key": "smarthome",
        "number": 9,
        "route": "service-smart-home.html",
        "image": "smart-home",
        "meta": _meta(
            "Smart Home Infrastructure & Automation | Linkwave",
            "Smart home infrastructure planning, supply and implementation with compatible lighting, "
            "curtains, climate and sensor automation solutions.",
            "البنية التحتية للمنازل الذكية وأنظمة التحكم الآلي | لينك ويف",
            "تخطيط وتوريد وتنفيذ البنية التحتية للمنازل الذكية مع حلول إضاءة وستائر وتكييف وحساسات "
            "تحكم آلي متوافقة.",
        ),
        "en": {
            "title": "Smart Home Infrastructure & Automation",
            "hero": "Smarter Living Starts with Better Infrastructure",
            "desc": (
                "Planning, supplying and implementing smart home infrastructure and compatible "
                "automation solutions."
            ),
            "alt": "Smart home control panel and mobile app controlling lighting, climate and security",
            "bullets": [
                "Smart home planning and infrastructure.",
                "Smart lighting, switches, dimmers and relays.",
                "Smart curtains and motorized blinds.",
                "Compatible air conditioning and climate controls.",
                "Motion, door/window, water-leak and temperature sensors.",
                "Smart gateways, hubs and control panels.",
                "Automation scenarios: Home, Away and Night.",
                "Testing, handover and maintenance.",
            ],
            "equipment": [
                "Smart gateways, hubs and control panels.",
                "Smart lighting modules, dimmers, switches and relays.",
                "Motorized curtain and blind controllers.",
                "Sensors for motion, doors/windows, water leaks and temperature.",
                "Compatible climate and air-conditioning interfaces (subject to equipment compatibility).",
            ],
            "process": [
                "Site survey and smart-home requirements.",
                "Infrastructure and device design.",
                "Compatibility verification with existing equipment.",
                "Supply and installation by qualified teams.",
                "Programming, scenarios and testing.",
                "Handover and maintenance.",
            ],
            "target": "New homes, villas, apartments, renovation projects and home offices.",
            "notes": [
                "Wired or wireless approaches depend on site conditions.",
                "Equipment compatibility is verified before any integration is specified.",
                "Electrical work must be performed by qualified personnel.",
                "Universal compatibility is not promised.",
            ],
            "security": [],
        },
        "ar": {
            "title": "البنية التحتية للمنازل الذكية وأنظمة التحكم الآلي",
            "hero": "حياة أذكى بتبدأ ببنية تحتية أفضل",
            "desc": (
                "تخطيط وتوريد وتنفيذ البنية التحتية للمنازل الذكية وحلول التحكم الآلي المتوافقة."
            ),
            "alt": "لوحة تحكم منزل ذكي وتطبيق موبايل بيتحكم في الإضاءة والتكييف والأمان",
            "bullets": [
                "تخطيط البنية التحتية للمنزل الذكي.",
                "إضاءة ذكية ومفاتيح ودايمرات وريلايات.",
                "ستائر ذكية وموتورات للستائر.",
                "تكييف وتحكم في المناخ متوافق.",
                "حساسات حركة وأبواب/شبابيك وتسريب مياه وحرارة.",
                "بوابات ذكية (Gateways) وHubs ولوحات تحكم.",
                "سيناريوهات تحكم: البيت، خارج البيت، الليل.",
                "اختبار وتسليم وصيانة.",
            ],
            "equipment": [
                "بوابات ذكية (Gateways) وHubs ولوحات تحكم.",
                "وحدات إضاءة ذكية ودايمرات ومفاتيح وريلايات.",
                "وحدات تحكم في الستائر والموتورات.",
                "حساسات حركة وأبواب/شبابيك وتسريب مياه وحرارة.",
                "واجهات تكييف وتحكم في المناخ المتوافقة (حسب توافق المعدات).",
            ],
            "process": [
                "معاينة الموقع وتحديد متطلبات المنزل الذكي.",
                "تصميم البنية التحتية والأجهزة.",
                "التحقق من التوافق مع المعدات الموجودة.",
                "التوريد والتركيب بواسطة فنيين مؤهلين.",
                "البرمجة والسيناريوهات والاختبار.",
                "التسليم والصيانة.",
            ],
            "target": "بيوت جديدة وفيلات وشقق ومشروعات تجديد ومكاتب منزلية.",
            "notes": [
                "اختيار الحل السلكي أو اللاسلكي حسب ظروف الموقع.",
                "بنتحقق من توافق المعدات قبل تحديد أي تكامل.",
                "أعمال الكهرباء تُنفَّذ بواسطة فنيين مؤهلين فقط.",
                "مش بنوعد بتوافق شامل مع كل الأجهزة.",
            ],
            "security": [],
        },
    },
    {
        "key": "homesec",
        "number": 10,
        "route": "service-home-security.html",
        "image": "home-security",
        "meta": _meta(
            "Home & Small Business Security Infrastructure | Linkwave",
            "CCTV, access control, intercom and alarm infrastructure for homes and small businesses, "
            "installed and commissioned by Linkwave Technology.",
            "أنظمة الأمن والمراقبة للمنازل والشركات الصغيرة | لينك ويف",
            "بنية تحتية للكاميرات والتحكم في الدخول والإنتركم والإنذار للمنازل والشركات الصغيرة، "
            "بتركيب وتشغيل من لينك ويف تكنولوجي.",
        ),
        "en": {
            "title": "Home & Small Business Security Infrastructure",
            "hero": "Protect What Matters Most",
            "desc": (
                "Supply, installation and commissioning of security, surveillance and controlled-entry "
                "infrastructure for homes and small businesses."
            ),
            "alt": "Technician installing an outdoor CCTV camera with a recording rack and monitoring screen",
            "bullets": [
                "CCTV surveillance: IP/Analog, Dome/Bullet, indoor/outdoor cameras.",
                "Video recording and storage: NVR/DVR, storage planning and retention requirements.",
                "Access control: cards, fingerprint, PIN, electric locks and exit buttons.",
                "Video intercom and door entry.",
                "Intrusion and alarm systems.",
                "Security cabling and power: appropriate cabling, PoE, UPS and cabinets.",
                "Secure remote monitoring and mobile access.",
                "Testing, maintenance and upgrades.",
            ],
            "equipment": [
                "IP and analog cameras (dome/bullet, indoor/outdoor as required).",
                "NVR/DVR recording units and storage sized to retention requirements.",
                "Access-control readers, electric locks, exit buttons and controllers.",
                "Video intercom and door-entry units.",
                "Alarm panel, sensors, cabling, PoE and UPS backup.",
            ],
            "process": [
                "Site survey and camera/access-point placement.",
                "Security design and retention planning.",
                "Supply and installation.",
                "Configuration, testing and remote-access setup.",
                "Privacy and placement checks.",
                "Handover, credentials transfer and maintenance.",
            ],
            "target": "Homes, villas, small businesses, retail stores, clinics and offices.",
            "notes": [],
            "security": [
                "No default passwords in delivered systems.",
                "No direct public exposure of NVR/DVR management interfaces.",
                "Use appropriate access controls and secure remote access.",
                "Respect privacy and authorized camera placement.",
                "Securely hand over administrator credentials.",
            ],
        },
        "ar": {
            "title": "أنظمة الأمن والمراقبة للمنازل والشركات الصغيرة",
            "hero": "احمي اللي يهمك",
            "desc": (
                "توريد وتركيب وتشغيل بنية تحتية للأمن والمراقبة والتحكم في الدخول للمنازل "
                "والشركات الصغيرة."
            ),
            "alt": "فني بيركّب كاميرا مراقبة خارجية مع راك تسجيل وشاشة مراقبة",
            "bullets": [
                "كاميرات مراقبة: IP/Analog وDome/Bullet وداخلي/خارجي.",
                "تسجيل وتخزين: NVR/DVR وتخطيط مساحة التخزين ومدة الاحتفاظ.",
                "تحكم في الدخول: كروت وبصمة وPIN وأقفال كهربائية وأزرار خروج.",
                "إنتركم فيديو ومداخل.",
                "أنظمة كشف تسلل وإنذار.",
                "كابلات وطاقة للأمن: كابلات مناسبة وPoE وUPS وكابينات.",
                "مراقبة آمنة عن بعد ووصول من الموبايل.",
                "اختبار وصيانة وتحديثات.",
            ],
            "equipment": [
                "كاميرات IP وAnalog (Dome/Bullet وداخلي/خارجي حسب الحاجة).",
                "وحدات تسجيل NVR/DVR وتخزين بحجم يناسب مدة الاحتفاظ المطلوبة.",
                "قوارئ تحكم في الدخول وأقفال كهربائية وأزرار خروج ووحدات تحكم.",
                "وحدات إنتركم فيديو ومداخل.",
                "لوحة إنذار وحساسات وكابلات وPoE وUPS احتياطي.",
            ],
            "process": [
                "معاينة الموقع وتحديد أماكن الكاميرات ونقاط الدخول.",
                "تصميم أمني وتخطيط مدة الاحتفاظ.",
                "التوريد والتركيب.",
                "الإعداد والاختبار وإعداد الوصول الآمن عن بعد.",
                "مراجعة الخصوصية وأماكن التركيب.",
                "التسليم وتسليم بيانات المدير والصيانة.",
            ],
            "target": "بيوت وفيلات وشركات صغيرة ومتاجر وعيادات ومكاتب.",
            "notes": [],
            "security": [
                "مفيش كلمات مرور افتراضية في الأنظمة المسلَّمة.",
                "مفيش تعريض مباشر لواجهات إدارة NVR/DVR على الإنترنت.",
                "ضوابط وصول مناسبة ووصول آمن عن بعد.",
                "احترام الخصوصية وتركيب الكاميرات في الأماكن المصرّح بها فقط.",
                "تسليم بيانات مدير النظام بشكل آمن.",
            ],
        },
    },
]
