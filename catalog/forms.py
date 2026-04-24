from __future__ import annotations

from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Category, Product, Review, Tag

MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024  # 5 МБ
MAX_LOGO_BYTES = 2 * 1024 * 1024  # 2 МБ
MAX_LONG_TEXT = 100_000

_TW_IN = "block w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 focus:outline-none"
_TW_TA = "block w-full rounded-lg border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 focus:outline-none"
_TW_SEL = _TW_IN
_TW_MULTI = _TW_IN + " min-h-[10rem]"


def _strip_nulls(s: str) -> str:
    return (s or "").replace("\x00", "")


class ReviewForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "class": "d-none",
            }
        ),
        help_text="",
    )

    class Meta:
        model = Review
        fields = ["author_name", "rating", "text"]
        widgets = {
            "author_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше имя"}),
            "rating": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "5"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Ваш отзыв"}),
        }

    def clean(self):
        cleaned = super().clean()
        # honeypot: если поле заполнено — почти наверняка бот
        if self.data.get("website"):
            raise forms.ValidationError("Ошибка отправки формы.")
        return cleaned


class ContentSubmissionForm(forms.Form):
    """
    Поля как у карточки сервиса (Product), без рейтинга, SEO-источника и настроек публикации.
    Данные сериализуются в ContentSubmission.product_data + файл submitted_logo.
    """

    name = forms.CharField(
        label=Product._meta.get_field("name").verbose_name,
        max_length=200,
        widget=forms.TextInput(attrs={"class": _TW_IN, "placeholder": "Название CRM / сервиса"}),
    )
    slug = forms.CharField(
        label=Product._meta.get_field("slug").verbose_name,
        max_length=220,
        required=False,
        help_text="Латиница, дефисы. Можно оставить пустым — подставится из названия при модерации.",
        widget=forms.TextInput(attrs={"class": _TW_IN, "placeholder": "например, my-awesome-crm"}),
    )
    short_description = forms.CharField(
        label=Product._meta.get_field("short_description").verbose_name,
        max_length=300,
        widget=forms.TextInput(attrs={"class": _TW_IN, "placeholder": "Одна строка — суть продукта"}),
    )
    category = forms.ModelChoiceField(
        label=Product._meta.get_field("category").verbose_name,
        queryset=Category.objects.select_related("parent").order_by("parent_id", "sort_order", "name"),
        empty_label=None,
        widget=forms.Select(attrs={"class": _TW_SEL}),
    )
    submitted_logo = forms.ImageField(
        label=Product._meta.get_field("logo").verbose_name,
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
            }
        ),
    )

    website_url = forms.URLField(
        label=Product._meta.get_field("website_url").verbose_name,
        max_length=500,
        required=False,
        widget=forms.URLInput(attrs={"class": _TW_IN, "placeholder": "https://"}),
    )
    documentation_url = forms.URLField(
        label=Product._meta.get_field("documentation_url").verbose_name,
        max_length=500,
        required=False,
        widget=forms.URLInput(attrs={"class": _TW_IN, "placeholder": "https://"}),
    )
    support_url = forms.URLField(
        label=Product._meta.get_field("support_url").verbose_name,
        max_length=500,
        required=False,
        widget=forms.URLInput(attrs={"class": _TW_IN, "placeholder": "https://"}),
    )

    description = forms.CharField(
        label=Product._meta.get_field("description").verbose_name,
        max_length=MAX_LONG_TEXT,
        required=False,
        widget=forms.Textarea(attrs={"class": _TW_TA, "rows": 6, "placeholder": "Полное описание (без HTML)"}),
    )
    extended_description = forms.CharField(
        label=Product._meta.get_field("extended_description").verbose_name,
        max_length=MAX_LONG_TEXT,
        required=False,
        widget=forms.Textarea(attrs={"class": _TW_TA, "rows": 5, "placeholder": "Дополнительно о продукте"}),
    )
    key_features = forms.CharField(
        label=Product._meta.get_field("key_features").verbose_name,
        max_length=MAX_LONG_TEXT,
        required=False,
        help_text=Product._meta.get_field("key_features").help_text or "",
        widget=forms.Textarea(attrs={"class": _TW_TA, "rows": 5, "placeholder": "По одной функции на строку"}),
    )
    advantages = forms.CharField(
        label=Product._meta.get_field("advantages").verbose_name,
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={"class": _TW_IN}),
    )
    disadvantages = forms.CharField(
        label=Product._meta.get_field("disadvantages").verbose_name,
        max_length=MAX_LONG_TEXT,
        required=False,
        widget=forms.Textarea(attrs={"class": _TW_TA, "rows": 4}),
    )

    deployment_type = forms.ChoiceField(
        label=Product._meta.get_field("deployment_type").verbose_name,
        choices=[("", "— не указано")] + list(Product.Deployment.choices),
        required=False,
        widget=forms.Select(attrs={"class": _TW_SEL}),
    )
    business_size = forms.ChoiceField(
        label=Product._meta.get_field("business_size").verbose_name,
        choices=[("", "— не указано")] + list(Product.BusinessSize.choices),
        required=False,
        widget=forms.Select(attrs={"class": _TW_SEL}),
    )
    support_24_7 = forms.BooleanField(
        label=Product._meta.get_field("support_24_7").verbose_name,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-teal-600 focus:ring-teal-500"}),
    )
    tags = forms.ModelMultipleChoiceField(
        label=Product._meta.get_field("tags").verbose_name,
        queryset=Tag.objects.all().order_by("group", "sort_order", "name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": _TW_MULTI, "size": 12}),
    )

    free_plan = forms.BooleanField(
        label=Product._meta.get_field("free_plan").verbose_name,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-teal-600 focus:ring-teal-500"}),
    )
    trial_available = forms.BooleanField(
        label=Product._meta.get_field("trial_available").verbose_name,
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "rounded border-slate-300 text-teal-600 focus:ring-teal-500"}),
    )
    pricing_model = forms.ChoiceField(
        label=Product._meta.get_field("pricing_model").verbose_name,
        choices=[("", "— не указано")] + list(Product.PricingModel.choices),
        required=False,
        widget=forms.Select(attrs={"class": _TW_SEL}),
    )
    pricing_details = forms.CharField(
        label=Product._meta.get_field("pricing_details").verbose_name,
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": _TW_IN}),
    )

    updated_info_at = forms.DateField(
        label=Product._meta.get_field("updated_info_at").verbose_name,
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": _TW_IN}),
    )

    executor_comment = forms.CharField(
        label="Комментарий к заказу",
        required=False,
        max_length=500,
        widget=forms.TextInput(
            attrs={
                "class": _TW_IN,
                "placeholder": "Номер заказа на бирже, ссылки на ТЗ и т.п.",
            }
        ),
    )
    attachment = forms.FileField(
        label="Дополнительный файл (PDF, DOCX, TXT, ZIP, MD)",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100"
            }
        ),
    )
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "style": "position:absolute;left:-9999px;width:1px;height:1px;",
                "aria-hidden": "true",
            }
        ),
    )

    def clean_name(self) -> str:
        return _strip_nulls(self.cleaned_data.get("name", "").strip())

    def clean_slug(self) -> str:
        raw = _strip_nulls((self.cleaned_data.get("slug") or "").strip().lower())
        if not raw:
            return ""
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if not set(raw) <= allowed:
            raise ValidationError("Только латинские буквы, цифры и дефис.")
        return raw

    def clean_short_description(self) -> str:
        return _strip_nulls(self.cleaned_data.get("short_description", "").strip())

    def clean_updated_info_at(self):
        d = self.cleaned_data.get("updated_info_at")
        if d and d > date.today():
            raise ValidationError("Дата не может быть в будущем.")
        return d

    def clean_submitted_logo(self):
        f = self.cleaned_data.get("submitted_logo")
        if not f:
            return None
        if f.size > MAX_LOGO_BYTES:
            raise ValidationError(f"Логотип больше {MAX_LOGO_BYTES // (1024 * 1024)} МБ.")
        return f

    def clean_attachment(self):
        f = self.cleaned_data.get("attachment")
        if not f:
            return None
        if f.size > MAX_ATTACHMENT_BYTES:
            raise ValidationError(f"Файл больше {MAX_ATTACHMENT_BYTES // (1024 * 1024)} МБ.")
        return f

    def clean(self):
        cleaned = super().clean()
        if self.data.get("website"):
            raise ValidationError("Ошибка отправки формы.")
        for key in (
            "description",
            "extended_description",
            "key_features",
            "advantages",
            "disadvantages",
            "pricing_details",
            "executor_comment",
        ):
            if key in cleaned and isinstance(cleaned[key], str):
                cleaned[key] = _strip_nulls(cleaned[key].strip())
        return cleaned

    def to_product_data(self) -> dict:
        """Сериализация для JSONField (без файлов)."""
        c = self.cleaned_data
        tags = c.get("tags") or []
        tag_ids = [t.pk for t in tags]
        uia = c.get("updated_info_at")
        slug_val = (c.get("slug") or "").strip()
        if not slug_val:
            slug_val = (slugify(c["name"]) or "service")[:220]
        return {
            "name": c["name"],
            "slug": slug_val,
            "short_description": c["short_description"],
            "category_id": c["category"].pk,
            "website_url": (c.get("website_url") or "").strip(),
            "documentation_url": (c.get("documentation_url") or "").strip(),
            "support_url": (c.get("support_url") or "").strip(),
            "description": (c.get("description") or "").strip(),
            "extended_description": (c.get("extended_description") or "").strip(),
            "key_features": (c.get("key_features") or "").strip(),
            "advantages": (c.get("advantages") or "").strip(),
            "disadvantages": (c.get("disadvantages") or "").strip(),
            "deployment_type": (c.get("deployment_type") or "").strip(),
            "business_size": (c.get("business_size") or "").strip(),
            "free_plan": bool(c.get("free_plan")),
            "trial_available": bool(c.get("trial_available")),
            "pricing_model": (c.get("pricing_model") or "").strip(),
            "pricing_details": (c.get("pricing_details") or "").strip(),
            "support_24_7": bool(c.get("support_24_7")),
            "updated_info_at": uia.isoformat() if uia else "",
            "tag_ids": tag_ids,
        }

