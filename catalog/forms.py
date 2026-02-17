from __future__ import annotations

from django import forms

from .models import Review


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

