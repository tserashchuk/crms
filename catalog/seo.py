"""
SEO: JSON-LD микроразметка (Schema.org) для поисковиков.
"""
from __future__ import annotations

import json

from .models import Product, Review


def _strip_script(s: str, max_len: int = 500) -> str:
    """Убирает </script> из строки и обрезает длину."""
    if not s:
        return ""
    s = str(s).replace("</script>", "").strip()[:max_len]
    return s


def organization_ld(
    base_url: str,
    name: str = "CRM Каталог",
    description: str | None = None,
    *,
    include_context: bool = True,
) -> dict:
    """Organization — организация/сайт. include_context=False для вложения (например, publisher)."""
    data = {
        "@type": "Organization",
        "name": _strip_script(name, 200),
        "url": base_url,
        "description": _strip_script(description or "Каталог CRM, CDP и ERP систем.", 300),
        "inLanguage": "ru",
    }
    if include_context:
        data = {"@context": "https://schema.org", **data}
    return data


def breadcrumb_list(breadcrumbs: list[tuple[str, str]], base_url: str) -> dict:
    """BreadcrumbList для списка (name, path). path — относительный путь."""
    base = base_url.rstrip("/")
    items = []
    for i, (name, path) in enumerate(breadcrumbs):
        url = base + path if path.startswith("/") else base + "/" + path.lstrip("/")
        items.append({
            "@type": "ListItem",
            "position": i + 1,
            "name": _strip_script(name, 200),
            "item": url,
        })
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def website_ld(
    base_url: str,
    name: str = "CRM Каталог",
    description: str | None = None,
    search_url: str | None = None,
) -> dict:
    """WebSite для главной с поиском (potentialAction)."""
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": _strip_script(name, 200),
        "url": base_url,
        "description": _strip_script(description or "Каталог CRM, CDP и ERP систем. Сравнение и отзывы.", 300),
        "inLanguage": "ru",
        "publisher": organization_ld(base_url, name, description, include_context=False),
    }
    if search_url:
        data["potentialAction"] = {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": search_url.rstrip("/") + "?q={search_term_string}",
            },
            "query-input": "required name=search_term_string",
        }
    return data


def software_application_ld(product: Product, base_url: str) -> dict:
    """SoftwareApplication для карточки сервиса."""
    app_url = base_url.rstrip("/") + product.get_absolute_url()
    data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": _strip_script(product.name, 200),
        "description": _strip_script(product.short_description or product.description, 500),
        "url": app_url,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "inLanguage": "ru",
    }
    if product.website_url:
        data["sameAs"] = product.website_url
    if product.rating and product.rating > 0:
        data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(product.rating),
            "ratingCount": product.reviews_count or 0,
            "bestRating": "5",
            "worstRating": "1",
        }
    if product.logo:
        data["image"] = base_url.rstrip("/") + product.logo.url
    return data


def item_list_ld(
    products: list[Product],
    base_url: str,
    list_name: str,
    list_description: str | None = None,
) -> dict:
    """ItemList — список сервисов (главная, категория)."""
    items = []
    for i, p in enumerate(products):
        url = base_url.rstrip("/") + p.get_absolute_url()
        item = {
            "@type": "ListItem",
            "position": i + 1,
            "url": url,
            "name": _strip_script(p.name, 200),
        }
        if p.short_description:
            item["description"] = _strip_script(p.short_description, 300)
        items.append(item)
    data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": _strip_script(list_name, 200),
        "numberOfItems": len(items),
        "itemListElement": items,
    }
    if list_description:
        data["description"] = _strip_script(list_description, 300)
    return data


def review_list_ld(product: Product, reviews: list[Review], base_url: str) -> dict | None:
    """Список Review для карточки сервиса (дополняет aggregateRating в SoftwareApplication)."""
    if not reviews:
        return None
    review_entries = []
    for r in reviews:
        review_entries.append({
            "@type": "Review",
            "author": {"@type": "Person", "name": _strip_script(r.author_name, 80)},
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": r.rating,
                "bestRating": 5,
                "worstRating": 1,
            },
            "reviewBody": _strip_script(r.text, 500),
            "datePublished": r.created_at.isoformat() if r.created_at else None,
        })
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": _strip_script(product.name, 200),
        "url": base_url.rstrip("/") + product.get_absolute_url(),
        "review": review_entries,
    }
