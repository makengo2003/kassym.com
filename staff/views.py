from base_object_presenter.views import BaseViewsPresenter
from .services import StaffServicesPresenter


class StaffViewsPresenter(BaseViewsPresenter):
    services = StaffServicesPresenter()
