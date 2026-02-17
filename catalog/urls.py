from django.urls import path

from . import views


app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("<slug:top_slug>/", views.category_top, name="category_top"),
    path("<slug:top_slug>/<slug:slug>/", views.category_or_product, name="category_or_product"),
]

