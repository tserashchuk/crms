from .models import Category


def top_categories(request):
    try:
        qs = Category.objects.filter(parent__isnull=True).order_by("sort_order", "name")
    except Exception:
        # Пока не применены миграции — таблиц ещё нет.
        qs = Category.objects.none()
    return {"TOP_CATEGORIES": qs}

