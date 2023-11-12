from typing import Mapping, MutableMapping

from django.contrib.auth.models import User

from base_object_presenter.services import BaseServicesPresenter
from cart.models import CartItem
from .models import OrderModelPresenter


class OrderServicesPresenter(BaseServicesPresenter):
    model_presenter = OrderModelPresenter()

    def calculate(self, user: User, data: Mapping):
        return self.model_presenter.calculate(user, data)

    def add_custom(self, add_request_schema: MutableMapping, files: Mapping) -> int:
        serializer = self.serializers["object_add_form"](data=add_request_schema)
        serializer.is_valid(raise_exception=True)
        return serializer.save(files=files).id
