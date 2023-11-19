from typing import Mapping, MutableMapping

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, When, Q
from django.shortcuts import get_object_or_404

from base_object_presenter.services import BaseServicesPresenter
from cart.models import CartItem
from project import settings
from .models import OrderModelPresenter


class OrderServicesPresenter(BaseServicesPresenter):
    model_presenter = OrderModelPresenter()

    def calculate(self, user: User, data: Mapping):
        return self.model_presenter.calculate(user, data)

    def add_custom(self, add_request_schema: MutableMapping, files: Mapping) -> int:
        serializer = self.serializers["object_add_form"](data=add_request_schema)
        serializer.is_valid(raise_exception=True)
        return serializer.save(files=files).id

    def get_orders_counts(self, created_at__date):
        orders_counts = self.model_presenter.model.objects.filter(created_at__date=created_at__date).aggregate(
            new_orders_count=Count("id", filter=Q(status="new")),
            accepted_orders_count=Count("id", filter=Q(status="accepted"))
        )

        return orders_counts

    def accept_order(self, order_id):
        self.model_presenter.model.objects.filter(id=order_id).update(status="accepted")

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "managers_room", {"type": "managers_message", "message": {"action": "orders_count_changed"}}
        )

    def edit_custom(self, obj_id, files):
        order = get_object_or_404(self.model_presenter.model, id=obj_id)
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        for file in files:
            if file.startswith("opened_order_uploaded_deliveries_qr_code: "):
                order.deliveries_qr_code = fs.save("deliveries_qr_code/" + files[file].name, files[file])

            elif file.startswith("opened_order_uploaded_selection_sheet_file: "):
                order.selection_sheet_file = fs.save("selection_sheet_files/" + files[file].name, files[file])

            elif file.startswith("opened_order_uploaded_paid_check_file: "):
                order.paid_check_file = fs.save("paid_check_files/" + files[file].name, files[file])

            elif file.startswith("order_item_uploaded_qr_code_"):
                order_item_id = int(file.split(":")[0].split("order_item_uploaded_qr_code_")[1])
                order.order_items.filter(id=order_item_id).update(qr_code=fs.save("products_qr_code/" + files[file].name, files[file]))

        order.one_file_products_qr_codes = self.model_presenter.get_one_file_products_qr_codes(
            order.user,
            [order_item.qr_code for order_item in order.order_items.all()]
        )

        order.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "managers_room", {"type": "managers_message", "message": {"action": "order_changed", "order_id": order.id}}
        )
