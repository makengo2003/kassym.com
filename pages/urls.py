from django.urls import path
from .views import *


urlpatterns = [
    path("", main_page_view, name="main_page"),
    path("favourites/", favourites_page_view, name="favourites_page"),
    path("my_cards/", my_cards_page_view, name="my_cards_page"),
    path("messages/", messages_page_view, name="messages_page"),
    path("messages/<str:message_type>/", message_page_view, name="message_page"),
    path("my_orders/", my_orders_page_view, name="my_orders_page"),
    path("my_order/", my_order_page_view, name="my_order_page"),
    path("products/", products_page_view, name="products_page"),
    path("product/", product_page_view, name="product_page"),
    path("admin/", admin_page_view, name="admin_page"),
    path("profile/", profile_page_view, name="profile_page"),
    path("courses/", courses_page_view, name="courses_page"),
    path("lesson/", lesson_page_view, name="lesson_page"),
    path("search_result/", search_page_view, name="search_result"),
    path("cart/", cart_page_view, name="cart_page"),
    path("manager/", manager_page_view, name="manager_page"),
    path("buyer/", buyer_page_view, name="buyer_page"),
    path("super_admin/", super_admin_page_view, name="super_admin_page"),
    path("supplier/", supplier_page_view, name="supplier_page"),

    path("about_us/", about_us_view, name="about_us"),
    path("agreement/", guarantee_view, name="guarantee"),
]
