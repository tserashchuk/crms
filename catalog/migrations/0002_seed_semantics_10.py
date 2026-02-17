from __future__ import annotations

from django.db import migrations, models
from django.utils.text import slugify


def _name_from_slug(slug: str) -> str:
    s = (slug or "").replace("_", "-").replace("-", " ").strip()
    if not s:
        return "Без названия"
    out: list[str] = []
    for w in s.split():
        lw = w.lower()
        if lw in {"crm", "cdp", "erp", "hr"}:
            out.append(lw.upper())
        elif lw == "1c":
            out.append("1С")
        elif any(c.isdigit() for c in lw):
            out.append(lw.upper())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def ensure_semantics_columns(apps, schema_editor):
    """
    Совместимость с БД, где уже есть NOT NULL столбцы source_page_url/source_keyword.
    - Если столбцов нет — добавим с DEFAULT ''.
    - Если есть — ничего не делаем.
    """
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(catalog_product)")
        cols = {row[1] for row in cursor.fetchall()}  # row[1] = name

    if "source_page_url" not in cols:
        schema_editor.execute(
            "ALTER TABLE catalog_product "
            "ADD COLUMN source_page_url varchar(500) NOT NULL DEFAULT ''"
        )
    if "source_keyword" not in cols:
        schema_editor.execute(
            "ALTER TABLE catalog_product "
            "ADD COLUMN source_keyword varchar(300) NOT NULL DEFAULT ''"
        )


def seed_semantics_10(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    crm, _ = Category.objects.get_or_create(
        parent_id=None,
        slug="crm-sistemy",
        defaults={"name": "CRM-системы", "sort_order": 10},
    )

    # 10 любых карточек, выбранных по семантике (пример из таблицы):
    # Источник таблицы: https://docs.google.com/spreadsheets/d/1MdpQh45EK-QrN6HnE6PedAEUPkiNeM0x/edit?gid=66941572#gid=66941572
    items = [
        ("usu", "https://crmindex.ru/products/usu", "усу"),
        ("moyklass", "https://crmindex.ru/products/moyklass", "мой класс класс"),
        ("2kurs", "https://crmindex.ru/products/2kurs", "2 курс"),
        ("poster", "https://crmindex.ru/products/poster", "poster"),
        ("x24", "https://crmindex.ru/products/x24", "х 24"),
        ("dela-idut", "https://crmindex.ru/products/dela_idut", "дела идут"),
        ("youtrack", "https://crmindex.ru/products/youtrack", "track you"),
        ("onebox-crm", "https://crmindex.ru/products/onebox_crm", "one box"),
        ("parus", "https://crmindex.ru/products/parus", "parus"),
        ("big-bird", "https://crmindex.ru/products/big_bird", "большая птица"),
    ]

    for raw_slug, url, keyword in items:
        slug = slugify(raw_slug.replace("_", "-")) or raw_slug
        name = _name_from_slug(raw_slug)
        short = f"Карточка сервиса «{name}» (из семантики: «{keyword}»)."
        short = short[:300]

        obj, created = Product.objects.get_or_create(
            category_id=crm.id,
            slug=slug,
            defaults={
                "name": name,
                "short_description": short,
                # В “официальный сайт” кладём URL из семантики, чтобы карточка была с кликабельной ссылкой.
                "website_url": url,
                "source_page_url": url,
                "source_keyword": keyword,
                "is_published": True,
                "sort_order": 100,
            },
        )

        # Если запись уже была создана (например, seed_demo), не перетираем контент — только публикуем.
        if not created:
            changed = False
            if not getattr(obj, "is_published", True):
                obj.is_published = True
                changed = True
            if not getattr(obj, "website_url", ""):
                obj.website_url = url
                changed = True
            if not getattr(obj, "short_description", ""):
                obj.short_description = short
                changed = True
            if not getattr(obj, "source_page_url", ""):
                obj.source_page_url = url
                changed = True
            if not getattr(obj, "source_keyword", "") and keyword:
                obj.source_keyword = keyword
                changed = True
            if changed:
                obj.save(
                    update_fields=[
                        "is_published",
                        "website_url",
                        "short_description",
                        "source_page_url",
                        "source_keyword",
                    ]
                )


def unseed_semantics_10(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")
    crm = Category.objects.filter(parent_id=None, slug="crm-sistemy").first()
    if not crm:
        return
    slugs = [
        "usu",
        "moyklass",
        "2kurs",
        "poster",
        "x24",
        "dela-idut",
        "youtrack",
        "onebox-crm",
        "parus",
        "big-bird",
    ]
    Product.objects.filter(category_id=crm.id, slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(ensure_semantics_columns, reverse_code=migrations.RunPython.noop)
            ],
            state_operations=[
                migrations.AddField(
                    model_name="product",
                    name="source_page_url",
                    field=models.URLField(
                        verbose_name="Источник (страница из семантики)",
                        max_length=500,
                        blank=True,
                        default="",
                    ),
                ),
                migrations.AddField(
                    model_name="product",
                    name="source_keyword",
                    field=models.CharField(
                        verbose_name="Ключевая фраза (семантика)",
                        max_length=300,
                        blank=True,
                        default="",
                    ),
                ),
            ],
        ),
        migrations.RunPython(seed_semantics_10, reverse_code=unseed_semantics_10),
    ]

