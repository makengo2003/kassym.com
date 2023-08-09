from typing import Optional, Mapping, Sequence

from django.contrib.auth.models import User
from django.db.models import F, Min, Max, Count
from django.shortcuts import get_object_or_404

from .models import Category
from .serializers import CategorySerializer, CategoryFormSerializer


def get_categories(get_all: Optional[bool] = False, serialize: Optional[bool] = True) -> CategorySerializer:
    if get_all:
        categories = Category.objects.prefetch_related("filtration__values").all().order_by("index").annotate(products_count=Count("products__id"))
    else:
        categories = Category.objects.filter(is_available=True).order_by("index").annotate(products_count=Count("products__id"))

    if serialize:
        categories = CategorySerializer(data=categories, many=True)
        categories.is_valid()
        return categories
    return categories


def get_category(category_id: int) -> CategorySerializer:
    category = Category.objects.prefetch_related("filtration__values", "products").annotate(
        min_price=Min(F("products__price")),
        max_price=Max(F("products__price"))
    ).filter(id=category_id)[0]

    return CategorySerializer(category)


def add_category(admin: User, data: Mapping, poster_file) -> None:
    serializer = CategoryFormSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(admin=admin, poster_file=poster_file)


def delete_category(category_id: int) -> None:
    Category.objects.filter(id=category_id).delete()


def edit_category(category_id: int, data: Mapping, poster_files) -> None:
    category = get_object_or_404(Category, id=category_id)

    if len(poster_files) == 0:
        poster_file = None
    else:
        poster_file = poster_files.getlist(next(iter(poster_files)))[0]

    serializer = CategoryFormSerializer(category, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(poster_file=poster_file)


def save_categories_order(categories_order: Sequence) -> None:
    categories_order_dict = {}

    for category_order in categories_order:
        categories_order_dict[category_order["id"]] = category_order["index"]

    categories = Category.objects.filter(id__in=[category_id for category_id in categories_order_dict.keys()])
    for category in categories:
        category.index = categories_order_dict[category.id]

    Category.objects.bulk_update(categories, ["index"])
