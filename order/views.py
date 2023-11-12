from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsUser
from base_object_presenter.views import BaseViewsPresenter, get_permissions_for_view
from .services import OrderServicesPresenter


class OrderViewsPresenter(BaseViewsPresenter):
    services = OrderServicesPresenter()
    permissions = {
        "calculate": [IsUser],
        "add": [IsUser],
    }

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("calculate")
    def calculate_view(self, request: Request) -> Response:
        calculation_data = self.services.calculate(request.user, request.query_params)
        return Response(calculation_data)

    @method_decorator(api_view(["POST"]))
    @method_decorator(parser_classes([MultiPartParser, FormParser]))
    @get_permissions_for_view("add")
    def add_view(self, request: Request) -> Response:
        obj_id = self.services.add_custom(request.data, request.FILES)
        return Response({"id": obj_id})
