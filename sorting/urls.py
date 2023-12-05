from django.urls import path
from .views import *

urlpatterns = [
    path("get_orders/", get_orders_view),
    path("start_to_sort/", start_to_sort_view),
    path("finish_sorting/", finish_sorting_view),
    path("save_sorting/", save_sorting_view)
]
