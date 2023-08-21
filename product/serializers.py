from typing import MutableMapping

import urllib.parse
from django.db.models import Q
from rest_framework import serializers
from .models import Product, ProductImage, ProductOption, ProductOptionValue


class ProductsSerializer(serializers.ModelSerializer):
    is_favourite = serializers.BooleanField(default=False)
    image = serializers.SerializerMethodField('get_default_image', required=False)
    category_name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "code", "image", "is_favourite", "category_name", "is_available", "count"]

    def get_default_image(self, obj):
        if hasattr(obj, "image"):
            return "/media/" + obj.image
        obj_image = obj.images.filter(default=True).first()
        if obj_image:
            return obj_image.image.url
        return None


class ProductOptionValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptionValue
        fields = ["value"]


class ProductOptionSerializer(serializers.ModelSerializer):
    values = ProductOptionValueSerializer(many=True)

    class Meta:
        model = ProductOption
        fields = ["name", "values"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "default"]


class ProductSerializer(serializers.ModelSerializer):
    is_favourite = serializers.BooleanField()
    options = ProductOptionSerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, required=False)
    category_id = serializers.IntegerField()

    class Meta:
        model = Product
        exclude = ["category"]


class ProductFormSerializer(serializers.ModelSerializer):
    options = serializers.JSONField(required=False)
    images = serializers.JSONField(required=False)
    category_id = serializers.IntegerField()

    class Meta:
        model = Product
        exclude = ["category"]

    def create(self, validated_data: MutableMapping) -> Product:
        validated_images = validated_data.pop("images", [])
        validated_options = validated_data.pop("options", [])
        files = validated_data.pop("files", {})

        options = list()
        option_values = list()
        images = list()

        product = Product(**validated_data)

        for option in validated_options:
            values = option.pop("values", [])
            product_option = ProductOption(**option, product=product)
            for value in values:
                option_values.append(ProductOptionValue(product_option=product_option, value=value["value"]))
            options.append(product_option)

        for image in validated_images:
            img = image.pop("image")
            img = files.get("image: " + img, img)
            images.append(ProductImage(**image, product=product, image=img))

        product.save()
        ProductImage.objects.bulk_create(images)
        ProductOption.objects.bulk_create(options)

        options = list(ProductOption.objects.all().order_by("-id")[:len(options)])
        options.reverse()

        for option_value in option_values:
            for option in options:
                if option.name == option_value.product_option.name:
                    option_value.product_option = option
                    break

        ProductOptionValue.objects.bulk_create(option_values)

        return product

    def update(self, product: Product, validated_data: MutableMapping) -> Product:
        options = list()
        option_values = list()
        images = list()
        files = validated_data.pop("files", {})

        for option in validated_data.pop("options", []):
            values = option.pop("values", [])
            product_option = ProductOption(**option, product=product)
            for value in values:
                option_values.append(ProductOptionValue(product_option=product_option, value=value["value"]))
            options.append(product_option)

        not_changed_images = []
        for image in validated_data.pop("images", []):
            img = files.pop("image: " + image["image"], False)

            if not img:
                not_changed_images.append(urllib.parse.unquote(image['image'].replace("/media/", "").replace("%25", "%"), encoding='utf-8'))
                continue

            image.pop("image")
            images.append(ProductImage(**image, product=product, image=img[0]))

        Product.objects.filter(id=product.pk).update(**validated_data)

        ProductImage.objects.filter(~Q(image__in=not_changed_images), product=product).delete()
        ProductImage.objects.bulk_create(images)

        ProductOption.objects.filter(product=product).delete()
        ProductOption.objects.bulk_create(options)

        options = list(ProductOption.objects.all().order_by("-id")[:len(options)])
        options.reverse()

        for option_value in option_values:
            for option in options:
                if option.name == option_value.product_option.name:
                    option_value.product_option = option
                    break

        ProductOptionValue.objects.filter(product_option__product=product).delete()
        ProductOptionValue.objects.bulk_create(option_values)

        return product
