from rest_framework import serializers
from order.models import OrderItem


class CommentsSerializer(serializers.ModelSerializer):
    comment = serializers.CharField()
    product_name = serializers.CharField()

    class Meta:
        model = OrderItem
        fields = ["comment", "product_name", "count"]
