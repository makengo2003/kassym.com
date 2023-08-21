from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Product(models.Model):
    category = models.ForeignKey("category.Category", on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=500)
    name_lower = models.CharField(max_length=500, null=True, editable=False, blank=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    is_available = models.BooleanField(default=False)
    code = models.CharField(max_length=50, default="", blank=True)
    vendor_number = models.CharField(max_length=50, null=True, blank=True)
    height = models.CharField(max_length=50, null=True, blank=True)
    width = models.CharField(max_length=50, null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)
    count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower() if self.name else None
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
