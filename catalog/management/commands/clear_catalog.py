"""
Очистка базы от контента каталога: отзывы, сервисы (продукты), теги, категории.
Пользователи (auth) не затрагиваются.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from catalog.models import Category, Product, Review, Tag


class Command(BaseCommand):
    help = "Удаляет весь контент каталога: отзывы, сервисы, теги, категории."

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            dest="no_input",
            help="Не спрашивать подтверждение.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        no_input = options["no_input"]

        review_count = Review.objects.count()
        product_count = Product.objects.count()
        tag_count = Tag.objects.count()
        category_count = Category.objects.count()

        if not any([review_count, product_count, tag_count, category_count]):
            self.stdout.write(self.style.WARNING("Каталог уже пуст."))
            return

        if not no_input:
            self.stdout.write(
                f"Будет удалено: отзывов {review_count}, сервисов {product_count}, "
                f"тегов {tag_count}, категорий {category_count}."
            )
            confirm = input("Продолжить? [y/N]: ")
            if confirm.lower() not in ("y", "yes", "д", "да"):
                self.stdout.write("Отменено.")
                return

        Review.objects.all().delete()
        Product.objects.all().delete()
        Tag.objects.all().delete()
        # Категории: из-за parent PROTECT удаляем с листьев к корню
        while Category.objects.exists():
            leaf = Category.objects.annotate(n=Count("children")).filter(n=0).first()
            if leaf is None:
                break
            leaf.delete()

        self.stdout.write(
            self.style.SUCCESS(
                "Каталог очищен. Запустите seed_demo для восстановления структуры категорий и демо-данных."
            )
        )
