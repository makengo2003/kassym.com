from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsUser
from base_object_presenter.views import BaseViewsPresenter, get_permissions_for_view
from .services import CartServicesPresenter


class CartViewsPresenter(BaseViewsPresenter):
    services = CartServicesPresenter()
    permissions = {
        "get_many": [IsUser],
        "delete": [IsUser],
        "add": [IsUser],
        "update_fields": [IsUser],
        "clear": [IsUser]
    }

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("clear")
    def clear_view(self, request: Request) -> Response:
        self.services.clear(request.user)
        return Response({"success": True})
