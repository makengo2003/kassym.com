from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request

from project.utils import request_schema_validation
from product import schemas as product_schemas

from . import services, schemas


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


def change_user_fullname_view(request):
    if request.user.is_authenticated and request.method == "POST":
        services.change_user_fullname(request.user, request.POST.get("first_name", "First Name"),
                                      request.POST.get("last_name", "Last Name"))
    return redirect("/profile/")


@api_view(["POST"])
@permission_classes([IsAdminUser])
def add_client_view(request: Request) -> Response:
    client_id = services.add_client(request.data)
    return Response({"success": True, "client_id": client_id})


@api_view(["POST"])
@permission_classes([IsAdminUser])
@request_schema_validation("POST", schemas.ClientIdSchema)
def edit_client_view(request: Request) -> Response:
    client_id = services.edit_client(request.data.get("client_id"), request.data)
    return Response({"success": True, "client_id": client_id})


@api_view(["POST"])
@permission_classes([IsAdminUser])
@request_schema_validation("POST", schemas.ClientIdSchema)
def delete_client_view(request: Request) -> Response:
    services.delete_client(request.data.get("client_id"))
    return Response({"success": True})


@api_view(["GET"])
@permission_classes([IsAdminUser])
@request_schema_validation("GET", schemas.ClientIdSchema)
def get_client_view(request: Request) -> Response:
    client = services.get_client(request.query_params.get("client_id"))
    return Response(client.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def get_clients_view(request: Request) -> Response:
    clients = services.get_clients(request.query_params.get("last_obj_id", 0))
    return Response(clients.data)
