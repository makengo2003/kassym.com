from rest_framework import serializers


class CategoryIdSchema(serializers.Serializer):
    category_id = serializers.IntegerField()


class _CategoryOrder(serializers.Serializer):
    id = serializers.IntegerField()
    index = serializers.IntegerField()


class SaveCategoriesOrderRequestSchema(serializers.Serializer):
    categories_order = _CategoryOrder(many=True)
