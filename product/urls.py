from django.urls import path
from .views import *


urlpatterns = [
    path("get_products/", get_products_view, name="get_products"),
    path("search_products/", search_products_view, name="search_products"),
    path("get_product/", get_product_view, name="get_product"),
    path("add_product/", add_product_view, name="add_product"),
    path("delete_product/", delete_product_view, name="delete_product"),
    path("edit_product/", edit_product_view, name="edit_product"),
    path("change_product_is_available_status/", change_product_is_available_status_view,
         name="change_product_is_available_status")
]
