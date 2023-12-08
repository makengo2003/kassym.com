from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsUser
from base_object_presenter.views import BaseViewsPresenter, get_permissions_for_view
from manager.permissions import IsManager
from . import services
from .services_presenter import OrderServicesPresenter


class OrderViewsPresenter(BaseViewsPresenter):
    services = OrderServicesPresenter()
    permissions = {
        "calculate": [IsUser],
        "add": [IsUser],
        "get_many": [IsUser],
        "get_orders_counts": [IsManager],
        "accept": [IsManager],
        "edit": [IsManager]
    }

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("calculate")
    def calculate_view(self, request: Request) -> Response:
        calculation_data = services.calculate(request.user, request.query_params)
        return Response(calculation_data)

    @method_decorator(api_view(["POST"]))
    @method_decorator(parser_classes([MultiPartParser, FormParser]))
    @get_permissions_for_view("add")
    def add_view(self, request: Request) -> Response:
        obj_id = self.services.add_custom(request.data, request.FILES)
        return Response({"id": obj_id})

    @method_decorator(api_view(["POST"]))
    @method_decorator(parser_classes([MultiPartParser, FormParser]))
    @get_permissions_for_view("edit")
    def edit_view(self, request: Request) -> Response:
        self.services.edit_custom(request.data.get("id"), request.data.get("new_comments", ""), request.FILES)
        return Response({"success": True})

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_many")
    def get_many_view(self, request: Request) -> Response:
        objs = self.services.get_many(request.query_params)
        return Response(objs.data)

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_orders_counts")
    def get_orders_counts_view(self, request):
        orders_counts = self.services.get_orders_counts(request.query_params.get("created_at__date"))
        return Response(orders_counts)

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("accept")
    def accept_view(self, request: Request) -> Response:
        self.services.accept_order(request.data.get("id"))
        return Response({"success": True})

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_many")
    def get_order_comments_view(self, request):
        comments = self.services.get_order_comments(request.query_params)
        return Response(comments)
