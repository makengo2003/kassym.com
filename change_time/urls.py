from django.urls import path
from .views import get_change_times_view, finish_change_time_view


urlpatterns = [
    path("get_many/", get_change_times_view),
    path("finish/", finish_change_time_view)
]
