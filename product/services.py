from typing import Optional, Mapping, TypeVar, Sequence

from django.contrib.auth.models import User
from django.db.models import Q, When, Case, F, Value, BooleanField, OuterRef, Exists
from django.db.models.functions import Coalesce

from user.models import FavouriteProduct
from .models import Product
from .serializers import ProductsSerializer, ProductSerializer, ProductFormSerializer

import functools

T = TypeVar("T")


def get_products(user: User, products_options_filtration: Optional[Mapping] = None,
                 products_filtration: Optional[Mapping] = None,
                 products_order_by: Optional[str] = "-id",
                 last_obj_id: Optional[Sequence] = None) -> ProductsSerializer:
    products_options_filtration = [] if not products_options_filtration else products_options_filtration
    products_filtration = {} if not products_filtration else products_filtration

    products_options_q_filter = Q()
    for option in products_options_filtration:
        for value in option["values"]:
            products_options_q_filter |= Q(options__name=option["option_name"], options__values__value=value)

    return _get_products(user, products_order_by, last_obj_id,
                         **products_filtration, q_filter=products_options_q_filter)


def get_product(user: User, product_id: int) -> ProductSerializer:
    if user.is_authenticated:
        is_favourite_case = Case(When(favourites__user__username=user.username, then=True), default=False)
    else:
        is_favourite_case = Case(When(id__gt=0, then=False))

    product = Product.objects.filter(id=product_id).prefetch_related("options__values", "images").annotate(
        is_favourite=is_favourite_case).distinct()[0]

    return ProductSerializer(product)


def delete_product(product_id: int) -> None:
    Product.objects.filter(id=product_id).delete()


def add_product(data: Mapping, files: Mapping) -> int:
    serializer = ProductFormSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save(files=files).id


def edit_product(product_id: int, data: Mapping, files: Mapping) -> None:
    product = Product.objects.filter(id=product_id)[0]
    serializer = ProductFormSerializer(product, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(files=files)


def search_products(user: User, search_input: str, last_obj_id: Sequence) -> ProductsSerializer:
    q_filter = Q()

    for word in search_input.split():
        q_filter |= Q(name__icontains=word) | Q(code__icontains=word)

    return _get_products(user, q_filter=q_filter, last_obj_id=last_obj_id)


def _get_products(user: User, order_by: str = "-id", last_obj_id: Sequence = None, q_filter: Q = Q(), **filter_query):
    if user.is_authenticated:
        # one more way: is just use favourites__user__username = user.username
        favourite_subquery = FavouriteProduct.objects.filter(
            user_id=user.pk, product_id=OuterRef('id')
        ).values('user_id')

        is_favourite_case = Coalesce(
            Exists(favourite_subquery), Value(False), output_field=BooleanField()
        )
    else:
        is_favourite_case = Case(When(id__gt=0, then=False))

    last_obj_id = last_obj_id if last_obj_id else None

    index_starts_at = 0

    if "already_fetched_products_count" in filter_query:
        index_starts_at = filter_query["already_fetched_products_count"]
        del filter_query["already_fetched_products_count"]
    elif type(last_obj_id) == int:
        q_filter &= Q(id__lt=last_obj_id)

    search_input = filter_query.get("search_input")
    if search_input:
        words = search_input.split()
        icontains_filters = [Q(name_lower__icontains=query.lower()) for query in words]
        combined_filter = functools.reduce(lambda a, b: a | b, icontains_filters)
        q_filter = q_filter & combined_filter
        del filter_query["search_input"]

    if user.is_superuser:
        products = Product.objects.prefetch_related("images").filter(q_filter, **filter_query, images__default=True).annotate(
            image=F("images__image"),
            is_favourite=is_favourite_case,
            category_name=F("category__name"),
        ).order_by(order_by, "-id").distinct().only("name", "price", "code", "is_available")[index_starts_at:index_starts_at+40]
    else:
        products = Product.objects.prefetch_related("images").filter(q_filter, **filter_query, images__default=True).annotate(
            image=F("images__image"),
            is_favourite=is_favourite_case,
            category_name=F("category__name"),
        ).order_by(order_by, "-id").distinct().only("name", "price", "code", "is_available")[index_starts_at:index_starts_at+40]

    products = ProductsSerializer(data=products, many=True)
    products.is_valid()
    return products


def change_product_is_available_status(product_id: int) -> None:
    Product.objects.filter(id=product_id).update(is_available=Case(
        When(is_available=True, then=False),
        When(is_available=False, then=True)
    ))
