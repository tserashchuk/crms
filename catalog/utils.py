from __future__ import annotations

from typing import Iterable

from .models import Category


def descendant_category_ids(root: Category) -> list[int]:
    """
    Простая рекурсия для небольшого каталога.
    Возвращает root + всех потомков.
    """

    ids: list[int] = [root.id]
    queue: list[int] = [root.id]
    while queue:
        parent_id = queue.pop(0)
        child_ids = list(Category.objects.filter(parent_id=parent_id).values_list("id", flat=True))
        ids.extend(child_ids)
        queue.extend(child_ids)
    return ids


def parse_multi(values: Iterable[str]) -> list[str]:
    return [v for v in values if v]

