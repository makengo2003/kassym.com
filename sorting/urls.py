from django.urls import path
from .views import *

urlpatterns = [
    path("get_orders/", get_orders_view),
    path("start_to_sort/", start_to_sort_view),
    path("finish_sorting/", finish_sorting_view),
    path("save_sorting/", save_sorting_view),
    path("get_order/", get_order_view),
    path("get_not_sorted_products/", get_not_sorted_products_view),
    path("get_not_sorted_product/", get_not_sorted_product_view),
]
