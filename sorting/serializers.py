from rest_framework import serializers

from order.models import Order, OrderItem
from product.models import Product
from purchase.models import Purchase, Buyer


class ProductSerializer(serializers.ModelSerializer):
    market = serializers.SerializerMethodField("get_market")

    def get_market(self, obj):
        return obj.get_market_display()

    class Meta:
        model = Product
        fields = '__all__'


class BuyerSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField('get_first_name')
    last_name = serializers.SerializerMethodField('get_last_name')

    def get_first_name(self, obj):
        return obj.account.first_name

    def get_last_name(self, obj):
        return obj.account.last_name

    class Meta:
        model = Buyer
        fields = ["first_name", "last_name"]


class PurchaseSerializer(serializers.ModelSerializer):
    buyer = BuyerSerializer(source="is_purchased_by")
    status_display = serializers.SerializerMethodField("get_status_display")

    def get_status_display(self, obj):
        if obj:
            return obj.get_status_display()
        return ""

    class Meta:
        model = Purchase
        fields = ["id", "status", "is_sorted", "replaced_by_product_image", "buyer", "status_display"]


class OrderItemSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True, read_only=True)
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('qr_code', 'purchases', "product")


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    client_phone_number = serializers.CharField(max_length=50, source="user.username")
    manager_phone_number = serializers.CharField(max_length=50, source="manager.account.username")
    manager_first_name = serializers.CharField(max_length=50, source="manager.account.first_name")
    manager_last_name = serializers.CharField(max_length=50, source="manager.account.last_name")

    class Meta:
        model = Order
        fields = ["id", "deliveries_qr_code", "selection_sheet_file", "company_name", "is_express", "comments",
                  "status", "is_sorting_by", "total_products_count", "order_items", "client_phone_number",
                  "manager_phone_number", "manager_first_name", "manager_last_name", "sorted_report"]
