from django.urls import path
from .views import *


urlpatterns = [
    path("get_categories/", get_categories_view, name="get_categories"),
    path("get_category/", get_category_view, name="get_category"),
    path("add_category/", add_category_view, name="add_category"),
    path("delete_category/", delete_category_view, name="delete_category"),
    path("edit_category/", edit_category_view, name="edit_category"),
    path("save_categories_order/", save_categories_order_view, name="save_categories_order")
]
