from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError, BadRequest
from django.db.models import Q

from change_time.models import ChangeTime
from change_time.serializers import ChangeTimeSerializer
from order.models import Order
from purchase.models import Purchase


def get_change_times():
    change_times = ChangeTime.objects.all().order_by("-id")[:10]
    return ChangeTimeSerializer(change_times, many=True)


def finish_change_time():
    last_change_time = ChangeTime.objects.last()

    if Order.objects.filter(created_at__date=last_change_time.dt, status="new").count() > 0:
        raise BadRequest("Для завершения смены необходимо обработать все сегодняшние заказы.")

    Purchase.objects.filter(Q(status="will_be_tomorrow") | Q(status="new")).update(status="new",
                                                                                   last_modified=last_change_time.dt)
    Purchase.objects.filter(Q(status="is_being_considered")).update(last_modified=last_change_time.dt)

    ChangeTime.objects.create(dt=last_change_time.dt + relativedelta(days=1))

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "managers_room", {"type": "managers_message", "message": {"action": "change_time_finished"}}
    )
