from rest_framework import serializers


class _ProductOptionValueSchema(serializers.Serializer):
    option_name = serializers.CharField(max_length=100)
    values = serializers.ListField(child=serializers.CharField())


class GetProductsRequestSchema(serializers.Serializer):
    products_order_by = serializers.CharField(max_length=50, default="-id", required=False)
    products_filtration = serializers.JSONField(required=False)
    products_options_filtration = serializers.JSONField(required=False)
    last_obj_id = serializers.JSONField(required=False)

    def validate_products_options_filtration(self, data):
        product_option_value_schema = _ProductOptionValueSchema(data=data, many=True)
        product_option_value_schema.is_valid(raise_exception=True)
        return product_option_value_schema.validated_data


class SearchProductsRequestSchema(serializers.Serializer):
    search_input = serializers.CharField(max_length=100)
    last_obj_id = serializers.JSONField(required=False)


class ProductIdSchema(serializers.Serializer):
    product_id = serializers.IntegerField()


class ProductsIdsSchema(serializers.Serializer):
    products_ids = serializers.ListField(child=serializers.IntegerField())
