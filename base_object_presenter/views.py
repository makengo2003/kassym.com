from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.utils.decorators import method_decorator

from .permission_classes import IsAdmin, NoPermission
from .services import BaseServicesPresenter


def get_permissions_for_view(view_name):
    def _get_permissions_for_view(view):
        def wrapper(self, *args, **kwargs):
            request = args[0]

            permissions = self.permissions.get(view_name, [])
            for permission in permissions:
                if not permission().has_permission(request, view):
                    return Response({"detail": "Permission denied"}, status=403)

            return view(self, *args, **kwargs)
        return wrapper
    return _get_permissions_for_view


class BaseViewsPresenter:
    services: BaseServicesPresenter
    permissions = {
        "get": [NoPermission],
        "get_many": [NoPermission],
        "delete": [IsAdmin],
        "add": [IsAdmin],
        "edit": [IsAdmin],
        "update_fields": [IsAdmin]
    }

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get_many")
    def get_many_view(self, request: Request) -> Response:
        objs = self.services.get_many(request.query_params)
        return Response(objs.data)

    @method_decorator(api_view(["GET"]))
    @get_permissions_for_view("get")
    def get_view(self, request: Request) -> Response:
        obj = self.services.get(request.query_params.get("id"))
        return Response(obj.data)

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("delete")
    def delete_view(self, request: Request) -> Response:
        self.services.delete(request.data.get("id"))
        return Response({"success": True})

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("add")
    def add_view(self, request: Request) -> Response:
        obj_id = self.services.add(request.data)
        return Response({"id": obj_id})

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("edit")
    def edit_view(self, request: Request) -> Response:
        self.services.edit(request.data.pop("id"), request.data)
        return Response({"success": True})

    @method_decorator(api_view(["POST"]))
    @get_permissions_for_view("update_fields")
    def update_fields_view(self, request: Request) -> Response:
        self.services.update_fields(request.data.pop("id"), request.data)
        return Response({"success": True})
