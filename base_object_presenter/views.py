from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.request import Request

from django.utils.decorators import method_decorator

from .permission_classes import IsAdmin
from .services import BaseServicesPresenter


class BaseViewsPresenter:
    services: BaseServicesPresenter
    permission_class: BasePermission = IsAdmin

    @method_decorator(api_view(["GET"]))
    def get_many_view(self, request: Request) -> Response:
        objs = self.services.get_many(request.query_params)
        return Response(objs.data)

    @method_decorator(api_view(["GET"]))
    def get_view(self, request: Request) -> Response:
        obj = self.services.get(request.query_params.get("id"))
        return Response(obj.data)

    @method_decorator(api_view(["GET"]))
    def search_view(self, request: Request) -> Response:
        objs = self.services.search(request.query_params.get("search_input"),
                                    request.query_params.get("searching_fields"))
        return Response(objs.data)

    @method_decorator(api_view(["POST"]))
    @method_decorator(permission_classes([permission_class]))
    def delete_view(self, request: Request) -> Response:
        self.services.delete(request.data.get("id"))
        return Response({"success": True})

    @method_decorator(api_view(["POST"]))
    @method_decorator(permission_classes([permission_class]))
    def add_view(self, request: Request) -> Response:
        obj_id = self.services.add(request.data)
        return Response({"id": obj_id})

    @method_decorator(api_view(["POST"]))
    @method_decorator(permission_classes([permission_class]))
    def edit_view(self, request: Request) -> Response:
        self.services.edit(request.data.pop("id"), request.data)
        return Response({"success": True})

    @method_decorator(api_view(["POST"]))
    @method_decorator(permission_classes([permission_class]))
    def update_fields_view(self, request: Request) -> Response:
        self.services.update_fields(request.data.pop("id"), request.data)
        return Response({"success": True})
