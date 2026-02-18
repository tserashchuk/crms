"""
Однократная синхронизация полей rating и reviews_count у всех продуктов
по данным опубликованных отзывов. После добавления сигналов пересчёт идёт автоматически.
"""
from django.core.management.base import BaseCommand

from catalog.models import Product, _update_product_review_stats


class Command(BaseCommand):
    help = "Пересчитать rating и reviews_count у всех продуктов по опубликованным отзывам"

    def handle(self, *args, **options):
        ids = Product.objects.values_list("id", flat=True)
        total = 0
        for pid in ids:
            _update_product_review_stats(pid)
            total += 1
        self.stdout.write(self.style.SUCCESS(f"Обновлено продуктов: {total}"))
