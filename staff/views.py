from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsStaff, IsAdmin
from base_object_presenter.views import BaseViewsPresenter
from .services import StaffServicesPresenter


class StaffViewsPresenter(BaseViewsPresenter):
    services = StaffServicesPresenter()
    permissions = {
        "get": [IsAdmin],
        "get_many": [IsAdmin],
        "delete": [IsAdmin],
        "add": [IsAdmin],
        "edit": [IsAdmin],
        "update_fields": [IsAdmin]
    }

    @method_decorator(api_view(["POST"]))
    @method_decorator(permission_classes([IsStaff]))
    def add_order_view(self, request: Request) -> Response:
        self.services.add_order(request.data)
        return Response({"success": True})
