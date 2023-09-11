from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from project.utils import request_schema_validation
from base_object_presenter.permission_classes import IsStaff
from . import services
from . import schemas


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_categories_view(request: Request) -> Response:
    serialized_categories = services.get_categories(get_all=request.user.is_superuser)
    return Response(serialized_categories.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@request_schema_validation("GET", schemas.CategoryIdSchema)
def get_category_view(request: Request) -> Response:
    serialized_category = services.get_category(request.query_params.get("category_id"))
    return Response(serialized_category.data)


@api_view(["POST"])
@permission_classes([IsStaff])
@parser_classes([MultiPartParser, FormParser])
def add_category_view(request: Request) -> Response:
    services.add_category(request.user, request.data, request.FILES.getlist(next(iter(request.FILES)))[0])
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsStaff])
@request_schema_validation("POST", schemas.CategoryIdSchema)
def delete_category_view(request: Request) -> Response:
    services.delete_category(request.data.pop("category_id"))
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsStaff])
@parser_classes([MultiPartParser, FormParser])
@request_schema_validation("POST", schemas.CategoryIdSchema)
def edit_category_view(request: Request) -> Response:
    services.edit_category(request.data.get("category_id"), request.data, request.FILES)
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsStaff])
@request_schema_validation("POST", schemas.SaveCategoriesOrderRequestSchema)
def save_categories_order_view(request: Request) -> Response:
    services.save_categories_order(request.data.get("categories_order"))
    return Response({"success": True})
