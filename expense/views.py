from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from purchase.permissions import IsBuyer, IsBuyerOrManager
from . import services


@api_view(["GET"])
@permission_classes([IsBuyerOrManager])
def get_expenses_view(request):
    expenses = services.get_expenses(request.user, request.query_params.get("change_time"))
    return Response(expenses)


@api_view(["POST"])
@permission_classes([IsBuyerOrManager])
def save_view(request):
    services.save(request.user, request.data)
    return Response({"success": True})
