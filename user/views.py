from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request

from project.utils import request_schema_validation
from product import schemas as product_schemas

from . import services, schemas
from base_object_presenter.permission_classes import IsAdmin


@api_view(["POST"])
@request_schema_validation("POST", schemas.LoginRequestSchema)
def login_view(request: Request) -> Response:
    services.login(request)
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request: Request) -> Response:
    services.change_password(request, request.user, request.data)
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@request_schema_validation("POST", product_schemas.ProductsIdsSchema)
def add_products_to_favourites_view(request: Request) -> Response:
    services.add_products_to_favourites(request.user, request.data.pop("products_ids"))
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@request_schema_validation("POST", product_schemas.ProductIdSchema)
def remove_product_from_favourites_view(request: Request) -> Response:
    services.remove_product_from_favourites(request.user, request.data.pop("product_id"))
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def clear_favourites_view(request: Request) -> Response:
    services.clear_favourites(request.user)
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_fullname_view(request):
    services.change_fullname(request.user, request.data.get("first_name", "First Name"),
                             request.data.get("last_name", "Last Name"))
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_company_name_view(request):
    services.change_company_name(request.user, request.data.get("company_name", "ИП"))
    return Response({"success": True})


@api_view(["POST"])
@permission_classes([IsAdmin])
def add_client_view(request: Request) -> Response:
    client_id = services.add_client(request.data)
    return Response({"success": True, "client_id": client_id})


@api_view(["POST"])
@permission_classes([IsAdmin])
@request_schema_validation("POST", schemas.ClientIdSchema)
def edit_client_view(request: Request) -> Response:
    client_id = services.edit_client(request.data.get("client_id"), request.data)
    return Response({"success": True, "client_id": client_id})


@api_view(["POST"])
@permission_classes([IsAdmin])
@request_schema_validation("POST", schemas.ClientIdSchema)
def delete_client_view(request: Request) -> Response:
    services.delete_client(request.data.get("client_id"))
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAdmin])
@request_schema_validation("GET", schemas.ClientIdSchema)
def get_client_view(request: Request) -> Response:
    client = services.get_client(request.query_params.get("client_id"))
    return Response(client.data)


@api_view(["GET"])
@permission_classes([IsAdmin])
def get_clients_view(request: Request) -> Response:
    clients = services.get_clients(request.query_params.get("last_obj_id", 0))
    return Response(clients.data)


@api_view(["GET"])
@permission_classes([IsAdmin])
def search_clients_view(request: Request) -> Response:
    clients = services.search_clients(request.query_params.get("clients_search_input", ""))
    return Response(clients.data)


@api_view(["POST"])
def leave_request_view(request: Request):
    services.leave_request(request.data)
    return Response({"success": True})
