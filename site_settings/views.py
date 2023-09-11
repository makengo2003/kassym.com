from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from user.permission_classes import IsAdmin
from . import services


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_contacts_view(_):
    contacts = services.get_contacts()
    return Response(contacts.data)


@api_view(["POST"])
@permission_classes([IsAdmin])
def save_contacts_view(request):
    services.save_contacts(request.data.get("contacts", []))
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_about_us_text_view(_):
    about_us = services.get_about_us_text()
    return Response({"about_us": about_us})


@api_view(["POST"])
@permission_classes([IsAdmin])
def save_about_us_text_view(request):
    services.save_about_us_text(request.data.get("text", "about us"))
    return Response({"success": True})


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAdmin])
def save_guarantee_text_view(request):
    services.save_guarantee_text(request.FILES)
    return Response({"success": True})
