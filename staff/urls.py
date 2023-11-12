from base_object_presenter.urls import BaseURLsPresenter
from .views import StaffViewsPresenter


class StaffURLsPresenter(BaseURLsPresenter):
    views = StaffViewsPresenter()
    urls = ["get_many", "add", "get", "edit", "delete", "add_order"]


urlpatterns = StaffURLsPresenter().get_urlpatterns()
