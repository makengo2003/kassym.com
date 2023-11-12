from base_object_presenter.urls import BaseURLsPresenter
from .views import CartViewsPresenter


class CartURLsPresenter(BaseURLsPresenter):
    views = CartViewsPresenter()
    urls: list = ["get_many", "add", "delete", "update_fields", "clear"]


urlpatterns = CartURLsPresenter().get_urlpatterns()
