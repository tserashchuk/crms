from __future__ import annotations

from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

import json

from .context_processors import MAX_COMPARE, SESSION_COMPARE, SESSION_SAVED
from .forms import ReviewForm
from .models import Category, Product, Review, Tag
from .seo import breadcrumb_list, item_list_ld, organization_ld, review_list_ld, software_application_ld, website_ld
from .utils import descendant_category_ids, parse_multi


PER_PAGE = 12
CROSSLINK_POPULAR_LIMIT = 8
SITE_NAME = "CRM Каталог"
DEFAULT_META_DESCRIPTION = "Каталог CRM, CDP и ERP систем. Сравнение возможностей, отзывы пользователей и подбор решений для бизнеса."


def _popular_products(category_ids: list[int] | None = None, exclude_product_id: int | None = None):
    """Популярные сервисы для перелинковки: по рейтингу и числу отзывов."""
    qs = Product.objects.filter(is_published=True).select_related("category")
    if category_ids is not None:
        qs = qs.filter(category_id__in=category_ids)
    if exclude_product_id is not None:
        qs = qs.exclude(pk=exclude_product_id)
    return qs.order_by("-rating", "-reviews_count", "name")[:CROSSLINK_POPULAR_LIMIT]


def _base_url(request: HttpRequest) -> str:
    return request.build_absolute_uri("/").rstrip("/")


def _structured_data_scripts(ld_list: list[dict]) -> list[str]:
    """Список JSON-строк для вставки в теги script (каждый объект отдельно, </ экранировано)."""
    result = []
    for obj in ld_list:
        out = json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")
        result.append(out)
    return result


def home(request: HttpRequest) -> HttpResponse:
    top_categories = Category.objects.filter(parent__isnull=True).order_by("sort_order", "name")
    q = (request.GET.get("q") or "").strip()
    base_qs = Product.objects.filter(is_published=True).select_related("category")
    if q:
        latest = (
            base_qs.filter(Q(name__icontains=q) | Q(short_description__icontains=q) | Q(description__icontains=q))
            .order_by("-updated_at")[:24]
        )
    else:
        latest = base_qs.order_by("-updated_at")[:12]

    base = _base_url(request)
    canonical_url = reverse("catalog:home")
    if q:
        canonical_url = f"{canonical_url}?q={request.GET.get('q', '')}"
    meta_description = f"Поиск по запросу «{q}». {DEFAULT_META_DESCRIPTION}" if q else DEFAULT_META_DESCRIPTION
    search_full_url = base + canonical_url if not q else base + reverse("catalog:home")
    structured = [
        organization_ld(base, SITE_NAME, DEFAULT_META_DESCRIPTION),
        website_ld(base, SITE_NAME, DEFAULT_META_DESCRIPTION, search_url=search_full_url),
    ]
    if latest:
        structured.append(
            item_list_ld(
                list(latest),
                base,
                "Новые и обновлённые системы" if not q else f"Поиск: {q}",
                list_description=None if q else "Последние обновления в каталоге CRM, CDP и ERP.",
            )
        )
    popular_products = _popular_products(category_ids=None) if not q else []
    return render(
        request,
        "catalog/home.html",
        {
            "top_categories": top_categories,
            "latest": latest,
            "q": q,
            "canonical_url": canonical_url,
            "meta_description": meta_description,
            "structured_data_scripts": _structured_data_scripts(structured),
            "popular_products": popular_products,
        },
    )


def _build_filters_context(request: HttpRequest, top: Category):
    # Теги показываем только из “общих” групп (интеграции/поддержка/языки)
    integrations = Tag.objects.filter(group=Tag.Group.INTEGRATION).order_by("sort_order", "name")
    supports = Tag.objects.filter(group=Tag.Group.SUPPORT).order_by("sort_order", "name")
    languages = Tag.objects.filter(group=Tag.Group.LANGUAGE).order_by("sort_order", "name")
    return {
        "integrations": integrations,
        "supports": supports,
        "languages": languages,
        "deployment_choices": Product.Deployment.choices,
        "business_size_choices": Product.BusinessSize.choices,
        "selected_integration": set(parse_multi(request.GET.getlist("integration"))),
        "selected_support": set(parse_multi(request.GET.getlist("support"))),
        "selected_language": set(parse_multi(request.GET.getlist("language"))),
        "top": top,
    }


