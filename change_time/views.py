from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .permissions import IsManagerOrBuyer
from .services import get_change_times, finish_change_time


@api_view(["GET"])
@permission_classes([IsManagerOrBuyer])
def get_change_times_view(_):
    change_times = get_change_times()
    return Response(change_times.data)


@api_view(["POST"])
@permission_classes([IsManagerOrBuyer])
def finish_change_time_view(_):
    finish_change_time()
    return Response({"success": True})
