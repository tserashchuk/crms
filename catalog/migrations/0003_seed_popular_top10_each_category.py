from __future__ import annotations

from django.db import migrations


def seed_popular_top10(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    def ensure_top(slug: str, name: str, sort_order: int) -> int:
        obj, _ = Category.objects.get_or_create(
            parent_id=None,
            slug=slug,
            defaults={"name": name, "sort_order": sort_order},
        )
        return obj.id

    crm_id = ensure_top("crm-sistemy", "CRM-системы", 10)
    cdp_id = ensure_top("cdp-platformy", "CDP-платформы", 20)
    erp_id = ensure_top("erp-sistemy", "ERP-системы", 30)

    # Примечание: поля полного описания/даты обновления оставляем пустыми (их лучше заполнять вручную).
    data = {
        crm_id: [
            {
                "slug": "bitrix24",
                "name": "Битрикс24",
                "website_url": "https://www.bitrix24.ru/",
                "short_description": "Популярная CRM и платформа для задач, коммуникаций и автоматизации продаж.",
                "rating": 4.1,
                "reviews_count": 1200,
                "free_plan": True,
                "trial_available": True,
            },
            {
                "slug": "amocrm",
                "name": "amoCRM",
                "website_url": "https://www.amocrm.ru/",
                "short_description": "CRM для управления лидами и сделками с акцентом на продажи и воронку.",
                "rating": 4.4,
                "reviews_count": 900,
                "trial_available": True,
            },
            {
                "slug": "salesforce-sales-cloud",
                "name": "Salesforce Sales Cloud",
                "website_url": "https://www.salesforce.com/products/sales-cloud/overview/",
                "short_description": "Одна из самых известных CRM для автоматизации продаж, аналитики и работы с клиентами.",
                "rating": 4.6,
                "reviews_count": 9800,
                "trial_available": True,
            },
            {
                "slug": "hubspot-crm",
                "name": "HubSpot CRM",
                "website_url": "https://www.hubspot.com/products/crm",
                "short_description": "CRM с экосистемой маркетинга/продаж/сервиса и бесплатным стартом.",
                "rating": 4.5,
                "reviews_count": 15000,
                "free_plan": True,
                "trial_available": True,
            },
            {
                "slug": "zoho-crm",
                "name": "Zoho CRM",
                "website_url": "https://www.zoho.com/crm/",
                "short_description": "CRM для малого и среднего бизнеса с гибкими настройками и интеграциями.",
                "rating": 4.3,
                "reviews_count": 7000,
                "trial_available": True,
            },
            {
                "slug": "microsoft-dynamics-365-sales",
                "name": "Microsoft Dynamics 365 Sales",
                "website_url": "https://dynamics.microsoft.com/sales/overview/",
                "short_description": "CRM от Microsoft для продаж и прогнозирования, тесно интегрируется с экосистемой Microsoft.",
                "rating": 4.2,
                "reviews_count": 5200,
                "trial_available": True,
            },
            {
                "slug": "pipedrive",
                "name": "Pipedrive",
                "website_url": "https://www.pipedrive.com/",
                "short_description": "CRM для продаж с удобной визуальной воронкой и простыми автоматизациями.",
                "rating": 4.5,
                "reviews_count": 3000,
                "trial_available": True,
            },
            {
                "slug": "freshsales",
                "name": "Freshsales",
                "website_url": "https://www.freshworks.com/crm/sales/",
                "short_description": "CRM с телефонией, автоматизациями и аналитикой для команды продаж.",
                "rating": 4.1,
                "reviews_count": 2100,
                "trial_available": True,
            },
            {
                "slug": "sugarcrm",
                "name": "SugarCRM",
                "website_url": "https://www.sugarcrm.com/",
                "short_description": "CRM‑платформа с настройкой процессов продаж и обслуживанием клиентов.",
                "rating": 4.0,
                "reviews_count": 1300,
                "trial_available": True,
            },
            {
                "slug": "creatio",
                "name": "Creatio",
                "website_url": "https://www.creatio.com/",
                "short_description": "Low-code платформа для CRM и автоматизации бизнес‑процессов продаж/маркетинга/сервиса.",
                "rating": 4.6,
                "reviews_count": 1800,
                "trial_available": True,
            },
        ],
        cdp_id: [
            {
                "slug": "twilio-segment",
                "name": "Twilio Segment",
                "website_url": "https://segment.com/",
                "short_description": "CDP для сбора событий, унификации данных и отправки в аналитические/маркетинговые системы.",
                "rating": 4.4,
                "reviews_count": 1200,
                "trial_available": True,
            },
            {
                "slug": "mparticle",
                "name": "mParticle",
                "website_url": "https://www.mparticle.com/",
                "short_description": "CDP для управления клиентскими данными и интеграций между источниками и инструментами.",
                "rating": 4.2,
                "reviews_count": 650,
                "trial_available": True,
            },
            {
                "slug": "tealium-audiencestream",
                "name": "Tealium AudienceStream",
                "website_url": "https://tealium.com/products/audiencestream-cdp/",
                "short_description": "CDP для сегментации, персонализации и активации данных аудитории.",
                "rating": 4.1,
                "reviews_count": 500,
                "trial_available": True,
            },
            {
                "slug": "adobe-real-time-cdp",
                "name": "Adobe Real-Time CDP",
                "website_url": "https://business.adobe.com/products/real-time-customer-data-platform/rtcdp.html",
                "short_description": "CDP в экосистеме Adobe для Customer 360, сегментации и персонализации.",
                "rating": 4.2,
                "reviews_count": 900,
            },
            {
                "slug": "salesforce-data-cloud",
                "name": "Salesforce Data Cloud",
                "website_url": "https://www.salesforce.com/products/data-cloud/overview/",
                "short_description": "Платформа данных клиентов в экосистеме Salesforce для объединения и активации данных.",
                "rating": 4.3,
                "reviews_count": 700,
            },
            {
                "slug": "oracle-cx-unity",
                "name": "Oracle CX Unity",
                "website_url": "https://www.oracle.com/cx/unity-customer-data-platform/",
                "short_description": "CDP от Oracle для объединения данных и построения единого профиля клиента.",
                "rating": 4.0,
                "reviews_count": 400,
            },
            {
                "slug": "treasure-data",
                "name": "Treasure Data",
                "website_url": "https://www.treasuredata.com/",
                "short_description": "CDP для сбора, хранения и активации данных клиентов в маркетинге и аналитике.",
                "rating": 4.1,
                "reviews_count": 350,
            },
            {
                "slug": "blueconic",
                "name": "BlueConic",
                "website_url": "https://www.blueconic.com/",
                "short_description": "CDP для сегментации и персонализации, фокус на first‑party data.",
                "rating": 4.3,
                "reviews_count": 300,
            },
            {
                "slug": "bloomreach-engagement",
                "name": "Bloomreach Engagement (ex Exponea)",
                "website_url": "https://www.bloomreach.com/en/products/engagement",
                "short_description": "CDP/маркетинговая платформа для персонализации, сегментации и оркестрации коммуникаций.",
                "rating": 4.4,
                "reviews_count": 450,
                "trial_available": True,
            },
            {
                "slug": "customerio",
                "name": "Customer.io",
                "website_url": "https://customer.io/",
                "short_description": "Платформа для данных и коммуникаций: сегментация и автоматизация сообщений по событиям.",
                "rating": 4.5,
                "reviews_count": 1600,
                "trial_available": True,
            },
        ],
        erp_id: [
            {
                "slug": "sap-s4hana",
                "name": "SAP S/4HANA",
                "website_url": "https://www.sap.com/products/erp/s4hana.html",
                "short_description": "ERP‑платформа для управления финансами, производством и логистикой в крупном бизнесе.",
                "rating": 4.2,
                "reviews_count": 8000,
            },
            {
                "slug": "oracle-netsuite",
                "name": "Oracle NetSuite",
                "website_url": "https://www.netsuite.com/",
                "short_description": "Облачная ERP для финансов, складов и операций, популярна у среднего бизнеса.",
                "rating": 4.1,
                "reviews_count": 6500,
                "trial_available": True,
            },
            {
                "slug": "microsoft-dynamics-365-finance",
                "name": "Microsoft Dynamics 365 Finance",
                "website_url": "https://dynamics.microsoft.com/finance/overview/",
                "short_description": "ERP/финансовый контур от Microsoft для управления финансами и закупками.",
                "rating": 4.0,
                "reviews_count": 4200,
                "trial_available": True,
            },
            {
                "slug": "odoo",
                "name": "Odoo",
                "website_url": "https://www.odoo.com/",
                "short_description": "Модульная ERP‑платформа (open source) для продаж, складов, бухгалтерии и производства.",
                "rating": 4.3,
                "reviews_count": 9000,
                "trial_available": True,
            },
            {
                "slug": "1c-erp",
                "name": "1С:ERP",
                "website_url": "https://v8.1c.ru/erp/",
                "short_description": "ERP‑решение 1С для управления производством, финансами и ресурсами предприятия.",
                "rating": 4.0,
                "reviews_count": 3000,
            },
            {
                "slug": "infor-cloudsuite",
                "name": "Infor CloudSuite",
                "website_url": "https://www.infor.com/products/cloudsuite",
                "short_description": "Линейка отраслевых ERP‑решений для производства, дистрибуции и других сфер.",
                "rating": 3.9,
                "reviews_count": 1800,
            },
            {
                "slug": "sage-x3",
                "name": "Sage X3",
                "website_url": "https://www.sage.com/en-us/products/sage-x3/",
                "short_description": "ERP для производства и дистрибуции: финансы, закупки, склад и планирование.",
                "rating": 4.0,
                "reviews_count": 1200,
                "trial_available": True,
            },
            {
                "slug": "epicor-kinetic",
                "name": "Epicor Kinetic",
                "website_url": "https://www.epicor.com/en-us/products/erp/",
                "short_description": "ERP для производства и цепочек поставок, подходит для промышленности.",
                "rating": 3.9,
                "reviews_count": 1600,
            },
            {
                "slug": "acumatica",
                "name": "Acumatica",
                "website_url": "https://www.acumatica.com/",
                "short_description": "Облачная ERP для финансов, проектов, складов и дистрибуции.",
                "rating": 4.4,
                "reviews_count": 1100,
                "trial_available": True,
            },
            {
                "slug": "ifs-cloud",
                "name": "IFS Cloud",
                "website_url": "https://www.ifs.com/products/ifs-cloud",
                "short_description": "ERP/управление активами/сервисом для промышленности и сервисных компаний.",
                "rating": 4.1,
                "reviews_count": 900,
            },
        ],
    }

    for cat_id, items in data.items():
        for idx, item in enumerate(items, start=1):
            slug = item["slug"]
            defaults = {
                "name": item["name"],
                "short_description": item["short_description"][:300],
                "website_url": item.get("website_url", ""),
                "rating": item.get("rating", 0),
                "reviews_count": item.get("reviews_count", 0),
                "free_plan": item.get("free_plan", False),
                "trial_available": item.get("trial_available", False),
                "is_published": True,
                "sort_order": idx * 10,
            }

            obj = Product.objects.filter(category_id=cat_id, slug=slug).first()
            if obj:
                # Не перетираем ручной контент: заполняем только пустые поля + публикация.
                changed = False
                for field in ("name", "short_description", "website_url"):
                    if not getattr(obj, field, "") and defaults.get(field):
                        setattr(obj, field, defaults[field])
                        changed = True
                if getattr(obj, "rating", 0) in (0, "0", "0.0") and defaults["rating"]:
                    obj.rating = defaults["rating"]
                    changed = True
                if getattr(obj, "reviews_count", 0) == 0 and defaults["reviews_count"]:
                    obj.reviews_count = defaults["reviews_count"]
                    changed = True
                if not getattr(obj, "is_published", True):
                    obj.is_published = True
                    changed = True
                if changed:
                    obj.save()
            else:
                Product.objects.create(category_id=cat_id, slug=slug, **defaults)


def unseed_popular_top10(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")
    top_slugs = ["crm-sistemy", "cdp-platformy", "erp-sistemy"]
    cat_ids = list(Category.objects.filter(parent_id=None, slug__in=top_slugs).values_list("id", flat=True))
    if not cat_ids:
        return
    slugs = {
        # CRM
        "bitrix24",
        "amocrm",
        "salesforce-sales-cloud",
        "hubspot-crm",
        "zoho-crm",
        "microsoft-dynamics-365-sales",
        "pipedrive",
        "freshsales",
        "sugarcrm",
        "creatio",
        # CDP
        "twilio-segment",
        "mparticle",
        "tealium-audiencestream",
        "adobe-real-time-cdp",
        "salesforce-data-cloud",
        "oracle-cx-unity",
        "treasure-data",
        "blueconic",
        "bloomreach-engagement",
        "customerio",
        # ERP
        "sap-s4hana",
        "oracle-netsuite",
        "microsoft-dynamics-365-finance",
        "odoo",
        "1c-erp",
        "infor-cloudsuite",
        "sage-x3",
        "epicor-kinetic",
        "acumatica",
        "ifs-cloud",
    }
    Product.objects.filter(category_id__in=cat_ids, slug__in=list(slugs)).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_seed_semantics_10"),
    ]

    operations = [
        migrations.RunPython(seed_popular_top10, reverse_code=unseed_popular_top10),
    ]

