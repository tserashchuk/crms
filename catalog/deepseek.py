"""
Запрос к DeepSeek API для заполнения карточки сервиса (CRM/CDP/ERP) по названию.
"""
from __future__ import annotations

import json
import re

import requests


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """Ты — помощник по заполнению карточек сервисов (CRM, CDP, ERP и подобных систем).
По названию сервиса верни JSON со следующими полями (все тексты на русском, только значения полей):
- short_description: краткое описание или слоган, до 300 символов
- website_url: официальный сайт (URL или пустая строка)
- documentation_url: ссылка на документацию (URL или пустая строка)
- support_url: ссылка на раздел поддержки (URL или пустая строка)
- description: полное описание сервиса, 2–5 предложений
- extended_description: расширенное описание (подробный текст, возможности, сценарии использования), можно несколько абзацев, суммарный объем около 1000 символов
- key_features: ключевые функции/модули, по одной на строку (многострочная строка)
- advantages: преимущества, до 300 символов
- disadvantages: недостатки или ограничения (строка, можно пусто)
- deployment_type: ровно одно из: saas, on_premise, hybrid, cloud или пустая строка
- business_size: ровно одно из: small, medium, large, startup или пустая строка
- free_plan: true или false
- trial_available: true или false
- pricing_model: ровно одно из: subscription, one_time, freemium, quote или пустая строка
- pricing_details: кратко о ценах/тарифах, до 200 символов
- support_24_7: true или false

Отвечай только валидным JSON, без markdown-блоков и без пояснений до или после."""

USER_PROMPT_TEMPLATE = """Собери информацию о сервисе/продукте для каталога CRM/CDP/ERP и верни JSON с полями как в инструкции. Название сервиса: «{name}»."""


def fetch_product_data(name: str, *, api_key: str, category_hint: str = "") -> dict:
    """
    Отправляет запрос в DeepSeek с названием сервиса, возвращает словарь
    с ключами, совпадающими с полями модели Product (частично).
    """
    if not name or not name.strip():
        return {"error": "Название сервиса не указано."}

    prompt = USER_PROMPT_TEMPLATE.format(name=name.strip())
    if category_hint:
        prompt += f" Контекст категории: {category_hint}."

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 3500,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    try:
        data = resp.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or "{}"
    except (IndexError, KeyError, TypeError):
        return {"error": "Неверный формат ответа API."}

    # Иногда модель оборачивает JSON в ```json ... ```
    content = content.strip()
    if "```" in content:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if match:
            content = match.group(1).strip()

    try:
        out = json.loads(content)
    except json.JSONDecodeError as e:
        return {"error": f"Ошибка разбора JSON: {e}"}

    # Нормализуем типы и обрезаем под ограничения модели
    result = {}
    str_fields = (
        "short_description",
        "website_url",
        "documentation_url",
        "support_url",
        "description",
        "extended_description",
        "key_features",
        "advantages",
        "disadvantages",
        "pricing_details",
    )
    for key in str_fields:
        if key in out and out[key] is not None:
            result[key] = str(out[key]).strip()[:5000]
        else:
            result[key] = ""

    result["short_description"] = result.get("short_description", "")[:300]
    result["advantages"] = result.get("advantages", "")[:300]
    result["pricing_details"] = result.get("pricing_details", "")[:200]

    choice_fields = {
        "deployment_type": ("saas", "on_premise", "hybrid", "cloud"),
        "business_size": ("small", "medium", "large", "startup"),
        "pricing_model": ("subscription", "one_time", "freemium", "quote"),
    }
    for key, allowed in choice_fields.items():
        val = out.get(key)
        if val is None or not str(val).strip():
            result[key] = ""
        else:
            val = str(val).strip().lower()
            result[key] = val if val in allowed else ""

    for key in ("free_plan", "trial_available", "support_24_7"):
        val = out.get(key)
        if isinstance(val, bool):
            result[key] = val
        elif isinstance(val, str):
            result[key] = val.strip().lower() in ("true", "1", "yes", "да")
        else:
            result[key] = False

    return result
