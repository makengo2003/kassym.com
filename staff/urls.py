from base_object_presenter.urls import BaseURLsPresenter
from .views import StaffViewsPresenter


class StaffURLsPresenter(BaseURLsPresenter):
    views = StaffViewsPresenter()


urlpatterns = StaffURLsPresenter().get_urlpatterns()
