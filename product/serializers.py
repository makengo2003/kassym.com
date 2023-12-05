from typing import MutableMapping

from django.core.files.storage import FileSystemStorage
from django_bulk_update.helper import bulk_update
from rest_framework import serializers

from project import settings
from .models import Product, ProductImage, ProductOption, ProductOptionValue


class ProductsSerializer(serializers.ModelSerializer):
    is_favourite = serializers.BooleanField(default=False)
    image = serializers.SerializerMethodField('get_default_image', required=False)
    category_name = serializers.CharField(max_length=255, required=False)
    price_with_discount = serializers.SerializerMethodField('get_price_with_discount', required=False)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "code", "image", "is_favourite", "category_name", "is_available", "count",
                  "currency", "discount_percentage", "price_with_discount"]

    def get_default_image(self, obj):
        if obj.poster:
            return obj.poster.url
        return None

    def get_price_with_discount(self, obj):
        return obj.price - int(obj.price * (obj.discount_percentage / 100))


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
    category_name = serializers.CharField(max_length=500)
    price_with_discount = serializers.SerializerMethodField('get_price_with_discount', required=False)

    class Meta:
        model = Product
        exclude = ["category"]

    def get_price_with_discount(self, obj):
        return obj.price - int(obj.price * (obj.discount_percentage / 100))


class ProductFormSerializer(serializers.ModelSerializer):
    options = serializers.JSONField(required=False)
    images = serializers.JSONField(required=False)
    category_id = serializers.IntegerField()

    class Meta:
        model = Product
        exclude = ["category"]

    def create(self, validated_data: MutableMapping) -> Product:
        validated_data["currency"] = "ru"
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

        i = 0
        for image in validated_images:
            img = image.pop("image")
            img = files.get("image: " + img, img)

            if i == 0:
                product.poster = img
                i += 1

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
        validated_data["currency"] = "ru"
        options = list()
        option_values = list()
        images = validated_data.pop("images", [])
        files = validated_data.pop("files", {})

        for option in validated_data.pop("options", []):
            values = option.pop("values", [])
            product_option = ProductOption(**option, product=product)
            for value in values:
                option_values.append(ProductOptionValue(product_option=product_option, value=value["value"]))
            options.append(product_option)

        i = 0
        product_images = list(product.images.all())
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        for image in images:
            img = files.pop("image: " + image['image'], False)

            if img:
                file = img[0]
                file_name = fs.save("products_images/" + file.name, file)

                product_images[i].image = file_name
                
                if i == 0:
                    validated_data["poster"] = file_name

            i += 1

        validated_data["name_lower"] = validated_data["name"].lower()
        validated_data["code_lower"] = validated_data["code"].lower()

        bulk_update(product_images, update_fields=["image"])
        Product.objects.filter(id=product.pk).update(**validated_data)

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
