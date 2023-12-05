from django.urls import path
from .views import *

urlpatterns = [
    path("get_orders/", get_orders_view),
    path("make_delivered/", make_delivered_view)
]
