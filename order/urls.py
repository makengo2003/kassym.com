from base_object_presenter.urls import BaseURLsPresenter
from .views import OrderViewsPresenter


class OrderURLsPresenter(BaseURLsPresenter):
    views = OrderViewsPresenter()
    urls: list = ["calculate", "add"]


urlpatterns = OrderURLsPresenter().get_urlpatterns()
