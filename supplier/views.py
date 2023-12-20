from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response

from base_object_presenter.permission_classes import IsAdmin
from .permissions import IsSupplierOrCardManager, IsAdminOrSuperAdmin
from rest_framework.parsers import MultiPartParser, FormParser
from . import services


@api_view(["GET"])
@permission_classes([IsSupplierOrCardManager])
def get_products_view(request):
    products, count = services.get_products(request, request.query_params)
    return Response({"products": products.data, "count": count})


@api_view(["GET"])
@permission_classes([IsAdminOrSuperAdmin])
def get_suppliers_view(_):
    suppliers = services.get_suppliers()
    return Response(suppliers)
