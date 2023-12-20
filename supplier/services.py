from django.db.models import Q

from product.models import Product
from supplier.models import Supplier
from supplier.serializers import ProductsSerializer


def get_products(request, query_params):
    if hasattr(request.user, "supplier"):
        supplier_filtration = Q(supplier=request.user.supplier)
    else:
        supplier_filtration = Q()

    query_params = query_params if query_params else {}
    query_params = query_params.copy()
    search = query_params.pop("search", [""])[0]
    if search:
        search_filtration = Q(name_lower__icontains=search.strip().lower()) | Q(code_lower__icontains=search.strip().lower())
    else:
        search_filtration = Q()

    offset = int(query_params.pop("offset", [0])[0])
    product_id = query_params.pop("id", [0])[0]
    if product_id:
        product_id_filtration = Q(id=product_id)
    else:
        product_id_filtration = Q()

    products = Product.objects.filter(product_id_filtration, supplier_filtration, search_filtration, **query_params).only(
        "id", "poster", "name", "code", "count", "status"
    ).order_by("-id")[offset:offset+40]

    count = Product.objects.filter(supplier_filtration, search_filtration, **query_params).only("id").count()
    return ProductsSerializer(products, many=True), count


def get_rating(good_remarks_count, bad_remarks_count):
    return round(5 - (5 * (bad_remarks_count / (((bad_remarks_count + good_remarks_count)
                                          if (bad_remarks_count + good_remarks_count) > 0 else 1)))), 1)


def get_suppliers():
    suppliers = Supplier.objects.filter(account__is_active=True).select_related("account")
    return [{"market": supplier.market, "boutique": supplier.boutique,
             "good_remarks_count": supplier.good_remarks_count, "bad_remarks_count": supplier.bad_remarks_count,
             "rating": get_rating(supplier.good_remarks_count, supplier.bad_remarks_count), "first_name": supplier.account.first_name, "last_name": supplier.account.last_name,
             "phone_number": supplier.account.username, "id": supplier.id,
             "market_display": supplier.get_market_display()} for supplier in suppliers]
