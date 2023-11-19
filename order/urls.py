from base_object_presenter.urls import BaseURLsPresenter
from .views import OrderViewsPresenter


class OrderURLsPresenter(BaseURLsPresenter):
    views = OrderViewsPresenter()
    urls: list = ["calculate", "add", "get_many", "get_orders_counts", "accept", "edit"]


urlpatterns = OrderURLsPresenter().get_urlpatterns()
