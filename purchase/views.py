from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response

from base_object_presenter.views import BaseViewsPresenter, get_permissions_for_view
from .permissions import IsBuyer
from .services import PurchaseServicesPresenter


class PurchaseViewsPresenter(BaseViewsPresenter):
    services = PurchaseServicesPresenter()
    permissions = {
        "get_many": [IsBuyer],
        "get_purchases_counts": [IsBuyer],
        "make": [IsBuyer],
    }

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_many")
    def get_purchases_view(self, request: Request) -> Response:
        purchases = self.services.get_purchases(request.query_params.get("change_time"),
                                                request.query_params.get("market"), request.query_params.get("status"))
        return Response(purchases.data)

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_purchases_counts")
    def get_purchases_counts_view(self, request: Request) -> Response:
        purchases_counts = self.services.get_purchases_counts(request.query_params.get("change_time", "2003-07-01"))
        return Response(purchases_counts)

    @method_decorator(api_view(["POST"]))
    @method_decorator(parser_classes([MultiPartParser, FormParser]))
    @get_permissions_for_view("make")
    def make_view(self, request: Request) -> Response:
        response = self.services.make_purchase(request.data, request.FILES)
        return Response(response)

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("make")
    def save_is_being_considered_purchases_view(self, request):
        self.services.save_is_being_considered_purchases(request.data)
        return Response({"success": True})

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_many")
    def get_is_being_considered_purchase_view(self, request):
        purchases = self.services.get_is_being_considered_purchase(request.query_params)
        return Response(purchases)
