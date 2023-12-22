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
    price = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        exclude = ["category", "supplier", "vendor_number", "market", "boutique", "name_lower", "code_lower", "poster"]

    def get_price(self, supplier_price):
        return supplier_price + 50

    def create(self, validated_data: MutableMapping) -> Product:
        validated_data["currency"] = "ru"
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        files = validated_data.pop("files", {})
        uploaded_images = validated_data.pop("images", [])
        images = list()
        supplier_input = validated_data.pop("supplier_input", None)
        request_user = getattr(settings, 'request_user', None)

        if hasattr(request_user, "supplier"):
            supplier_price = validated_data.pop("supplier_price")
            price = self.get_price(supplier_price)
        else:
            price = validated_data.pop("price")
            supplier_price = validated_data.pop("supplier_price")

        product = Product(**validated_data, price=price, supplier_price=supplier_price)

        i = 0
        for image in uploaded_images:
            img = image.pop("image")
            img = files.get(img)

            file_name = fs.save("products_images/" + img.name, img)

            if i == 0:
                product.poster = file_name
                i += 1

            images.append(ProductImage(**image, product=product, image=file_name))

        validated_data["name_lower"] = validated_data["name"].lower()
        validated_data["code_lower"] = validated_data["code"].lower()

        if hasattr(request_user, "supplier"):
            supplier = Supplier.objects.get(account=request_user)
            product.supplier = supplier
            product.market = supplier.market
            product.boutique = supplier.boutique
            product.vendor_number = request_user.username
        else:
            product.status = "accepted"

            if supplier_input:
                phone_number = supplier_input.split(", ")[0]
                supplier = Supplier.objects.filter(account__username=phone_number).first()

                if supplier:
                    product.supplier = supplier
                    product.market = supplier.market
                    product.boutique = supplier.boutique
                    product.vendor_number = supplier.account.username
                else:
                    product.vendor_number = phone_number
                    product.market = "sadovod"
            else:
                product.market = "sadovod"

        product.save()
        ProductImage.objects.bulk_create(images)

        return product

    def update(self, product: Product, validated_data: MutableMapping) -> Product:
        validated_data["currency"] = "ru"
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        files = validated_data.pop("files", {})
        product_images = list(product.images.all())

        request_user = getattr(settings, 'request_user', None)
        product_form = {}

        if validated_data["category_id"] == 7 or not product.supplier:
            price = validated_data.get("price")
            supplier_price = validated_data.get("supplier_price")
        elif hasattr(request_user, "supplier"):
            supplier_price = validated_data.get("supplier_price")
            price = self.get_price(supplier_price)
        else:
            price = product.price
            supplier_price = product.supplier_price

        i = 0
        for image in validated_data.pop("images", []):
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

        if hasattr(request_user, "supplier"):
            supplier = Supplier.objects.get(account=request_user)
            product_form["supplier"] = supplier
            product_form["market"] = supplier.market
            product_form["boutique"] = supplier.boutique
            product_form["vendor_number"] = request_user.username
        else:
            supplier_input = validated_data.pop("supplier_input", None)

            if supplier_input:
                phone_number = supplier_input.split(", ")[0]
                supplier = Supplier.objects.filter(account__username=phone_number).first()

                if supplier:
                    product_form["supplier"] = supplier
                    product_form["market"] = supplier.market
                    product_form["boutique"] = supplier.boutique
                    product_form["vendor_number"] = supplier.account.username
                else:
                    product_form["vendor_number"] = phone_number
                    product_form["market"] = "sadovod"
                    product_form["boutique"] = None
                    product_form["supplier"] = None
            else:
                product_form["market"] = "sadovod"
                product_form["vendor_number"] = None
                product_form["boutique"] = None
                product_form["supplier"] = None

        status = validated_data.pop("status", None)
        if not status:
            status = product.status

        validated_data.pop("supplier_price", None)
        validated_data.pop("price", None)

        bulk_update(product_images, update_fields=["image"])
        Product.objects.filter(id=product.pk).update(**validated_data, **product_form, price=price,
                                                     supplier_price=supplier_price, status=status)

        return product
