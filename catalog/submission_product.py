from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def _parse_date(val: str | None) -> date | None:
    if not val or not isinstance(val, str):
        return None
    s = val.strip()[:10]
    if len(s) < 10:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _in_choices(val: str, choices: list[tuple[str, str]]) -> str:
    allowed = {c[0] for c in choices}
    return val if val in allowed else ""


def try_create_product_for_submission(submission_id: int):
    """
    Если заявка одобрена и сервис ещё не создан — создаёт Product и привязывает к заявке.
    Идемпотентно: повторные вызовы безопасны.
    """
    from .models import Category, ContentSubmission, Product, Tag

    with transaction.atomic():
        sub = (
            ContentSubmission.objects.select_for_update()
            .filter(pk=submission_id)
            .first()
        )
        if not sub:
            return None
        if sub.status != ContentSubmission.Status.APPROVED:
            return sub.created_product if sub.created_product_id else None
        if sub.created_product_id:
            return sub.created_product

        data = sub.product_data or {}
        category_id = data.get("category_id")
        if not category_id:
            logger.warning("ContentSubmission %s: нет category_id в product_data", sub.pk)
            return None
        try:
            category = Category.objects.get(pk=int(category_id))
        except (Category.DoesNotExist, TypeError, ValueError):
            logger.warning("ContentSubmission %s: категория %s не найдена", sub.pk, category_id)
            return None

        name = (data.get("name") or "").strip()[:200]
        short_description = (data.get("short_description") or "").strip()[:300]
        if not name or not short_description:
            logger.warning("ContentSubmission %s: пустое имя или слоган", sub.pk)
            return None

        slug_base = (data.get("slug") or "").strip().lower() or slugify(name) or "service"
        slug_base = slug_base[:220]
        slug = slug_base
        n = 0
        while Product.objects.filter(category=category, slug=slug).exists():
            n += 1
            suffix = f"-{n}" if n < 200 else f"-{sub.public_code.lower()}"
            slug = (slug_base[: 220 - len(suffix)] + suffix)[:220]

        dep = _in_choices((data.get("deployment_type") or "").strip(), list(Product.Deployment.choices))
        biz = _in_choices((data.get("business_size") or "").strip(), list(Product.BusinessSize.choices))
        prc = _in_choices((data.get("pricing_model") or "").strip(), list(Product.PricingModel.choices))

        updated_at = _parse_date(data.get("updated_info_at") or None)
        if updated_at and updated_at > date.today():
            updated_at = None

        product = Product(
            name=name,
            slug=slug,
            short_description=short_description,
            category=category,
            website_url=(data.get("website_url") or "")[:500],
            documentation_url=(data.get("documentation_url") or "")[:500],
            support_url=(data.get("support_url") or "")[:500],
            description=(data.get("description") or "")[:100_000],
            extended_description=(data.get("extended_description") or "")[:100_000],
            key_features=(data.get("key_features") or "")[:100_000],
            advantages=(data.get("advantages") or "")[:300],
            disadvantages=(data.get("disadvantages") or "")[:100_000],
            deployment_type=dep,
            business_size=biz,
            free_plan=bool(data.get("free_plan")),
            trial_available=bool(data.get("trial_available")),
            pricing_model=prc,
            pricing_details=(data.get("pricing_details") or "")[:200],
            support_24_7=bool(data.get("support_24_7")),
            updated_info_at=updated_at,
            rating=Decimal("0"),
            reviews_count=0,
            is_published=True,
        )

        try:
            product.full_clean()
        except ValidationError as e:
            logger.exception("ContentSubmission %s: ошибка валидации Product: %s", sub.pk, e)
            return None

        product.save()

        tag_ids = data.get("tag_ids") or []
        if isinstance(tag_ids, list) and tag_ids:
            try:
                ids = [int(x) for x in tag_ids]
            except (TypeError, ValueError):
                ids = []
            if ids:
                product.tags.set(Tag.objects.filter(pk__in=ids))

        if sub.submitted_logo:
            try:
                fname = sub.submitted_logo.name.rsplit("/", 1)[-1] or "logo.png"
                with sub.submitted_logo.open("rb") as src:
                    product.logo.save(fname, ContentFile(src.read()), save=True)
            except OSError as e:
                logger.warning("ContentSubmission %s: не удалось скопировать логотип: %s", sub.pk, e)

        ContentSubmission.objects.filter(pk=sub.pk).update(created_product=product)
        product.refresh_from_db()
        return product
