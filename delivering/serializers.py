from rest_framework import serializers

from manager.models import Manager
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
    first_name = serializers.SerializerMethodField("get_first_name")
    last_name = serializers.SerializerMethodField("get_last_name")

    def get_first_name(self, obj):
        if obj:
            return obj.account.first_name
        return ""

    def get_last_name(self, obj):
        if obj:
            return obj.account.last_name
        return ""

    class Meta:
        model = Buyer
        fields = ['first_name', 'last_name']


class PurchaseSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField("get_status")
    buyer = BuyerSerializer(source="is_purchased_by")
    last_modified = serializers.SerializerMethodField("get_last_modified")

    def get_status(self, obj):
        return obj.get_status_display()

    def get_last_modified(self, obj):
        if obj.last_modified:
            return obj.last_modified.strftime("%d.%m.%Y, %H:%M")
        return ""

    class Meta:
        model = Purchase
        fields = ["id", "status", "replaced_by_product_image", "buyer", "last_modified"]


class OrderItemSerializer(serializers.ModelSerializer):
    purchases = PurchaseSerializer(many=True, read_only=True)
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('qr_code', 'purchases', "product")


class ManagerSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField("get_first_name")
    last_name = serializers.SerializerMethodField("get_last_name")

    def get_first_name(self, obj):
        if obj:
            return obj.account.first_name
        return ""

    def get_last_name(self, obj):
        if obj:
            return obj.account.last_name
        return ""

    class Meta:
        model = Manager
        fields = ['first_name', 'last_name']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    manager = ManagerSerializer()

    delivered_dt = serializers.SerializerMethodField("get_delivered_dt")
    def get_delivered_dt(self, obj):
        if obj.delivered_dt:
            return obj.delivered_dt.strftime("%d.%m.%Y, %H:%M")
        return ""

    sorted_dt = serializers.SerializerMethodField("get_sorted_dt")
    def get_sorted_dt(self, obj):
        if obj.sorted_dt:
            return obj.sorted_dt.strftime("%d.%m.%Y, %H:%M")
        return ""

    accepted_dt = serializers.SerializerMethodField("get_accepted_dt")
    def get_accepted_dt(self, obj):
        if obj.accepted_dt:
            return obj.accepted_dt.strftime("%d.%m.%Y, %H:%M")
        return ""

    class Meta:
        model = Order
        fields = ["id", "deliveries_qr_code", "selection_sheet_file", "company_name", "is_express", "comments",
                  "status", "is_sorting_by", "delivered_by", "total_products_count", "order_items", "manager", "delivered_dt",
                  "sorted_dt", "accepted_dt"]
