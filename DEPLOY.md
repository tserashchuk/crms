# Публикация на Heroku

## Требования

- Аккаунт [Heroku](https://www.heroku.com/)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) установлен
- Git

## Шаги

### 1. Логин и создание приложения

```bash
heroku login
heroku create
# или с именем: heroku create имя-вашего-приложения
```

### 2. Добавить PostgreSQL

В бесплатном плане Heroku Postgres больше недоступен. Используйте мини-план или другой аддон:

```bash
heroku addons:create heroku-postgresql:mini
```

После этого переменная `DATABASE_URL` будет установлена автоматически.

### 3. Переменные окружения

```bash
heroku config:set SECRET_KEY="ваш-длинный-секретный-ключ"
heroku config:set DEBUG=0
heroku config:set ALLOWED_HOSTS=".herokuapp.com"
```

Опционально (для кнопки «Заполнить через DeepSeek» в карточке сервиса):

```bash
heroku config:set DEEPSEEK_API_KEY="ваш-ключ-deepseek-api"
```

Сгенерировать SECRET_KEY (локально):

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4. Деплой

```bash
git add .
git commit -m "Prepare for Heroku"
git push heroku main
```

Если ветка называется `master`:

```bash
git push heroku master
```

### 5. Миграции и суперпользователь

Миграции выполняются автоматически при деплое (процесс `release` в Procfile).

Создать суперпользователя админки:

```bash
heroku run python manage.py createsuperuser
```

### 6. Открыть приложение

```bash
heroku open
```

Админка: `https://ваше-приложение.herokuapp.com/admin/`

## Важно

- **Медиафайлы (загрузки логотипов)** на Heroku не сохраняются между деплоями (файловая система эфемерная). Для продакшена нужен внешний сторидж (например Amazon S3 + django-storages).
- **Статика** отдаётся через WhiteNoise, отдельный CDN не обязателен.
- Для продакшена обязательно установите `DEBUG=0` и надёжный `SECRET_KEY` (иначе Django покажет предупреждения и куки сессии будут небезопасны).
- При `DEBUG=0` автоматически включаются: редирект на HTTPS, Secure-флаги для куки, HSTS.

## Локальная проверка перед деплоем

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Запуск с Gunicorn локально:

```bash
gunicorn crm_catalog.wsgi
```