def _apply_product_filters(request: HttpRequest, qs):
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(short_description__icontains=q) | Q(description__icontains=q))

    deployment = (request.GET.get("deployment") or "").strip()
    if deployment:
        qs = qs.filter(deployment_type=deployment)

    business_size = (request.GET.get("business_size") or "").strip()
    if business_size:
        qs = qs.filter(business_size=business_size)

    if request.GET.get("free_plan") == "1":
        qs = qs.filter(free_plan=True)
    if request.GET.get("trial") == "1":
        qs = qs.filter(trial_available=True)

    rating_min = (request.GET.get("rating_min") or "").strip()
    if rating_min:
        try:
            qs = qs.filter(rating__gte=Decimal(rating_min))
        except Exception:
            pass

    integration_slugs = parse_multi(request.GET.getlist("integration"))
    if integration_slugs:
        qs = qs.filter(tags__group=Tag.Group.INTEGRATION, tags__slug__in=integration_slugs).distinct()

    support_slugs = parse_multi(request.GET.getlist("support"))
    if support_slugs:
        qs = qs.filter(tags__group=Tag.Group.SUPPORT, tags__slug__in=support_slugs).distinct()

    language_slugs = parse_multi(request.GET.getlist("language"))
    if language_slugs:
        qs = qs.filter(tags__group=Tag.Group.LANGUAGE, tags__slug__in=language_slugs).distinct()

    sort = (request.GET.get("sort") or "").strip()
    if sort == "rating":
        qs = qs.order_by("-rating", "name")
    elif sort == "name":
        qs = qs.order_by("name")
    else:
        qs = qs.order_by("sort_order", "name")

    return qs


def category_top(request: HttpRequest, top_slug: str) -> HttpResponse:
    top = get_object_or_404(Category, parent__isnull=True, slug=top_slug)
    category = top
    category_ids = descendant_category_ids(category)
    qs = (
        Product.objects.filter(is_published=True, category_id__in=category_ids)
        .select_related("category")
        .prefetch_related("tags")
    )
    qs = _apply_product_filters(request, qs)

    paginator = Paginator(qs, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    breadcrumbs = [("Главная", reverse("catalog:home")), (top.name, top.get_absolute_url())]
    base = _base_url(request)
    meta_description = f"{category.name}. Сервисы и системы в каталоге. {DEFAULT_META_DESCRIPTION}"
    if category.description:
        meta_description = f"{category.name} — {category.description[:200]}{'…' if len(category.description) > 200 else ''}"
    structured = [breadcrumb_list(breadcrumbs, base)]
    if page_obj.object_list:
        structured.append(
            item_list_ld(
                list(page_obj.object_list),
                base,
                category.name,
                list_description=category.description[:300] if category.description else None,
            )
        )
    popular_products = _popular_products(category_ids=category_ids)
    popular_products_title = f"Популярные в категории «{category.name}»" if popular_products else ""
    return render(
        request,
        "catalog/category_list.html",
        {
            "category": category,
            "top": top,
            "breadcrumbs": breadcrumbs,
            "page_obj": page_obj,
            "canonical_url": top.get_absolute_url(),
            "meta_description": meta_description,
            "structured_data_scripts": _structured_data_scripts(structured),
            "popular_products": popular_products,
            "popular_products_title": popular_products_title,
            **_build_filters_context(request, top),
        },
    )


def category_or_product(request: HttpRequest, top_slug: str, slug: str) -> HttpResponse:
    top = get_object_or_404(Category, parent__isnull=True, slug=top_slug)

    # 1) Если slug совпал с подкатегорией — показываем список подкатегории.
    subcat = Category.objects.filter(parent=top, slug=slug).first()
    if subcat:
        category_ids = descendant_category_ids(subcat)
        qs = (
            Product.objects.filter(is_published=True, category_id__in=category_ids)
            .select_related("category")
            .prefetch_related("tags")
        )
        qs = _apply_product_filters(request, qs)

        paginator = Paginator(qs, PER_PAGE)
        page_obj = paginator.get_page(request.GET.get("page"))
        breadcrumbs = [
            ("Главная", reverse("catalog:home")),
            (top.name, top.get_absolute_url()),
            (subcat.name, subcat.get_absolute_url()),
        ]
        base = _base_url(request)
        meta_description = f"{subcat.name}. Сервисы в каталоге. {DEFAULT_META_DESCRIPTION}"
        if subcat.description:
            meta_description = f"{subcat.name} — {subcat.description[:200]}{'…' if len(subcat.description) > 200 else ''}"
        structured = [breadcrumb_list(breadcrumbs, base)]
        if page_obj.object_list:
            structured.append(
                item_list_ld(
                    list(page_obj.object_list),
                    base,
                    subcat.name,
                    list_description=subcat.description[:300] if subcat.description else None,
                )
            )
        popular_products = _popular_products(category_ids=category_ids)
        popular_products_title = f"Популярные в категории «{subcat.name}»" if popular_products else ""
        return render(
            request,
            "catalog/category_list.html",
            {
                "category": subcat,
                "top": top,
                "breadcrumbs": breadcrumbs,
                "page_obj": page_obj,
                "canonical_url": subcat.get_absolute_url(),
                "meta_description": meta_description,
                "structured_data_scripts": _structured_data_scripts(structured),
                "popular_products": popular_products,
                "popular_products_title": popular_products_title,
                **_build_filters_context(request, top),
            },
        )

    # 2) Иначе — карточка сервиса.
    top_ids = descendant_category_ids(top)
    product = (
        Product.objects.filter(is_published=True, category_id__in=top_ids, slug=slug)
        .select_related("category")
        .prefetch_related("tags")
        .first()
    )
    if not product:
        raise Http404

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = {k: v for k, v in form.cleaned_data.items() if k != "website"}
            Review.objects.create(product=product, **data)
            return redirect(product.get_absolute_url() + "#reviews")
    else:
        form = ReviewForm()

    published_reviews = product.reviews.filter(is_published=True)
    breadcrumbs = [
        ("Главная", reverse("catalog:home")),
        (top.name, top.get_absolute_url()),
        (product.name, product.get_absolute_url()),
    ]
    base = _base_url(request)
    meta_description = (product.short_description or product.description or "")[:160]
    if not meta_description:
        meta_description = f"{product.name} — обзор в каталоге {top.name}. {DEFAULT_META_DESCRIPTION}"
    else:
        meta_description = meta_description.strip() + ("…" if len((product.short_description or product.description or "")) > 160 else "")
    structured = [
        breadcrumb_list(breadcrumbs, base),
        software_application_ld(product, base),
    ]
    review_ld = review_list_ld(product, list(published_reviews), base)
    if review_ld:
        structured.append(review_ld)
    saved_ids = list(request.session.get(SESSION_SAVED, []))
    compare_ids = list(request.session.get(SESSION_COMPARE, []))
    top_ids = descendant_category_ids(top)
    popular_products = _popular_products(category_ids=top_ids, exclude_product_id=product.id)
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "top": top,
            "breadcrumbs": breadcrumbs,
            "canonical_url": product.get_absolute_url(),
            "meta_description": meta_description,
            "structured_data_scripts": _structured_data_scripts(structured),
            "published_reviews": published_reviews,
            "review_form": form,
            "tags_by_group": product.get_tags_by_group(),
            "product_in_saved": product.id in saved_ids,
            "product_in_compare": product.id in compare_ids,
            "popular_products": popular_products,
        },
    )


