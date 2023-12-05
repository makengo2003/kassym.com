from django.db import models
from django.contrib.auth.models import User

from order.models import OrderItem
from project.utils import datetime_now


class Buyer(models.Model):
    account = models.OneToOneField(User, on_delete=models.PROTECT, related_name="buyer")


PURCHASE_STATUSES = (("new", "В обработке"), ("purchased", "Куплен"),
                     ("not_available", "Нет в наличий"),
                     ("will_be_tomorrow", "Будет завтра"),
                     ("replaced", "Заменён"),
                     ("is_being_considered", "Рассматривается"))


def get_main_buyer():
    return Buyer.objects.get(account__username="+77777777773").id


class Purchase(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="purchases")
    status = models.CharField(max_length=50, default="new", choices=PURCHASE_STATUSES)
    price_per_count = models.PositiveIntegerField(default=0)
    replaced_by_product_image = models.ImageField(upload_to="replaced_by_product_image/", null=True, blank=True)
    is_sorted = models.BooleanField(default=False, null=True, blank=True)
    last_modified = models.DateTimeField(default=datetime_now)
    is_purchased_by = models.ForeignKey(Buyer, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.order_item.product.name
