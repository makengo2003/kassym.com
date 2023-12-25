from django.urls import path
from .views import get_expenses_view, save_view


urlpatterns = [
    path("get_expenses/", get_expenses_view),
    path("save/", save_view),
]
