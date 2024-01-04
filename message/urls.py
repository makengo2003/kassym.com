from django.urls import path
from .views import add_message_view, get_chats_view

urlpatterns = [
    path("add_message/", add_message_view),
    path("get_chats/", get_chats_view),
]
