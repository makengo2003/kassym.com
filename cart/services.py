from django.contrib.auth.models import User

from base_object_presenter.services import BaseServicesPresenter
from .models import CartModelPresenter


class CartServicesPresenter(BaseServicesPresenter):
    model_presenter = CartModelPresenter()

    def clear(self, user: User) -> None:
        self.model_presenter.model.objects.filter(user=user).delete()
