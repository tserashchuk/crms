from django.contrib import admin

from .models import Category, Product, Review, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "sort_order")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("parent__id", "sort_order", "name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "slug", "sort_order")
    list_filter = ("group",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("group", "sort_order", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "deployment_type",
        "business_size",
        "free_plan",
        "trial_available",
        "rating",
        "is_published",
        "updated_info_at",
    )
    list_filter = (
        "is_published",
        "deployment_type",
        "business_size",
        "free_plan",
        "trial_available",
        "support_24_7",
        "category",
        "pricing_model",
    )
    search_fields = ("name", "slug", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tags",)
    ordering = ("sort_order", "name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основное", {"fields": ("name", "slug", "logo", "short_description", "category", "website_url", "is_published", "sort_order")}),
        ("Описание", {"fields": ("description", "key_features", "advantages", "disadvantages")}),
        ("Характеристики", {"fields": ("deployment_type", "business_size", "support_24_7", "tags")}),
        ("Цены", {"fields": ("pricing_model", "pricing_details", "free_plan", "trial_available")}),
        ("Рейтинг", {"fields": ("rating", "reviews_count")}),
        ("SEO/Актуальность", {"fields": ("updated_info_at",)}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "author_name", "rating", "is_published", "created_at")
    list_filter = ("is_published", "rating", "created_at")
    search_fields = ("author_name", "text", "product__name")
    ordering = ("-created_at",)

