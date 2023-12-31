from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import *

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change_password/", change_password_view, name="change_password"),
    path("add_products_to_favourites/", add_products_to_favourites_view, name="add_products_to_favourites"),
    path("remove_product_from_favourites/", remove_product_from_favourites_view, name="remove_product_from_favourites"),
    path("clear_favourites/", clear_favourites_view, name="clear_favourites"),
    path("change_fullname/", change_fullname_view, name="change_fullname"),
    path("change_company_name/", change_company_name_view, name="change_company_name"),
    path("add_client/", add_client_view, name="add_client"),
    path("edit_client/", edit_client_view, name="edit_client"),
    path("delete_client/", delete_client_view, name="delete_client"),
    path("get_client/", get_client_view, name="get_client"),
    path("get_clients/", get_clients_view, name="get_clients"),
    path("search_clients/", search_clients_view, name="search_clients"),
    path("leave_request/", leave_request_view, name="leave_request"),
    path("get_finance/", get_finance_view, name="get_finance"),
    path("add_to_my_cards/", add_to_my_cards_view, name="add_to_my_cards"),
    path("remove_from_my_cards/", remove_from_my_cards_view, name="remove_from_my_cards")
]
