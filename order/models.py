from django.db import models

from manager.models import Manager
from project.utils import datetime_now
from django.contrib.auth.models import User


class Order(models.Model):
    created_at = models.DateTimeField(default=datetime_now, editable=False)
    status = models.CharField(max_length=100, default="new", choices=(("new", "В обработке"), ("accepted", "Принят"), ("is_sorting", "Сортируется"), ("sorted", "Сортирован"), ("delivered", "Отправлен"), ("canceled", "Отменен")),
                              blank=True)
    company_name = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    manager = models.ForeignKey(Manager, on_delete=models.PROTECT, null=True, blank=True)
    deliveries_qr_code = models.FileField(upload_to="deliveries_qr_code/")
    selection_sheet_file = models.FileField(upload_to="selection_sheet_files/")
    is_express = models.BooleanField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    paid_check_file = models.FileField(upload_to="paid_check_files/")

    ruble_rate = models.FloatField()
    total_products_price = models.PositiveIntegerField()
    total_sum_in_tenge = models.FloatField()
    total_sum_in_ruble = models.PositiveIntegerField()

    total_products_count = models.PositiveIntegerField()
    service_price_per_count = models.PositiveIntegerField()
    express_price_per_count = models.PositiveIntegerField()
    total_service_price = models.PositiveIntegerField()
    specific_product = models.BooleanField()
    price_for_specific_product = models.PositiveIntegerField()

    is_sorting_by = models.CharField(max_length=500, null=True, blank=True)
    delivered_by = models.CharField(max_length=500, null=True, blank=True)
    sorted_dt = models.DateTimeField(null=True, blank=True)
    accepted_dt = models.DateTimeField(null=True, blank=True)
    canceled_dt = models.DateTimeField(null=True, blank=True)
    delivered_dt = models.DateTimeField(null=True, blank=True)
    sorted_report = models.ImageField(upload_to="order_is_sorted_reports/", null=True, blank=True)

    is_same_with_last_order = models.BooleanField(default=False, null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT)
    count = models.PositiveIntegerField()
    qr_code = models.FileField(upload_to="products_qr_code/")
    product_price = models.PositiveIntegerField()
    total_price = models.PositiveIntegerField()
    comments = models.TextField(null=True, blank=True)


class OrderReport(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reports")
    report = models.FileField(upload_to="order_reports/")
