import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q, Case, When, Count, F, Value, BooleanField

from change_time.models import ChangeTime
from order.models import Order, OrderReport
from product.models import Product
from project import settings
from project.utils import datetime_now
from purchase.models import Purchase
from purchase.serializers import PurchaseSerializer
from .serializers import OrderSerializer, OrdersSerializer


def get_orders(status, order_id):
    if order_id:
        order_id_filtration = Q(id=order_id)
        has_no_available_product_filtration = Q()
    else:
        order_id_filtration = Q()
        has_no_available_product_filtration = Q(has_no_available_product=False)

    orders = Order.objects.annotate(
        has_no_available_product=Case(
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
    ).filter(
        order_id_filtration, has_no_available_product_filtration, status=status,
        created_at__date__lt=ChangeTime.objects.last().dt
    ).only("id", "company_name").order_by("-is_express", "id")

    return OrdersSerializer(orders, many=True).data


def get_order(order_id):
    order = Order.objects.filter(id=order_id).prefetch_related(
        "order_items", "order_items__purchases", "order_items__product",
        "order_items__purchases__is_purchased_by__account",
        "manager", "user", "reports"
    ).select_related("manager", "user").first()

    return OrderSerializer(order).data


def start_to_sort(id, fullname):
    Order.objects.filter(id=id).update(is_sorting_by=fullname, status="is_sorting")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": id}}
    )


def save_sorting(order_id, sorted_purchases, check_defects_checkbox, with_gift_checkbox, reports, files):
    sorted_purchases_ids = json.loads(sorted_purchases)
    check_defects_checkbox_ids = json.loads(check_defects_checkbox)
    with_gift_checkbox_ids = json.loads(with_gift_checkbox)
    reports = json.loads(reports)

    order_reports = []

    for report in reports:
        file = files.get(report)
        order_reports.append(OrderReport(order_id=order_id, report=file))

    OrderReport.objects.bulk_create(order_reports)
    Purchase.objects.filter(~Q(id__in=sorted_purchases_ids), order_item__order_id=order_id).update(is_sorted=False)
    Purchase.objects.filter(order_item__order_id=order_id, id__in=sorted_purchases_ids).update(is_sorted=True)

    Purchase.objects.filter(~Q(id__in=check_defects_checkbox_ids), order_item__order_id=order_id).update(
        check_defects_checkbox=False
    )
    Purchase.objects.filter(order_item__order_id=order_id, id__in=check_defects_checkbox_ids).update(
        check_defects_checkbox=True
    )

    Purchase.objects.filter(~Q(id__in=with_gift_checkbox_ids), order_item__order_id=order_id).update(
        with_gift_checkbox=False
    )
    Purchase.objects.filter(order_item__order_id=order_id, id__in=with_gift_checkbox_ids).update(
        with_gift_checkbox=True
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": order_id}}
    )


def finish_sorting(order_id):
    request_user = getattr(settings, 'request_user', None)
    Order.objects.filter(id=order_id).update(status="sorted",
                                             is_sorting_by=request_user.first_name + " " + request_user.last_name,
                                             sorted_dt=datetime_now())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "sorters_room", {"type": "sorters_message", "message": {"action": "orders_count_changed",
                                                                "order_id": order_id}}
    )


def get_not_sorted_products(search_input):
    if search_input:
        search_filtration = Q(order_item__product__name_lower__icontains=search_input.strip().lower()) | Q(
            order_item__product__code_lower__icontains=search_input.strip().lower())
    else:
        search_filtration = Q()

    products = Purchase.objects.filter(
        search_filtration,
        ~Q(order_item__order__status="canceled") & ~Q(order_item__order__status="sorted"),
        (Q(status="purchased") | Q(status="replaced")),
        is_sorted=False
    ).values(
        "order_item__product__id", "order_item__order__is_express",
        "order_item__product__boutique", "order_item__product__poster", "order_item__product__name",
        "order_item__product__vendor_number", "order_item__product__price", "price_per_count",
        "replaced_by_product_image"
    ).annotate(count=Count("id"), check_defects_count=Count("id", filter=Q(check_defects=True))).distinct().order_by(
        "-order_item__order__is_express",
        'order_item__product__boutique',
        '-order_item__product__id')

    return PurchaseSerializer(products, many=True)


def get_not_sorted_product(product_id):
    filtration = ((Q(order_items__purchases__status="purchased") | Q(order_items__purchases__status="replaced")) &
                  (Q(order_items__purchases__is_sorted=False) & Q(order_items__product__id=product_id)))

    orders = Order.objects.filter(
        ~Q(status="canceled"),
        filtration,
    ).annotate(
        product_count=Count("order_items__purchases__id", filter=filtration)
    ).distinct()

    return [{"id": order.id, "product_count": order.product_count} for order in orders]
