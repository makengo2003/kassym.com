from base_object_presenter.services import BaseServicesPresenter
from .models import StaffModelPresenter


class StaffServicesPresenter(BaseServicesPresenter):
    def __init__(self):
        self.model_presenter = StaffModelPresenter()
        super().__init__()
