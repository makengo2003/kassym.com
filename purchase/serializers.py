from rest_framework import serializers
from order.models import OrderItem


class PurchaseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source="order_item__product__id")
    product_poster = serializers.CharField(max_length=500, source="order_item__product__poster")
    product_name = serializers.CharField(max_length=500, source="order_item__product__name")
    product_market = serializers.CharField(max_length=500, source="order_item__product__market")
    product_market_display = serializers.SerializerMethodField()
    product_vendor_number = serializers.CharField(max_length=55, source="order_item__product__vendor_number")
    product_boutique = serializers.CharField(max_length=500, source="order_item__product__boutique")
    product_price = serializers.IntegerField(source="order_item__product__price")
    count = serializers.IntegerField()
    check_defects_count = serializers.IntegerField()
    price_per_count = serializers.IntegerField()
    replaced_by_product_image = serializers.CharField(max_length=500)

    def get_product_market_display(self, obj):
        if obj["order_item__product__market"] == "sadovod":
            return "Садовод"
        elif obj["order_item__product__market"] == "yuzhnye_vorota":
            return "Южные ворота"
        else:
            return ""


class CommentsSerializer(serializers.ModelSerializer):
    comment = serializers.CharField()
    order_comment = serializers.CharField()
    client_phone_number = serializers.CharField()
    company_name = serializers.CharField()

    class Meta:
        model = OrderItem
        fields = ["comment", "company_name", "count", "client_phone_number", "order_comment"]
