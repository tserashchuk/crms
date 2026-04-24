from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.views.decorators.http import require_http_methods

from .deepseek import fetch_product_data
from .models import Category, ContentOrder, ContentSubmission, Product, Review, Tag


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
    change_form_template = "admin/catalog/product/change_form.html"

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
    search_fields = ("name", "slug", "short_description", "description", "extended_description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tags",)
    ordering = ("sort_order", "name")
    readonly_fields = ("created_at", "updated_at")

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path(
                "deepseek-fill/",
                self.admin_site.admin_view(require_http_methods(["POST"])(self._deepseek_fill_view)),
                name="catalog_product_deepseek_fill",
            ),
        ]
        return extra + urls

    def _deepseek_fill_view(self, request):
        api_key = getattr(settings, "DEEPSEEK_API_KEY", None) or ""
        if not api_key:
            return JsonResponse({"error": "DEEPSEEK_API_KEY не задан."}, status=400)
        name = (request.POST.get("name") or "").strip()
        category_hint = (request.POST.get("category_hint") or "").strip()
        result = fetch_product_data(name, api_key=api_key, category_hint=category_hint)
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=400)
        return JsonResponse(result)

    fieldsets = (
        ("Основное", {"fields": ("name", "slug", "logo", "short_description", "category", "website_url", "documentation_url", "support_url", "is_published", "sort_order")}),
        ("Описание", {"fields": ("description", "extended_description", "key_features", "advantages", "disadvantages")}),
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


@admin.register(ContentOrder)
class ContentOrderAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "max_submissions", "submissions_count", "submit_link", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "token", "internal_note")
    readonly_fields = ("token", "submit_link", "created_at", "updated_at")
    fields = ("title", "internal_note", "is_active", "max_submissions", "token", "submit_link", "created_at", "updated_at")

    @admin.display(description="Заявок")
    def submissions_count(self, obj: ContentOrder) -> int:
        return obj.submissions.count()

    @admin.display(description="Ссылка для биржи")
    def submit_link(self, obj: ContentOrder) -> str:
        if not obj.pk:
            return "—"
        path = obj.get_submit_path()
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', path, path)


@admin.register(ContentSubmission)
class ContentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("public_code", "submission_name", "order", "status", "catalog_product_link", "submitted_at", "ip_address")
    list_filter = ("status", "submitted_at")
    search_fields = ("public_code", "executor_comment", "order__title")
    readonly_fields = ("public_code", "submitted_at", "ip_address", "product_data", "created_product")
    ordering = ("-submitted_at",)
    raw_id_fields = ("order", "created_product")
    fieldsets = (
        (
            None,
            {
                "fields": ("order", "public_code", "status", "created_product", "submitted_at", "ip_address"),
                "description": "При смене статуса на «Одобрено» и сохранении заявки автоматически создаётся сервис в каталоге (если ещё не создан). "
                "Для уже одобрённых ранее заявок без сервиса выполните: python manage.py sync_approved_submissions",
            },
        ),
        ("Карточка сервиса (как придёт в каталог после модерации)", {"fields": ("product_data", "submitted_logo", "attachment")}),
        ("Исполнитель", {"fields": ("executor_comment",)}),
        ("Модерация", {"fields": ("moderator_note",)}),
    )

    @admin.display(description="Название в заявке")
    def submission_name(self, obj: ContentSubmission) -> str:
        return (obj.product_data or {}).get("name") or "—"

    @admin.display(description="В каталоге")
    def catalog_product_link(self, obj: ContentSubmission) -> str:
        if not obj.created_product_id:
            return "—"
        p = obj.created_product
        url = p.get_absolute_url()
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, p.name)

