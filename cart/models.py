from django.db import models
from django.db.models import F, Value
from django.db.models.functions import Concat
from rest_framework import serializers

from base_object_presenter.models import BaseModelPresenter
from django.contrib.auth.models import User
from project import settings


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    count = models.PositiveIntegerField()


class CartModelPresenter(BaseModelPresenter):
    model = CartItem

    @staticmethod
    def get_many_service():
        request_user = getattr(settings, 'request_user', None)

        return {
            "prefetch_related": [],
            "select_related": ["product"],
            "annotate": {
                "product_name": F("product__name"),
                "product_price": F("product__price"),
                "product_poster": Concat(Value('/media/'), F('product__poster'), output_field=models.CharField()),
            },
            "only": ["id", "product_id", "count"],
            "filtration": {"user": request_user}
        }

    @staticmethod
    def get_objects_serializer_fields():
        return ["id", "count", "product_id"]

    @staticmethod
    def get_objects_serializer_extra_fields():
        return {
            "product_name": serializers.CharField(max_length=500),
            "product_price": serializers.IntegerField(),
            "product_poster": serializers.CharField(max_length=500),
        }

    @staticmethod
    def get_object_add_form_serializer_fields():
        return ["count", "product_id"]

    @staticmethod
    def get_object_add_form_serializer_extra_fields():
        return {
            "product_id": serializers.IntegerField()
        }

    def object_add_form_serializer_create(self, validated_data):
        request_user = getattr(settings, 'request_user', None)

        return self.model.objects.create(user=request_user, **validated_data)

    @staticmethod
    def get_updatable_fields():
        return ["count"]
