from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Product, Tag


class Command(BaseCommand):
    help = "Создаёт базовые категории/теги и несколько демо-сервисов."

    @transaction.atomic
    def handle(self, *args, **options):
        crm, _ = Category.objects.get_or_create(
            parent=None,
            slug="crm-sistemy",
            defaults={"name": "CRM-системы", "sort_order": 10},
        )
        cdp, _ = Category.objects.get_or_create(
            parent=None,
            slug="cdp-platformy",
            defaults={"name": "CDP-платформы", "sort_order": 20},
        )
        erp, _ = Category.objects.get_or_create(
            parent=None,
            slug="erp-sistemy",
            defaults={"name": "ERP-системы", "sort_order": 30},
        )

        crm_small, _ = Category.objects.get_or_create(
            parent=crm,
            slug="dlya-malogo-biznesa",
            defaults={"name": "CRM для малого бизнеса", "sort_order": 10},
        )
        crm_medium, _ = Category.objects.get_or_create(
            parent=crm,
            slug="dlya-srednego-biznesa",
            defaults={"name": "CRM для среднего бизнеса", "sort_order": 20},
        )
        erp_retail, _ = Category.objects.get_or_create(
            parent=erp,
            slug="dlya-roznichnoy-torgovli",
            defaults={"name": "ERP для розничной торговли", "sort_order": 10},
        )

        def tag(group: str, slug: str, name: str, sort_order: int = 100) -> Tag:
            obj, _ = Tag.objects.get_or_create(
                group=group,
                slug=slug,
                defaults={"name": name, "sort_order": sort_order},
            )
            return obj

        # Языки
        ru = tag(Tag.Group.LANGUAGE, "ru", "Русский", 10)
        en = tag(Tag.Group.LANGUAGE, "en", "Английский", 20)

        # Интеграции (минимальный набор)
        t_1c = tag(Tag.Group.INTEGRATION, "1c", "1С", 10)
        t_ms = tag(Tag.Group.INTEGRATION, "microsoft-365", "Microsoft Office / 365", 20)
        t_google = tag(Tag.Group.INTEGRATION, "google-workspace", "Google Workspace", 30)
        t_msg = tag(Tag.Group.INTEGRATION, "messengers", "Мессенджеры (Telegram/WhatsApp/Viber)", 40)
        t_telephony = tag(Tag.Group.INTEGRATION, "telephony", "Телефония / IP-телефония", 50)

        # Поддержка
        s_chat = tag(Tag.Group.SUPPORT, "online-chat", "Онлайн-чат", 10)
        s_phone = tag(Tag.Group.SUPPORT, "phone", "Телефон", 20)
        s_email = tag(Tag.Group.SUPPORT, "email", "Email", 30)
        s_kb = tag(Tag.Group.SUPPORT, "knowledge-base", "База знаний", 40)

        # Демо-сервисы
        bitrix, _ = Product.objects.get_or_create(
            category=crm_small,
            slug="bitrix24",
            defaults={
                "name": "Битрикс24",
                "short_description": "CRM и задачи для продаж, коммуникаций и проектов.",
                "deployment_type": Product.Deployment.CLOUD,
                "business_size": Product.BusinessSize.SMALL,
                "free_plan": True,
                "trial_available": True,
                "pricing_model": Product.PricingModel.FREEMIUM,
                "pricing_details": "Есть бесплатный тариф и платные планы.",
                "rating": 4.1,
                "reviews_count": 1200,
                "support_24_7": True,
                "updated_info_at": date.today(),
                "is_published": True,
                "sort_order": 10,
            },
        )
        bitrix.tags.set([ru, t_msg, t_telephony, s_chat, s_phone, s_email, s_kb])

        salesforce, _ = Product.objects.get_or_create(
            category=crm_medium,
            slug="salesforce-sales-cloud",
            defaults={
                "name": "Salesforce Sales Cloud",
                "short_description": "CRM для автоматизации продаж, воронки и аналитики.",
                "deployment_type": Product.Deployment.SAAS,
                "business_size": Product.BusinessSize.MEDIUM,
                "free_plan": False,
                "trial_available": True,
                "pricing_model": Product.PricingModel.SUBSCRIPTION,
                "pricing_details": "Подписка, цены зависят от редакции.",
                "rating": 4.6,
                "reviews_count": 9800,
                "support_24_7": False,
                "updated_info_at": date.today(),
                "is_published": True,
                "sort_order": 20,
            },
        )
        salesforce.tags.set([en, t_ms, t_google, s_email, s_kb])

        demo_cdp, _ = Product.objects.get_or_create(
            category=cdp,
            slug="demo-cdp-platform",
            defaults={
                "name": "Demo CDP Platform",
                "short_description": "Платформа данных клиентов: сбор, унификация и сегментация.",
                "deployment_type": Product.Deployment.SAAS,
                "business_size": Product.BusinessSize.MEDIUM,
                "free_plan": False,
                "trial_available": True,
                "pricing_model": Product.PricingModel.QUOTE,
                "pricing_details": "Стоимость по запросу.",
                "rating": 4.0,
                "reviews_count": 110,
                "support_24_7": False,
                "updated_info_at": date.today(),
                "is_published": True,
                "sort_order": 10,
            },
        )
        demo_cdp.tags.set([ru, en, t_google, s_email])

        demo_erp, _ = Product.objects.get_or_create(
            category=erp_retail,
            slug="demo-erp-retail",
            defaults={
                "name": "Demo ERP Retail",
                "short_description": "ERP для розницы: запасы, закупки и финансы.",
                "deployment_type": Product.Deployment.ON_PREMISE,
                "business_size": Product.BusinessSize.LARGE,
                "free_plan": False,
                "trial_available": False,
                "pricing_model": Product.PricingModel.ONE_TIME,
                "pricing_details": "Разовая покупка + сопровождение.",
                "rating": 3.8,
                "reviews_count": 42,
                "support_24_7": False,
                "updated_info_at": date.today(),
                "is_published": True,
                "sort_order": 10,
            },
        )
        demo_erp.tags.set([ru, t_1c, s_phone, s_email])

        self.stdout.write(self.style.SUCCESS("Демо-данные созданы/обновлены."))

