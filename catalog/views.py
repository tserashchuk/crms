from __future__ import annotations

from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ReviewForm
from .models import Category, Product, Review, Tag
from .utils import descendant_category_ids, parse_multi


PER_PAGE = 12


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
    return render(
        request,
        "catalog/home.html",
        {
            "top_categories": top_categories,
            "latest": latest,
            "q": q,
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

    return render(
        request,
        "catalog/category_list.html",
        {
            "category": category,
            "top": top,
            "breadcrumbs": [("Главная", reverse("catalog:home")), (top.name, top.get_absolute_url())],
            "page_obj": page_obj,
            "canonical_url": top.get_absolute_url(),
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

        return render(
            request,
            "catalog/category_list.html",
            {
                "category": subcat,
                "top": top,
                "breadcrumbs": [
                    ("Главная", reverse("catalog:home")),
                    (top.name, top.get_absolute_url()),
                    (subcat.name, subcat.get_absolute_url()),
                ],
                "page_obj": page_obj,
                "canonical_url": subcat.get_absolute_url(),
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
            Review.objects.create(product=product, **form.cleaned_data)
            return redirect(product.get_absolute_url() + "#reviews")
    else:
        form = ReviewForm()

    published_reviews = product.reviews.filter(is_published=True)

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "top": top,
            "breadcrumbs": [
                ("Главная", reverse("catalog:home")),
                (top.name, top.get_absolute_url()),
                (product.name, product.get_absolute_url()),
            ],
            "canonical_url": product.get_absolute_url(),
            "published_reviews": published_reviews,
            "review_form": form,
            "integration_tags": product.tags.filter(group=Tag.Group.INTEGRATION).order_by("sort_order", "name"),
            "support_tags": product.tags.filter(group=Tag.Group.SUPPORT).order_by("sort_order", "name"),
            "language_tags": product.tags.filter(group=Tag.Group.LANGUAGE).order_by("sort_order", "name"),
        },
    )

