import functools
import json
from typing import Mapping, MutableMapping

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Q, F
from django.shortcuts import get_object_or_404

from base_object_presenter.serializers import BaseSerializer
from base_object_presenter.services import BaseServicesPresenter
from project import settings
from project.utils import datetime_now
from .model_presenter import OrderModelPresenter
from .models import OrderItem
from .serializers import CommentsSerializer


class OrderServicesPresenter(BaseServicesPresenter):
    model_presenter = OrderModelPresenter()

    def add_custom(self, add_request_schema: MutableMapping, files: Mapping) -> int:
        serializer = self.serializers["object_add_form"](data=add_request_schema)
        serializer.is_valid(raise_exception=True)
        return serializer.save(files=files).id

    def get_many(self, get_many_request_schema: MutableMapping = {}) -> BaseSerializer:
        ordering = get_many_request_schema.get("ordering", [])
        if type(ordering) == str:
            ordering = json.loads(get_many_request_schema.get("ordering", "[]"))

        filtration = get_many_request_schema.get("filtration", {})
        if type(filtration) == str:
            filtration = json.loads(get_many_request_schema.get("filtration", "{}"))

        searching = get_many_request_schema.get("searching", {})
        if type(searching) == str:
            searching = json.loads(get_many_request_schema.get("searching", "{}"))

        offset = get_many_request_schema.get("offset", 0)
        limit = get_many_request_schema.get("limit", None)

        words = searching.get("text", "").split()
        searching_filters = []
        searchable_fields = self.model_presenter.get_searchable_fields()

        for searching_field in searching.get("searching_fields", []):
            if searching_field.get("field_name") in searchable_fields:
                if searching_field.get("with__icontains"):
                    if searching_field.get("each_word"):
                        for query in words:
                            searching_filters.append(
                                Q(**{f"{searching_field['field_name']}__icontains": query.lower()}))
                    else:
                        searching_filters.append(
                            Q(**{f'{searching_field["field_name"]}__icontains': searching["text"].lower()}))
                else:
                    searching_filters.append(Q(**{searching_field["field_name"]: searching["text"].lower()}))

        if len(searching_filters) > 0:
            searching_filtration = functools.reduce(lambda a, b: a | b, searching_filters)
        else:
            searching_filtration = Q()

        request_user = getattr(settings, 'request_user', None)
        if hasattr(request_user, "manager") and filtration.get("status", None) == "accepted":
            accepted_status_q = ~Q(status="new")
            del filtration["status"]
        else:
            accepted_status_q = Q()

        get_many_query = self.model_presenter.get_many_service()
        objects = (self.model_presenter.model.objects
                   .prefetch_related(*get_many_query["prefetch_related"])
                   .select_related(*get_many_query["select_related"])
                   .filter(accepted_status_q, searching_filtration, **{**get_many_query.get("filtration"), **filtration})
                   .annotate(**get_many_query["annotate"])
                   .order_by(*ordering)
                   .only(*get_many_query["only"])
                   .distinct()[offset:limit])

        return self.serializers["objects"](objects, many=True)

    def get_orders_counts(self, created_at__date):
        orders_counts = self.model_presenter.model.objects.filter(created_at__date=created_at__date).aggregate(
            new_orders_count=Count("id", filter=Q(status="new")),
            accepted_orders_count=Count("id", filter=~Q(status="new"))
        )

        return orders_counts

    def accept_order(self, order_id):
        request_user = getattr(settings, 'request_user', None)
        self.model_presenter.model.objects.filter(id=order_id).update(status="accepted", manager=request_user.manager, accepted_dt=datetime_now())

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "managers_room", {"type": "managers_message", "message": {"action": "orders_count_changed",
                                                                      "order_id": order_id}}
        )

    def edit_custom(self, obj_id, new_comments, files):
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
                order.order_items.filter(id=order_item_id).update(qr_code=fs.save("products_qr_code/" +
                                                                                  files[file].name, files[file]))

        if new_comments:
            if order.comments:
                order.comments += "\n"
            order.comments += " - " + new_comments.strip()

        order.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "managers_room", {"type": "managers_message", "message": {
                "action": "order_changed", "order_id": order.id
            }}
        )

    def get_order_comments(self, params):
        order_id = params.get("order_id", None)

        comments = OrderItem.objects.filter(
            Q(comments__isnull=False) & ~Q(comments=""), order_id=order_id
        ).annotate(
            product_name=F("product__name"),
            comment=F("comments")
        ).only("count").distinct()

        return CommentsSerializer(comments, many=True).data
