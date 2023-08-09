from django.urls import path
from .views import *


urlpatterns = [
    path("", main_page_view, name="main_page"),
    path("favourites/", favourites_page_view, name="favourites_page"),
    path("products/", products_page_view, name="products_page"),
    path("product/", product_page_view, name="product_page"),
    path("admin/", admin_page_view, name="admin_page"),
    path("profile/", profile_page_view, name="profile_page"),
    path("courses/", courses_page_view, name="courses_page"),
    path("lesson/", lesson_page_view, name="lesson_page"),
    path("search_result/", search_result_page_view, name="search_result"),

    path("about_us/", about_us_view, name="about_us"),
    path("agreement/", guarantee_view, name="guarantee"),
]
