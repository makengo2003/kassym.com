from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsAdmin
from manager.permissions import IsManager
from .services import get_change_times, finish_change_time


@api_view(["GET"])
@permission_classes([IsManager])
def get_change_times_view(_):
    change_times = get_change_times()
    return Response(change_times.data)


@api_view(["POST"])
@permission_classes([IsManager])
def finish_change_time_view(_):
    finish_change_time()
    return Response({"success": True})
