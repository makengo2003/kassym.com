from base_object_presenter.urls import BaseURLsPresenter
from .views import OrderViewsPresenter


class OrderURLsPresenter(BaseURLsPresenter):
    views = OrderViewsPresenter()
    urls: list = ["calculate", "add", "get_many", "get_orders_counts", "accept", "edit", "get_order_comments"]


urlpatterns = OrderURLsPresenter().get_urlpatterns()
