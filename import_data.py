import json
import os
import django
from datetime import date

# УСТАНОВИТЕ ЗДЕСЬ ИМЯ ВАШЕГО ПРОЕКТА
# Например, если папка с settings.py называется 'config', напишите 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_catalog.settings')
django.setup()

# Импортируем модели (замените 'catalog' на название вашего приложения)
from catalog.models import Category, Product, Tag

def load_data():
    file_path = 'db_data.json'
    
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден!")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print("--- НАЧАЛО ИМПОРТА ---")

    # 1. Создание Категорий
    print(">>> Импорт категорий...")
    # Сначала создаем родительские категории
    for cat_data in data['categories']:
        parent, _ = Category.objects.update_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'parent': None
            }
        )
        # Создаем подкатегории
        for child in cat_data.get('children', []):
            Category.objects.update_or_create(
                slug=child['slug'],
                defaults={
                    'name': child['name'],
                    'description': child['description'],
                    'parent': parent
                }
            )

    # 2. Создание Тегов
    print(">>> Импорт тегов...")
    for tag_data in data['tags']:
        Tag.objects.update_or_create(
            slug=tag_data['slug'],
            defaults={
                'name': tag_data['name'],
                'group': tag_data['group']
            }
        )

    # 3. Создание Продуктов
    print(">>> Импорт продуктов...")
    for prod_data in data['products']:
        # Ищем категорию
        cat_slug = prod_data.pop('category_slug')
        category = Category.objects.filter(slug=cat_slug).first()
        
        if not category:
            print(f"[!] ОШИБКА: Категория '{cat_slug}' не найдена для товара '{prod_data['name']}'")
            continue

        # Извлекаем список тегов (они ManyToMany, их нельзя передать в defaults напрямую)
        tags_slugs = prod_data.pop('tags', [])
        
        # Подготовка полей
        prod_data['category'] = category
        prod_data['updated_info_at'] = date.today()
        
        # Создаем или обновляем продукт
        product, created = Product.objects.update_or_create(
            slug=prod_data['slug'],
            defaults=prod_data
        )

        # Привязываем теги
        if tags_slugs:
            tags = Tag.objects.filter(slug__in=tags_slugs)
            product.tags.set(tags)

        action = "Создан" if created else "Обновлен"
        print(f"{action}: {product.name}")

    print("--- ИМПОРТ ЗАВЕРШЕН УСПЕШНО ---")

if __name__ == '__main__':
    load_data()