def _toggle_session_list(request: HttpRequest, key: str, product_id: int, max_size: int | None) -> bool:
    """Добавляет или убирает product_id из списка в сессии. Возвращает True если теперь в списке."""
    ids = list(request.session.get(key, []))
    if product_id in ids:
        ids.remove(product_id)
        request.session[key] = ids
        return False
    if max_size is not None and len(ids) >= max_size:
        return False
    if product_id not in ids:
        ids.append(product_id)
        request.session[key] = ids
    return True


def toggle_saved(request: HttpRequest, product_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("catalog:home")
    product = get_object_or_404(Product, pk=product_id, is_published=True)
    _toggle_session_list(request, SESSION_SAVED, product.id, max_size=None)
    next_url = request.GET.get("next") or request.POST.get("next") or product.get_absolute_url()
    return redirect(next_url)


def toggle_compare(request: HttpRequest, product_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("catalog:home")
    product = get_object_or_404(Product, pk=product_id, is_published=True)
    _toggle_session_list(request, SESSION_COMPARE, product.id, max_size=MAX_COMPARE)
    next_url = request.GET.get("next") or request.POST.get("next") or product.get_absolute_url()
    return redirect(next_url)


def clear_saved(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        request.session[SESSION_SAVED] = []
    return redirect("catalog:saved_list")


def saved_list(request: HttpRequest) -> HttpResponse:
    ids = list(request.session.get(SESSION_SAVED, []))
    products = Product.objects.filter(id__in=ids, is_published=True).select_related("category")
    # Сохраняем порядок из сессии
    by_id = {p.id: p for p in products}
    products_ordered = [by_id[i] for i in ids if i in by_id]
    breadcrumbs = [("Главная", reverse("catalog:home")), ("Сохранённые", reverse("catalog:saved_list"))]
    base = _base_url(request)
    structured = [breadcrumb_list(breadcrumbs, base)]
    return render(
        request,
        "catalog/saved_list.html",
        {
            "products": products_ordered,
            "breadcrumbs": breadcrumbs,
            "canonical_url": reverse("catalog:saved_list"),
            "meta_description": f"Сохранённые системы. {DEFAULT_META_DESCRIPTION}",
            "structured_data_scripts": _structured_data_scripts(structured),
        },
    )


def clear_compare(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        request.session[SESSION_COMPARE] = []
    return redirect("catalog:compare_list")


def compare_list(request: HttpRequest) -> HttpResponse:
    ids = list(request.session.get(SESSION_COMPARE, []))
    products = Product.objects.filter(id__in=ids, is_published=True).select_related("category").prefetch_related("tags")
    by_id = {p.id: p for p in products}
    products_ordered = [by_id[i] for i in ids if i in by_id]
    breadcrumbs = [("Главная", reverse("catalog:home")), ("Сравнение", reverse("catalog:compare_list"))]
    base = _base_url(request)
    structured = [breadcrumb_list(breadcrumbs, base)]
    return render(
        request,
        "catalog/compare.html",
        {
            "products": products_ordered,
            "breadcrumbs": breadcrumbs,
            "canonical_url": reverse("catalog:compare_list"),
            "meta_description": f"Сравнение систем. {DEFAULT_META_DESCRIPTION}",
            "structured_data_scripts": _structured_data_scripts(structured),
        },
    )

