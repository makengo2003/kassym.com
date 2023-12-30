import json
import random
from threading import Thread
from typing import Optional, Mapping, TypeVar, Sequence

from django.contrib.auth.models import User
from django.db.models import Q, When, Case, F, Value, BooleanField, OuterRef, Exists, Min, Max, Count
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string

from category.models import Category
from message.services import create_product_status_messages
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
        favourite_subquery = FavouriteProduct.objects.filter(
            user_id=user.pk, product_id=OuterRef('id')
        ).values('user_id')

        is_favourite_case = Coalesce(
            Exists(favourite_subquery), Value(False), output_field=BooleanField()
        )
    else:
        is_favourite_case = Case(When(id__gt=0, then=False))

    try:
        if hasattr(user, "supplier") or user.is_superuser:
            status_filtration = Q()
        else:
            status_filtration = Q(status="accepted")

        product = Product.objects.filter(status_filtration, id=product_id).select_related(
            "supplier", "supplier__account"
        ).prefetch_related("options__values", "images").annotate(
            is_favourite=is_favourite_case, category_name=F("category__name")
        ).distinct()[0]
    except:
        return ProductSerializer()

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
    q_filter = Q(name_lower__icontains=search_input.lower())

    for word in search_input.split():
        q_filter |= Q(code_lower__icontains=word.lower())

    return _get_products(user, q_filter=q_filter, last_obj_id=last_obj_id, searching=True)


def _get_products(user: User, order_by: str = "-id", last_obj_id: Sequence = None, q_filter: Q = Q(), searching: bool = False, **filter_query):
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
        icontains_filters = [Q(code_lower__icontains=query.lower()) for query in words]
        combined_filter = functools.reduce(lambda a, b: a | b, icontains_filters)
        combined_filter |= Q(name_lower__icontains=search_input.lower())
        q_filter = q_filter & combined_filter
        del filter_query["search_input"]

    if "status" in filter_query:
        status_filtration = Q(status=filter_query["status"])
    else:
        status_filtration = Q(status="accepted")

    if user.is_superuser:
        products = Product.objects.filter(q_filter, status_filtration, **filter_query).annotate(
            image=F("poster"),
            is_favourite=is_favourite_case,
            category_name=F("category__name"),
        ).order_by(order_by, "-id").distinct().only("name", "price", "code", "is_available", "count", "currency", "poster", "discount_percentage")[index_starts_at:index_starts_at+40]
    elif searching:
        products = Product.objects.filter(q_filter, status_filtration, **filter_query).annotate(
            image=F("poster"),
            is_favourite=is_favourite_case,
            category_name=F("category__name"),
        ).order_by(order_by, "-id").distinct().only("name", "price", "code", "is_available", "count", "currency", "poster", "discount_percentage")
    else:
        products = Product.objects.filter(q_filter, status_filtration, **filter_query).annotate(
            image=F("poster"),
            is_favourite=is_favourite_case,
            category_name=F("category__name"),
        ).order_by(order_by, "-id").distinct().only("name", "price", "code", "is_available", "count", "currency", "poster", "discount_percentage")[index_starts_at:index_starts_at+40]

    products = ProductsSerializer(data=products, many=True)
    products.is_valid()
    return products


def change_product_is_available_status(product_id: int) -> None:
    Product.objects.filter(id=product_id).update(is_available=Case(
        When(is_available=True, then=False),
        When(is_available=False, then=True)
    ))
    Thread(target=create_product_status_messages, args=(product_id,)).start()


def get_top_5_products_of_each_category(user):
    products = []
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

    categories = Category.objects.prefetch_related("products", "products__category").all()
    for category in categories:
        for product in category.products.annotate(
            is_favourite=is_favourite_case
        ).filter(~Q(poster=None) & ~Q(poster=''), status="accepted").order_by("-id")[:3]:
            products.append({
                "id": product.id,
                "name": product.name,
                "category_name": product.category.name,
                "price": product.price,
                "image": "/media/" + str(product.poster),
                "is_available": product.is_available,
                "count": product.count,
                "category_id": product.category.id,
                "is_favourite": product.is_favourite,
                "discount_percentage": product.discount_percentage,
                "price_with_discount": product.price - int(product.price * (product.discount_percentage / 100))
            })

    random.shuffle(products)
    return products


def get_category_info(selected_category_id):
    category_info = Product.objects.filter(category_id=selected_category_id).aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
        count=Count("id")
    )

    return category_info


def get_many(user, get_many_request_schema):
    ordering = get_many_request_schema.get("ordering", [])
    if type(ordering) == str:
        ordering = json.loads(get_many_request_schema.get("ordering", "[]"))

    filtration = get_many_request_schema.get("filtration", {})
    if type(filtration) == str:
        filtration = json.loads(get_many_request_schema.get("filtration", "{}"))

    offset = int(get_many_request_schema.get("offset", 0))
    limit = int(get_many_request_schema.get("limit", 24))

    search_input = get_many_request_schema.get("search_input", "")
    words = search_input.split()
    q_filter = Q()

    if words:
        icontains_filters = [Q(code_lower__icontains=query.lower()) for query in words]
        q_filter = functools.reduce(lambda a, b: a | b, icontains_filters)
        q_filter |= Q(name_lower__icontains=search_input.lower())

    favourite_subquery = FavouriteProduct.objects.filter(
        user_id=user.pk, product_id=OuterRef('id')
    ).values('user_id')
    is_favourite_case = Coalesce(
        Exists(favourite_subquery), Value(False), output_field=BooleanField()
    )

    count = Product.objects.filter(q_filter, **filtration, status="accepted").count()
    products = Product.objects.filter(q_filter, **filtration, status="accepted").annotate(
        is_favourite=is_favourite_case,
        image=F("poster"),
        category_name=F("category__name"),
    ).order_by(*ordering).distinct().only("id", "name", "price", "code", "is_available", "count", "currency", "poster")[offset:offset+limit]

    return {
        "count": count,
        "html": render_to_string("v2/products.html", {"user": user, "products": ProductsSerializer(products, many=True).data})
    }
