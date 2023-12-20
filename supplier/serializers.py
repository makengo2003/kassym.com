from rest_framework import serializers

from product.models import Product


class ProductsSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField("get_status_display")

    def get_status_display(self, obj):
        return obj.get_status_display()

    class Meta:
        model = Product
        fields = ["id", "poster", "name", "code", "count", "status", "status_display"]
