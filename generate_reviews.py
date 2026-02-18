"""
Скрипт создаёт для каждого продукта (сервиса) случайное количество отзывов:
- от 3 до 10 отзывов на сервис;
- рейтинг от 3 до 4 (целое число).
"""
import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_catalog.settings')
django.setup()

from catalog.models import Product, Review

# Имена и короткие тексты для генерации отзывов
AUTHOR_NAMES = [
    "Алексей", "Мария", "Дмитрий", "Елена", "Сергей", "Анна", "Игорь", "Ольга",
    "Андрей", "Наталья", "Михаил", "Татьяна", "Павел", "Екатерина", "Николай",
    "Светлана", "Владимир", "Юлия", "Александр", "Ирина", "Максим", "Виктория",
]

REVIEW_TEXTS = [
    "Всё работает стабильно, устраивает.",
    "Удобный интерфейс, разобрался быстро.",
    "Пока без нареканий, пользуюсь с удовольствием.",
    "Хороший функционал за свои деньги.",
    "Подходит для наших задач, рекомендуем.",
    "Настройка заняла немного времени, но результат того стоит.",
    "Используем в команде, всем нравится.",
    "Поддержка отвечает оперативно, спасибо.",
    "Ставлю 4, есть куда расти, но в целом доволен.",
    "Попробовали несколько решений — это оказалось оптимальным.",
    "Внедрили недавно, пока всё ок.",
    "Нормальный сервис, соответствует описанию.",
]


def generate_reviews():
    products = list(Product.objects.all())
    if not products:
        print("В каталоге нет продуктов. Сначала выполните импорт данных.")
        return

    total_created = 0
    for product in products:
        n = random.randint(3, 10)
        # Используем больше имён/текстов, чем есть в списках — комбинируем или повторяем
        names_pool = random.choices(AUTHOR_NAMES, k=n)
        texts_pool = random.choices(REVIEW_TEXTS, k=n)
        for i in range(n):
            rating = random.randint(3, 4)
            author = names_pool[i]
            text = texts_pool[i]
            Review.objects.create(
                product=product,
                author_name=author,
                rating=rating,
                text=text,
                is_published=True,
            )
            total_created += 1
        print(f"  {product.name}: добавлено отзывов: {n} (рейтинг 3–4)")

    print(f"--- Всего создано отзывов: {total_created} ---")


if __name__ == '__main__':
    print("--- Генерация отзывов для сервисов ---")
    generate_reviews()
