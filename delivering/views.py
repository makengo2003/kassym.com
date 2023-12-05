from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from purchase.permissions import IsBuyer
from . import services


@api_view(["GET"])
@permission_classes([IsBuyer])
def get_orders_view(request):
    orders = services.get_orders(request.query_params.get("status", None), request.query_params.get("id", None))
    return Response(orders)


@api_view(["POST"])
@permission_classes([IsBuyer])
def make_delivered_view(request):
    services.make_delivered(request.data.get("id"), request.user.first_name + " " + request.user.last_name)
    return Response({"success": True})
