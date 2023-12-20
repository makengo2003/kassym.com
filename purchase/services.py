from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Q, F, Case, When, Value
from django_bulk_update.helper import bulk_update

from order.models import Order, OrderItem
from product.models import Product
from project.utils import datetime_now
from supplier.models import Supplier
from .models import Purchase, PURCHASE_STATUSES
from purchase.serializers import PurchaseSerializer, CommentsSerializer
from project import settings


class PurchaseServicesPresenter:
    @staticmethod
    def get_purchases_counts(change_time):
        markets_count = Purchase.objects.filter(
            ~Q(order_item__order__status="canceled"), last_modified__date=change_time
        ).values("order_item__product__market", "order_item__product__id", "status", "price_per_count",
                 "replaced_by_product_image").annotate(
            count=Count('order_item__product__id')
        )

        purchases_count = {}

        for market_count in markets_count:
            market = market_count['order_item__product__market']

            if not market:
                market = "china"

            purchases_count[market] = \
                purchases_count.get(market, 0) + 1

        return purchases_count

    @staticmethod
    def get_purchases(change_time, market, status):
        request_user = getattr(settings, 'request_user', None)
        change_time_filtration = Q(last_modified__date=change_time)

        if hasattr(request_user, "manager"):
            category = Q()
            market_filtration = Q()
        else:
            if market == "china":
                category = Q(order_item__product__category_id=7)
                market_filtration = Q(order_item__product__market=None)
            else:
                category = Q()
                market_filtration = Q(order_item__product__market=market)

        products = Purchase.objects.filter(
            category,
            ~Q(order_item__order__status="canceled"),
            market_filtration,
            change_time_filtration,
            status=status,
        ).values(
            "order_item__product__id", "order_item__order__is_express",
            "order_item__product__boutique", "order_item__product__poster", "order_item__product__name",
            "order_item__product__vendor_number", "order_item__product__price", "price_per_count",
            "replaced_by_product_image"
        ).annotate(count=Count("id")).distinct().order_by("-order_item__order__is_express",
                                                          'order_item__product__boutique',
                                                          '-order_item__product__id')

        return PurchaseSerializer(products, many=True)

    @staticmethod
    def make_purchase(data, files):
        last_modified = data["change_time"]
        purchases = list(Purchase.objects.filter(~Q(order_item__order__status="canceled"),
                                                 order_item__product_id=int(data["product_id"]), status=data["status"],
                                                 last_modified__date=last_modified
                                                 ).prefetch_related(
            "order_item__order__user__client"
        ).only("id", "status", "is_purchased_by", "price_per_count", "last_modified", "replaced_by_product_image"))

        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        file = files.get(data['replaced_by_product_image'], "")
        if file:
            saved_file_name = fs.save("replaced_by_product_image/" + file.name, file)
        else:
            saved_file_name = ""

        is_being_considered_report = {
            "product_poster": Product.objects.filter(id=data["product_id"]).only("poster").first().poster.url,
            "replaced_by_product_image": saved_file_name,
            "clients": []
        }
        clients = {}

        i = 0
        replaced_found = False
        request_user = getattr(settings, 'request_user', None)
        bad_remark = False

        for status in PURCHASE_STATUSES:
            for j in range(int(data.get(status[0] + "_count", 0))):
                if status[0] == "replaced" or status[0] == "not_available":
                    bad_remark = True
                elif status[0] == "purchased":
                    bad_remark = False

                purchases[i].is_purchased_by = request_user.buyer
                purchases[i].price_per_count = data["price_per_count"]
                purchases[i].last_modified = last_modified

                if status[0] == "replaced":
                    replaced_found = True
                    purchases[i].status = "is_being_considered"
                    purchases[i].replaced_by_product_image = saved_file_name

                    phone_number = purchases[i].order_item.order.user.username
                    if clients.get(phone_number):
                        clients[phone_number]["product_count"] += 1
                    else:
                        clients[phone_number] = {
                            "product_count": 1,
                            "fullname": purchases[i].order_item.order.user.client.fullname
                        }
                else:
                    purchases[i].status = status[0]

                i += 1

        bulk_update(purchases, update_fields=["status", "price_per_count", "replaced_by_product_image", "last_modified",
                                              "is_purchased_by"])

        if bad_remark:
            Supplier.objects.filter(products__id=data["product_id"]).update(bad_remarks_count=F("bad_remarks_count") + Value(1))
        else:
            Supplier.objects.filter(products__id=data["product_id"]).update(good_remarks_count=F("good_remarks_count") + Value(1))

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "buyers_room", {"type": "buyers_message", "message": {"action": "purchases_count_changed",
                                                                  "product_id": data["product_id"]}}
        )

        for key, value in clients.items():
            is_being_considered_report["clients"].append({
                "phone_number": key,
                "fullname": clients[key]["fullname"],
                "product_count": clients[key]["product_count"],
            })

        if replaced_found:
            return {"success": True, "is_being_considered_report": is_being_considered_report}
        return {"success": True}

    def save_is_being_considered_purchases(self, data):
        Purchase.objects.filter(id__in=data["replaced_purchases_ids"]).update(status="replaced", price_per_count=int(
            data["price_per_count"]))
        Purchase.objects.filter(id__in=data["not_available_purchases_ids"]).update(status="not_available",
                                                                                   replaced_by_product_image=None)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "buyers_room", {"type": "buyers_message", "message": {"action": "purchases_count_changed",
                                                                  "product_id": data["product_id"]}}
        )

    def get_is_being_considered_purchase(self, query_params):
        product_id = query_params.get("id")
        change_time = query_params.get("change_time")

        product = Product.objects.filter(id=product_id).values("poster", "vendor_number", "boutique", "price").first()
        purchases = Purchase.objects.filter(~Q(order_item__order__status="canceled"),
                                            order_item__product__id=product_id, last_modified=change_time,
                                            status="is_being_considered"
                                            ).prefetch_related("order_item__order__user__client").only(
            "id", "order_item__order__user__username", "order_item__order__user__client__fullname",
            "replaced_by_product_image"
        )

        return {
            "product_poster": "/media/" + product["poster"],
            "count": len(purchases),
            "product_vendor_number": product["vendor_number"],
            "product_boutique": product["boutique"],
            "product_price": product["price"],
            "replaced_by_product_image": purchases[0].replaced_by_product_image.url,
            "price_per_count": 0,
            "purchases": [{"id": purchase.id,
                           "client_fullname": purchase.order_item.order.user.client.fullname,
                           "client_phone_number": purchase.order_item.order.user.username,
                           "status": "replaced"}
                          for purchase in purchases]
        }

    def get_purchase_comments(self, params):
        change_time = params.get("change_time", None)
        status = params.get("status", None)
        product_id = params.get("product_id", None)

        comments = OrderItem.objects.filter(~Q(order__status="canceled"),
            Q(comments__isnull=False) & ~Q(comments=""), purchases__last_modified__date=change_time, purchases__status=status,
            product_id=product_id
        ).annotate(
            client_phone_number=F("order__user__username"),
            company_name=F("order__company_name"),
            comment=F("comments"),
            order_comment=F("order__comments")
        ).only("count").distinct()

        return CommentsSerializer(comments, many=True).data

    def get_purchase_for_manager(self, product_id, change_time, status):
        product = Product.objects.filter(id=product_id).values("id", "poster", "name").first()
        orders = Order.objects.filter(
            ~Q(status="canceled"),
            order_items__purchases__last_modified=change_time,
            order_items__purchases__status=status,
            order_items__product__id=product_id,
        ).annotate(
            product_count=Count("order_items__purchases__id", filter=Q(order_items__purchases__status=status))
        ).prefetch_related("user", "user__client").distinct()

        result = {
            "product_id": product["id"],
            "product_poster": "/media/" + product["poster"],
            "product_name": product["name"],
            "clients": [{"fullname": order.user.client.fullname,
                         "phone_number": order.user.username, "product_count": order.product_count}
                        for order in orders]
        }

        if status == "is_being_considered":
            result["replaced_by_product_image"] = Purchase.objects.filter(order_item__order_id=orders[0].id, status="is_being_considered").only("replaced_by_product_image").first().replaced_by_product_image.url

        return result

    def get_purchased_product_orders(self, product_id, status, change_time):
        filtration = Q(order_items__purchases__status=status) & Q(order_items__product__id=product_id) & Q(order_items__purchases__last_modified__date=change_time)

        orders = Order.objects.filter(
            ~Q(status="canceled"),
            filtration,
        ).annotate(
            product_count=Count("order_items__purchases__id", filter=filtration)
        ).distinct()

        return [{"id": order.id, "product_count": order.product_count} for order in orders]
