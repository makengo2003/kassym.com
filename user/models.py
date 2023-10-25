from django.db import models
from django.contrib.auth.models import User

from project.utils import datetime_now


class FavouriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favourites")
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name="favourites")


class Client(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, related_name="client")
    fullname = models.CharField(max_length=255)
    password = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=255)
    created_at = models.DateField(default=datetime_now, editable=False)
    expires_at = models.DateField()
    device1 = models.CharField(max_length=255, null=True, blank=True)
    device2 = models.CharField(max_length=255, null=True, blank=True)
    ignore_device_verification = models.BooleanField(default=False)

    @property
    def is_expired(self):
        try:
            result = self.expires_at < datetime_now().date()
            return result
        except Exception as e:
            print(e)
            return False


class UserRequest(models.Model):
    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
