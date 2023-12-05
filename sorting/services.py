import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django_bulk_update.helper import bulk_update

from change_time.models import ChangeTime
from order.models import Order
from project import settings
from project.utils import datetime_now
from purchase.models import Purchase
from .serializers import OrderSerializer


def get_orders(status, id):
    filtration = {}

    if status:
        filtration["status"] = status

    if id:
        filtration["id"] = id

    orders = Order.objects.filter(**filtration, created_at__date__lt=ChangeTime.objects.last().dt).prefetch_related(
        "order_items", "order_items__purchases", "order_items__purchases", "order_items__purchases__is_purchased_by__account"
    ).select_related("manager", "user").order_by("-is_express", "id")

    return OrderSerializer(orders, many=True).data


def start_to_sort(id, fullname):
    Order.objects.filter(id=id).update(is_sorting_by=fullname, status="is_sorting")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": id}}
    )


def save_sorting(order_id, sorted_purchases, replaced_purchases, not_available_purchases, files):
    sorted_purchases_ids = json.loads(sorted_purchases)
    replaced_purchases_ids = json.loads(replaced_purchases)
    not_available_purchases_ids = json.loads(not_available_purchases)

    replaced_purchases = Purchase.objects.filter(order_item__order_id=order_id, id__in=replaced_purchases_ids)

    fs = FileSystemStorage(location=settings.MEDIA_ROOT)

    for purchase in replaced_purchases:
        purchase.status = "replaced"
        file = files.get("replaced_" + str(purchase.id))
        purchase.replaced_by_product_image = fs.save("replaced_by_product_image/" + file.name, file)

    bulk_update(replaced_purchases, update_fields=["status", "replaced_by_product_image"])

    Purchase.objects.filter(order_item__order_id=order_id, is_sorted=True).update(is_sorted=False)
    Purchase.objects.filter(order_item__order_id=order_id, id__in=sorted_purchases_ids).update(is_sorted=True)

    Purchase.objects.filter(order_item__order_id=order_id, order_item__product__category_id=7, status="not_available").update(status="purchased")
    Purchase.objects.filter(order_item__order_id=order_id, order_item__product__category_id=7, id__in=not_available_purchases_ids).update(status="not_available")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": order_id}}
    )


def finish_sorting(id, sorted_report):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    file_name = fs.save("order_is_sorted_reports/" + sorted_report.name, sorted_report)

    request_user = getattr(settings, 'request_user', None)
    Order.objects.filter(id=id).update(status="sorted", is_sorting_by=request_user.first_name + " " + request_user.last_name, sorted_dt=datetime_now(), sorted_report=file_name)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": id}}
    )
