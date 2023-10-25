from django.urls import path
from .views import *


urlpatterns = [
    path("get_contacts/", get_contacts_view, name="get_contacts"),
    path("save_contacts/", save_contacts_view, name="save_contacts"),
    path("get_about_us_text/", get_about_us_text_view, name="get_about_us_text"),
    path("save_about_us_text/", save_about_us_text_view, name="save_about_us_text"),
    path("save_guarantee_text/", save_guarantee_text_view, name="save_guarantee_text"),

    path("get_slides/", get_slides_view, name="get_slides"),
    path("save_slides/", save_slides_view, name="save_slides"),
]
