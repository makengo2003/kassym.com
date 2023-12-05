from rest_framework.decorators import permission_classes, api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
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
def start_to_sort_view(request):
    services.start_to_sort(request.data.get("id"), request.user.first_name + " " + request.user.last_name)
    return Response({"success": True})


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsBuyer])
def save_sorting_view(request):
    services.save_sorting(request.data.get("order_id"), request.data.get("sorted_purchases"),
                          request.data.get("replaced_purchases"),
                          request.data.get("not_available_purchases"), request.FILES)
    return Response({"success": True})


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsBuyer])
def finish_sorting_view(request):
    services.finish_sorting(request.data.get("id"), request.data.get("sorted_report"))
    return Response({"success": True})
