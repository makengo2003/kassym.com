from django.contrib.auth.models import User
from base_object_presenter.models import BaseModelPresenter


class StaffModelPresenter(BaseModelPresenter):
    model = User
