from __future__ import annotations

from urllib.parse import urlencode

from django import template


register = template.Library()


@register.simple_tag
def querystring(request, **kwargs) -> str:
    """
    Сохраняет текущие GET параметры и позволяет переопределить часть из них.
    Пример: href="{% querystring request page=2 %}"
    """
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = str(value)
    qs = params.urlencode()
    return f"?{qs}" if qs else ""

