from django.urls import path
from .views import *


urlpatterns = [
    path("get_products/", get_products_view),
    path("get_suppliers/", get_suppliers_view)
]
