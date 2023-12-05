from rest_framework import serializers


class PurchaseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source="order_item__product__id")
    product_poster = serializers.CharField(max_length=500, source="order_item__product__poster")
    product_name = serializers.CharField(max_length=500, source="order_item__product__name")
    product_vendor_number = serializers.CharField(max_length=55, source="order_item__product__vendor_number")
    product_boutique = serializers.CharField(max_length=500, source="order_item__product__boutique")
    product_price = serializers.IntegerField(source="order_item__product__price")
    count = serializers.IntegerField()
    price_per_count = serializers.IntegerField()
    replaced_by_product_image = serializers.CharField(max_length=500)