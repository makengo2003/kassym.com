from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from project.utils import request_schema_validation
from base_object_presenter.permission_classes import IsStaff
from supplier.permissions import IsSupplierOrCardManager
from . import services, schemas


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@request_schema_validation("GET", schemas.GetProductsRequestSchema)
def get_products_view(request: Request) -> Response:
    serialized_products = services.get_products(request.user,
                                                request.query_params.get("products_options_filtration", []),
                                                request.query_params.get("products_filtration", {}),
                                                request.query_params.get("products_order_by", "-id"),
                                                request.query_params.get("last_obj_id", []))
    return Response(serialized_products.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@request_schema_validation("GET", schemas.ProductIdSchema)
def get_product_view(request: Request) -> Response:
    serialized_product = services.get_product(request.user, request.query_params.get("product_id"))
    return Response(serialized_product.data)


@api_view(["POST"])
@permission_classes([IsSupplierOrCardManager])
@parser_classes([MultiPartParser, FormParser])
def add_product_view(request: Request) -> Response:
    product_id = services.add_product(request.data, request.FILES)
    return Response({"success": True, "product_id": product_id})


@api_view(["POST"])
@permission_classes([IsSupplierOrCardManager])
@request_schema_validation("POST", schemas.ProductIdSchema)
def delete_product_view(request: Request) -> Response:
    services.delete_product(request.data.pop("product_id"))
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsSupplierOrCardManager])
@parser_classes([MultiPartParser, FormParser])
def edit_product_view(request: Request) -> Response:
    services.edit_product(request.data.get("id"), request.data, request.FILES)
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@request_schema_validation("GET", schemas.SearchProductsRequestSchema)
def search_products_view(request: Request) -> Response:
    products = services.search_products(request.user, request.query_params.get("search_input"),
                                        request.query_params.get("last_obj_id"))
    return Response(products.data)


@api_view(["POST"])
@permission_classes([IsStaff])
@request_schema_validation("POST", schemas.ProductIdSchema)
def change_product_is_available_status_view(request: Request) -> Response:
    services.change_product_is_available_status(request.data.get("product_id"))
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_many_view(request):
    data = services.get_many(request.user, request.query_params)
    return Response(data)
