from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    Иерархия: верхний уровень (CRM/CDP/ERP) -> подкатегории (по необходимости).
    URL:
      /<top_slug>/
      /<top_slug>/<subcategory_slug>/
    """

    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Slug", max_length=200)
    parent = models.ForeignKey(
        "self",
        verbose_name="Родительская категория",
        related_name="children",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    description = models.TextField("Описание", blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        constraints = [
            models.UniqueConstraint(fields=["parent", "slug"], name="uniq_category_parent_slug")
        ]

    def __str__(self) -> str:
        if self.parent_id:
            return f"{self.parent.name} / {self.name}"
        return self.name

    def is_top(self) -> bool:
        return self.parent_id is None

    def get_top(self) -> "Category":
        cur: Category = self
        while cur.parent_id is not None:
            cur = cur.parent  # type: ignore[assignment]
        return cur

    def get_absolute_url(self) -> str:
        if self.parent_id is None:
            return reverse("catalog:category_top", kwargs={"top_slug": self.slug})
        return reverse(
            "catalog:category_or_product",
            kwargs={"top_slug": self.get_top().slug, "slug": self.slug},
        )


class Tag(models.Model):
    class Group(models.TextChoices):
        INTEGRATION = "integration", "Интеграции"
        SUPPORT = "support", "Поддержка"
        LANGUAGE = "language", "Языки"
        FEATURE = "feature", "Функции"
        INDUSTRY = "industry", "Отрасли"
        OTHER = "other", "Другое"

    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", max_length=140)
    group = models.CharField("Группа", max_length=32, choices=Group.choices, default=Group.OTHER)
    sort_order = models.PositiveIntegerField("Порядок", default=100)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        constraints = [models.UniqueConstraint(fields=["group", "slug"], name="uniq_tag_group_slug")]

    def __str__(self) -> str:
        return f"{self.get_group_display()}: {self.name}"


class Product(models.Model):
    """
    Карточка сервиса (CRM/CDP/ERP).
    URL (по рекомендации): /<top_slug>/<product_slug>/
    """

    class Deployment(models.TextChoices):
        SAAS = "saas", "Облачное (SaaS)"
        ON_PREMISE = "on_premise", "On-premise (локальное)"
        HYBRID = "hybrid", "Гибридное"
        CLOUD = "cloud", "Облако"

    class BusinessSize(models.TextChoices):
        SMALL = "small", "Малый бизнес (до 50 сотрудников)"
        MEDIUM = "medium", "Средний бизнес (50-500 сотрудников)"
        LARGE = "large", "Крупный бизнес (более 500 сотрудников)"
        STARTUP = "startup", "Для стартапов"

    class PricingModel(models.TextChoices):
        SUBSCRIPTION = "subscription", "Подписка"
        ONE_TIME = "one_time", "Разовая покупка"
        FREEMIUM = "freemium", "Freemium"
        QUOTE = "quote", "По запросу"

    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Slug", max_length=220)
    logo = models.ImageField("Логотип", upload_to="logos/", blank=True, null=True)
    short_description = models.CharField("Краткое описание/слоган", max_length=300)

    category = models.ForeignKey(Category, verbose_name="Категория/подкатегория", on_delete=models.PROTECT)
    website_url = models.URLField("Официальный сайт", max_length=500, blank=True)
    source_page_url = models.URLField("Источник (страница из семантики)", max_length=500, blank=True, default="")
    source_keyword = models.CharField("Ключевая фраза (семантика)", max_length=300, blank=True, default="")

    description = models.TextField("Полное описание", blank=True)
    key_features = models.TextField("Ключевые функции/модули", blank=True, help_text="Список, по одной на строку.")
    advantages = models.CharField(
        "Преимущества",
        max_length=300,
        blank=True,
        help_text="Коротко (200–300 символов).",
    )
    disadvantages = models.TextField("Недостатки/ограничения", blank=True)

    deployment_type = models.CharField("Тип развертывания", max_length=32, choices=Deployment.choices, blank=True)
    business_size = models.CharField("Размер бизнеса", max_length=16, choices=BusinessSize.choices, blank=True)

    free_plan = models.BooleanField("Есть бесплатная версия", default=False)
    trial_available = models.BooleanField("Есть пробный период", default=False)

    pricing_model = models.CharField("Модель ценообразования", max_length=24, choices=PricingModel.choices, blank=True)
    pricing_details = models.CharField("Цены/тарифы (кратко)", max_length=200, blank=True)

    rating = models.DecimalField(
        "Средний рейтинг",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    reviews_count = models.PositiveIntegerField("Количество отзывов", default=0)

    tags = models.ManyToManyField(Tag, verbose_name="Теги", blank=True)

    support_24_7 = models.BooleanField("Поддержка 24/7", default=False)

    updated_info_at = models.DateField("Дата последнего обновления информации", blank=True, null=True)

    is_published = models.BooleanField("Опубликовано", default=True)
    sort_order = models.PositiveIntegerField("Порядок", default=100)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published", "sort_order", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["category", "slug"], name="uniq_product_category_slug")
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        # Не даём оставлять дату обновления в будущем.
        if self.updated_info_at and self.updated_info_at > date.today():
            raise ValidationError({"updated_info_at": "Дата не может быть в будущем."})

        # Конфликт URL: /<top>/<slug>/ может быть и подкатегорией, и продуктом.
        # Стараемся избегать совпадений slug'ов продукта и подкатегории в рамках одного top.
        top = self.category.get_top()
        if Category.objects.filter(parent=top, slug=self.slug).exists():
            raise ValidationError(
                {"slug": "Этот slug уже занят подкатегорией в выбранной верхней категории."}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_top(self) -> Category:
        return self.category.get_top()

    def get_absolute_url(self) -> str:
        top = self.get_top()
        return reverse("catalog:category_or_product", kwargs={"top_slug": top.slug, "slug": self.slug})

    def tag_slugs(self, group: str) -> list[str]:
        return list(self.tags.filter(group=group).values_list("slug", flat=True))


class Review(models.Model):
    product = models.ForeignKey(Product, verbose_name="Сервис", related_name="reviews", on_delete=models.CASCADE)
    author_name = models.CharField("Имя", max_length=80)
    rating = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField("Текст отзыва", max_length=2000)

    is_published = models.BooleanField("Опубликовано", default=False)

    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.product.name}: {self.rating}★ от {self.author_name}"

