from typing import MutableMapping

from rest_framework import serializers
from .models import Category, CategoryFiltration, CategoryFiltrationValue


class CategoryFiltrationValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryFiltrationValue
        fields = ("value",)


class CategoryFiltrationSerializer(serializers.ModelSerializer):
    values = CategoryFiltrationValueSerializer(many=True)

    class Meta:
        model = CategoryFiltration
        fields = ("name", "values")


class CategorySerializer(serializers.ModelSerializer):
    filtration = CategoryFiltrationSerializer(many=True, required=False)
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)
    products_count = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = ("id", "is_available", "name", "poster", "filtration", "min_price", "max_price", "products_count")


class CategoryFormSerializer(serializers.ModelSerializer):
    filtration = serializers.JSONField()

    class Meta:
        model = Category
        fields = ("id", "is_available", "name", "filtration")

    def create(self, validated_data: MutableMapping) -> Category:
        category = Category(name=validated_data.get("name"), is_available=validated_data.get("is_available"),
                            poster=validated_data.get("poster_file"))
        category_filtration = list()
        category_filtration_values = list()

        for filtration in validated_data.get("filtration", []):
            category_filtration.append(CategoryFiltration(category=category, name=filtration.get("name")))

        category.save()
        CategoryFiltration.objects.bulk_create(category_filtration)
        category_filtration = list(CategoryFiltration.objects.all().order_by("-id")[:len(category_filtration)])
        category_filtration.reverse()

        for filtration in validated_data.get("filtration", []):
            i_category_filtration = None

            for i_category_filtration in category_filtration:
                if i_category_filtration.name == filtration.get("name") and i_category_filtration.category == category:
                    break

            for filtration_value in filtration.get("values"):
                category_filtration_values.append(CategoryFiltrationValue(
                    category_filtration=i_category_filtration, value=filtration_value["value"]))

        CategoryFiltrationValue.objects.bulk_create(category_filtration_values)
        return category

    def update(self, category: Category, validated_data: MutableMapping) -> Category:
        category_filtration = list()
        category_filtration_values = list()

        for filtration in validated_data.get("filtration", []):
            category_filtration.append(CategoryFiltration(category=category, name=filtration.get("name")))

        category.name = validated_data.pop("name")
        category.is_available = validated_data.pop("is_available")

        poster_file = validated_data.pop("poster_file")
        if not poster_file:
            poster_file = category.poster

        category.poster = poster_file
        category.save(update_fields=["name", "is_available", "poster"])

        CategoryFiltration.objects.filter(category=category).delete()
        CategoryFiltration.objects.bulk_create(category_filtration)

        category_filtration = list(CategoryFiltration.objects.all().order_by("-id")[:len(category_filtration)])
        category_filtration.reverse()

        for filtration in validated_data.get("filtration", []):
            i_category_filtration = None

            for i_category_filtration in category_filtration:
                if i_category_filtration.name == filtration.get("name") and i_category_filtration.category == category:
                    break

            for filtration_value in filtration.get("values"):
                category_filtration_values.append(CategoryFiltrationValue(
                    category_filtration=i_category_filtration, value=filtration_value["value"]))

        CategoryFiltrationValue.objects.filter(category_filtration__category=category).delete()
        CategoryFiltrationValue.objects.bulk_create(category_filtration_values)

        return category
