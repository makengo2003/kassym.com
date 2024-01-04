from rest_framework.decorators import permission_classes, api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsUser
from manager.permissions import IsManager
from . import services


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsUser])
def add_message_view(request):
    services.add_message(request.user, request.data, request.FILES)
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsManager])
def get_chats_view(request):
    chats = services.get_chats(request.query_params.get("search_input", None))
    return Response(chats)
