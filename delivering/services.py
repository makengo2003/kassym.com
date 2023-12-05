from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from change_time.models import ChangeTime
from order.models import Order
from project.utils import datetime_now
from .serializers import OrderSerializer


def get_orders(status, id):
    filtration = {}
    limit = None

    if status:
        filtration["status"] = status

    if id:
        filtration["id"] = id

    if status == "delivered":
        limit = 500

    orders = Order.objects.filter(**filtration, created_at__date__lt=ChangeTime.objects.last().dt).prefetch_related(
        "order_items", "order_items__purchases", "order_items__purchases",
        "order_items__purchases__is_purchased_by__account"
    ).select_related("manager", "user").order_by("-is_express", "id")[:limit]

    return OrderSerializer(orders, many=True).data


def make_delivered(id, fullname):
    Order.objects.filter(id=id).update(delivered_by=fullname, status="delivered", delivered_dt=datetime_now())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "deliverymen_room", {"type": "deliverymen_message", "message": {"action": "orders_count_changed",
                                                                        "order_id": id}}
    )
