from datetime import datetime
from threading import Thread

import PyPDF2
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.storage import FileSystemStorage
from django.db.models import Prefetch, Case, When, F, Value, CharField, Count, BooleanField
from django.db.models.functions import Concat
from rest_framework import serializers

from base_object_presenter.models import BaseModelPresenter
from cart.models import CartItem
from purchase.models import Purchase
from .models import Order, OrderItem
from .services import calculate
from product.models import Product
from project import settings


class FormattedDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        return value.strftime('%d.%m.%Y, %H:%M')

    def to_internal_value(self, value):
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


class OrderModelPresenter(BaseModelPresenter):
    model = Order

    @staticmethod
    def get_many_service():
        request_user = getattr(settings, 'request_user', None)

        if hasattr(request_user, "client"):
            filtration = {"user_id": request_user.id}
        else:
            filtration = {}

        product_prefetch_only_fields = Prefetch("order_items__product",
                                                queryset=Product.objects.only("id", "poster", "name", "code", "price",
                                                                              "category_id"))
        cart_item_prefetch_only_fields = Prefetch("order_items",
                                                  queryset=OrderItem.objects.only("id", "count", "qr_code",
                                                                                  "order_id", "product_id"))
        return {
            "prefetch_related": [cart_item_prefetch_only_fields, product_prefetch_only_fields],
            "select_related": [],
            "annotate": {
                "user_fullname": Case(
                    When(user__client__isnull=False, then=F('user__client__fullname')),
                    default=Concat(F('user__first_name'), Value(" "), F('user__last_name')),
                    output_field=CharField()
                ),
                "user_phone_number": F('user__username'),
                "has_no_available_product": Case(
                    When(
                        total_products_count=Count(
                            Case(
                                When(
                                    order_items__purchases__status='not_available',
                                    then=F('order_items__purchases__id')
                                ),
                                default=None
                            )
                        ),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            },
            "only": ["id", "created_at", "status", "company_name", "deliveries_qr_code", "selection_sheet_file",
                     "is_express", "comments", "paid_check_file", "total_products_count",
                     "total_sum_in_tenge", "is_same_with_last_order", "cancellation_reason", "sorted_report"],
            "filtration": filtration
        }

    @staticmethod
    def get_objects_serializer_fields():
        return ["id", "created_at", "status", "company_name", "deliveries_qr_code", "selection_sheet_file",
                "is_express", "comments", "paid_check_file", "total_products_count",
                "total_sum_in_tenge", "is_same_with_last_order", "cancellation_reason", "sorted_report"]

    @staticmethod
    def get_objects_serializer_extra_fields():
        return {
            "items": OrderItemSerializer(many=True, source="order_items"),
            "user_fullname": serializers.CharField(max_length=255),
            "user_phone_number": serializers.CharField(max_length=55),
            "created_at": FormattedDateTimeField(),
            "status_display": serializers.CharField(source="get_status_display"),
            "has_no_available_product": serializers.BooleanField()
        }

    @staticmethod
    def get_object_add_form_serializer_fields():
        return ["is_express", "deliveries_qr_code", "selection_sheet_file", "paid_check_file"]

    @staticmethod
    def get_object_add_form_serializer_extra_fields():
        return {
            "comments": serializers.JSONField(),
            "order_comments": serializers.CharField(required=False)
        }

    def object_add_form_serializer_create(self, validated_data):
        request_user = getattr(settings, 'request_user', None)
        cart_items = CartItem.objects.select_related("product").filter(user=request_user)

        order_items = []
        files = validated_data.pop("files")
        comments = validated_data.pop("comments", {})
        i = 0

        for qr_code in files:
            if qr_code.startswith("cart_item_qr_code_"):
                cart_item = cart_items[i]
                product_price = (cart_item.product.price - cart_item.product.price *
                                 cart_item.product.discount_percentage / 100)
                total_price = cart_item.count * product_price
                comment = comments.get(str(cart_item.id), "")
                order_items.append(
                    OrderItem(qr_code=files[qr_code], count=cart_item.count, product_id=cart_item.product_id,
                              product_price=product_price, total_price=total_price, comments=comment))
                i += 1

        additional_selection_lists = []
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        for selection_list in files:
            if selection_list.startswith("selection_list_file_"):
                file = files[selection_list]
                file_name = fs.save("selection_sheet_files/" + file.name, file)
                additional_selection_lists.append(file_name)

        file = validated_data.pop("selection_sheet_file")
        file_name = fs.save("selection_sheet_files/" + file.name, file)
        selection_sheet_file = merge_pdfs([file_name] + additional_selection_lists)

        calculated_prices = calculate(request_user,
                                      {"is_express": validated_data.get("is_express")},
                                      cart_items=cart_items)
        deliveries_qr_code = validated_data.pop("deliveries_qr_code")
        paid_check_file = validated_data.pop("paid_check_file")
        order_comments = validated_data.pop("order_comments", "")

        if hasattr(request_user, "client"):
            company_name = request_user.client.company_name
        else:
            company_name = "Менеджер"

        order = Order(user=request_user, company_name=company_name,
                      deliveries_qr_code=deliveries_qr_code,
                      selection_sheet_file=selection_sheet_file, paid_check_file=paid_check_file, comments=order_comments,
                      **validated_data, **calculated_prices)

        for order_items_obj in order_items:
            order_items_obj.order = order

        order.save()
        OrderItem.objects.bulk_create(order_items)

        order_items = OrderItem.objects.filter(order=order)
        purchases = []

        for order_item in order_items:
            purchase = Purchase(order_item=order_item)
            purchases += [purchase] * order_item.count

        Purchase.objects.bulk_create(purchases)
        CartItem.objects.filter(user=request_user).delete()

        Thread(target=self.after_making_order, args=(order,)).start()

        return order

    @staticmethod
    def after_making_order(order):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "managers_room", {"type": "managers_message", "message": {"action": "orders_count_changed",
                                                                      "order_id": order.id}}
        )

    @staticmethod
    def get_updatable_fields():
        return ["status"]


class ProductSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField("get_product_type")

    class Meta:
        model = Product
        fields = ["id", "poster", "name", "code", "price", "type"]

    def get_product_type(self, obj):
        if obj.category_id == 7:
            return "Китай"
        return "Базар"


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "count", "qr_code", "product"]


def merge_pdfs(pdf_files):
    pdf_writer = PyPDF2.PdfWriter()

    for pdf_file in pdf_files:
        with open("../media/" + pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

    with open("../media/" + pdf_files[0], 'wb') as output_file:
        pdf_writer.write(output_file)

    return pdf_files[0]
