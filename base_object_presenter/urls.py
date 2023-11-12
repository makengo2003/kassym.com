from django.urls import path
from .views import BaseViewsPresenter


class BaseURLsPresenter:
    views: BaseViewsPresenter
    urls: list = ["get_many", "add", "get", "edit", "delete", "update_fields"]

    def get_urlpatterns(self) -> list:
        return [path(url + "/", getattr(self.views, url + "_view")) for url in self.urls]
