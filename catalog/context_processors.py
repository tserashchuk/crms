from .models import Category

# Ключи сессии для списков «Сохранённые» и «Сравнение»
SESSION_SAVED = "saved_product_ids"
SESSION_COMPARE = "compare_product_ids"
MAX_COMPARE = 4


def _get_saved_ids(request):
    return list(request.session.get(SESSION_SAVED, []))


def _get_compare_ids(request):
    return list(request.session.get(SESSION_COMPARE, []))


def top_categories(request):
    try:
        qs = Category.objects.filter(parent__isnull=True).order_by("sort_order", "name")
    except Exception:
        # Пока не применены миграции — таблиц ещё нет.
        qs = Category.objects.none()
    saved_ids = _get_saved_ids(request)
    compare_ids = _get_compare_ids(request)
    return {
        "TOP_CATEGORIES": qs,
        "saved_product_ids": saved_ids,
        "compare_product_ids": compare_ids,
        "saved_count": len(saved_ids),
        "compare_count": len(compare_ids),
        "max_compare": MAX_COMPARE,
    }

