import json
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django_bulk_update.helper import bulk_update

from change_time.models import ChangeTime
from order.models import Order, OrderReport
from project import settings
from project.utils import datetime_now
from purchase.models import Purchase
from .serializers import OrderSerializer


def get_orders(status, id):
    filtration = {}
    purchase_status_filtration = None

    if status:
        filtration["status"] = status
        purchase_status_filtration = Q()

    if id:
        filtration["id"] = id
        purchase_status_filtration = Q()

    orders = Order.objects.filter(
        purchase_status_filtration, **filtration, created_at__date__lt=ChangeTime.objects.last().dt
    ).prefetch_related(
        "order_items", "order_items__purchases", "order_items__product",
        "order_items__purchases__is_purchased_by__account",
        "manager", "user", "reports"
    ).select_related("manager", "user").order_by("-is_express", "id").distinct()

    return OrderSerializer(orders, many=True).data


def start_to_sort(id, fullname):
    Order.objects.filter(id=id).update(is_sorting_by=fullname, status="is_sorting")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": id}}
    )


def save_sorting(order_id, sorted_purchases, reports, files):
    sorted_purchases_ids = json.loads(sorted_purchases)
    reports = json.loads(reports)

    order_reports = []

    for report in reports:
        file = files.get(report)
        order_reports.append(OrderReport(order_id=order_id, report=file))

    OrderReport.objects.bulk_create(order_reports)
    Purchase.objects.filter(~Q(id__in=sorted_purchases_ids), order_item__order_id=order_id).update(is_sorted=False)
    Purchase.objects.filter(order_item__order_id=order_id, id__in=sorted_purchases_ids).update(is_sorted=True)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": order_id}}
    )


def finish_sorting(order_id):
    request_user = getattr(settings, 'request_user', None)
    Order.objects.filter(id=order_id).update(status="sorted", is_sorting_by=request_user.first_name + " " + request_user.last_name, sorted_dt=datetime_now())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": order_id}}
    )
