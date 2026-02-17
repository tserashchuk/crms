from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                ("slug", models.SlugField(max_length=200, verbose_name="Slug")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("sort_order", models.PositiveIntegerField(default=100, verbose_name="Порядок")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="children",
                        to="catalog.category",
                        verbose_name="Родительская категория",
                    ),
                ),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="Название")),
                ("slug", models.SlugField(max_length=140, verbose_name="Slug")),
                (
                    "group",
                    models.CharField(
                        choices=[
                            ("integration", "Интеграции"),
                            ("support", "Поддержка"),
                            ("language", "Языки"),
                            ("feature", "Функции"),
                            ("industry", "Отрасли"),
                            ("other", "Другое"),
                        ],
                        default="other",
                        max_length=32,
                        verbose_name="Группа",
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(default=100, verbose_name="Порядок")),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Название")),
                ("slug", models.SlugField(max_length=220, verbose_name="Slug")),
                ("logo", models.ImageField(blank=True, null=True, upload_to="logos/", verbose_name="Логотип")),
                ("short_description", models.CharField(max_length=300, verbose_name="Краткое описание/слоган")),
                ("website_url", models.URLField(blank=True, max_length=500, verbose_name="Официальный сайт")),
                ("description", models.TextField(blank=True, verbose_name="Полное описание")),
                (
                    "key_features",
                    models.TextField(
                        blank=True,
                        help_text="Список, по одной на строку.",
                        verbose_name="Ключевые функции/модули",
                    ),
                ),
                (
                    "advantages",
                    models.CharField(
                        blank=True,
                        help_text="Коротко (200–300 символов).",
                        max_length=300,
                        verbose_name="Преимущества",
                    ),
                ),
                ("disadvantages", models.TextField(blank=True, verbose_name="Недостатки/ограничения")),
                (
                    "deployment_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("saas", "Облачное (SaaS)"),
                            ("on_premise", "On-premise (локальное)"),
                            ("hybrid", "Гибридное"),
                            ("cloud", "Облако"),
                        ],
                        max_length=32,
                        verbose_name="Тип развертывания",
                    ),
                ),
                (
                    "business_size",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("small", "Малый бизнес (до 50 сотрудников)"),
                            ("medium", "Средний бизнес (50-500 сотрудников)"),
                            ("large", "Крупный бизнес (более 500 сотрудников)"),
                            ("startup", "Для стартапов"),
                        ],
                        max_length=16,
                        verbose_name="Размер бизнеса",
                    ),
                ),
                ("free_plan", models.BooleanField(default=False, verbose_name="Есть бесплатная версия")),
                ("trial_available", models.BooleanField(default=False, verbose_name="Есть пробный период")),
                (
                    "pricing_model",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("subscription", "Подписка"),
                            ("one_time", "Разовая покупка"),
                            ("freemium", "Freemium"),
                            ("quote", "По запросу"),
                        ],
                        max_length=24,
                        verbose_name="Модель ценообразования",
                    ),
                ),
                ("pricing_details", models.CharField(blank=True, max_length=200, verbose_name="Цены/тарифы (кратко)")),
                (
                    "rating",
                    models.DecimalField(
                        decimal_places=1,
                        default=0,
                        max_digits=2,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Средний рейтинг",
                    ),
                ),
                ("reviews_count", models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")),
                ("support_24_7", models.BooleanField(default=False, verbose_name="Поддержка 24/7")),
                (
                    "updated_info_at",
                    models.DateField(blank=True, null=True, verbose_name="Дата последнего обновления информации"),
                ),
                ("is_published", models.BooleanField(default=True, verbose_name="Опубликовано")),
                ("sort_order", models.PositiveIntegerField(default=100, verbose_name="Порядок")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "category",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="catalog.category", verbose_name="Категория/подкатегория"),
                ),
                ("tags", models.ManyToManyField(blank=True, to="catalog.tag", verbose_name="Теги")),
            ],
            options={
                "verbose_name": "Сервис",
                "verbose_name_plural": "Сервисы",
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("author_name", models.CharField(max_length=80, verbose_name="Имя")),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Оценка",
                    ),
                ),
                ("text", models.TextField(max_length=2000, verbose_name="Текст отзыва")),
                ("is_published", models.BooleanField(default=False, verbose_name="Опубликовано")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="catalog.product",
                        verbose_name="Сервис",
                    ),
                ),
            ],
            options={
                "verbose_name": "Отзыв",
                "verbose_name_plural": "Отзывы",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(fields=("parent", "slug"), name="uniq_category_parent_slug"),
        ),
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(fields=("group", "slug"), name="uniq_tag_group_slug"),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(fields=("category", "slug"), name="uniq_product_category_slug"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["slug"], name="catalog_pro_slug_3b0c44_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["is_published", "sort_order", "name"], name="catalog_pro_is_publ_6a2b0f_idx"),
        ),
    ]

