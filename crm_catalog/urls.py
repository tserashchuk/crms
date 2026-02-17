from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "Каталог CRM/CDP/ERP"
admin.site.site_title = "Админка каталога"
admin.site.index_title = "Управление контентом"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

