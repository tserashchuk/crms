from django.urls import path

from . import views


app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("saved/", views.saved_list, name="saved_list"),
    path("saved/clear/", views.clear_saved, name="clear_saved"),
    path("compare/", views.compare_list, name="compare_list"),
    path("compare/clear/", views.clear_compare, name="clear_compare"),
    path("saved/toggle/<int:product_id>/", views.toggle_saved, name="toggle_saved"),
    path("compare/toggle/<int:product_id>/", views.toggle_compare, name="toggle_compare"),
    path("<slug:top_slug>/", views.category_top, name="category_top"),
    path("<slug:top_slug>/<slug:slug>/", views.category_or_product, name="category_or_product"),
]

