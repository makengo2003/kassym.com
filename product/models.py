from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User


class Product(models.Model):
    category = models.ForeignKey("category.Category", on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=500)
    name_lower = models.CharField(max_length=500, null=True, editable=False, blank=True)
    code_lower = models.CharField(max_length=500, null=True, editable=False, blank=True)
    description = models.TextField()
    price = models.PositiveIntegerField(editable=False)
    discount_percentage = models.PositiveIntegerField(blank=True, default=0)
    is_available = models.BooleanField(default=True)
    code = models.CharField(max_length=50, default="", blank=True)
    vendor_number = models.CharField(max_length=50, null=True, blank=True)
    boutique = models.CharField(max_length=500, null=True, blank=True)
    height = models.CharField(max_length=50, null=True, blank=True)
    width = models.CharField(max_length=50, null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=10, default="ru", choices=(("kz", "KZ"), ("ru", "RU")))
    poster = models.ImageField(upload_to="products_posters/", null=True, editable=False, blank=True)
    market = models.CharField(max_length=255, null=True, blank=True, choices=(("sadovod", "Садовод"), ("yuzhnye_vorota", "Южные ворота")))
    status = models.CharField(max_length=255, default="new", choices=(("new", "В обработке"), ("accepted", "Активный"), ("canceled", "Отклоненный")), null=True, blank=True)
    supplier = models.ForeignKey("supplier.Supplier", on_delete=models.PROTECT, null=True, blank=True, related_name="products")
    card_manager = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    supplier_price = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower() if self.name else None
        self.code_lower = self.code.lower() if self.name else None
        return super().save(*args, **kwargs)


class ProductImage(models.Model):
    image = models.ImageField(upload_to="products_images/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_query_name="images",
                                related_name="images")
    default = models.BooleanField(default=False)


class ProductOption(models.Model):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_query_name="options",
                                related_name="options")


class ProductOptionValue(models.Model):
    product_option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_query_name="values",
                                       related_name="values")
    value = models.CharField(max_length=255)
