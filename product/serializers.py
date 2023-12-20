from typing import MutableMapping

from django.core.files.storage import FileSystemStorage
from django_bulk_update.helper import bulk_update
from rest_framework import serializers

from project import settings
from supplier.models import Supplier
from supplier.services import get_rating
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


class SupplierSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    def get_phone_number(self, obj):
        return obj.account.username

    first_name = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.account.first_name

    last_name = serializers.SerializerMethodField()

    def get_last_name(self, obj):
        return obj.account.last_name

    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return get_rating(obj.good_remarks_count, obj.bad_remarks_count)

    class Meta:
        model = Supplier
        fields = ["id", "phone_number", "first_name", "last_name", "rating", "good_remarks_count", "bad_remarks_count"]


class ProductSerializer(serializers.ModelSerializer):
    is_favourite = serializers.BooleanField()
    options = ProductOptionSerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, required=False)
    category_id = serializers.IntegerField()
    category_name = serializers.CharField(max_length=500)
    price_with_discount = serializers.SerializerMethodField('get_price_with_discount', required=False)
    supplier = SupplierSerializer(required=False)

    class Meta:
        model = Product
        exclude = ["category"]

    def get_price_with_discount(self, obj):
        return obj.price - int(obj.price * (obj.discount_percentage / 100))


class ProductFormSerializer(serializers.ModelSerializer):
    images = serializers.JSONField(required=False)
    category_id = serializers.IntegerField()
    supplier_input = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Product
        exclude = ["category", "supplier"]

    def get_price(self, supplier_price):
        return supplier_price + 50

    def create(self, validated_data: MutableMapping) -> Product:
        validated_data["currency"] = "ru"
        validated_images = validated_data.pop("images", [])
        files = validated_data.pop("files", {})
        images = list()

        supplier_price = validated_data.get("supplier_price")
        supplier_input = validated_data.pop("supplier_input", None)
        price = self.get_price(supplier_price)
        product = Product(**validated_data, price=price)
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        i = 0
        for image in validated_images:
            img = image.get("image")
            img = files.get(img)

            file_name = fs.save("products_images/" + img.name, img)

            if i == 0:
                product.poster = file_name
                i += 1

            image.pop("image")
            images.append(ProductImage(**image, product=product, image=file_name))

        request_user = getattr(settings, 'request_user', None)
        if hasattr(request_user, "supplier"):
            supplier = Supplier.objects.get(account=request_user)
            product.supplier = supplier
            product.market = supplier.market
            product.boutique = supplier.boutique
            product.vendor_number = request_user.username
        else:
            product.market = "sadovod"
            product.status = "accepted"

            if supplier_input:
                phone_number = supplier_input.split(", ")[0]
                supplier = Supplier.objects.filter(account__username=phone_number).first()
                if supplier:
                    product.supplier = supplier
                else:
                    product.vendor_number = phone_number

        if validated_data["count"] > 0:
            product.is_available = True
        else:
            product.is_available = False

        product.save()
        ProductImage.objects.bulk_create(images)

        return product

    def update(self, product: Product, validated_data: MutableMapping) -> Product:
        validated_data["currency"] = "ru"
        images = validated_data.pop("images", [])
        files = validated_data.pop("files", {})

        i = 0
        product_images = list(product.images.all())
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        for image in images:
            img = files.pop(image['image'], False)

            if img:
                file = img[0]
                file_name = fs.save("products_images/" + file.name, file)

                product_images[i].image = file_name
                
                if i == 0:
                    validated_data["poster"] = file_name

            i += 1

        validated_data["name_lower"] = validated_data["name"].lower()
        validated_data["code_lower"] = validated_data["code"].lower()

        request_user = getattr(settings, 'request_user', None)
        supplier_input = validated_data.pop("supplier_input", None)

        if supplier_input:
            supplier = Supplier.objects.filter(account__username=supplier_input.split(", ")[0]).first()
            validated_data["market"] = supplier.market
            validated_data["boutique"] = supplier.boutique
            validated_data["vendor_number"] = request_user.username
        else:
            supplier = product.supplier

        validated_data.pop("price", None)
        if hasattr(request_user, "supplier"):
            price = self.get_price(validated_data["supplier_price"])
            count = validated_data["count"]

            if count > 0:
                is_available = True
            else:
                is_available = False

            supplier = request_user.supplier
        else:
            price = product.price
            count = product.count
            is_available = validated_data.pop("is_available", None)

        status = validated_data.pop("status", None)
        if not status:
            status = product.status

        validated_data.pop("count", None)
        validated_data.pop("is_available", None)
        bulk_update(product_images, update_fields=["image"])
        Product.objects.filter(id=product.pk).update(**validated_data, price=price, supplier=supplier, status=status,
                                                     count=count, is_available=is_available)

        return product
